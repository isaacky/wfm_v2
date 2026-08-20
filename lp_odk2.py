import os
import requests
import pandas as pd
from sqlalchemy import create_engine

# Load configuration from environment variables
# ODK_BASE_URL   = os.getenv("ODK_BASE_URL")
# PROJECT_ID     = os.getenv("ODK_PROJECT_ID")
# FORM_ID        = os.getenv("ODK_FORM_ID")
# ODK_USER       = os.getenv("ODK_EMAIL")      # ODK Central user email (optional if token used)
# ODK_PASSWORD   = os.getenv("ODK_PASSWORD")   # ODK Central user password (optional if token used)
# ODK_TOKEN      = os.getenv("ODK_TOKEN")      # ODK Central API token (optional alternative to email/password)
# DB_HOST        = os.getenv("DB_HOST", "localhost")
# DB_NAME        = os.getenv("DB_NAME")
# DB_USER        = os.getenv("DB_USER")
# DB_PASSWORD    = os.getenv("DB_PASSWORD")
# TABLE_NAME     = FORM_ID  # use form ID as table name by default (you can change this)

ODK_BASE_URL   = "https://rri.kplcinstitute.ac.ke/"
PROJECT_ID     = "8"
FORM_ID        = "lp_2025_2026"
ODK_USER       = "inthusa@kplc.co.ke"      # ODK Central user email (optional if token used)
ODK_PASSWORD   = "Jayden29.Facilities"   # ODK Central user password (optional if token used)
ODK_TOKEN      =''      # ODK Central API token (optional alternative to email/password)
DB_HOST        = "localhost"
DB_NAME        = "lp_2025-26"
DB_USER        = "postgres"
DB_PASSWORD    = "Jayden29.Postgres"
TABLE_NAME     = FORM_ID  # use form ID as table name by default (you can change this)



# Validate required configuration
if not ODK_BASE_URL or not PROJECT_ID or not FORM_ID:
    raise RuntimeError("Please set ODK_BASE_URL, ODK_PROJECT_ID, and ODK_FORM_ID environment variables.")
if not ((ODK_USER and ODK_PASSWORD) or ODK_TOKEN):
    raise RuntimeError("Please set either ODK_EMAIL/ODK_PASSWORD or ODK_TOKEN for authentication.")
if not (DB_NAME and DB_USER and DB_PASSWORD):
    raise RuntimeError("Please set DB_NAME, DB_USER, and DB_PASSWORD for the PostgreSQL connection.")

# Define which fields to extract from each submission.
# TODO: Replace 'field1', 'field2', ... with actual field names from your form.
fields_to_extract = ["__id", "xy", "meter_number", "customer_name"]  
# '__id' is the submission's unique identifier in OData output (same as instanceID):contentReference[oaicite:2]{index=2}.
# Include any other top-level form fields you need. Nested fields (e.g., within groups) 
# should be handled by extracting sub-fields if necessary (see below).

# Prepare authentication for ODK Central
session = requests.Session()
headers = {}
if ODK_TOKEN:
    # Use the provided token directly as a Bearer token
    headers["Authorization"] = f"Bearer {ODK_TOKEN}"
else:
    # Obtain a session token using user credentials (POST /v1/sessions):contentReference[oaicite:3]{index=3}:contentReference[oaicite:4]{index=4}
    auth_url = f"{ODK_BASE_URL.strip('/')}/v1/sessions"
    resp = session.post(auth_url, json={"email": ODK_USER, "password": ODK_PASSWORD})
    if resp.status_code != 200:
        raise RuntimeError(f"Authentication failed: {resp.text}")
    token = resp.json().get("token")
    headers["Authorization"] = f"Bearer {token}"
    # Note: The token is valid for 24 hours by default:contentReference[oaicite:5]{index=5}. For long-term use, consider re-authenticating or using a persistent token.

# Build the OData endpoint URL for the form's submissions
# OData service endpoint format: /v1/projects/{projectId}/forms/{formId}.svc/Submissions
odata_url = f"{ODK_BASE_URL.strip('/')}/v1/projects/{PROJECT_ID}/forms/{FORM_ID}.svc/Submissions"

# Fetch all submissions, handling pagination via @odata.nextLink if present:contentReference[oaicite:6]{index=6}.
all_records = []  # will accumulate all submission records (dicts)
url = odata_url
while url:
    resp = session.get(url, headers=headers)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch submissions: {resp.status_code} - {resp.text}")
    data = resp.json()
    records = data.get("value", [])
    if not records:
        break
    # If specific fields are defined, filter each record to only those fields
    for rec in records:
        # Optionally, extract nested fields if needed. Example: extract instanceID from meta.
        if "meta" in rec and isinstance(rec["meta"], dict):
            rec["instanceID"] = rec["meta"].get("instanceID")
        # Reduce the record to only the desired fields
        filtered = {field: rec.get(field) for field in fields_to_extract}
        all_records.append(filtered)
    # Check for pagination link
    next_link = data.get("@odata.nextLink")
    if next_link:
        # The next_link might be relative, so make it absolute if necessary
        if next_link.startswith("http"):
            url = next_link
        else:
            url = ODK_BASE_URL.strip("/") + next_link
    else:
        url = None

# Convert the collected records into a pandas DataFrame
df = pd.DataFrame(all_records)
if df.empty:
    print("No submissions found for the specified form.")
    exit(0)

# (Optional) Rename columns if needed to match database conventions
# e.g., rename "__id" to "submission_uuid" for clarity, or any field names that conflict with SQL keywords.
# df = df.rename(columns={"__id": "submission_uuid"})

# Create a SQLAlchemy engine for the PostgreSQL database
db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(db_url)

# Write the DataFrame to PostgreSQL.
# This will create the table if it does not exist and insert all records.
# If the table exists, new data will be appended. Use if_exists='replace' to drop and recreate the table instead.
df.to_sql(name=TABLE_NAME, con=engine, if_exists='append', index=False)
print(f"Inserted {len(df)} records into table '{TABLE_NAME}'.")
