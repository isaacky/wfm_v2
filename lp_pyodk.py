import os
import json
import psycopg2
import psycopg2.extras
from pyodk.client import Client
import pandas as pd

# --- 1. CONFIGURATION ---
# It's best practice to use environment variables for credentials
# For example: os.getenv("ODK_PASSWORD")

# ODK Central Configuration
ODK_CONFIG = {
    "base_url": "https://rri.kplcinstitute.ac.ke/",
    "username": "inthusa@kplc.co.ke",
    "password": "Jayden29.Facilities", # Use an App User password
    "project_id": 8,
    "form_id": "lp_2025_2026"
}



# PostgreSQL Database Configuration
DB_CONFIG = {
    "dbname": "lp_2025-26",
    "user": "postgres",
    "password": "Jayden29.Postgres",
    "host": "localhost",  # or your db host
    "port": "5432"
}

# The name of the table you want to save data into
TABLE_NAME = "lp_inspections_1"


def get_odk_submissions():
    """
    Connects to ODK Central and fetches all submission data for a form.
    """
    print("Step 1: Fetching data from ODK Central...")
    # try:
    #     client = Client(config=ODK_CONFIG)
    #     submissions = client.submissions.get_table()
    #     print(f"Successfully fetched {len(submissions['value'])} submissions.")
    #     return submissions["value"]
    # except Exception as e:
    #     print(f"Error fetching data from ODK Central: {e}")
    #     return None
    
    with Client(config_path='.pyodk_config.toml', cache_path='cache.toml') as client:
        submissions = client.submissions.get_table(form_id='lp_2025_2026')
        print(f"Successfully fetched {len(submissions['value'])} submissions.")
        return submissions["value"]

def prepare_database(conn):
    """
    Ensures the target table exists in the database.
    ADAPT THE COLUMN DEFINITIONS TO MATCH YOUR FORM!
    """
    print("Step 2: Preparing database table...")
    # NOTE: ODK geopoints are strings like "lat long alt accuracy"
    # It's often best to store them as TEXT or use PostGIS for geographic queries.
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        instance_id TEXT PRIMARY KEY,
        submitter_name TEXT,
        submission_date TIMESTAMPTZ,
        start TIMESTAMPTZ,
        x TEXT,
        y TEXT,
        meter_number TEXT,
        customer_name TEAXT,
        srn_number TEXT,
        account_number TEXT,
        region TEXT,
        county TEXT,
        type_of_industry TEXT,
        metering_installation TEXT,
        progaming_initial TEXT,
        progaming_final TEXT,
        meter_terminal_initial TEXT,
        meter_terminal_final TEXT,
        test_block_initial TEXT,
        test_block_final TEXT,
        meter_body_seal_initial TEXT,
        meter_body_seal_final TEXT,
        smart_meter_enclosure_initial TEXT,
        smart_meter_enclosure_final TEXT,
        amr_initial TEXT,
        amr_final TEXT,
        other_seals TEXT,
        connection_configs TEXT,
        meter_voltage_atsite TEXT,
        ct_ratio_progammed TEXT,
        ct_ratio_prog_at_meter TEXT,
        ct_ratio_installed TEXT,
        vt_ratio TEXT,
        y_n TEXT,
        ct_vt_match TEXT,
        mismatch_description TEXT,
        zera_test_done TEXT,
        error_trial_per TEXT,
        error_test_remarks TEXT,
        error_per TEXT,
        test_results_remarks TEXT,
        meter_pass_test TEXT,
        red_phase_amcorder TEXT,
        red_phase_meter TEXT,
        yellow_phase_amcorder TEXT,
        yellow_phase_meter TEXT,
        blue_phase_amcorder TEXT,
        blue_phase_meter TEXT,
        load_balancing TEXT,
        m_n_clamp_currents TEXT,
        time_actual TEXT,
        time_meter TEXT,
        date_actual TEXT,
        date_meter TEXT,
        current_180_kwh TEXT,
        memory_180_kwh TEXT,
        image_180_kwh TEXT,
        current_280_kwh TEXT,
        memory_280_kwh TEXT,
        image_280_kwh TEXT,
        current_960_kva TEXT,
        memory_960_kva TEXT,
        current_150_kwh TEXT,
        memory_150_kwh TEXT,
        current_181_kwh TEXT,
        memory_181_kwh TEXT,
        current_182_kwh TEXT,
        memory_182_kwh TEXT,
        instatenious_970_kva TEXT,
        instatenious_170_kva TEXT,
        red_phase_voltage TEXT,
        yellow_phase_voltage TEXT,
        blue_phase_voltage TEXT,
        red_phase_current TEXT,
        yellow_phase_current TEXT,
        blue_phase_current TEXT,
        power_factor TEXT,
        reading_remarks TEXT,
        solar_installation TEXT,
        solar_size TEXT,
        solar_installation_date TIMESTAMPTZ,
        overall_remarks TEXT
        declaration TEXT


    );
    """
    try:
        with conn.cursor() as cur:
            cur.execute(create_table_sql)
            conn.commit()
            print(f"Table '{TABLE_NAME}' is ready.")
    except Exception as e:
        print(f"Error creating database table: {e}")
        conn.rollback() # Roll back in case of error
        raise

def load_data_to_postgres(conn, submissions):
    """
    Loads submission data into the PostgreSQL table, skipping duplicates.
    """
    print(f"Step 3: Loading data into PostgreSQL table '{TABLE_NAME}'...")
    
    # ADAPT the INSERT statement and data mapping to match your table columns
    insert_sql = f"""
    INSERT INTO {TABLE_NAME} (
        instance_id, submitter_name, submission_date, 
        start, x,y, meter_number, customer_name, srn_number
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (instance_id) DO NOTHING;
    """
    
    records_to_insert = []
    for sub in submissions:
        xy = sub.get("gis_location",{}).get("xy").get("coordinates")[1]
        print(xy)
        # --- Data Transformation Step ---
        # Map ODK data to your table columns. Use .get() for safety.sub
        # This prevents errors if a question was not answered.
        record = (
            sub.get("__id"),                                  # ODK instanceID
            sub.get("__system", {}).get("submitterName"),      # Submitter Name from metadata
            sub.get("__system", {}).get("submissionDate"),    # Submission Date from metadata
            sub.get("start"), 
            sub.get("gis_location",{}).get("xy").get("coordinates")[0],  
            sub.get("gis_location",{}).get("xy").get("coordinates")[1],                                 # Your form's 'name' field
            sub.get("part_one", {}).get("meter_number"),                            # Your form's 'visit_date' field
            sub.get("part_one", {}).get("customer_name")                           # Your form's 'gps_location' field
        )
        records_to_insert.append(record)

    if not records_to_insert:
        print("No new records to insert.")
        return

    try:
        with conn.cursor() as cur:
            # Use execute_batch for efficient bulk insertion
            psycopg2.extras.execute_batch(cur, insert_sql, records_to_insert)
            conn.commit()
            # The cursor.rowcount will show how many rows were actually inserted (not skipped)
            print(f"Successfully processed {len(records_to_insert)} records.")
            print(f"{cur.rowcount} new record(s) were inserted into the database.")
    except Exception as e:
        print(f"Error inserting data into PostgreSQL: {e}")
        conn.rollback()
        raise

def main():
    """Main ETL function."""
    submissions = get_odk_submissions()
    
    if submissions is not None:
        conn = None
        try:
            # Connect to PostgreSQL
            conn = psycopg2.connect(**DB_CONFIG)
            
            # Ensure the table exists
            prepare_database(conn)
            
            # Load the data
            load_data_to_postgres(conn, submissions)
            
        except psycopg2.Error as e:
            print(f"Database connection error: {e}")
        finally:
            if conn:
                conn.close()
                print("Database connection closed.")

if __name__ == "__main__":
    main()