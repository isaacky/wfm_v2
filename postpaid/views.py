from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponse, StreamingHttpResponse
import csv
import datetime
import time
from datetime import timedelta, date
from .models import *
from user.models import Account, UserProfile
from main.models import County, Region
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import F, Q
from django.db.models import Count, Sum, FloatField
from django.views.decorators.cache import cache_page

from itertools import chain
from django_pandas.io import read_frame
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd
from django.db import transaction
import os
from django.db.models.functions import Cast
from django.db.models import IntegerField
from django.template.loader import get_template
from xhtml2pdf import pisa



from pyodk.client import Client

from django.conf import settings
from django.templatetags.static import static
import os

def absolute_path(relative_url):
    return os.path.join(settings.MEDIA_ROOT, relative_url.replace(settings.MEDIA_URL, ""))

@login_required(login_url="login")
def amcorder_pdf(request, pk):
    # Load full workflow in one optimized query
    amcorder = (
        Amcorder.objects
        .select_related(
            "meter",
            "user_id",
            "meter_retrieval",
            "meter_analysis",
        )
        .prefetch_related(
            "meter_analysis__anomalies"  # only if ManyToMany
        )
        .get(id=pk)
    )

    template_path = "postpaid/lp/amcorder_pdf.html"
    context = {"amcorder": amcorder,"abs": absolute_path,

}

    # Render HTML to string
    template = get_template(template_path)
    html = template.render(context)

    # Create PDF response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="amcorder_{amcorder.id}.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    return response

@login_required(login_url="login")
def amcorder_dashboard(request):
    dashboard = (
        Amcorder.objects
        .select_related(
            "meter",
            "user_id",
            "meter_retrieval",
            "meter_analysis",
        )
        .prefetch_related(
            "meter_analysis__anomalies"
        )
        .order_by("-dtadd")
    )

    return render(request, "postpaid/lp/dashboard.html", {
        "dashboard": dashboard
    })

@login_required(login_url="login")
def amcorder_analysis(request, pk):
    img = get_object_or_404(AmcorderAnalysis, meter_id=pk)


    if request.method == "POST":
        m_form = AmcorderAnalysisForm(request.POST, request.FILES, instance=img)
        if m_form.is_valid():
            zerov = m_form.save(commit=False)

            profile = request.user.userprofile
            zerov.meter = img.meter
            zerov.user_id = profile
            zerov.status = True

            zerov.save()
            m_form.save_m2m()

            messages.success(
                request, "Your Analysis Has been successfully saved."
            )
            return redirect("postpaid:amcorder-my-installed")
        messages.error(request, "Invalid form submission. Please correct the errors.")

    else:
        m_form = AmcorderAnalysisForm(instance=img)

    return render(request, "postpaid/lp/amcorder_analysis.html", {"form": m_form})

@login_required(login_url="login")
def amcorder_retrieve(request, pk):
    img = get_object_or_404(AmcorderRetrieval, meter_id=pk)


    if request.method == "POST":
        m_form = AmcorderRetrievalForm(request.POST, request.FILES, instance=img)
        if m_form.is_valid():
            zerov = m_form.save(commit=False)

            profile = request.user.userprofile
            zerov.meter = img.meter
            zerov.user_id = profile
            zerov.status = True

            zerov.save()

            messages.success(
                request, "Your Retrieval Has been successfully saved."
            )
            return redirect("postpaid:amcorder-my-installed")
        messages.error(request, "Invalid form submission. Please correct the errors.")

    else:
        m_form = AmcorderRetrievalForm(instance=img)

    return render(request, "postpaid/lp/amcorder_retrieve.html", {"form": m_form})

@login_required(login_url="login")
def search_by_lp(request):
    keyword = request.GET.get("keyword", "")

    sb_list = Largepower_accounts_2024.objects.values(
        "meterno", "id", "accountno", "customer_name"
    )

    if keyword:
        sb_list = sb_list.filter(meterno__icontains=keyword)[:10]  # limit suggestions

    context = {"data": sb_list}

    # If HTMX request → return only the suggestion list
    if request.headers.get("HX-Request"):
        return render(request, "postpaid/lp/partials/lp_autocomplete.html", context)

    # Normal page load
    return render(request, "postpaid/lp/amcorder_search.html", context)



@login_required(login_url="login")
def amcorder_install(request, pk):
    img = get_object_or_404(Amcorder, id=pk)

    if request.method == "POST":
        m_form = AmcorderForm(request.POST, request.FILES, instance=img)
        if m_form.is_valid():
            zerov = m_form.save(commit=False)

            profile = request.user.userprofile
            zerov.meter = img.meter
            zerov.user_id = profile
            zerov.region = profile.region
            zerov.county = profile.county
            zerov.status = True

            zerov.save()

            messages.success(
                request, "Your Installation Has been successfully saved."
            )
            return redirect("postpaid:amcorder-my-installed")
        messages.error(request, "Invalid form submission. Please correct the errors.")

    else:
        m_form = AmcorderForm(instance=img)

    return render(request, "postpaid/lp/amcmorder_inspect.html", {"form": m_form})

@login_required(login_url="login")
def amcorder_myinstalled(request):

    meters = (
        Amcorder.objects
        .select_related('meter','meter_retrieval','meter_analysis')
        .filter(user_id=request.user.userprofile)
        .order_by("-dtadd")
    )

    paginator = Paginator(meters, 20)
    paged_uploads = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "postpaid/lp/amcoder_myinstallations.html",
        {
            "meters": paged_uploads,
            "meters_count": meters.count(),
            "nbar": "alluploads",
        },
    )

@login_required(login_url="login")
def amcorder_installed(request):
    meters = Amcorder.objects.all().order_by("-dtadd")

    paginator = Paginator(meters, 20)
    paged_uploads = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "postpaid/lp/amcorder_installed.html",
        {
            "meters": paged_uploads,
            "meters_count": meters.count(),
            "nbar": "alluploads",
        },
    )

@login_required(login_url="login")
def amcorder_inspect(request, pk):
    img = get_object_or_404(Largepower_accounts_2024, id=pk)
    profile = request.user.userprofile
    try:
        with transaction.atomic():
            new_installation = Amcorder.objects.create(
                meter=img,
                user_id=profile,
                county=profile.county,
                region=profile.region,
            )
            AmcorderRetrieval.objects.create(meter=new_installation, user_id=profile)
            AmcorderAnalysis.objects.create(meter=new_installation, user_id=profile)
        messages.success(request, "Draft inspection created successfully.")
        return redirect("postpaid:amcorder-my-installed")

    except Exception as e:
        messages.error(request, f"Error creating inspection: {str(e)}")
        return redirect("postpaid:amcorder-search")


@login_required(login_url="login")
def search_by_lpp(request):
    # sb_list = Substation.objects.filter(county=request.user.userprofile.county)
    sb_list = Largepower_accounts_2024.objects.values('meterno','id','accountno','customer_name')

    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            sb_list = sb_list.filter(meterno__icontains=keyword)


    context = {
         'data' : sb_list,
    }
    return  render(request, 'postpaid/lp/amcorder_search.html', context)

@login_required(login_url="login")
def amcorder_search(request):
    if request.user.is_authenticated:
        user = request.user


    return render(request, 'postpaid/lp/amcorder_search.html',)

@login_required(login_url="login")
def public_lighting_target_export(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

    meters = Public_lighting_target.objects.select_related('county').filter(status=False, region=request.user.userprofile.region)

    writer.writerow(['METER NUMBER', 'ACCOUNT NUMBER', 'COUNTY','SYSTEM READING','AVG CONSUMMPTION', 'SUPPLY LOCATION', 'LONGITUDE', 'LATITUDE'])
    for meter in meters:
        writer.writerow([meter.meterno, meter.accountno, meter.county,meter.system_reading,meter.consumption, meter.supplylocation, meter.x, meter.y])

    response['Content-Disposition'] = 'attachment; filename="PUBLIC LIGHTING TARGET.csv" '
    return response


@cache_page(60 * 15)
@login_required(login_url="login")
def retrofit_dashboard(request):
    overall_inspected_t = RetrofitAccounts.objects.select_related(
        "county", "region"
    ).values('meterno', 'dtupdate', 'county', 'region').filter(status=True)

    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    def count_business_days(start_date, end_date):
        # Define a list of weekend days (Saturday and Sunday)
        weekend_days = [5, 6]  # Monday is 0 and Sunday is 6
        # Initialize a counter for business days
        business_days = 0
        target = 0
        # Iterate through each day in the date range
        current_date = start_date
        while current_date <= end_date:
            # Check if the current day is a weekend day
            if current_date.weekday() not in weekend_days:
                business_days += 1
                target += 1072
            # Move to the next day
            current_date += datetime.timedelta(days=1)
        return business_days, target

    # Test the function
    start_date = datetime.date(2025, 1, 6)
    end_date = datetime.date.today()

    result = count_business_days(start_date, end_date)

    def target_achievement():
        t_a = overall_inspected_t.count()
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Planned ToDate",
                    x=["Planned ToDate"],
                    y=[result[1]],
                ),
                go.Bar(name="Achieved ToDate", x=["Achieved ToDate"], y=[t_a]),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Target vs Achievement. Total Target = 133,939",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="No Of Retrofits",
                titlefont_size=16,
                tickfont_size=14,
            ),
            xaxis=dict(
                title="Year(2024/25)",
            ),
            legend=dict(
                bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
            ),
            barmode="group",
            bargap=0.15,  # gap between bars of adjacent location coordinates.
            bargroupgap=0.1,  # gap between bars of the same location coordinate.
        )
        fig_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return fig_plot

    def daily_trend():
        df = read_frame(overall_inspected_t)
        df["dtupdate"] = pd.to_datetime(df["dtupdate"]).dt.date
        df = df.groupby(by="dtupdate", as_index=False, sort=False)["meterno"].count()
        df = px.bar(
            df,
            x=df.dtupdate,
            y=df.meterno,
            title=f"Daily Overall Retrofitting Target = {1072}",
            text_auto=True,
            text=df.meterno,
            labels={"meterno": "Meter Count", "dtupdate": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    regional_analytics = (
        Region.objects.select_related("retrofits_region")
        .values("name")  # select_related('dc_region')
        .annotate(
            hc_target_acs=(Sum("retrofit_target", distinct=True)),
            dc_daily_target=(Sum("retrofit_daily_target", distinct=True)),
            hc_inspected=(Count("retrofits_region", distinct=True, filter=Q(retrofits_region__status=True), )),

            hc_today=Count(
                "retrofits_region",
                distinct=True,
                filter=Q(retrofits_region__dtupdate__date=today, retrofits_region__status=True),
            ),
            hc_yesturday=Count(
                "retrofits_region",
                distinct=True,
                filter=Q(retrofits_region__dtupdate__date=yesterday, retrofits_region__status=True),
            ),
            hc_yesturday_1=Count(
                "retrofits_region",
                distinct=True,
                filter=Q(retrofits_region__dtupdate__date=yesterday_1, retrofits_region__status=True),
            ),
            hc_yesturday_2=Count(
                "retrofits_region",
                distinct=True,
                filter=Q(retrofits_region__dtupdate__date=yesterday_2, retrofits_region__status=True),
            ),
            hc_yesturday_3=Count(
                "retrofits_region",
                distinct=True,
                filter=Q(retrofits_region__dtupdate__date=yesterday_3, retrofits_region__status=True),
            ),
        )
        .order_by()
    )
    county_analytics = (
        County.objects.select_related("retrofits_county")
        .values("name", "region_id")  # select_related('dc_region')
        .annotate(
            hc_target_acs=(Sum("retrofit_target", distinct=True)),
            dc_daily_target=(Sum("retrofit_daily_target", distinct=True)),
            hc_inspected=(Count("retrofits_county", distinct=True, filter=Q(retrofits_county__status=True))),
            hc_today=Count(
                "retrofits_county",
                distinct=True,
                filter=Q(retrofits_county__dtupdate__date=today, retrofits_county__status=True),
            ),
            hc_yesturday=Count(
                "retrofits_county",
                distinct=True,
                filter=Q(retrofits_county__dtupdate__date=yesterday, retrofits_county__status=True),
            ),
            hc_yesturday_1=Count(
                "retrofits_county",
                distinct=True,
                filter=Q(retrofits_county__dtupdate__date=yesterday_1, retrofits_county__status=True),
            ),
            hc_yesturday_2=Count(
                "retrofits_county",
                distinct=True,
                filter=Q(retrofits_county__dtupdate__date=yesterday_2, retrofits_county__status=True),
            ),
            hc_yesturday_3=Count(
                "retrofits_county",
                distinct=True,
                filter=Q(retrofits_county__dtupdate__date=yesterday_3, retrofits_county__status=True),
            ),
        )
        .order_by("region_id")
    )

    context = {
        "daily_trend_plot": daily_trend(),
        "target_achievement": target_achievement(),

        "regional_analytics": regional_analytics,
        "county_analytics": county_analytics,
        'yesterday': yesterday,
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,
    }

    return render(request, "postpaid/retrofits/retrofits_dashboard.html", context=context)


@login_required(login_url="login")
def retrofit_target_export(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

    meters = RetrofitAccounts.objects.filter(status=False, county=user)

    writer.writerow(['METER NUMBER', 'ACCOUNT NUMBER', 'SECTOR', 'ZONE', 'ITINERARY', 'CUSTOMER NAME', 'SUPPLY ADDRESS',
                     'LONGITUDE', 'LATITUDE'])
    for meter in meters:
        writer.writerow([meter.meterno, meter.accountno, meter.sector, meter.zone, meter.itin, meter.customer_name,
                         meter.supply_address, meter.x, meter.y])

    response['Content-Disposition'] = 'attachment; filename="RETROFIT TARGET.csv" '
    return response


@login_required(login_url="login")
def retrofitting_target(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters = RetrofitAccounts.objects.filter(status=False, county=user)
    paginator = Paginator(meters, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_pending = meters.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_pending,
        'nbar': 'alluploads'}
    return render(request, 'postpaid/retrofits/retrofit_target.html', context)


@cache_page(60 * 15)
@login_required(login_url="login")
def lp_2024_analytics(request):
    target = Largepower_accounts_2024.objects.select_related('lp_new_inspection').values('id','lp_new_inspection__save_status','lp_new_inspection__dtadd','lp_new_inspection__id','lp_new_inspection__dtupdate')
    finalised = target.filter(lp_new_inspection__save_status = True)
    odk = LPODK.objects.select_related('odk_region').values('SubmissionDate',"id")


    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    # def target_achievement():
    #     t_a = target.count()
    #     a_a = finalised.count()
    #     fig = go.Figure(
    #         data=[
    #             go.Bar(
    #                 name="Target",
    #                 x=["Target"],
    #                 y=[t_a],
    #             ),
    #             go.Bar(
    #                 name="Achieved", x=["Achieved"], y=[a_a]
    #             ),
    #         ]
    #     )
    #
    #     fig.update_layout(barmode="group")
    #     fig.update_layout(title_text="Overall Target vs Achievement")
    #     fig.update_traces(
    #         texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
    #         textposition="outside",
    #     )
    #     fig.update_layout(
    #         title="Target vs Achievement",
    #         xaxis_tickfont_size=14,
    #         yaxis=dict(
    #             title="No Of Inspections",
    #             titlefont_size=16,
    #             tickfont_size=14,
    #         ),
    #         xaxis=dict(
    #             title="Year(2024)",
    #         ),
    #         legend=dict(
    #             bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
    #         ),
    #         barmode="group",
    #         bargap=0.15,  # gap between bars of adjacent location coordinates.
    #         bargroupgap=0.1,  # gap between bars of the same location coordinate.
    #     )
    #     fig_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    #     return fig_plot

    def daily_trend():
        df = read_frame(finalised)
        df["lp_new_inspection__dtupdate"] = pd.to_datetime(df["lp_new_inspection__dtupdate"]).dt.date
        df = df.groupby(by="lp_new_inspection__dtupdate", as_index=False, sort=False)["lp_new_inspection__id"].count()
        df = px.bar(
            df,
            x=df.lp_new_inspection__dtupdate,
            y=df.lp_new_inspection__id,
            title=f"Daily Overall Inspections.",
            text_auto=True,
            text=df.lp_new_inspection__id,
            labels={"lp_new_inspection__id": "Meter Count", "lp_new_inspection__dtupdate": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    def daily_trend_odk():
        df = read_frame(odk)
        df["SubmissionDate"] = pd.to_datetime(df["SubmissionDate"]).dt.date
        df = df.groupby(by="SubmissionDate", as_index=False, sort=False)["id"].count()
        df = px.bar(
            df,
            x=df.SubmissionDate,
            y=df.id,
            title=f"Daily Overall Inspections(ODK).",
            text_auto=True,
            text=df.id,
            labels={"id": "Meter Count", "SubmissionDate": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    # def metering_status():
    #     df = read_frame(oveall_inspected)
    #     df = df.groupby(by="meteringstatus", as_index=False, sort=False)["id"].count()
    #     values = df.meteringstatus
    #     names = df.id
    #     df = px.pie(
    #         df,
    #         values=names,
    #         names=values,
    #         title="Meter Status",
    #         labels={
    #             "id": "Meter Count",
    #             "meteringstatus": "Metering Status",
    #         },
    #     )
    #     df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
    #     return df

    # def incms_status():
    #     df_validate = read_frame(oveall_inspected)
    #     df_validate = df_validate.groupby(by="validate_status", as_index=False, sort=False)["id"].count()
    #     values = df_validate.validate_status
    #     names = df_validate.id
    #     df = px.pie(
    #         df_validate,
    #         values=names,
    #         names=values,
    #         title="Meter Validation Status(WO Resolved)",
    #         labels={
    #             "id": "Meter Count",
    #             "validate_status": "InCMS Validation Status",
    #         },
    #     )
    #     df_validate_incms = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
    #     return df_validate_incms




    region_analytics = (
            Region.objects.select_related("lp_new_inspection_region","odk_region")
            .values("name", "id")  # select_related('dc_region')
            .annotate(
                lp_target=(Sum("tid_overall_target", distinct=True)),
                lp_inspected=(
                                Count(
                                    "lp_new_inspection_region",
                                    distinct=True,
                                    filter=Q(
                                        lp_new_inspection_region__save_status=True

                                    ),
                                )
                            ),
                lp_inspected_odk=(
                    Count(
                        "odk_region",
                        distinct=True,
                    )
                ),
                lp_daily_target=(Sum("tid_daily_target", distinct=True)),

                today=Count(
                    "lp_new_inspection_region",
                    distinct=True,
                    filter=Q(lp_new_inspection_region__save_status=True,lp_new_inspection_region__dtupdate=today),
                ),
                today_odk=Count(
                    "odk_region",
                    distinct=True,
                    filter=Q(odk_region__SubmissionDate=today),
                ),
                today_1=Count(
                    "lp_new_inspection_region",
                    distinct=True,
                    filter=Q(lp_new_inspection_region__save_status=True,lp_new_inspection_region__dtupdate=yesterday),
                ),
                today_1_odk=Count(
                    "odk_region",
                    distinct=True,
                    filter=Q(odk_region__SubmissionDate=yesterday),
                ),
                today_2=Count(
                    "lp_new_inspection_region",
                    distinct=True,
                    filter=Q(lp_new_inspection_region__save_status=True,lp_new_inspection_region__dtupdate=yesterday_1),
                ),
                today_2_ODK=Count(
                    "odk_region",
                    distinct=True,
                    filter=Q(odk_region__SubmissionDate=yesterday_1),
                ),
                today_3=Count(
                    "lp_new_inspection_region",
                    distinct=True,
                    filter=Q(lp_new_inspection_region__save_status=True,lp_new_inspection_region__dtupdate=yesterday_2),
                ),
                today_3_ODK=Count(
                    "odk_region",
                    distinct=True,
                    filter=Q(odk_region__SubmissionDate=yesterday_2),
                ),
                today_4=Count(
                    "lp_new_inspection_region",
                    distinct=True,
                    filter=Q(lp_new_inspection_region__save_status=True,lp_new_inspection_region__dtupdate=yesterday_3),
                ),
                today_4_ODK=Count(
                    "odk_region",
                    distinct=True,
                    filter=Q(odk_region__SubmissionDate=yesterday_3),
                ),
            )
            .order_by("name")
    )
    # county_analytics = (
    #     County.objects.select_related("region")
    #     .values("name", "id")  # select_related('dc_region')
    #     .annotate(
    #         dc_target_acs=(Sum("dc_target", distinct=True)),
    #         dc_inspected=(Count("county_elsewedy_repalcement", distinct=True)),
    #         dc_insp_faulty=(
    #             Count(
    #                 "county_elsewedy_repalcement",
    #                 distinct=True,
    #                 filter=~Q(
    #                     county_elsewedy_repalcement__meteringstatus__in=[
    #                         "faulty",
    #                         "tampered",
    #                         "bypassed",
    #                     ]
    #                 ),
    #             )
    #         ),
    #         un_validated=(
    #             Count(
    #                 "county_elsewedy_repalcement",
    #                 distinct=True,
    #                 filter=(
    #                     Q(county_elsewedy_repalcement__validate_status=False)
    #
    #                 ),
    #             )
    #         ),
    #         today=Count(
    #             "county_elsewedy_repalcement",
    #             distinct=True,
    #             filter=Q(county_elsewedy_repalcement__dtadd__date=today),
    #         ),
    #         today_1=Count(
    #             "county_elsewedy_repalcement",
    #             distinct=True,
    #             filter=Q(county_elsewedy_repalcement__dtadd__date=yesterday),
    #         ),
    #         today_2=Count(
    #             "county_elsewedy_repalcement",
    #             distinct=True,
    #             filter=Q(county_elsewedy_repalcement__dtadd__date=yesterday_1),
    #         ),
    #         today_3=Count(
    #             "county_elsewedy_repalcement",
    #             distinct=True,
    #             filter=Q(county_elsewedy_repalcement__dtadd__date=yesterday_2),
    #         ),
    #         today_4=Count(
    #             "county_elsewedy_repalcement",
    #             distinct=True,
    #             filter=Q(county_elsewedy_repalcement__dtadd__date=yesterday_3),
    #         ),
    #     )
    #     .order_by("name")
    # )




    context = {
        "daily_trend_plot": daily_trend(),
        # "target_achievement": target_achievement(),
        # "metering_status": metering_status(),
        # "metering_status_notokay": incms_status(),
        "region_analytics": region_analytics,
        "daily_trend_odk": daily_trend_odk(),
        "yesterday": yesterday,
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,
    }
    return render(request, "postpaid/lp/lp_2024_dashboard.html", context)


@login_required(login_url="login")
def lp_new_not_in_target(request):
    # userprofile = get_object_or_404(UserProfile, user=request.user)

    campaign = request.user.userprofile

    if campaign.campaign == "lp" and campaign.profiletype == 'cse':
        if request.method == "POST":
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = Largepower_accounts_2024Form(request.POST, request.FILES)

            check = Largepower_accounts_2024.objects.filter(meterno=request.POST["meterno"])
            if check:
                messages.error(request, "The Meter already exists.")
                return redirect("postpaid:lp-new-target")

            if m_form.is_valid():
                resolution = Largepower_accounts_2024()
                resolution.accountno = m_form.cleaned_data["accountno"]
                resolution.srn = m_form.cleaned_data["srn"]
                resolution.meterno = m_form.cleaned_data["meterno"]
                resolution.customer_name = m_form.cleaned_data["customer_name"]
                resolution.asigned = request.user.userprofile
                resolution.county = m_form.cleaned_data["county"]
                resolution.region = m_form.cleaned_data["region"]
                resolution.save()
                messages.success(
                    request, "The LP Account Has been successfully saved."
                )
                return redirect("postpaid:lp-new-target")
            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = Largepower_accounts_2024Form()
        context = {
            "form": m_form,
        }
    else:
        messages.error(request, "Kindly send the details to the regional LP Engineer.")
        return redirect("postpaid:lp-new-target")

    return render(request, "postpaid/lp/lp_not_in_target.html", context)


@login_required(login_url="login")
def lp_new_search_meterno_inspected_my(request):
    if request.user.is_authenticated:
        campaign = request.user.userprofile
    if campaign.campaign == 'lp':
        meters_list = Lp_new_inspection.objects.select_related('county', 'region').values('dtupdate', 'lp__zera_failed',
                                                                                          'lp__currents_mismatch',
                                                                                          'lp__ctvt_mismatch',
                                                                                          'lp__over_per',
                                                                                          'lp__inspection_status',
                                                                                          'lp__id', 'lp__srn',
                                                                                          'lp__meterno',
                                                                                          'lp__accountno',
                                                                                          'lp__customer_name',
                                                                                          'county__name').filter(
            inspectedby=campaign).order_by('-dtupdate')
        if 'keyword' in request.GET:
            keyword = request.GET["keyword"]
            if keyword:
                paged_uploads = meters_list.filter(lp__meterno__icontains=keyword)
    else:
        messages.error(request, "Access denied.")
        return redirect("main:my-dashboard")

    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/lp/lp_inspected_my.html', context)


@login_required(login_url="login")
def lp_new_search_srn_inspected_my(request):
    if request.user.is_authenticated:
        campaign = request.user.userprofile
    if campaign.campaign == 'lp':
        meters_list = Lp_new_inspection.objects.select_related('county', 'region').values('dtupdate', 'lp__zera_failed',
                                                                                          'lp__currents_mismatch',
                                                                                          'lp__ctvt_mismatch',
                                                                                          'lp__over_per',
                                                                                          'lp__inspection_status',
                                                                                          'lp__id', 'lp__srn',
                                                                                          'lp__meterno',
                                                                                          'lp__accountno',
                                                                                          'lp__customer_name',
                                                                                          'county__name').filter(
            inspectedby=campaign).order_by('-dtupdate')
        if 'keyword' in request.GET:
            keyword = request.GET["keyword"]
            if keyword:
                paged_uploads = meters_list.filter(lp__srn__icontains=keyword)
    else:
        messages.error(request, "Access denied.")
        return redirect("main:my-dashboard")

    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/lp/lp_inspected_my.html', context)


@login_required(login_url="login")
def lp_new_inspected_my(request):
    if request.user.is_authenticated:
        campaign = request.user.userprofile
    if campaign.campaign == 'lp':
        meters = Lp_new_inspection.objects.select_related('county', 'region').values('dtupdate', 'lp__zera_failed',
                                                                                     'lp__currents_mismatch',
                                                                                     'lp__ctvt_mismatch',
                                                                                     'lp__over_per',
                                                                                     'lp__inspection_status', 'lp__id',
                                                                                     'lp__srn', 'lp__meterno',
                                                                                     'lp__accountno',
                                                                                     'lp__customer_name',
                                                                                     'county__name').filter(
            inspectedby=campaign).order_by('-dtupdate')
        paginator = Paginator(meters, 10)
        page = request.GET.get('page')
        paged_uploads = paginator.get_page(page)

    else:
        messages.error(request, "Access denied.")
        return redirect("main:my-dashboard")

    context = {
        'meters': paged_uploads, }
    return render(request, 'postpaid/lp/lp_inspected_my.html', context)


@login_required(login_url="login")
def elsewedy_export_inspected_county(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    county = request.user.userprofile.county

    meters = (
        ElsewedyAccounts.objects.select_related("county")
        .filter(
            county=county,
            status=False,
        )
        .order_by("itin")
    )

    writer.writerow(
        [
            "COUNTY",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "ITIN",
            "SECTOR",
            "ZONE",
            "X",
            "Y"
        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.county,
                meter.meterno,
                meter.accountno,
                meter.itin,
                meter.sector,
                meter.zone,
                meter.x,
                meter.y
            ]
        )

    response["Content-Disposition"] = (
        'attachment; filename="ELSEWEDY_PENDING.csv" '
    )
    return response


@login_required(login_url="login")
def elsewedy_target_search_account(request):
    if request.user.is_authenticated:
        campaign = request.user.userprofile
    meters_list = ElsewedyAccounts.objects.select_related('county', 'region').values('id', 'meterno', 'accountno',
                                                                                     'customer_name',
                                                                                     'county__name').filter(
        county=campaign.county, status=False)
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {"meters": paged_uploads}
    return render(request, "postpaid/elsewedy/elsewedy_target.html", context)



@cache_page(60 * 15)
@login_required(login_url="login")
def elsewedy_replacememt_dashboard(request):
    # oveall_target = County.objects.aggregate(Sum("publiclighting_target"))

    oveall_inspected = ElsewedyReplacement.objects.values(
        "dtadd", "id", "meteringstatus", "validate_status"
    )
    overall_not_okay = oveall_inspected.exclude(
        meteringstatus__in=["okay"]
    )

    # Test the function
    start_date = datetime.date(2024, 9, 9)
    end_date = datetime.date.today()

    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    def target_achievement():
        t_a = oveall_inspected.count()
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Target",
                    x=["Target"],
                    y=[105457],
                ),
                go.Bar(
                    name="Achieved", x=["Achieved"], y=[t_a]
                ),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Target vs Achievement",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="No Of Replacements",
                titlefont_size=16,
                tickfont_size=14,
            ),
            xaxis=dict(
                title="Year(2024)",
            ),
            legend=dict(
                bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
            ),
            barmode="group",
            bargap=0.15,  # gap between bars of adjacent location coordinates.
            bargroupgap=0.1,  # gap between bars of the same location coordinate.
        )
        fig_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return fig_plot

    def daily_trend():
        df = read_frame(oveall_inspected)
        df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
        df = df.groupby(by="dtadd", as_index=False, sort=False)["id"].count()
        df = px.bar(
            df,
            x=df.dtadd,
            y=df.id,
            title=f"Daily Overall Replacements.",
            text_auto=True,
            text=df.id,
            labels={"id": "Meter Count", "dtadd": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    def metering_status():
        df = read_frame(oveall_inspected)
        df = df.groupby(by="meteringstatus", as_index=False, sort=False)["id"].count()
        values = df.meteringstatus
        names = df.id
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Meter Status",
            labels={
                "id": "Meter Count",
                "meteringstatus": "Metering Status",
            },
        )
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    def incms_status():
        df_validate = read_frame(oveall_inspected)
        df_validate = df_validate.groupby(by="validate_status", as_index=False, sort=False)["id"].count()
        values = df_validate.validate_status
        names = df_validate.id
        df = px.pie(
            df_validate,
            values=names,
            names=values,
            title="Meter Validation Status(WO Resolved)",
            labels={
                "id": "Meter Count",
                "validate_status": "InCMS Validation Status",
            },
        )
        df_validate_incms = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df_validate_incms

    region_analytics = (
        Region.objects.select_related("region")
        .values("name", "id")  # select_related('dc_region')
        .annotate(
            dc_target_acs=(Sum("dc_target", distinct=True)),
            dc_inspected=(Count("region_elsewedy_repalcement", distinct=True)),
            dc_insp_faulty=(
                Count(
                    "region_elsewedy_repalcement",
                    distinct=True,
                    filter=~Q(
                        region_elsewedy_repalcement__meteringstatus__in=[
                            "okay"
                        ]
                    ),
                )
            ),
            un_validated=(
                Count(
                    "region_elsewedy_repalcement",
                    distinct=True,
                    filter=(
                        Q(region_elsewedy_repalcement__validate_status=False)

                    ),
                )
            ),
            today=Count(
                "region_elsewedy_repalcement",
                distinct=True,
                filter=Q(region_elsewedy_repalcement__dtadd__date=today),
            ),
            today_1=Count(
                "region_elsewedy_repalcement",
                distinct=True,
                filter=Q(region_elsewedy_repalcement__dtadd__date=yesterday),
            ),
            today_2=Count(
                "region_elsewedy_repalcement",
                distinct=True,
                filter=Q(region_elsewedy_repalcement__dtadd__date=yesterday_1),
            ),
            today_3=Count(
                "region_elsewedy_repalcement",
                distinct=True,
                filter=Q(region_elsewedy_repalcement__dtadd__date=yesterday_2),
            ),
            today_4=Count(
                "region_elsewedy_repalcement",
                distinct=True,
                filter=Q(region_elsewedy_repalcement__dtadd__date=yesterday_3),
            ),
        )
        .order_by("name")
    )
    county_analytics = (
        County.objects.select_related("region")
        .values("name", "id")  # select_related('dc_region')
        .annotate(
            dc_target_acs=(Sum("dc_target", distinct=True)),
            dc_inspected=(Count("county_elsewedy_repalcement", distinct=True)),
            dc_insp_faulty=(
                Count(
                    "county_elsewedy_repalcement",
                    distinct=True,
                    filter=~Q(
                        county_elsewedy_repalcement__meteringstatus__in=[
                            "faulty",
                            "tampered",
                            "bypassed",
                        ]
                    ),
                )
            ),
            un_validated=(
                Count(
                    "county_elsewedy_repalcement",
                    distinct=True,
                    filter=(
                        Q(county_elsewedy_repalcement__validate_status=False)

                    ),
                )
            ),
            today=Count(
                "county_elsewedy_repalcement",
                distinct=True,
                filter=Q(county_elsewedy_repalcement__dtadd__date=today),
            ),
            today_1=Count(
                "county_elsewedy_repalcement",
                distinct=True,
                filter=Q(county_elsewedy_repalcement__dtadd__date=yesterday),
            ),
            today_2=Count(
                "county_elsewedy_repalcement",
                distinct=True,
                filter=Q(county_elsewedy_repalcement__dtadd__date=yesterday_1),
            ),
            today_3=Count(
                "county_elsewedy_repalcement",
                distinct=True,
                filter=Q(county_elsewedy_repalcement__dtadd__date=yesterday_2),
            ),
            today_4=Count(
                "county_elsewedy_repalcement",
                distinct=True,
                filter=Q(county_elsewedy_repalcement__dtadd__date=yesterday_3),
            ),
        )
        .order_by("name")
    )

    context = {
        "daily_trend_plot": daily_trend(),
        "target_achievement": target_achievement(),
        "metering_status": metering_status(),
        "metering_status_notokay": incms_status(),
        "region_analytics": region_analytics,
        "county_analytics": county_analytics,
        "yesterday": yesterday,
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,
    }
    return render(request, "postpaid/elsewedy/elsewedy_dashboard.html", context)


@login_required(login_url="login")
def region_elsewedy_useranalytics(request):
    if request.user.is_authenticated:
        user = request.user
    county = request.user.userprofile.region
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    inspectors = ElsewedyReplacement.objects.select_related('inspector').values('inspector__county__name',
                                                                                'inspector__user_id__stid',
                                                                                'inspector__user_id__name',
                                                                                'inspector__user_id__mobile').filter(
        region=county).annotate(
        the_count=Count("inspector"),
        today=Count("inspector", filter=Q(dtadd__date=today)),
        yesturday=Count(
            "inspector", filter=Q(dtadd__date=yesterday)
        ),
        yesturday_1=Count(
            "inspector", filter=Q(dtadd__date=yesterday_1)
        ),
        yesturday_2=Count(
            "inspector", filter=Q(dtadd__date=yesterday_2)
        ),
        yesturday_3=Count(
            "inspector", filter=Q(dtadd__date=yesterday_3)
        ),
    ).order_by("inspector__county__name")

    # inspectors = (
    #     UserProfile.objects.values("user_id__stid", "user_id__name", "user_id__mobile", "county__name","id")
    #     .filter(campaign__in=('zerobills','dc','threephase','telcos','publiclighting','other'), county=county)
    #     .annotate(
    #         the_count=Count("tid_inspector"),
    #         today=Count("tid_inspector", distinct=True, filter=Q(tid_inspector__dtadd__date=today)),
    #         yesturday=Count(
    #             "tid_inspector", distinct=True, filter=Q(tid_inspector__dtadd__date=yesterday)
    #         ),
    #         yesturday_1=Count(
    #             "tid_inspector", distinct=True, filter=Q(tid_inspector__dtadd__date=yesterday_1)
    #         ),
    #         yesturday_2=Count(
    #             "tid_inspector",distinct=True, filter=Q(tid_inspector__dtadd__date=yesterday_2)
    #         ),
    #         yesturday_3=Count(
    #             "tid_inspector",distinct=True, filter=Q(tid_inspector__dtadd__date=yesterday_3)
    #         ),
    #     )
    #     .order_by("county__name")
    # )

    # inspectors = Threephase_inspection.objects.all().select_related('inspector').values('inspector__user_id__stid','inspector__user_id__name','inspector__county__name','inspector__user_id__mobile').annotate(
    #      the_count=Count('id'),
    #      today=Count('id',filter=Q(dtadd__date=today)),
    #      yesturday=Count('id',filter=Q(dtadd__date=yesterday)),
    #      yesturday_1=Count('id',filter=Q(dtadd__date=yesterday_1)),
    #      yesturday_2=Count('id',filter=Q(dtadd__date=yesterday_2)),
    #      #yesturday_2_d=Count('id',filter=Q(dtadd__date=yesterday_2)),
    #      #yesturday_3_d=Count('id',filter=Q(dtadd__date=yesterday_3)),
    #     ).order_by('inspector__county__name')

    context = {
        "analytics": inspectors,
        "nbar": "analytics",
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,
        'county': county
    }
    return render(request, "postpaid/elsewedy/replace_inspector_analytics.html", context)


@login_required(login_url="login")
def elsewedy_replaced_search_account(request):
    meters_list = ElsewedyReplacement.objects.select_related("county")
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(newmeter__icontains=keyword)
    context = {"meters": paged_uploads}
    return render(request, "postpaid/elsewedy/view_replacements.html", context)


@login_required(login_url="login")
def view_replaced_elsewedy(request, pk):
    meter = ElsewedyReplacement.objects.get(id=pk)

    context = {
        "meter": meter,

    }
    return render(request, "postpaid/elsewedy/replaced_detail.html", context)


@login_required(login_url="login")
def elsewedy_replaced_list(request):
    if request.user.is_authenticated:
        user = request.user.userprofile

    meters = ElsewedyReplacement.objects.order_by('-dtadd')
    paginator = Paginator(meters, 30)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_count,
    }
    return render(request, 'postpaid/elsewedy/view_replacements.html', context)


@login_required(login_url="login")
def myelsewedy_list(request):
    if request.user.is_authenticated:
        user = request.user.userprofile

    meters = ElsewedyReplacement.objects.filter(inspector=user).order_by('-dtadd')
    paginator = Paginator(meters, 30)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_count,
    }
    return render(request, 'postpaid/elsewedy/elsewedy_my.html', context)


@login_required(login_url="login")
def replace_elsewedy(request, pk):
    # userprofile = get_object_or_404(UserProfile, user=request.user)
    img = ElsewedyAccounts.objects.get(id=pk)

    campaign = request.user.userprofile.campaign
    if campaign == 'elsewedy_replacement':
        if request.method == "POST":
            m_form = ElsewedyReplacementForm(request.POST, request.FILES, instance=img)
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                resolution = ElsewedyReplacement()
                resolution.oldmeter = img.meterno
                resolution.accountno = img.accountno
                resolution.elsewedy = img
                resolution.newmeter = m_form.cleaned_data["newmeter"]
                resolution.meteringstatus = m_form.cleaned_data["meteringstatus"]
                resolution.faultystatus = m_form.cleaned_data["faultystatus"]
                resolution.tamperedstatus = m_form.cleaned_data["tamperedstatus"]
                resolution.bypassstatus = m_form.cleaned_data["bypassstatus"]
                resolution.removal_reading = m_form.cleaned_data["removal_reading"]
                resolution.removal_img = m_form.cleaned_data["removal_img"]
                resolution.comment = m_form.cleaned_data["comment"]
                resolution.removal_reading = m_form.cleaned_data["removal_reading"]
                resolution.seal_cover = m_form.cleaned_data["seal_cover"]
                resolution.region = request.user.userprofile.region
                resolution.county = request.user.userprofile.county
                resolution.diffunits = resolution.removal_reading - zerov.billed_reading
                resolution.inspector = request.user.userprofile

                with transaction.atomic():
                    resolution.save()
                    zerov.status = True
                    zerov.save()
                    messages.success(
                        request, "Your Inspection & Replacement Has been successfully saved."
                    )
                    return redirect("postpaid:myelsewedy-list")
            else:
                print("invalid form")
                print(m_form.errors)
        else:
            m_form = ElsewedyReplacementForm()
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

    context = {'form': m_form,
               'img': img}

    return render(request, "postpaid/elsewedy/replace_elsewedy.html", context)


@login_required(login_url="login")
def elsewedy_accounts(request):
    if request.user.is_authenticated:
        campaign = request.user.userprofile
    meters = ElsewedyAccounts.objects.select_related('county', 'region').values('id', 'meterno', 'accountno',
                                                                                'customer_name', 'county__name').filter(
        county=campaign.county, status=False)
    paginator = Paginator(meters, 10)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context = {
        'meters': paged_uploads, }
    return render(request, 'postpaid/elsewedy/elsewedy_target.html', context)


@login_required(login_url="login")
def lp_new_search_meterno_inspected(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters_list = Largepower_accounts_2024.objects.select_related('county', 'region').values('over_per',
                                                                                             'inspection_status', 'id',
                                                                                             'srn', 'meterno',
                                                                                             'accountno',
                                                                                             'customer_name',
                                                                                             'county__name').exclude(
        inspection_status=0)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/lp/lp_inspected.html', context)


@login_required(login_url="login")
def lp_new_search_meterno(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters_list = Largepower_accounts_2024.objects.select_related('county', 'region').values('inspection_status', 'id',
                                                                                             'srn', 'meterno',
                                                                                             'accountno',
                                                                                             'customer_name',
                                                                                             'county__name').filter(
        status=False)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/lp/lp_target.html', context)

@cache_page(60 * 15)
@login_required(login_url="login")
def lp_new_inspector_analytics(request):
    if request.user.is_authenticated:
        user = request.user
    county = request.user.userprofile.region
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    inspectors = Lp_new_inspection.objects.select_related('lp_new_inspected_by').values('inspectedby__region__name',
                                                                                          'inspectedby__user_id__stid',
                                                                                          'inspectedby__user_id__name',
                                                                                          'inspectedby__user_id__mobile').filter(
        region=county, save_status=True, inspectedby__campaign='lp').annotate(
        the_count=Count("inspectedby"),
        today=Count("inspectedby", filter=Q(dtupdate__date=today)),
        yesturday=Count(
            "inspectedby", filter=Q(dtadd__date=yesterday)
        ),
        yesturday_1=Count(
            "inspectedby", filter=Q(dtadd__date=yesterday_1)
        ),
        yesturday_2=Count(
            "inspectedby", filter=Q(dtadd__date=yesterday_2)
        ),
        yesturday_3=Count(
            "inspectedby", filter=Q(dtadd__date=yesterday_3)
        ),
    ).order_by("inspectedby__user_id__name")

    # inspectors = (UserProfile.objects.select_related('odk_staff', 'lp_new_inspected_by')
    #        .values('user__stid','user__name','region__name')
    #        .filter(region=county,campaign='lp')
    #        .annotate(
    #            total=(Count("lp_new_inspected_by", distinct=True)),
    #            total_odk=(Count("odk_staff", distinct=True)),
    #            today=Count("lp_new_inspected_by", filter=Q(lp_new_inspected_by__dtupdate=today)),
    #            today_odk=Count("odk_staff", filter=Q(odk_staff__SubmissionDate=today)),
    #            today_1_odk=Count("odk_staff", distinct=True, filter=Q(odk_staff__SubmissionDate=yesterday)),
    #            today_1=Count("lp_new_inspected_by", filter=Q(lp_new_inspected_by__dtupdate=yesterday)),
    #            today_2_odk=Count("odk_staff", filter=Q(odk_staff__SubmissionDate=yesterday_1)),
    #            today_2=Count("lp_new_inspected_by", filter=Q(lp_new_inspected_by__dtupdate=yesterday_1)),
    #            today_3_odk=Count("odk_staff", filter=Q(odk_staff__SubmissionDate=yesterday_2)),
    #            today_3=Count("lp_new_inspected_by", filter=Q(lp_new_inspected_by__dtupdate=yesterday_2)),
    #            today_4_odk=Count("odk_staff", filter=Q(odk_staff__SubmissionDate=yesterday_3)),
    #            today_4=Count("lp_new_inspected_by", filter=Q(lp_new_inspected_by__dtupdate=yesterday_3)),
    # ).order_by('user__stid')
    #        )


    context = {
        'analytics': inspectors,
        'yesterday' : yesterday,
        'yesterday_1': yesterday_1,
        'yesterday_2': yesterday_2,
        "yesterday_3": yesterday_3,

    }
    return render(request, 'postpaid/lp/lp_user_analytics.html', context)


@login_required(login_url="login")
def inspection_print(request, pk=None):
    inspection = Lp_new_inspection.objects.select_related('lp_solar', 'lp_customerdata', 'lp_sealing', 'lp_ctvt',
                                                          'lp_zeratest', 'lp_current', 'lp_mreadings').get(lp_id=pk)
    customer = Largepower_accounts_2024.objects.get(id=pk)
    context = {
        'customer': customer,
        'inspection': inspection
    }

    return render(request, 'postpaid/lp/inspection_print.html', context)


@login_required(login_url="login")
def inspection_delete(request, pk):
    inspection = Lp_new_inspection.objects.filter(lp_id=pk)
    customer = Largepower_accounts_2024.objects.get(id=pk)

    if request.user.userprofile != inspection.first().inspectedby:
        messages.error(request, 'The Inspection can only be deleted by the person who created')
        return redirect('postpaid:lp-new-inspected')

    if request.method == 'POST':
        with transaction.atomic():
            for i in inspection:
                i.delete()
            # customer.status = False
            customer.inspection_status = 0
            customer.save()
        messages.success(request, 'The Inspection was deleted successfully')
        return redirect('postpaid:lp-new-inspected-my')
    context = {'object': customer}
    return render(request, 'postpaid/lp/inspection_confirm_deletion.html', context)


@login_required(login_url="login")
def finalsubmission(request, pk=None):
    customer = Largepower_accounts_2024.objects.get(id=pk)
    inspection = Lp_new_inspection.objects.get(lp_id=pk)

    if request.user.userprofile != inspection.inspectedby:
        messages.error(request, 'The Inspection can only be submitted by the person who created')
        return redirect("postpaid:lp-update-inspection", pk)

    campaign = request.user.userprofile.campaign
    m_form = LPNewInspectionForm(request.POST, request.FILES, instance=inspection)
    if campaign == "lp":
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.lp = customer
                zerov.over_rem = m_form.cleaned_data["over_rem"]
                zerov.declaration = m_form.cleaned_data["declaration"]
                zerov.inspectedby = request.user.userprofile
                zerov.save_status = True

                with transaction.atomic():

                    if customer.customer_data == 1 and customer.sealing_data == 1 and customer.ctvt_data == 1 and customer.zera_test == 1 and customer.meter_rading == 1 and customer.otherinfo == 1 and customer.current == 1:
                        customer.inspection_status = 2
                        customer.status = True
                        customer.final_sub = 1
                        customer.over_per = (
                                                        customer.customer_data + customer.sealing_data + customer.ctvt_data + customer.zera_test + customer.meter_rading + customer.current + customer.otherinfo + customer.final_sub) / 8 * 100
                        customer.save()
                    else:
                        customer.inspection_status = 1
                        zerov.save_status = False
                        customer.status = False
                        messages.error(
                            request, "Please check, there are other parameters of inspection that are pending"
                        )
                        return redirect("postpaid:lp-new-inspected-my")

                    zerov.save()

                    messages.success(
                        request, "The Final Inspection Data has been submitted successfully"
                    )
                    return redirect("postpaid:lp-new-inspected-my")
            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)
        else:
            m_form = LPNewInspectionForm(instance=inspection)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:dashboard")


@login_required(login_url="login")
def lp_otherinfo_data(request, pk=None):
    cust = Lp_new_inspection.objects.get(lp_id=pk)
    customer = Lp_inspect_info.objects.get(lp=cust)
    asset = Largepower_accounts_2024.objects.get(id=pk)

    campaign = request.user.userprofile.campaign
    m_form = LPOtherinfoForm(request.POST, request.FILES, instance=customer)
    if campaign == "lp":
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.lp = customer.lp
                zerov.solar_installed = m_form.cleaned_data["solar_installed"]
                zerov.solar_size = m_form.cleaned_data["solar_size"]
                zerov.dt_installation = m_form.cleaned_data["dt_installation"]
                zerov.overal_rem = m_form.cleaned_data["overal_rem"]
                zerov.inspectedby = request.user.userprofile
                with transaction.atomic():
                    zerov.save()
                    asset.otherinfo = 1
                    asset.over_per = (
                                                 asset.customer_data + asset.sealing_data + asset.ctvt_data + asset.zera_test + asset.meter_rading + asset.current + asset.otherinfo + asset.final_sub) / 8 * 100
                    asset.save()
                messages.success(
                    request, "The LP Other Info Data saved successfully saved."
                )
                return redirect("postpaid:lp-update-inspection", pk)
            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)
        else:
            m_form = LPOtherinfoForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")


@login_required(login_url="login")
def lp_mreadings_data(request, pk=None):
    cust = Lp_new_inspection.objects.get(lp_id=pk)
    customer = LP_meter_readings.objects.get(lp=cust)
    asset = Largepower_accounts_2024.objects.get(id=pk)

    campaign = request.user.userprofile.campaign
    m_form = LPMeterReadingsForm(request.POST, request.FILES, instance=customer)
    if campaign == "lp":
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.lp = customer.lp
                zerov.meter_time_actual = m_form.cleaned_data["meter_time_actual"]
                zerov.meter_time_meter = m_form.cleaned_data["meter_time_meter"]
                zerov.meter_date_actual = m_form.cleaned_data["meter_date_actual"]
                zerov.meter_date_meter = m_form.cleaned_data["meter_date_meter"]
                zerov.kwh_180_cur = m_form.cleaned_data["kwh_180_cur"]
                zerov.kwh_180_mem = m_form.cleaned_data["kwh_180_mem"]
                zerov.reading_180_img = m_form.cleaned_data["reading_180_img"]
                zerov.reading_280_img = m_form.cleaned_data["reading_280_img"]
                zerov.kwh_280_cur = m_form.cleaned_data["kwh_280_cur"]
                zerov.kwh_280_mem = m_form.cleaned_data["kwh_280_mem"]
                zerov.kva_960_cur = m_form.cleaned_data["kva_960_cur"]
                zerov.kva_960_mem = m_form.cleaned_data["kva_960_mem"]
                zerov.kwh_181_cur = m_form.cleaned_data["kwh_181_cur"]
                zerov.kwh_181_mem = m_form.cleaned_data["kwh_181_mem"]
                zerov.kwh_182_cur = m_form.cleaned_data["kwh_182_cur"]
                zerov.kwh_182_mem = m_form.cleaned_data["reading_280_img"]
                zerov.kwh_150_cur = m_form.cleaned_data["kwh_150_cur"]
                zerov.kwh_150_mem = m_form.cleaned_data["kwh_150_mem"]
                zerov.kva_970_cur = m_form.cleaned_data["kva_970_cur"]
                zerov.kva_970_mem = m_form.cleaned_data["kva_970_mem"]
                zerov.kwh_170_cur = m_form.cleaned_data["kwh_170_cur"]
                zerov.kwh_170_mem = m_form.cleaned_data["kwh_170_mem"]
                zerov.r_phase_v = m_form.cleaned_data["r_phase_v"]
                zerov.y_phase_v = m_form.cleaned_data["y_phase_v"]
                zerov.b_phase_v = m_form.cleaned_data["b_phase_v"]
                zerov.r_phase_c = m_form.cleaned_data["r_phase_c"]
                zerov.y_phase_c = m_form.cleaned_data["y_phase_c"]
                zerov.b_phase_c = m_form.cleaned_data["b_phase_c"]
                zerov.pw_f = m_form.cleaned_data["pw_f"]
                zerov.m_remarks = m_form.cleaned_data["m_remarks"]
                zerov.inspectedby = request.user.userprofile
                with transaction.atomic():
                    zerov.save()
                    asset.meter_rading = 1
                    asset.over_per = (
                                                 asset.customer_data + asset.sealing_data + asset.ctvt_data + asset.zera_test + asset.meter_rading + asset.current + asset.otherinfo + asset.final_sub) / 8 * 100
                    asset.save()
                messages.success(
                    request, "The LP Meter Readings Data saved successfully saved."
                )
                return redirect("postpaid:lp-update-inspection", pk)
            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)
        else:
            m_form = LPCurrentsForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:dashboard")


@login_required(login_url="login")
def lp_currents_data(request, pk=None):
    cust = Lp_new_inspection.objects.get(lp_id=pk)
    customer = Lp_inspect_current.objects.get(lp=cust)
    asset = Largepower_accounts_2024.objects.get(id=pk)

    campaign = request.user.userprofile.campaign
    m_form = LPCurrentsForm(request.POST, request.FILES, instance=customer)
    if campaign == "lp":
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.lp = customer.lp
                zerov.rphase_amcoder = m_form.cleaned_data["rphase_amcoder"]
                zerov.rphase_meter = m_form.cleaned_data["rphase_meter"]
                zerov.yphase_amcoder = m_form.cleaned_data["yphase_amcoder"]
                zerov.yphase_meter = m_form.cleaned_data["yphase_meter"]
                zerov.bphase_amcoder = m_form.cleaned_data["bphase_amcoder"]
                zerov.bphase_meter = m_form.cleaned_data["bphase_meter"]
                zerov.load_balancing = m_form.cleaned_data["load_balancing"]
                zerov.currents_range = m_form.cleaned_data["currents_range"]
                zerov.inspectedby = request.user.userprofile
                with transaction.atomic():
                    zerov.save()
                    asset.current = 1
                    if zerov.currents_range == 'NO':
                        asset.currents_mismatch = 'NO'
                    else:
                        asset.currents_mismatch = 'YES'
                    asset.over_per = (
                                                 asset.customer_data + asset.sealing_data + asset.ctvt_data + asset.zera_test + asset.meter_rading + asset.current + asset.otherinfo + asset.final_sub) / 8 * 100
                    asset.save()
                messages.success(
                    request, "The LP Currents Data saved successfully saved."
                )
                return redirect("postpaid:lp-update-inspection", pk)
            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)
        else:
            m_form = LPCurrentsForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:dashboard")


@login_required(login_url="login")
def lp_new_search_srn_inspected(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters_list = Largepower_accounts_2024.objects.select_related('county', 'region').values('dtupdate', 'over_per',
                                                                                             'inspection_status', 'id',
                                                                                             'srn', 'meterno',
                                                                                             'accountno',
                                                                                             'customer_name',
                                                                                             'county__name').exclude(
        inspection_status=0)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(srn__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/lp/lp_inspected.html', context)


@login_required(login_url="login")
def lp_new_inspected(request):
    if request.user.is_authenticated:
        campaign = request.user.userprofile.campaign
    if campaign == 'lp':
        meters = Largepower_accounts_2024.objects.select_related('county', 'region').values('dtupdate', 'zera_failed',
                                                                                            'currents_mismatch',
                                                                                            'ctvt_mismatch', 'over_per',
                                                                                            'inspection_status', 'id',
                                                                                            'srn', 'meterno',
                                                                                            'accountno',
                                                                                            'customer_name',
                                                                                            'county__name').exclude(
            inspection_status=0)
        paginator = Paginator(meters, 10)
        page = request.GET.get('page')
        paged_uploads = paginator.get_page(page)

    else:
        messages.error(request, "Access denied.")
        return redirect("main:my-dashboard")

    context = {
        'meters': paged_uploads, }
    return render(request, 'postpaid/lp/lp_inspected.html', context)


@login_required(login_url="login")
def lp_zeratest_data(request, pk=None):
    cust = Lp_new_inspection.objects.get(lp_id=pk)
    customer = Lp_inspect_zeratest.objects.get(lp=cust)
    asset = Largepower_accounts_2024.objects.get(id=pk)

    campaign = request.user.userprofile.campaign
    m_form = LPZeraTestForm(request.POST, request.FILES, instance=customer)
    if campaign == "lp":
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.lp = customer.lp
                zerov.zeratest = m_form.cleaned_data["zeratest"]
                zerov.error_trial = m_form.cleaned_data["error_trial"]
                zerov.error_test_rem = m_form.cleaned_data["error_test_rem"]
                zerov.register_error = m_form.cleaned_data["register_error"]
                zerov.register_error_rem = m_form.cleaned_data["register_error_rem"]
                zerov.meter_passed = m_form.cleaned_data["meter_passed"]
                zerov.inspectedby = request.user.userprofile
                with transaction.atomic():
                    zerov.save()
                    asset.zera_test = 1
                    if zerov.meter_passed == 'YES':
                        asset.zera_failed = 'YES'
                    else:
                        asset.zera_failed = 'NO'
                    asset.over_per = (
                                                 asset.customer_data + asset.sealing_data + asset.ctvt_data + asset.zera_test + asset.meter_rading + asset.current + asset.otherinfo + asset.final_sub) / 8 * 100
                    asset.save()
                messages.success(
                    request, "The LP Zera Test  Data saved successfully saved."
                )
                return redirect("postpaid:lp-update-inspection", pk)
            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)
        else:
            m_form = LPZeraTestForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:dashboard")


@login_required(login_url="login")
def lp_ctvt_data(request, pk=None):
    cust = Lp_new_inspection.objects.get(lp_id=pk)
    customer = Lp_inspect_ctvt.objects.get(lp=cust)
    asset = Largepower_accounts_2024.objects.get(id=pk)

    campaign = request.user.userprofile.campaign
    m_form = LPCtVtInspectionForm(request.POST, request.FILES, instance=customer)
    if campaign == "lp":
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.lp = customer.lp
                zerov.meter_config = m_form.cleaned_data["meter_config"]
                zerov.meter_voltage = m_form.cleaned_data["meter_voltage"]
                zerov.ct_ratio_prmed = m_form.cleaned_data["ct_ratio_prmed"]
                zerov.ctratio_img = m_form.cleaned_data["ctratio_img"]
                zerov.ct_ratio_inst = m_form.cleaned_data["ct_ratio_inst"]
                zerov.vt_ratio_prmed = m_form.cleaned_data["vt_ratio_prmed"]
                zerov.amr_recovered = m_form.cleaned_data["amr_recovered"]
                zerov.ctvt_match = m_form.cleaned_data["ctvt_match"]
                zerov.ctvt_mismatch_text = m_form.cleaned_data["ctvt_mismatch_text"]
                zerov.inspectedby = request.user.userprofile
                with transaction.atomic():
                    zerov.save()
                    asset.ctvt_data = 1
                    if zerov.ctvt_match == 'NO':
                        asset.ctvt_mismatch = 'NO'
                    else:
                        asset.ctvt_mismatch = 'YES'
                    asset.over_per = (
                                                 asset.customer_data + asset.sealing_data + asset.ctvt_data + asset.zera_test + asset.meter_rading + asset.current + asset.otherinfo + asset.final_sub) / 8 * 100
                    # if zerov.ctvt_match == 'NO':
                    #     asset.ctvt_mismatch == zerov.ctvt_match
                    # else:
                    #     asset.ctvt_mismatch == 'YES'
                    asset.save()
                messages.success(
                    request, "The LP CT VT  Data saved successfully saved."
                )
                return redirect("postpaid:lp-update-inspection", pk)
            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)
        else:
            m_form = LPCtVtInspectionForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:dashboard")


@login_required(login_url="login")
def lp_sealing_data(request, pk=None):
    cust = Lp_new_inspection.objects.get(lp_id=pk)
    customer = LP_inspection_sealing.objects.get(lp=cust)
    asset = Largepower_accounts_2024.objects.get(id=pk)

    campaign = request.user.userprofile.campaign
    m_form = LPSealingInspectionForm(request.POST, request.FILES, instance=customer)
    if campaign == "lp":
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.lp = customer.lp
                zerov.prg_seal_init = m_form.cleaned_data["prg_seal_init"]
                zerov.prg_seal_fin = m_form.cleaned_data["prg_seal_fin"]
                zerov.term_sl_init = m_form.cleaned_data["term_sl_init"]
                zerov.term_sl_fin = m_form.cleaned_data["term_sl_fin"]
                zerov.testb_sl_init = m_form.cleaned_data["testb_sl_init"]
                zerov.testb_sl_fin = m_form.cleaned_data["testb_sl_fin"]
                zerov.body_sl_init = m_form.cleaned_data["body_sl_init"]
                zerov.body_sl_fin = m_form.cleaned_data["body_sl_fin"]
                zerov.smart_meter_sl_init = m_form.cleaned_data["smart_meter_sl_init"]
                zerov.smart_meter_sl_fin = m_form.cleaned_data["smart_meter_sl_fin"]
                zerov.amr_sl_init = m_form.cleaned_data["amr_sl_init"]
                zerov.amr_sl_fin = m_form.cleaned_data["amr_sl_fin"]
                zerov.other_sl_init = m_form.cleaned_data["other_sl_init"]
                zerov.other_sl_fin = m_form.cleaned_data["other_sl_fin"]
                zerov.inspectedby = request.user.userprofile
                # if (zerov.term_sl_init == zerov.term_sl_fin) or (zerov.testb_sl_init == zerov.testb_sl_fin)  or (zerov.smart_meter_sl_init == zerov.smart_meter_sl_fin) or (zerov.amr_sl_init == zerov.amr_sl_fin):
                #     messages.error(
                #         request, "THE INITAIL SEALS SHOULD NOT BE THE SAME AS THE FINAL SEALS."
                #     )
                #     return redirect("postpaid:lp-update-inspection", pk)

                with transaction.atomic():
                    zerov.save()
                    asset.sealing_data = 1
                    asset.over_per = (
                                                 asset.customer_data + asset.sealing_data + asset.ctvt_data + asset.zera_test + asset.meter_rading + asset.current + asset.otherinfo + asset.final_sub) / 8 * 100
                    asset.save()
                messages.success(
                    request, "The LP Sealing  Data saved successfully saved."
                )
                return redirect("postpaid:lp-update-inspection", pk)
            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)
        else:
            m_form = LPSealingInspectionForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:dashboard")


@login_required(login_url="login")
def lp_customer_data(request, pk=None):
    cust = Lp_new_inspection.objects.get(lp_id=pk)
    customer = Lp_inspect_customerData.objects.get(lp=cust)
    asset = Largepower_accounts_2024.objects.get(id=pk)
    seals = LP_inspection_sealing.objects.get(lp=cust)

    campaign = request.user.userprofile.campaign
    m_form = LPCustomerDataInspectionForm(request.POST, request.FILES, instance=customer)
    if campaign == "lp":
        if request.method == "POST":
            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.lp = customer.lp
                zerov.meterno = m_form.cleaned_data["meterno"]
                zerov.accountno = customer.accountno
                zerov.type_of_industry = m_form.cleaned_data["type_of_industry"]
                zerov.smart_meter_i = m_form.cleaned_data["smart_meter_i"]
                zerov.latitude = m_form.cleaned_data["latitude"]
                zerov.longitude = m_form.cleaned_data["longitude"]
                zerov.inspectedby = request.user.userprofile
                if m_form.cleaned_data["smart_meter_i"] == 'AMRMETERING':
                    seals.is_amr = 'YES'
                else:
                    seals.is_amr = 'NO'
                with transaction.atomic():
                    zerov.save()
                    asset.customer_data = 1
                    asset.over_per = (
                                                 asset.customer_data + asset.sealing_data + asset.ctvt_data + asset.zera_test + asset.meter_rading + asset.current + asset.otherinfo + asset.final_sub) / 8 * 100
                    asset.save()
                    seals.save()
                messages.success(
                    request, "The LP Customer  Data saved successfully saved."
                )
                return redirect("postpaid:lp-update-inspection", pk)
            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)
        else:
            m_form = LPCustomerDataInspectionForm(instance=customer)
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:dashboard")


@login_required(login_url="login")
def lp_update_inspection(request, pk=None):
    customer = Largepower_accounts_2024.objects.get(pk=pk)
    inspection = Lp_new_inspection.objects.get(lp=customer)
    customer_data = Lp_inspect_customerData.objects.get(lp=inspection)
    sealing_data = LP_inspection_sealing.objects.get(lp=inspection)
    ctvt_data = Lp_inspect_ctvt.objects.get(lp=inspection)
    zera_test = Lp_inspect_zeratest.objects.get(lp=inspection)
    currents = Lp_inspect_current.objects.get(lp=inspection)
    mreadings = LP_meter_readings.objects.get(lp=inspection)
    otherinfo = Lp_inspect_info.objects.get(lp=inspection)

    m_form = LPCustomerDataInspectionForm(instance=customer_data)
    m_form1 = LPSealingInspectionForm(instance=sealing_data)
    m_form2 = LPCtVtInspectionForm(instance=ctvt_data)
    m_form3 = LPZeraTestForm(instance=zera_test)
    m_form4 = LPCurrentsForm(instance=currents)
    m_form5 = LPMeterReadingsForm(instance=mreadings)
    m_form6 = LPOtherinfoForm(instance=otherinfo)
    m_form7 = LPNewInspectionForm(instance=inspection)

    context = {
        'customer': customer,
        'form': m_form,
        'form1': m_form1,
        'form2': m_form2,
        'form3': m_form3,
        'form4': m_form4,
        'form5': m_form5,
        'form6': m_form6,
        'form7': m_form7,

    }
    return render(request, "postpaid/lp/lp_inspection_update.html", context)


@login_required(login_url="login")
def lp_new_inspections(request, pk=None):
    lp = get_object_or_404(Largepower_accounts_2024, id=pk)
    with transaction.atomic():
        new_inspection = Lp_new_inspection.objects.create(
            lp=lp,
            meterno=lp.meterno,
            inspectedby=request.user.userprofile,
            county=request.user.userprofile.county,
            region=request.user.userprofile.region
        )
        new_inspection.save()
        customer_data = Lp_inspect_customerData.objects.create(
            lp=new_inspection,
            inspectedby=request.user.userprofile,
        )
        customer_data.save()
        sealing_data = LP_inspection_sealing.objects.create(
            lp=new_inspection,
            inspectedby=request.user.userprofile,
        )
        sealing_data.save()
        ctvt_data = Lp_inspect_ctvt.objects.create(
            lp=new_inspection,
            inspectedby=request.user.userprofile,
        )
        ctvt_data.save()
        zera_test = Lp_inspect_zeratest.objects.create(
            lp=new_inspection,
            inspectedby=request.user.userprofile,
        )
        zera_test.save()
        current = Lp_inspect_current.objects.create(
            lp=new_inspection,
            inspectedby=request.user.userprofile,
        )
        current.save()
        mreadings = LP_meter_readings.objects.create(
            lp=new_inspection,
            inspectedby=request.user.userprofile,
        )
        mreadings.save()
        otherinfo = Lp_inspect_info.objects.create(
            lp=new_inspection,
            inspectedby=request.user.userprofile,
        )
        otherinfo.save()
        lp.inspection_status = 1
        lp.save()
    if new_inspection:
        messages.success(
            request,
            "A Draft of the New Inspection was saved successfully. Open to continue with the inspection",
        )
    else:
        messages.error(
            request,
            "There was an error in submitting.",
        )
        return redirect("postpaid:lp-new-inspected-my")
    context = {
        "inspection_id": new_inspection.id,
    }
    return render(request, "postpaid/lp/lp_target.html", context)


@login_required(login_url="login")
def lp_new_search_srn(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters_list = Largepower_accounts_2024.objects.select_related('county', 'region').values('inspection_status', 'id',
                                                                                             'srn', 'meterno',
                                                                                             'accountno',
                                                                                             'customer_name',
                                                                                             'county__name').filter(
        status=False)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(srn__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/lp/lp_target.html', context)


@login_required(login_url="login")
def lp_new_target(request):
    if request.user.is_authenticated:
        campaign = request.user.userprofile.campaign
    if campaign in ('lp', 'lpx'):
        meters = Largepower_accounts_2024.objects.select_related('county', 'region').values('over_per',
                                                                                            'inspection_status', 'id',
                                                                                            'srn', 'meterno',
                                                                                            'accountno',
                                                                                            'customer_name',
                                                                                            'county__name').order_by(
            'county__name')
        paginator = Paginator(meters, 10)
        page = request.GET.get('page')
        paged_uploads = paginator.get_page(page)

    else:
        messages.error(request, "Access denied.")
        return redirect("main:my-dashboard")

    context = {
        'meters': paged_uploads, }
    return render(request, 'postpaid/lp/lp_target.html', context)


@login_required(login_url="login")
def hexing_pending_county(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    county = request.user.userprofile.county
    meters = (
        Anomlalous_accounts.objects.select_related("county")
        .filter(
            county=county, source='REPLACE 1414', status=False
        )
        .order_by("-customer_name")
    )

    writer.writerow(
        [

            "COUNTY",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "SECTOR",
            "ZONE",
            "ITIN",
            "SUPPLY ADDRESS",
            "CUSTOMER NAME",
            "LONGITUDE",
            "LATITUDE",

        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.county,
                meter.meterno,
                meter.accountno,
                meter.sector,
                meter.zone,
                meter.itin,
                meter.supply_address,
                meter.customer_name,
                meter.longitude,
                meter.latitude,

            ]
        )

    response["Content-Disposition"] = (
        'attachment; filename="HEXING1414_PENDING_REPLACEMENT.csv" '
    )
    return response


@login_required(login_url="login")
def anomalous_export_resolved_all(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    county = request.user.userprofile.county
    meters = (
        Anomalous_resolved.objects.select_related("region", "county", "user")
        .filter(
            dtadd__gt=datetime.datetime.today() - datetime.timedelta(days=14),
        )
        .order_by("-dtadd")
    )

    writer.writerow(
        [

            "REGION",
            "COUNTY",
            "METER NUMBER",
            "NEW METER NUMBER",
            "ACCOUNT NUMBER",
            "ANOMALY TYPE",
            "RESOLUTION TYPE",
            "SOURCE",
            "RESOLUTION DATE",
            "COMMENT",
            "VALIDATION",
            "STAFF"

        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.region,
                meter.county,
                meter.meterno,
                meter.new_meterno,
                meter.accountno,
                meter.anomaly.anomaly_type,
                meter.faultystatus,
                meter.anomaly.source,
                meter.dtadd,
                meter.comment,
                meter.incms_status,
                meter.user,

            ]
        )

    response["Content-Disposition"] = (
        'attachment; filename="FALLBACK_RRI_RESOLVED.csv" '
    )
    return response


@login_required(login_url="login")
def anomalous_export_resolved_county(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    county = request.user.userprofile.county
    meters = (
        Anomalous_resolved.objects.select_related("county", "user")
        .filter(
            county=county,
            dtadd__gt=datetime.datetime.today() - datetime.timedelta(days=14),
        )
        .order_by("-dtadd")
    )

    writer.writerow(
        [

            "COUNTY",
            "METER NUMBER",
            "NEW METER NUMBER",
            "ACCOUNT NUMBER",
            "ANOMALY TYPE",
            "RESOLUTION TYPE",
            "SOURCE",
            "RESOLUTION DATE",
            "COMMENT",
            "VALIDATION",
            "STAFF"
        ]
    )
    for meter in meters:
        writer.writerow(
            [

                meter.county,
                meter.meterno,
                meter.new_meterno,
                meter.accountno,
                meter.anomaly.anomaly_type,
                meter.faultystatus,
                meter.anomaly.source,
                meter.dtadd,
                meter.comment,
                meter.incms_status,
                meter.user,
            ]
        )

    response["Content-Disposition"] = (
        'attachment; filename="FALLBACK_RRI_RESOLVED.csv" '
    )
    return response


@login_required(login_url="login")
def telcos_repl_pending_export(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    county = request.user.userprofile.county
    meters = (
        Telcos_target.objects.select_related("region", "county")
        .filter(
            county=county,
            status=False
        )
        .order_by("-dtadd")
    )

    writer.writerow(
        [

            "COUNTY",
            "SITE ID",
            "SITE NAME",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "LONGITUDE",
            "LATITUDE",
            "STATUS",
        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.county,
                meter.siteid,
                meter.sitename,
                meter.meterno,
                meter.accountno,
                meter.lon,
                meter.lat,
                meter.status,
            ]
        )

    response["Content-Disposition"] = (
        'attachment; filename="TELCOS_PENDING_SMART_METERING.csv" '
    )
    return response


@login_required(login_url="login")
def anomalous_export_uploads(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    county = request.user.userprofile.county
    meters = (
        Anomlalous_accounts.objects.select_related("region", "county")
        .filter(
            county=county,
            status=False
        )

    )

    writer.writerow(
        [
            "REGION",
            "COUNTY",
            "SECTOR",
            "ZONE",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "ANOMALY TYPE",
            "SOURCE",
            "SOURCE DATE",
            "ITIN",
            "STATUS",
            "LATITUDE",
            "LONGITUDE",
        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.region,
                meter.county,
                meter.sector,
                meter.zone,
                meter.meterno,
                meter.accountno,
                meter.anomaly_type,
                meter.source,
                meter.source_dt,
                meter.itin,
                meter.status,
                meter.latitude,
                meter.longitude,
            ]
        )

    response["Content-Disposition"] = (
        'attachment; filename="FALLBACK_RRI_ACCOUNTS.csv" '
    )
    return response


# @cache_page(60 * 15)
@login_required(login_url="login")
def anomalous_dashboard(request):
    # with Client(config_path='.pyodk_config.toml', cache_path='cache.toml') as client:
    #     submissions = client.submissions.get_table(form_id='RRI Inspection')
    #     df = pd.json_normalize(data=submissions['value'], sep='/')
    df = pd.read_csv('transf_data.csv')

    inspection_count = f"{df['id'].count():,.0f}"

    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)
    oveall_inspected = Anomalous_resolved.objects.select_related('region', 'county').values("faultystatus", "dtadd",
                                                                                            "id")
    anomalous_target = Anomlalous_accounts.objects.select_related("region", "county", "source").values("source", "id")

    def target_achievement():
        t_a = oveall_inspected.count()
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Planned",
                    x=["Planned"],
                    y=[282005],
                ),
                go.Bar(name="Achieved", x=["Achieved"], y=[t_a]),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Target vs Achievement",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="No Of Resolutions",
                titlefont_size=16,
                tickfont_size=14,
            ),
            xaxis=dict(
                title="Year(2023/24)",
            ),
            legend=dict(
                bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
            ),
            barmode="group",
            bargap=0.15,  # gap between bars of adjacent location coordinates.
            bargroupgap=0.1,  # gap between bars of the same location coordinate.
        )
        fig_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return fig_plot

    def daily_trend():
        analysed = df.groupby(['submission_date']).agg(id_count=('id', 'count')).reset_index()
        df_daily = px.bar(
            analysed,
            x=analysed.submission_date,
            y=analysed.id_count,
            title=f"Daily Overall Resolutions.",
            text_auto=True,
            text=analysed.id_count,
            labels={"id_count": "Meter Count", "submission_date": "Date"},
        )
        df_daolytrend = json.dumps(df_daily, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    def meter_type():
        analysed = df.groupby(['meter_type']).agg(id_count=('id', 'count')).reset_index()

        customerType_chart = px.pie(analysed, names='meter_type', values='id_count',
                                    title="Meter Types", hole=0.6,
                                    # width=600, height=400,
                                    # color_discrete_sequence=theme.COLOR_PALLETE,
                                    hover_data=['id_count'],
                                    labels={'id_count': 'Count'})

        customerType_chart.update_traces(textposition='inside',
                                         textinfo='percent+label',
                                         showlegend=False)
        customerType_chart.update_layout(
            yaxis=dict(showticklabels=False), margin=dict(l=10, r=15, t=60, b=15)
        )
        df_meter_type = json.dumps(customerType_chart, cls=plotly.utils.PlotlyJSONEncoder)
        return df_meter_type

    def anomaly_type():
        analysed = df.groupby(['installation_status']).agg(id_count=('id', 'count')).reset_index()

        anomaly_Type_chart = px.pie(analysed, names='installation_status', values='id_count',
                                    title="Anomaly Status",
                                    # width=600, height=400,
                                    # color_discrete_sequence=theme.COLOR_PALLETE,
                                    hover_data=['id_count'],
                                    labels={'id_count': 'Count'})

        anomaly_Type_chart.update_traces(textposition='inside', textinfo='percent+label',
                                         showlegend=False)
        anomaly_Type_chart.update_layout(
            yaxis=dict(showticklabels=False), margin=dict(l=10, r=15, t=60, b=15)
        )
        df_anomaly_type = json.dumps(anomaly_Type_chart, cls=plotly.utils.PlotlyJSONEncoder)
        return df_anomaly_type

    region_analytics = (
        Region.objects.prefetch_related("anomlalous_accounts_set", "anomalous_resolved_set")
        .values("name", "id")  # select_related('dc_region')
        .annotate(
            dc_target_acs=(Sum("fallbackrri_target", distinct=True)),
            recoveries=(Sum("anomalous_recoveries", distinct=True)),
            dc_inspected=(Count("region_anomalous_resolved", distinct=True)),
            pending_faulty=(Sum("fallbackrri_faulty", distinct=True)),
            found_okay=(Count(
                "region_anomalous_resolved",
                distinct=True,
                filter=Q(
                    region_anomalous_resolved__faultystatus="found_meter_okay"
                ),
            )),
            resolved_faulty=(
                Count(
                    "region_anomalous_resolved",
                    distinct=True,
                    filter=Q(
                        region_anomalous_resolved__anomaly__anomaly_type="FAULTY"
                    ),
                )
            ),
            pending_tampered=(Sum("fallbackrri_tampered", distinct=True)),
            resolved_tampered=(
                Count(
                    "region_anomalous_resolved",
                    distinct=True,
                    filter=Q(
                        region_anomalous_resolved__anomaly__anomaly_type="TAMPERED"
                    ),
                )
            ),
            pending_normalised=(Sum("fallbackrri_bypassed", distinct=True)),
            resolved_normalised=(
                Count(
                    "region_anomalous_resolved",
                    distinct=True,
                    filter=Q(
                        region_anomalous_resolved__anomaly__anomaly_type="BYPASSED"
                    ),
                )
            ),
            pending_directconn=(Sum("fallbackrri_dc", distinct=True)),
            resolved_directconn=(
                Count(
                    "region_anomalous_resolved",
                    distinct=True,
                    filter=Q(
                        region_anomalous_resolved__anomaly__anomaly_type="DIRECT CONNECTION"
                    ),
                )
            ),
            pending_repacements=(Sum("fallbackrri_replace", distinct=True)),
            resolved_replacements=(
                Count(
                    "region_anomalous_resolved",
                    distinct=True,
                    filter=Q(
                        region_anomalous_resolved__anomaly__anomaly_type="REPLACEMENT"
                    ),
                )
            ),
            un_validated=(
                Count(
                    "region_anomalous_resolved",
                    distinct=True,
                    filter=(Q(region_anomalous_resolved__incms_status=False) & ~Q(
                        region_anomalous_resolved__faultystatus='found_meter_okay')),
                )
            ),
            today=Count(
                "region_anomalous_resolved",
                distinct=True,
                filter=Q(region_anomalous_resolved__dtadd__date=today),
            ),
            today_1=Count(
                "region_anomalous_resolved",
                distinct=True,
                filter=Q(region_anomalous_resolved__dtadd__date=yesterday),
            ),
            today_2=Count(
                "region_anomalous_resolved",
                distinct=True,
                filter=Q(region_anomalous_resolved__dtadd__date=yesterday_1),
            ),
            today_3=Count(
                "region_anomalous_resolved",
                distinct=True,
                filter=Q(region_anomalous_resolved__dtadd__date=yesterday_2),
            ),
            today_4=Count(
                "region_anomalous_resolved",
                distinct=True,
                filter=Q(region_anomalous_resolved__dtadd__date=yesterday_3),
            ),
        )
        .order_by("name")
    )

    county_analytics = (
        County.objects.prefetch_related("anomlalous_accounts_set", "anomalous_resolved_set")
        .values("name", "region_id")  # select_related('dc_region')
        .annotate(
            dc_target_acs=(Sum("fallbackrri_target", distinct=True)),
            recoveries=(Sum("anomalous_recoveries", distinct=True)),
            dc_inspected=(Count("county_anomalous_resolved", distinct=True)),
            pending_faulty=(Sum("fallbackrri_faulty", distinct=True)),
            found_okay=(Count(
                "county_anomalous_resolved",
                distinct=True,
                filter=Q(
                    county_anomalous_resolved__faultystatus="found_meter_okay"
                ),
            )),
            resolved_faulty=(
                Count(
                    "county_anomalous_resolved",
                    distinct=True,
                    filter=Q(
                        county_anomalous_resolved__anomaly__anomaly_type="FAULTY"
                    ),
                )
            ),
            pending_tampered=(Sum("fallbackrri_tampered", distinct=True)),
            resolved_tampered=(
                Count(
                    "county_anomalous_resolved",
                    distinct=True,
                    filter=Q(
                        county_anomalous_resolved__anomaly__anomaly_type="TAMPERED"
                    ),
                )
            ),
            pending_normalised=(Sum("fallbackrri_bypassed", distinct=True)),
            resolved_normalised=(
                Count(
                    "county_anomalous_resolved",
                    distinct=True,
                    filter=Q(
                        county_anomalous_resolved__anomaly__anomaly_type="BYPASSED"
                    ),
                )
            ),
            pending_directconn=(Sum("fallbackrri_dc", distinct=True)),
            resolved_directconn=(
                Count(
                    "county_anomalous_resolved",
                    distinct=True,
                    filter=Q(
                        county_anomalous_resolved__anomaly__anomaly_type="DIRECT CONNECTION"
                    ),
                )
            ),
            pending_repacements=(Sum("fallbackrri_replace", distinct=True)),
            resolved_replacements=(
                Count(
                    "county_anomalous_resolved",
                    distinct=True,
                    filter=Q(
                        county_anomalous_resolved__anomaly__anomaly_type="REPLACEMENT"
                    ),
                )
            ),
            pending_tid=(Sum("fallbackrri_tid", distinct=True)),
            resolved_tid=(
                Count(
                    "county_anomalous_resolved",
                    distinct=True,
                    filter=Q(
                        county_anomalous_resolved__anomaly__anomaly_type="TID UNCOMPLIANT"

                    ),
                )
            ),
            un_validated=(
                Count(
                    "county_anomalous_resolved",
                    distinct=True,
                    filter=(Q(county_anomalous_resolved__incms_status=False) & ~Q(
                        county_anomalous_resolved__faultystatus='found_meter_okay')),
                )
            ),
            today=Count(
                "county_anomalous_resolved",
                distinct=True,
                filter=Q(county_anomalous_resolved__dtadd__date=today),
            ),
            today_1=Count(
                "county_anomalous_resolved",
                distinct=True,
                filter=Q(county_anomalous_resolved__dtadd__date=yesterday),
            ),
            today_2=Count(
                "county_anomalous_resolved",
                distinct=True,
                filter=Q(county_anomalous_resolved__dtadd__date=yesterday_1),
            ),
            today_3=Count(
                "county_anomalous_resolved",
                distinct=True,
                filter=Q(county_anomalous_resolved__dtadd__date=yesterday_2),
            ),
            today_4=Count(
                "county_anomalous_resolved",
                distinct=True,
                filter=Q(county_anomalous_resolved__dtadd__date=yesterday_3),
            ),
        )
        .order_by("region_id")
    )
    context = {
        "yesterday": yesterday,
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,
        "region_analytics": region_analytics,
        "county_analytics": county_analytics,
        "daily_trend_plot": daily_trend(),
        "target_achievement": target_achievement(),
        "meter_type": meter_type(),
        "anomaly_type": anomaly_type(),
        'total_inspections': inspection_count,
    }
    return render(request, "postpaid/anomalous/rri_dashboard.html", context)


@login_required(login_url="login")
def anomalous_inspector_analytics(request):
    if request.user.is_authenticated:
        user = request.user
    county = request.user.userprofile.county
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    inspectors = (
        Anomalous_resolved.objects.select_related("user")
        .values(
            "user__user_id__stid",
            "user__user_id__name",
            "user__user_id__mobile",
        )
        .filter(county=county)
        .annotate(
            the_count=Count("user"),
            today=Count("user", filter=Q(dtadd__date=today)),
            yesturday=Count("user", filter=Q(dtadd__date=yesterday)),
            yesturday_1=Count("user", filter=Q(dtadd__date=yesterday_1)),
            yesturday_2=Count("user", filter=Q(dtadd__date=yesterday_2)),
            yesturday_3=Count("user", filter=Q(dtadd__date=yesterday_3)),
        ).order_by("user__user_id__stid")
    )

    context = {
        "analytics": inspectors,
        "nbar": "analytics",
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,
        "county": county,
    }
    return render(request, "postpaid/anomalous/anomalous_user_analytics.html", context)


@login_required(login_url="login")
def anomaly_resolved_list(request):
    if request.user.is_authenticated:
        user = request.user.userprofile

    meters = Anomalous_resolved.objects.order_by("-dtadd")
    paginator = Paginator(meters, 30)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {
        "meters": paged_uploads,
        "nbar": "myuploads",
    }
    return render(request, "postpaid/anomalous/anomalous_resolved_list.html", context)


@login_required(login_url="login")
def myanomalous_list(request):
    meters = (
        Anomalous_resolved.objects.select_related("user")
        .filter(user=request.user.userprofile)
        .order_by("-dtadd")
    )
    paginator = Paginator(meters, 30)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {
        "meters": paged_uploads,
    }
    return render(request, "postpaid/anomalous/anomalous_resolved_my.html", context)


@login_required(login_url="login")
def anomalous_replace_faulty(request, pk):
    # userprofile = get_object_or_404(UserProfile, user=request.user)
    img = Anomlalous_accounts.objects.get(id=pk)

    campaign = request.user.userprofile.campaign

    if campaign not in (
            "network_technician",
            "network_supervisors",
            "network_region",
            "contractor_safaricom",
            "contractor_allandick",
            "other",
    ):
        if request.method == "POST":
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = AnomalousForm(request.POST, request.FILES, instance=img)

            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                resolution = Anomalous_resolved()
                resolution.longitude = m_form.cleaned_data["longitude"]
                resolution.latitude = m_form.cleaned_data["latitude"]
                resolution.faultystatus = m_form.cleaned_data["faultystatus"]
                resolution.comment = m_form.cleaned_data["comment"]
                resolution.new_meterno = m_form.cleaned_data["new_meterno"]
                resolution.accountno = img.accountno
                resolution.meterno = img.meterno
                resolution.anomaly = img
                resolution.user = request.user.userprofile
                resolution.region = request.user.userprofile.region
                resolution.county = request.user.userprofile.county

                resolution.save()
                zerov.status = True
                zerov.save()
                messages.success(
                    request, "Your Inspection Has been successfully saved."
                )
                return redirect("postpaid:myanomalous-list")
            else:
                print("invalid form")
                print(m_form.errors)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = AnomalousForm(instance=img)
        context = {
            "form": m_form,
        }
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

    return render(request, "postpaid/anomalous/resolve_faulty.html", context)


@login_required(login_url="login")
def anomalous_search_meter(request):
    county = request.user.userprofile.county
    meters_list = Anomlalous_accounts.objects.select_related("county").filter(
        status=False, county=county
    )
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {"meters": paged_uploads, "county": county}
    return render(request, "postpaid/anomalous/anomalous_target.html", context)


@login_required(login_url="login")
def anomalous_target(request):
    county = request.user.userprofile.county
    meters = Anomlalous_accounts.objects.select_related("county").filter(
        status=False, county=county
    )
    paginator = Paginator(meters, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {"meters": paged_uploads, "nbar": "alluploads", "county": county}
    return render(request, "postpaid/anomalous/anomalous_target.html", context)


@login_required(login_url="login")
def view_zerobill_county(request, pk):
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    county_analytics = (
        County.objects.select_related("county")
        .filter(region=pk)
        .values("name")
        .annotate(
            dc_target_acs=(Sum("zerobill_march", distinct=True)),
            dc_inspected=(Count("county_zb_resolved", distinct=True)),
            dc_insp_faulty=(
                Count(
                    "county_zb_resolved",
                    distinct=True,
                    filter=~Q(
                        county_zb_resolved__status4__in=[
                            "meterokay",
                            "disconnected",
                            "vacantpremises",
                        ]
                    ),
                )
            ),
            un_validated=(
                Count(
                    "county_zb_resolved",
                    distinct=True,
                    filter=(
                            Q(county_zb_resolved__status2="pending")
                            & (
                                ~Q(
                                    county_zb_resolved__status4__in=[
                                        "meterokay",
                                        "disconnected",
                                        "vacantpremises",
                                    ]
                                )
                            )
                    ),
                )
            ),
            today=Count(
                "county_zb_resolved",
                distinct=True,
                filter=Q(county_zb_resolved__dtadd__date=today),
            ),
            today_1=Count(
                "county_zb_resolved",
                distinct=True,
                filter=Q(county_zb_resolved__dtadd__date=yesterday),
            ),
            today_2=Count(
                "county_zb_resolved",
                distinct=True,
                filter=Q(county_zb_resolved__dtadd__date=yesterday_1),
            ),
            today_3=Count(
                "county_zb_resolved",
                distinct=True,
                filter=Q(county_zb_resolved__dtadd__date=yesterday_2),
            ),
            today_4=Count(
                "county_zb_resolved",
                distinct=True,
                filter=Q(county_zb_resolved__dtadd__date=yesterday_3),
            ),
        )
        .order_by("region")
    )
    context = {
        "county_analytics": county_analytics,
        "yesterday": yesterday,
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,
        "region": Region.objects.get(id=pk)
    }
    return render(
        request, "postpaid/zerobills/confiermed_zerobill_county.html", context
    )


@login_required(login_url="login")
def zerobills_search_account(request):
    meters_list = Zerobillresolved.objects.select_related("county")
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {"meters": paged_uploads}
    return render(request, "postpaid/zerobills/zerobills_confirmed_list.html", context)


@login_required(login_url="login")
def zerobill_confirmation_dashboard(request):
    # oveall_target = County.objects.aggregate(Sum("publiclighting_target"))

    oveall_inspected = Zerobillresolved.objects.values(
        "status4", "dtadd", "id", "status2"
    )
    overall_not_okay = oveall_inspected.exclude(
        status4__in=["meterokay", "disconnected", "vacantpremises"]
    )

    # Test the function
    start_date = datetime.date(2023, 10, 28)
    end_date = datetime.date.today()

    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    def non_consent():
        df = read_frame(oveall_inspected)
        df = df.groupby(by="concurrence", as_index=False, sort=False)[
            "newmeter"
        ].count()
        values = df.concurrence
        names = df.newmeter
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Collaboration-Consent status",
            labels={
                "newmeter": "Meter Count",
                "validate_status": "Consent Status",
            },
        )
        df.update_traces(textposition="inside", textinfo="percent+label")
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    def metering_status_notokay():
        df = read_frame(overall_not_okay)
        df = df.groupby(by="status2", as_index=False, sort=False)["id"].count()
        values = df.status2
        names = df.id
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Confirmed Not Okay Backoffice Status",
            labels={
                "id": "Meter Count",
                "status2": "Validation Status",
            },
        )
        df.update_traces(textposition="inside", textinfo="percent+label")
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    def metering_status():
        df = read_frame(oveall_inspected)
        df = df.groupby(by="status4", as_index=False, sort=False)["id"].count()
        values = df.status4
        names = df.id
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Meter Status",
            labels={
                "id": "Meter Count",
                "status4": "Metering Status",
            },
        )
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    def target_achievement():
        t_a = oveall_inspected.count()
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Planned Current-Month",
                    x=["Planned Current-Month"],
                    y=[41242],
                ),
                go.Bar(
                    name="Achieved Current-Month", x=["Achieved Current-Month"], y=[t_a]
                ),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Target vs Achievement",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="No Of Confirmations",
                titlefont_size=16,
                tickfont_size=14,
            ),
            xaxis=dict(
                title="Year(2023/24)",
            ),
            legend=dict(
                bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
            ),
            barmode="group",
            bargap=0.15,  # gap between bars of adjacent location coordinates.
            bargroupgap=0.1,  # gap between bars of the same location coordinate.
        )
        fig_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return fig_plot

    def daily_trend():
        df = read_frame(oveall_inspected)
        df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
        df = df.groupby(by="dtadd", as_index=False, sort=False)["id"].count()
        df = px.bar(
            df,
            x=df.dtadd,
            y=df.id,
            title=f"Daily Overall Confirmation.",
            text_auto=True,
            text=df.id,
            labels={"id": "Meter Count", "dtadd": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    region_analytics = (
        Region.objects.select_related("region")
        .values("name", "id")  # select_related('dc_region')
        .annotate(
            dc_target_acs=(Sum("zerobill_march", distinct=True)),
            recoveries=(Sum("zerobill_recoveries", distinct=True)),
            dc_inspected=(Count("region_zb_resolved", distinct=True)),
            dc_insp_faulty=(
                Count(
                    "region_zb_resolved",
                    distinct=True,
                    filter=~Q(
                        region_zb_resolved__status4__in=[
                            "meterokay",
                            "disconnected",
                            "vacantpremises",
                        ]
                    ),
                )
            ),
            un_validated=(
                Count(
                    "region_zb_resolved",
                    distinct=True,
                    filter=(
                            Q(region_zb_resolved__status2="pending")
                            & (
                                ~Q(
                                    region_zb_resolved__status4__in=[
                                        "meterokay",
                                        "disconnected",
                                        "vacantpremises",
                                    ]
                                )
                            )
                    ),
                )
            ),
            today=Count(
                "region_zb_resolved",
                distinct=True,
                filter=Q(region_zb_resolved__dtadd__date=today),
            ),
            today_1=Count(
                "region_zb_resolved",
                distinct=True,
                filter=Q(region_zb_resolved__dtadd__date=yesterday),
            ),
            today_2=Count(
                "region_zb_resolved",
                distinct=True,
                filter=Q(region_zb_resolved__dtadd__date=yesterday_1),
            ),
            today_3=Count(
                "region_zb_resolved",
                distinct=True,
                filter=Q(region_zb_resolved__dtadd__date=yesterday_2),
            ),
            today_4=Count(
                "region_zb_resolved",
                distinct=True,
                filter=Q(region_zb_resolved__dtadd__date=yesterday_3),
            ),
        )
        .order_by("name")
    )
    county_analytics = (
        County.objects.select_related("county")
        .values("name")
        .annotate(
            dc_target_acs=(Sum("zerobill_march", distinct=True)),
            dc_inspected=(Count("county_zb_resolved", distinct=True)),
            dc_insp_faulty=(
                Count(
                    "county_zb_resolved",
                    distinct=True,
                    filter=~Q(
                        county_zb_resolved__status4__in=[
                            "meterokay",
                            "disconnected",
                            "vacantpremises",
                        ]
                    ),
                )
            ),
            un_validated=(
                Count(
                    "county_zb_resolved",
                    distinct=True,
                    filter=(
                            Q(county_zb_resolved__status2="pending")
                            & (
                                ~Q(
                                    county_zb_resolved__status4__in=[
                                        "meterokay",
                                        "disconnected",
                                        "vacantpremises",
                                    ]
                                )
                            )
                    ),
                )
            ),
            today=Count(
                "county_zb_resolved",
                distinct=True,
                filter=Q(county_zb_resolved__dtadd__date=today),
            ),
            today_1=Count(
                "county_zb_resolved",
                distinct=True,
                filter=Q(county_zb_resolved__dtadd__date=yesterday),
            ),
            today_2=Count(
                "county_zb_resolved",
                distinct=True,
                filter=Q(county_zb_resolved__dtadd__date=yesterday_1),
            ),
            today_3=Count(
                "county_zb_resolved",
                distinct=True,
                filter=Q(county_zb_resolved__dtadd__date=yesterday_2),
            ),
            today_4=Count(
                "county_zb_resolved",
                distinct=True,
                filter=Q(county_zb_resolved__dtadd__date=yesterday_3),
            ),
        )
        .order_by("region")
    )

    context = {
        # "oveall_target": oveall_target,
        # "per_insp": per_insp,
        # "oveall_inspected": overall_inspected_count,
        # "overall_faulty": overall_faulty,
        # "overall_tampered": overall_tampered,
        # "overall_bypassed": overall_bypassed,
        # "non_consent": non_consent(),
        "daily_trend_plot": daily_trend(),
        "target_achievement": target_achievement(),
        "metering_status": metering_status(),
        "metering_status_notokay": metering_status_notokay(),
        "region_analytics": region_analytics,
        "county_analytics": county_analytics,
        "yesterday": yesterday,
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,
    }
    return render(request, "postpaid/zerobills/zerobills_dashboard.html", context)


@login_required(login_url="login")
def county_telcosrep_useranalytics(request):
    if request.user.is_authenticated:
        user = request.user
    county = request.user.userprofile.county
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)
    yesterday_4 = date.today() - timedelta(days=5)

    inspectors = Telcos_replacement.objects.select_related('inspector').values('inspector__user_id__stid',
                                                                               'inspector__user_id__name',
                                                                               'inspector__user_id__mobile').filter(
        county=county).annotate(
        the_count=Count("inspector"),
        today=Count("inspector", filter=Q(dtadd__date=today)),
        yesturday=Count(
            "inspector", filter=Q(dtadd__date=yesterday)
        ),
        yesturday_1=Count(
            "inspector", filter=Q(dtadd__date=yesterday_1)
        ),
        yesturday_2=Count(
            "inspector", filter=Q(dtadd__date=yesterday_2)
        ),
        yesturday_3=Count(
            "inspector", filter=Q(dtadd__date=yesterday_3)
        ),
        yesturday_4=Count(
            "inspector", filter=Q(dtadd__date=yesterday_4)
        ),

    ).order_by('inspector__user_id__stid')

    context = {
        "analytics": inspectors,
        "nbar": "analytics",
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,
        "yesterday_4": yesterday_4,
        'county': county
    }
    return render(request, "postpaid/telcos/user_replacement_analytics.html", context)


@login_required(login_url="login")
def zerobill_inspector_analytics(request):
    if request.user.is_authenticated:
        user = request.user
    county = request.user.userprofile.county
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)

    inspectors = (
        UserProfile.objects.select_related('county').filter(campaign="zerobills", county=county)
        .values("user_id__id", "user_id__name", "user_id__mobile", "county__name", "user_id__stid")
        .annotate(
            the_count=Count("Zerobillresolved_user"),
            today=Count(
                "Zerobillresolved_user",
                filter=Q(Zerobillresolved_user__dtadd__date=today),
            ),
            yesturday=Count(
                "Zerobillresolved_user",
                filter=Q(Zerobillresolved_user__dtadd__date=yesterday),
            ),
            yesturday_1=Count(
                "Zerobillresolved_user",
                filter=Q(Zerobillresolved_user__dtadd__date=yesterday_1),
            ),
            yesturday_2=Count(
                "Zerobillresolved_user",
                filter=Q(Zerobillresolved_user__dtadd__date=yesterday_2),
            ),
        )
        .order_by("county__name")
    )

    context = {
        "analytics": inspectors,
        "nbar": "analytics",
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        'county': county
    }
    return render(request, "postpaid/zerobills/zerobills_user_analytics.html", context)


@login_required(login_url="login")
def zerobills__all_export_uploads(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)

    meters = Zerobillresolved.objects.select_related('region', 'county', 'user').filter(
        dtadd__gt=datetime.datetime.today() - datetime.timedelta(days=14)
        ).order_by("-dtadd")

    writer.writerow(
        [
            "REGION",
            "COUNTY",
            "SECTOR",
            "ZONE",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "STATUS",
            "SYSTEM READING",
            "METER READING",
            "IMAGE URL",
            'DATE CONFIRMED',
            'USER',
            'COMMENT',
            'LATITUDE',
            'LONGITUDE'

        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.region,
                meter.county,
                meter.zerobill.sector,
                meter.zerobill.zone,
                meter.meterno,
                meter.accountno,
                meter.status4,
                meter.zerobill.reading,
                meter.readings,
                meter.meterimg,
                meter.dtadd,
                meter.user,
                meter.comment,
                meter.latitude,
                meter.longitude
            ]
        )

    response["Content-Disposition"] = 'attachment; filename="ZEROBILL_ACCOUNTS_CONFIRMED.csv" '
    return response


@login_required(login_url="login")
def zerobills_export_uploads(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    county = request.user.userprofile.county
    meters = Zerobillresolved.objects.select_related('region', 'county', 'user').filter(county=county,
                                                                                        dtadd__gt=datetime.datetime.today() - datetime.timedelta(
                                                                                            days=14)
                                                                                        ).order_by("-dtadd")

    writer.writerow(
        [
            "REGION",
            "COUNTY",
            "SECTOR",
            "ZONE",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "STATUS",
            "SYSTEM READING",
            "METER READING",
            "IMAGE URL",
            'DATE CONFIRMED',
            'USER',
            'COMMENT',
            'LATITUDE',
            'LONGITUDE'

        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.region,
                meter.county,
                meter.zerobill.sector,
                meter.zerobill.zone,
                meter.meterno,
                meter.accountno,
                meter.status4,
                meter.zerobill.reading,
                meter.readings,
                meter.meterimg,
                meter.dtadd,
                meter.user,
                meter.comment,
                meter.latitude,
                meter.longitude
            ]
        )

    response["Content-Disposition"] = 'attachment; filename="ZEROBILL_ACCOUNTS_CONFIRMED.csv" '
    return response


@login_required(login_url="login")
def zerobills_targets_export_uploads(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    county = request.user.userprofile.county
    meters = Zerobills.objects.select_related('region', 'county').filter(county=county,status=False).order_by('sector')

    writer.writerow(
        [
            "REGION",
            "COUNTY",
            "SECTOR",
            "ZONE",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "CUSTOMER",
            "SYSTEM READING",
            "NO. ZEROBILL",
            'STATUS'
        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.region,
                meter.county,
                meter.sector,
                meter.zone,
                meter.meterno,
                meter.accountno,
                meter.customername,
                meter.reading,
                meter.notimeszero,
                meter.status
            ]
        )

    response["Content-Disposition"] = 'attachment; filename="ZEROBILL_ACCOUNTS.csv" '
    return response


@login_required(login_url="login")
def view_confirmed_meter(request, pk):
    meter = Zerobillresolved.objects.get(id=pk)
    context = {
        "meter": meter,
    }
    return render(request, "postpaid/zerobills/confirmed_detail.html", context)


@login_required(login_url="login")
def zerobills_confirmed_list(request):
    if request.user.is_authenticated:
        user = request.user.userprofile

    meters = Zerobillresolved.objects.order_by("-dtadd")
    paginator = Paginator(meters, 30)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {
        "meters": paged_uploads,
        "nbar": "myuploads",
    }
    return render(request, "postpaid/zerobills/zerobills_confirmed_list.html", context)


@login_required(login_url="login")
def myzerobills_list(request):
    if request.user.is_authenticated:
        user = request.user.userprofile

    meters = Zerobillresolved.objects.filter(user=user).order_by("-dtadd")
    paginator = Paginator(meters, 30)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {
        "meters": paged_uploads,
        "nbar": "myuploads",
    }
    return render(request, "postpaid/zerobills/zerobills_confirmed_my.html", context)


@login_required(login_url="login")
def zerobill_confirm(request, pk):
    # userprofile = get_object_or_404(UserProfile, user=request.user)
    img = Zerobills.objects.get(id=pk)

    campaign = request.user.userprofile.campaign

    if campaign not in (
            "network_technician",
            "network_supervisors",
            "network_region",
            "contractor_safaricom",
            "contractor_allandick",
            "other",
    ):
        if request.method == "POST":
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = MeterForm(request.POST, request.FILES, instance=img)

            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                resolution = Zerobillresolved()
                resolution.longitude = m_form.cleaned_data["longitude"]
                resolution.latitude = m_form.cleaned_data["latitude"]
                resolution.readings = m_form.cleaned_data["readings"]
                resolution.comment = m_form.cleaned_data["comment"]
                resolution.status4 = m_form.cleaned_data["status4"]
                resolution.meterimg = m_form.cleaned_data["meterimg"]
                resolution.accountno = img.accountno
                resolution.meterno = img.meterno
                resolution.zerobill = img
                resolution.reading = img.reading
                resolution.user = request.user.userprofile
                resolution.region = request.user.userprofile.region
                resolution.county = request.user.userprofile.county
                resolution.diffunits = resolution.readings - img.reading

                resolution.save()
                zerov.status = True
                zerov.save()
                messages.success(
                    request, "Your Inspection Has been successfully saved."
                )
                return redirect("postpaid:myzerobills-list")
            else:
                print("invalid form")
                print(m_form.errors)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = MeterForm(instance=img)
        context = {
            "form": m_form,
        }
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

    return render(request, "postpaid/zerobills/confirm_zerobill.html", context)


@login_required(login_url="login")
def zerobills_search_meter(request):
    county = request.user.userprofile.county
    meters_list = Zerobills.objects.select_related("county").filter(status=False, county=county)
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {
        "meters": paged_uploads,
        'county': county
    }
    return render(request, "postpaid/zerobills/zerobills_target.html", context)


@login_required(login_url="login")
def zerobills_target(request):
    county = request.user.userprofile.county
    meters = Zerobills.objects.select_related("county").filter(status=False, county=county)
    paginator = Paginator(meters, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {
        "meters": paged_uploads,
        "nbar": "alluploads",
        'county': county
    }
    return render(request, "postpaid/zerobills/zerobills_target.html", context)


@login_required(login_url="login")
def replacement_edit(request, pk):
    # userprofile = get_object_or_404(UserProfile, user=request.user)
    img = Telcos_replacement.objects.get(id=pk)

    campaign = request.user.userprofile.campaign

    if campaign == "telcos":
        if request.method == "POST":
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = Telcos_replacementForm(request.POST, request.FILES, instance=img)

            if m_form.is_valid():
                # if m_form.cleaned_data['meterno'] is None:
                # messages.success(request, 'You need to take the Cordinates.')
                # return redirect('postpaid:mythreephase-list')
                #

                resolution = m_form.save(commit=False)
                resolution.siteid = m_form.cleaned_data["siteid"]
                resolution.sitename = m_form.cleaned_data["sitename"]
                resolution.oldmeter = m_form.cleaned_data["oldmeter"]
                resolution.newmeter = m_form.cleaned_data["newmeter"]
                resolution.accountno = img.accountno
                resolution.meteringstatus = m_form.cleaned_data["meteringstatus"]
                resolution.faultystatus = m_form.cleaned_data["faultystatus"]
                resolution.tamperedstatus = m_form.cleaned_data["tamperedstatus"]
                resolution.bypassstatus = m_form.cleaned_data["bypassstatus"]
                resolution.removal_img = m_form.cleaned_data["removal_img"]
                resolution.install_img = m_form.cleaned_data["install_img"]
                resolution.removal_reading = m_form.cleaned_data["removal_reading"]
                resolution.install_reading = m_form.cleaned_data["install_reading"]
                resolution.phase = m_form.cleaned_data["phase"]
                resolution.comment = m_form.cleaned_data["comment"]
                resolution.x = m_form.cleaned_data["x"]
                resolution.y = m_form.cleaned_data["y"]
                resolution.county = m_form.cleaned_data["county"]
                resolution.txnumber = m_form.cleaned_data["txnumber"]
                resolution.feeder_name = m_form.cleaned_data["feeder_name"]
                resolution.dedicated_lv = m_form.cleaned_data["dedicated_lv"]
                resolution.seal_terminalcover = m_form.cleaned_data["seal_terminalcover"]
                resolution.seal_gprs = m_form.cleaned_data["seal_gprs"]
                resolution.gprs_ariel = m_form.cleaned_data["gprs_ariel"]
                resolution.inspector = request.user.userprofile
                resolution.region = request.user.userprofile.region
                resolution.system_reading = img.telcos.system_reading
                resolution.units = resolution.removal_reading - resolution.system_reading

                resolution.save()

                messages.success(
                    request, "Your Inspection Has been successfully saved."
                )
                return redirect("postpaid:mytelcos-replc_list")
            else:
                print("invalid form")
                print(m_form.errors)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = Telcos_replacementForm(instance=img)
        context = {
            "form": m_form,
        }
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

    return render(request, "postpaid/telcos/replace_telcos.html", context)


@login_required(login_url="login")
def export_replacements_telcos(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    meters = Telcos_replacement.objects.select_related('county')
    meters = meters.filter(dtadd__gt=datetime.datetime.today() - datetime.timedelta(days=14)).order_by('-dtadd')

    writer.writerow(
        [
            "SITE ID",
            "SITE NAME",
            "ACCOUNT NUMBER",
            "OLD NUMBER",
            "OLD METER METERING STATUS",
            "REMOVAL READING",
            "NEW METER",
            "NEW METER READING",
            "COUNTY",
            "REPLACED BY",
            "COLLABORATED BY",
            'DATE REPALCED',
            'OLD METER IMAGE URL',
            'NEW METER IMAGE URL'

        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.siteid,
                meter.sitename,
                meter.accountno,
                meter.oldmeter,
                meter.meteringstatus,
                meter.removal_reading,
                meter.newmeter,
                meter.install_reading,
                meter.county,
                meter.inspector,
                meter.concurrence_staff,
                meter.dtadd,
                meter.removal_img,
                meter.install_img

            ]
        )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="TELCOS_REPLACEMENTS.csv" '
    return response


@login_required(login_url="login")
def telcos_repalcement_dashboard(request):
    # oveall_target = County.objects.aggregate(Sum("publiclighting_target"))

    oveall_inspected = Telcos_replacement.objects.values(
        "meteringstatus", "newmeter", "dtadd", 'validate_status', 'concurrence'
    )
    target_daone = Telcos_rpl_target.objects.values('id').filter(status=True)
    overall_not_okay = oveall_inspected.exclude(meteringstatus="okay")

    def count_business_days(start_date, end_date):
        # Define a list of weekend days (Saturday and Sunday)
        weekend_days = [5, 6]  # Monday is 0 and Sunday is 6
        # Initialize a counter for business days
        business_days = 0
        target = 0
        # Iterate through each day in the date range
        current_date = start_date
        while current_date <= end_date:
            # Check if the current day is a weekend day
            if current_date.weekday() not in weekend_days:
                business_days += 1
                target += 650
            # Move to the next day
            current_date += datetime.timedelta(days=1)
        return business_days, target

    # Test the function
    start_date = datetime.date(2023, 11, 14)
    end_date = datetime.date.today()

    result = count_business_days(start_date, end_date)

    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    def non_consent():
        df = read_frame(oveall_inspected)
        df = df.groupby(by="concurrence", as_index=False, sort=False)[
            "newmeter"
        ].count()
        values = df.concurrence
        names = df.newmeter
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Collaboration-Consent status",
            labels={
                "newmeter": "Meter Count",
                "validate_status": "Consent Status",
            },
        )
        df.update_traces(textposition="inside", textinfo="percent+label")
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    def metering_status_notokay():
        df = read_frame(oveall_inspected)
        df = df.groupby(by="validate_status", as_index=False, sort=False)[
            "newmeter"
        ].count()
        values = df.validate_status
        names = df.newmeter
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Installed Meter Validation Status",
            labels={
                "newmeter": "Meter Count",
                "validate_status": "Validation Status",
            },
        )
        df.update_traces(textposition="inside", textinfo="percent+label")
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    def metering_status():
        df = read_frame(oveall_inspected)
        df = df.groupby(by="meteringstatus", as_index=False, sort=False)[
            "newmeter"
        ].count()
        values = df.meteringstatus
        names = df.newmeter
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Removed Meter Metering Status",
            labels={
                "newmeter": "Meter Count",
                "meteringstatus": "Metering Status",
            },
        )
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    def target_achievement():
        t_a = target_daone.count()
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Planned ToDate",
                    x=["Planned ToDate"],
                    # y=[result[1]],
                    y=[7694],
                ),
                go.Bar(name="Achieved ToDate", x=["Achieved ToDate"], y=[t_a]),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Target vs Achievement",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="No Of Replacements",
                titlefont_size=16,
                tickfont_size=14,
            ),
            xaxis=dict(
                title="Year(2023/24)",
            ),
            legend=dict(
                bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
            ),
            barmode="group",
            bargap=0.15,  # gap between bars of adjacent location coordinates.
            bargroupgap=0.1,  # gap between bars of the same location coordinate.
        )
        fig_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return fig_plot

    def daily_trend():
        df = read_frame(oveall_inspected)
        df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
        df = df.groupby(by="dtadd", as_index=False, sort=False)["newmeter"].count()
        df = px.bar(
            df,
            x=df.dtadd,
            y=df.newmeter,
            title=f"Daily Overall Replacement.Daily Target = {650}",
            text_auto=True,
            text=df.newmeter,
            labels={"newmeter": "Meter Count", "dtadd": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    region_analytics = (
        Region.objects.select_related("region")
        .values("name")  # select_related('dc_region')
        .annotate(
            dc_target_acs=(Sum("telcos_replace_target", distinct=True)),
            dc_daily_target=(Sum("telcos_replace_target_daily", distinct=True)),
            dc_inspected=(Count("region_repalcement", distinct=True)),
            dc_insp_faulty=(
                Count(
                    "region_repalcement",
                    distinct=True,
                    exclude=Q(region_repalcement__meteringstatus="okay"),
                )
            ),
            un_validated=(
                Count(
                    "region_repalcement",
                    distinct=True,
                    filter=Q(region_repalcement__validate_status=False),
                )
            ),

            today=Count(
                "region_repalcement",
                distinct=True,
                filter=Q(region_repalcement__dtadd__date=today),
            ),
            today_1=Count(
                "region_repalcement",
                distinct=True,
                filter=Q(region_repalcement__dtadd__date=yesterday),
            ),
            today_2=Count(
                "region_repalcement",
                distinct=True,
                filter=Q(region_repalcement__dtadd__date=yesterday_1),
            ),
            today_3=Count(
                "region_repalcement",
                distinct=True,
                filter=Q(region_repalcement__dtadd__date=yesterday_2),
            ),
            today_4=Count(
                "region_repalcement",
                distinct=True,
                filter=Q(region_repalcement__dtadd__date=yesterday_3),
            ),
        )
        .order_by("name")
    )
    county_analytics = (
        County.objects.select_related("county")
        .values("name")
        .annotate(
            dc_target_acs=(Sum("telcos_replace_target", distinct=True)),
            dc_daily_target=(Sum("telcos_replace_target_daily", distinct=True)),
            dc_inspected=(Count("county_repalcement", distinct=True)),
            dc_insp_faulty=(
                Count(
                    "county_repalcement",
                    distinct=True,
                    exclude=Q(region_repalcement__meteringstatus="okay"),
                )
            ),
            un_validated=(
                Count(
                    "county_repalcement",
                    distinct=True,
                    filter=Q(county_repalcement__validate_status=False),
                )
            ),
            today=Count(
                "county_repalcement",
                distinct=True,
                filter=Q(county_repalcement__dtadd__date=today),
            ),
            today_1=Count(
                "county_repalcement",
                distinct=True,
                filter=Q(county_repalcement__dtadd__date=yesterday),
            ),
            today_2=Count(
                "county_repalcement",
                distinct=True,
                filter=Q(county_repalcement__dtadd__date=yesterday_1),
            ),
            today_3=Count(
                "county_repalcement",
                distinct=True,
                filter=Q(county_repalcement__dtadd__date=yesterday_2),
            ),
            today_4=Count(
                "county_repalcement",
                distinct=True,
                filter=Q(county_repalcement__dtadd__date=yesterday_3),
            ),
        )
        .order_by("region")
    )

    context = {
        # "oveall_target": oveall_target,
        # "per_insp": per_insp,
        # "oveall_inspected": overall_inspected_count,
        # "overall_faulty": overall_faulty,
        # "overall_tampered": overall_tampered,
        # "overall_bypassed": overall_bypassed,
        "non_consent": non_consent(),
        "daily_trend_plot": daily_trend(),
        "target_achievement": target_achievement(),
        "metering_status": metering_status(),
        "metering_status_notokay": metering_status_notokay(),
        "region_analytics": region_analytics,
        "county_analytics": county_analytics,
        "yesterday": yesterday,
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,
    }
    return render(request, "postpaid/telcos/replacement_dashboard.html", context)


@login_required(login_url="login")
def search_by_siteid_replaced(request):
    meters_list = Telcos_replacement.objects.all()
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(siteid__icontains=keyword)
    context = {
        "meters": paged_uploads,
    }
    return render(request, "postpaid/telcos/replaced_all.html", context)


@login_required(login_url="login")
def search_by_newmeter_replaced(request):
    meters_list = Telcos_replacement.objects.all()
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(newmeter__icontains=keyword)
    context = {
        "meters": paged_uploads,
    }
    return render(request, "postpaid/telcos/replaced_all.html", context)


@login_required(login_url="login")
def replacement_print(request, pk):
    meter = Telcos_replacement.objects.get(id=pk)

    context = {
        "meter": meter,

    }
    return render(request, "postpaid/telcos/replacement_print.html", context)


@login_required(login_url="login")
def collaborate(request, pk=None):
    telcos = get_object_or_404(Telcos_replacement, id=pk)

    if request.method == 'POST':
        form = ConsentTelcosForm(request.POST, instance=telcos)

        if form.is_valid():
            regis = form.save(commit=False)
            regis.concurrence = form.cleaned_data['concurrence']
            regis.concurrence_notes = form.cleaned_data['concurrence_notes']
            regis.concurrence_staff = request.user.userprofile
            regis.concurrence_status = True
            regis.save()
            messages.success(request, 'The Telcos Meter Replacement Was Collaborated Successfully.')
            return redirect('postpaid:view-replc_telcos')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = ConsentTelcosForm(instance=telcos)

    context = {
        'lvinspection': telcos,
        'form': form
    }
    return render(request, 'postpaid/telcos/replace_detail.html', context)


@login_required(login_url="login")
def view_replaced_site(request, pk):
    meter = Telcos_replacement.objects.get(id=pk)
    form = ConsentTelcosForm()

    context = {
        "meter": meter,
        'form': form,
    }
    return render(request, "postpaid/telcos/replace_detail.html", context)


@login_required(login_url="login")
def view_replaced_telcos_ad(request):
    meters = (
        Telcos_replacement.objects.select_related("telcos")
        .filter(telcos__telcos_type="allandick")
        .order_by("-dtadd")
    )
    paginator = Paginator(meters, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {
        "meters": paged_uploads,
        "nbar": "alluploads",
    }
    return render(request, "postpaid/telcos/replaced_all.html", context)


@login_required(login_url="login")
def view_replaced_telcos_sf(request):
    meters = (
        Telcos_replacement.objects.select_related("telcos")
        .filter(telcos__telcos_type="safaricom")
        .order_by("-dtadd")
    )
    paginator = Paginator(meters, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {
        "meters": paged_uploads,
        "nbar": "alluploads",
    }
    return render(request, "postpaid/telcos/replaced_all.html", context)


@login_required(login_url="login")
def view_replaced_telcos(request):
    meters = Telcos_replacement.objects.select_related('telcos').order_by("-dtadd")
    paginator = Paginator(meters, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {
        "meters": paged_uploads,
        "nbar": "alluploads",
    }
    return render(request, "postpaid/telcos/replaced_all.html", context)


@login_required(login_url="login")
def mytelcos_replc_list(request):
    if request.user.is_authenticated:
        user = request.user.userprofile

    meters = Telcos_replacement.objects.filter(inspector=user).order_by("-dtadd")
    paginator = Paginator(meters, 30)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {
        "meters": paged_uploads,
        "nbar": "myuploads",
    }
    return render(request, "postpaid/telcos/replace_telcos_my.html", context)


@login_required(login_url="login")
def replace_telcos(request, pk):
    # userprofile = get_object_or_404(UserProfile, user=request.user)
    img = Telcos_rpl_target.objects.get(id=pk)

    campaign = request.user.userprofile.campaign

    if campaign not in (
            'network_technician', 'network_supervisors', 'network_region', 'contractor_safaricom',
            'contractor_allandick',
            'other'):

        if request.method == "POST":
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = Telcos_replacementForm(request.POST, request.FILES, instance=img)

            if m_form.is_valid():
                # if m_form.cleaned_data['meterno'] is None:
                # messages.success(request, 'You need to take the Cordinates.')
                # return redirect('postpaid:mythreephase-list')
                #

                zerov = m_form.save(commit=False)
                resolution = Telcos_replacement()
                resolution.siteid = m_form.cleaned_data["siteid"]
                resolution.sitename = m_form.cleaned_data["sitename"]
                resolution.oldmeter = m_form.cleaned_data["oldmeter"]
                resolution.newmeter = m_form.cleaned_data["newmeter"]
                resolution.accountno = img.accountno
                resolution.meteringstatus = m_form.cleaned_data["meteringstatus"]
                resolution.faultystatus = m_form.cleaned_data["faultystatus"]
                resolution.tamperedstatus = m_form.cleaned_data["tamperedstatus"]
                resolution.bypassstatus = m_form.cleaned_data["bypassstatus"]
                resolution.removal_img = m_form.cleaned_data["removal_img"]
                resolution.install_img = m_form.cleaned_data["install_img"]
                resolution.removal_reading = m_form.cleaned_data["removal_reading"]
                resolution.install_reading = m_form.cleaned_data["install_reading"]
                resolution.phase = m_form.cleaned_data["phase"]
                resolution.comment = m_form.cleaned_data["comment"]
                resolution.x = m_form.cleaned_data["x"]
                resolution.y = m_form.cleaned_data["y"]
                resolution.telcos = img
                resolution.county = m_form.cleaned_data["county"]
                resolution.txnumber = m_form.cleaned_data["txnumber"]
                resolution.feeder_name = m_form.cleaned_data["feeder_name"]
                resolution.dedicated_lv = m_form.cleaned_data["dedicated_lv"]
                resolution.seal_terminalcover = m_form.cleaned_data["seal_terminalcover"]
                resolution.seal_gprs = m_form.cleaned_data["seal_gprs"]
                resolution.gprs_ariel = m_form.cleaned_data["gprs_ariel"]
                resolution.inspector = request.user.userprofile
                resolution.region = request.user.userprofile.region
                resolution.system_reading = img.system_reading
                resolution.units = resolution.removal_reading - img.system_reading

                resolution.save()
                zerov.status = True
                zerov.save()
                messages.success(
                    request, "Your Inspection Has been successfully saved."
                )
                return redirect("postpaid:mytelcos-replc_list")
            else:
                print("invalid form")
                print(m_form.errors)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = Telcos_replacementForm(instance=img)
        context = {
            "form": m_form,
        }
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

    return render(request, "postpaid/telcos/replace_telcos.html", context)


@login_required(login_url="login")
def telcos_replc_search_siteid(request):
    meters_list = Telcos_rpl_target.objects.filter(status=False)
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(siteid__icontains=keyword)
    context = {
        "meters": paged_uploads,
    }
    return render(request, "postpaid/telcos/replacement_target.html", context)


@login_required(login_url="login")
def telcos_replc_search_meter(request):
    meters_list = Telcos_rpl_target.objects.filter(status=False)
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {
        "meters": paged_uploads,
    }
    return render(request, "postpaid/telcos/replacement_target.html", context)


@login_required(login_url="login")
def telcos_replc_target(request):
    meters = Telcos_rpl_target.objects.select_related('county').filter(status=False)
    paginator = Paginator(meters, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {
        "meters": paged_uploads,
        "nbar": "alluploads",
    }
    return render(request, "postpaid/telcos/replacement_target.html", context)


@login_required(login_url="login")
def tcos_dashboard(request):
    Telcos = Telcos_inspection.objects.all()

    def daily_trend():
        df = read_frame(Telcos)
        df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
        df = df.groupby(by="dtadd", as_index=False, sort=False)["meterno"].count()
        df = px.bar(
            df,
            x=df.dtadd,
            y=df.meterno,
            title=f"Daily Overall Inspections.Daily Target = {0}",
            text_auto=True,
            text=df.meterno,
            labels={"meterno": "Meter Count", "dtadd": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    context = {
        'daily_trend': daily_trend,
    }
    return render(request, "postpaid/tcos_dashboard.html", context=context)


@login_required(login_url="login")
def generation_stns_dashboard(request):
    oveall_target = Generation_stations.objects.all()
    oveall_inspected = Generation_stations_inspection.objects.values(
        "id", "meterno", "dtadd"
    )

    def target_achievement():
        t_a = oveall_inspected.count()
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Target",
                    x=["Target"],
                    y=[oveall_target.count()],
                ),
                go.Bar(name="Achieved ToDate", x=["Achieved ToDate"], y=[t_a]),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Target vs Achievement",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="No Of Inspections",
                titlefont_size=16,
                tickfont_size=14,
            ),
            xaxis=dict(
                title="Year(2023/24)",
            ),
            legend=dict(
                bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
            ),
            barmode="group",
            bargap=0.15,  # gap between bars of adjacent location coordinates.
            bargroupgap=0.1,  # gap between bars of the same location coordinate.
        )
        fig_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return fig_plot

    def daily_trend():
        df = read_frame(oveall_inspected)
        df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
        df = df.groupby(by="dtadd", as_index=False, sort=False)["meterno"].count()
        df = px.bar(
            df,
            x=df.dtadd,
            y=df.meterno,
            title="Daily Overall Inspections.",
            text_auto=True,
            text=df.meterno,
            labels={"meterno": "Meter Count", "dtadd": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    context = {
        "target_achievement": target_achievement(),
        "daily_trend_plot": daily_trend(),
    }
    return render(request, "postpaid/genstns/genstns_dashboard.html", context)


@login_required(login_url="login")
def view_genstn_inspeted(request, pk):
    meter = Generation_stations_inspection.objects.get(id=pk)

    context = {
        "meter": meter,
    }
    return render(request, "postpaid/genstns/view_detail_inspection.html", context)


@login_required(login_url="login")
def genstn_viewinspected(request):
    if request.user.is_authenticated:
        campaign = request.user.userprofile.campaign
    if campaign == 'genstns':
        meters = Generation_stations_inspection.objects.all().order_by("-dtadd")
        paginator = Paginator(meters, 20)
        page = request.GET.get("page")
        paged_uploads = paginator.get_page(page)
    # meters_count = meters.count()
    else:
        messages.error(request, "Access denied.")
        return redirect("main:my-dashboard")

    context = {
        "meters": paged_uploads,
        # "meters_count": meters_count,
        "nbar": "alluploads",
    }
    return render(request, "postpaid/genstns/view_genstns.html", context)


@login_required(login_url="login")
def my_genstns(request):
    if request.user.is_authenticated:
        user = request.user.userprofile
    today = date.today()
    meters = Generation_stations_inspection.objects.filter(
        inspector=user, dtadd__date=today
    ).order_by("-dtadd")

    paginator = Paginator(meters, 30)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()

    context = {
        "meters": paged_uploads,
        "meters_count": meters_count,
        "nbar": "myuploads",
    }
    return render(request, "postpaid/genstns/my_genstns.html", context)


@login_required(login_url="login")
def inspect_genstn(request, pk):
    img = get_object_or_404(Generation_stations, id=pk)
    campaign = request.user.userprofile.campaign

    if campaign == "genstns":
        if request.method == "POST":
            m_form = GenerationStationsForm(request.POST, request.FILES, instance=img)

            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                resolution = Generation_stations_inspection()
                resolution.meterno = m_form.cleaned_data["meterno"]
                resolution.generation_type = m_form.cleaned_data["generation_type"]
                resolution.genstn = img
                resolution.x = m_form.cleaned_data["x"]
                resolution.y = m_form.cleaned_data["y"]
                resolution.inspector = request.user.userprofile
                resolution.md_reset_b4 = m_form.cleaned_data["md_reset_b4"]
                resolution.md_reset_after = m_form.cleaned_data["md_reset_after"]
                resolution.meterbox_terminal_seal_b4 = m_form.cleaned_data[
                    "meterbox_terminal_seal_b4"
                ]
                resolution.meterbox_terminal_seal_after = m_form.cleaned_data[
                    "meterbox_terminal_seal_after"
                ]
                resolution.testblock_seal_b4 = m_form.cleaned_data["testblock_seal_b4"]
                resolution.testblock_seal_after = m_form.cleaned_data[
                    "testblock_seal_after"
                ]
                resolution.meterbody_seal_b4 = m_form.cleaned_data["meterbody_seal_b4"]
                resolution.meterbody_seal_after = m_form.cleaned_data[
                    "meterbody_seal_after"
                ]
                resolution.noofequipments = m_form.cleaned_data["noofequipments"]
                resolution.testequipment = m_form.cleaned_data["testequipment"]
                resolution.equipment_srn = m_form.cleaned_data["equipment_srn"]
                resolution.testequipment1 = m_form.cleaned_data["testequipment1"]
                resolution.equipment_srn1 = m_form.cleaned_data["equipment_srn1"]
                resolution.testequipment2 = m_form.cleaned_data["testequipment2"]
                resolution.equipment_srn2 = m_form.cleaned_data["equipment_srn2"]
                resolution.testequipment3 = m_form.cleaned_data["testequipment3"]
                resolution.equipment_srn3 = m_form.cleaned_data["equipment_srn3"]
                resolution.portable_energy_std = m_form.cleaned_data[
                    "portable_energy_std"
                ]
                resolution.portable_srn = m_form.cleaned_data["portable_srn"]
                resolution.accuracy_class = m_form.cleaned_data["accuracy_class"]
                resolution.relative_humid_start = m_form.cleaned_data[
                    "relative_humid_start"
                ]
                resolution.relative_humid_end = m_form.cleaned_data[
                    "relative_humid_end"
                ]
                resolution.relative_humid_avg = m_form.cleaned_data[
                    "relative_humid_avg"
                ]
                resolution.temp_start = m_form.cleaned_data["temp_start"]
                resolution.temp_end = m_form.cleaned_data["temp_end"]
                resolution.temp_avg = m_form.cleaned_data["temp_avg"]
                resolution.per_error_trial1 = m_form.cleaned_data["per_error_trial1"]
                resolution.per_error_trial2 = m_form.cleaned_data["per_error_trial2"]
                resolution.per_error_trial3 = m_form.cleaned_data["per_error_trial3"]
                resolution.avg_per_error = m_form.cleaned_data["avg_per_error"]
                resolution.results_remarks = m_form.cleaned_data["results_remarks"]
                resolution.register_trail1 = m_form.cleaned_data["register_trail1"]
                resolution.register_trail2 = m_form.cleaned_data["register_trail2"]
                resolution.register_avg_per_error = m_form.cleaned_data[
                    "register_avg_per_error"
                ]
                resolution.register_remarks = m_form.cleaned_data["register_remarks"]
                resolution.ct_r_serialno = m_form.cleaned_data["ct_r_serialno"]
                resolution.ct_r_manufacturer = m_form.cleaned_data["ct_r_manufacturer"]
                resolution.ct_r_ratedvoltage = m_form.cleaned_data["ct_r_ratedvoltage"]
                resolution.ct_r_nameplate_ratio = m_form.cleaned_data[
                    "ct_r_nameplate_ratio"
                ]
                resolution.ct_r_testvoltage = m_form.cleaned_data["ct_r_testvoltage"]
                resolution.ct_r_turnsratio = m_form.cleaned_data["ct_r_turnsratio"]
                resolution.ct_r_per_ratiodeviation = m_form.cleaned_data[
                    "ct_r_per_ratiodeviation"
                ]
                resolution.ct_r_remarks = m_form.cleaned_data["ct_r_remarks"]
                resolution.ct_y_serialno = m_form.cleaned_data["ct_y_serialno"]
                resolution.ct_y_manufacturer = m_form.cleaned_data["ct_y_manufacturer"]
                resolution.ct_y_ratedvoltage = m_form.cleaned_data["ct_y_ratedvoltage"]
                resolution.ct_y_nameplate_ratio = m_form.cleaned_data[
                    "ct_y_nameplate_ratio"
                ]
                resolution.ct_y_testvoltage = m_form.cleaned_data["ct_y_testvoltage"]
                resolution.ct_y_turnsratio = m_form.cleaned_data["ct_y_turnsratio"]
                resolution.ct_y_per_ratiodeviation = m_form.cleaned_data[
                    "ct_y_per_ratiodeviation"
                ]
                resolution.ct_y_remarks = m_form.cleaned_data["ct_y_remarks"]
                resolution.ct_b_serialno = m_form.cleaned_data["ct_b_serialno"]
                resolution.ct_b_manufacturer = m_form.cleaned_data["ct_b_manufacturer"]
                resolution.ct_b_ratedvoltage = m_form.cleaned_data["ct_b_ratedvoltage"]
                resolution.ct_b_nameplate_ratio = m_form.cleaned_data[
                    "ct_b_nameplate_ratio"
                ]
                resolution.ct_b_testvoltage = m_form.cleaned_data["ct_b_testvoltage"]
                resolution.ct_b_turnsratio = m_form.cleaned_data["ct_b_turnsratio"]
                resolution.ct_b_per_ratiodeviation = m_form.cleaned_data[
                    "ct_b_per_ratiodeviation"
                ]
                resolution.ct_b_remarks = m_form.cleaned_data["ct_b_remarks"]
                resolution.vt_r_serialno = m_form.cleaned_data["vt_r_serialno"]
                resolution.vt_r_manufacturer = m_form.cleaned_data["vt_r_manufacturer"]
                resolution.vt_r_ratedvoltage = m_form.cleaned_data["vt_r_ratedvoltage"]
                resolution.vt_r_nameplate_ratio = m_form.cleaned_data[
                    "vt_r_nameplate_ratio"
                ]
                resolution.vt_r_testvoltage = m_form.cleaned_data["vt_r_testvoltage"]
                resolution.vt_r_turnsratio = m_form.cleaned_data["vt_r_turnsratio"]
                resolution.vt_r_per_ratiodeviation = m_form.cleaned_data[
                    "vt_r_per_ratiodeviation"
                ]
                resolution.vt_r_remarks = m_form.cleaned_data["vt_r_remarks"]
                resolution.vt_y_serialno = m_form.cleaned_data["vt_y_serialno"]
                resolution.vt_y_manufacturer = m_form.cleaned_data["vt_y_manufacturer"]
                resolution.vt_y_ratedvoltage = m_form.cleaned_data["vt_y_ratedvoltage"]
                resolution.vt_y_nameplate_ratio = m_form.cleaned_data[
                    "vt_y_nameplate_ratio"
                ]
                resolution.vt_y_testvoltage = m_form.cleaned_data["vt_y_testvoltage"]
                resolution.vt_y_turnsratio = m_form.cleaned_data["vt_y_turnsratio"]
                resolution.vt_y_per_ratiodeviation = m_form.cleaned_data[
                    "vt_y_per_ratiodeviation"
                ]
                resolution.vt_y_remarks = m_form.cleaned_data["vt_y_remarks"]
                resolution.vt_b_serialno = m_form.cleaned_data["vt_b_serialno"]
                resolution.vt_b_manufacturer = m_form.cleaned_data["vt_b_manufacturer"]
                resolution.vt_b_ratedvoltage = m_form.cleaned_data["vt_b_ratedvoltage"]
                resolution.vt_b_nameplate_ratio = m_form.cleaned_data[
                    "vt_b_nameplate_ratio"
                ]
                resolution.vt_b_testvoltage = m_form.cleaned_data["vt_b_testvoltage"]
                resolution.vt_b_turnsratio = m_form.cleaned_data["vt_b_turnsratio"]
                resolution.vt_b_per_ratiodeviation = m_form.cleaned_data[
                    "vt_b_per_ratiodeviation"
                ]
                resolution.vt_b_remarks = m_form.cleaned_data["vt_b_remarks"]
                resolution.reading_180 = m_form.cleaned_data["reading_180"]
                resolution.reading_280 = m_form.cleaned_data["reading_280"]
                resolution.img_180 = m_form.cleaned_data["img_180"]
                resolution.img_280 = m_form.cleaned_data["img_280"]
                resolution.cert = m_form.cleaned_data["cert"]
                resolution.team = m_form.cleaned_data["team"]
                resolution.overall_remarks = m_form.cleaned_data["overall_remarks"]
                resolution.confirmation = m_form.cleaned_data["confirmation"]
                resolution.manufacturer = m_form.cleaned_data["manufacturer"]
                resolution.yr_manufacturer = m_form.cleaned_data["yr_manufacturer"]
                resolution.meter_accuracy_class = m_form.cleaned_data["meter_accuracy_class"]
                resolution.vt_chamber_r_initail = m_form.cleaned_data["vt_chamber_r_initail"]
                resolution.vt_chamber_r_final = m_form.cleaned_data["vt_chamber_r_final"]
                resolution.vt_chamber_y_initail = m_form.cleaned_data["vt_chamber_y_initail"]
                resolution.vt_chamber_y_final = m_form.cleaned_data["vt_chamber_y_final"]
                resolution.vt_chamber_b_initail = m_form.cleaned_data["vt_chamber_b_initail"]
                resolution.vt_chamber_b_final = m_form.cleaned_data["vt_chamber_b_final"]
                resolution.ct_chamber_r_initail = m_form.cleaned_data["ct_chamber_r_initail"]
                resolution.ct_chamber_r_final = m_form.cleaned_data["ct_chamber_r_final"]
                resolution.ct_chamber_y_initail = m_form.cleaned_data["ct_chamber_y_initail"]
                resolution.ct_chamber_y_final = m_form.cleaned_data["ct_chamber_y_final"]
                resolution.ct_chamber_b_initail = m_form.cleaned_data["ct_chamber_b_initail"]
                resolution.ct_chamber_b_final = m_form.cleaned_data["ct_chamber_b_final"]
                resolution.ct_yom_red = m_form.cleaned_data["ct_yom_red"]
                resolution.vt_yom_red = m_form.cleaned_data["vt_yom_red"]
                resolution.ct_yom_yellow = m_form.cleaned_data["ct_yom_yellow"]
                resolution.vt_yom_yellow = m_form.cleaned_data["vt_yom_yellow"]
                resolution.ct_yom_blue = m_form.cleaned_data["ct_yom_blue"]
                resolution.vt_yom_blue = m_form.cleaned_data["vt_yom_blue"]
                resolution.ct_noofcores_red = m_form.cleaned_data["ct_noofcores_red"]
                resolution.vt_noofcores_red = m_form.cleaned_data["vt_noofcores_red"]
                resolution.ct_noofcores_yellow = m_form.cleaned_data["ct_noofcores_yellow"]
                resolution.vt_noofcores_yellow = m_form.cleaned_data["vt_noofcores_yellow"]
                resolution.ct_noofcores_blue = m_form.cleaned_data["ct_noofcores_blue"]
                resolution.vt_noofcores_blue = m_form.cleaned_data["vt_noofcores_blue"]
                resolution.ct_connected_red = m_form.cleaned_data["ct_connected_red"]
                resolution.vt_connected_red = m_form.cleaned_data["vt_connected_red"]
                resolution.ct_connected_yellow = m_form.cleaned_data["ct_connected_yellow"]
                resolution.vt_connected_yellow = m_form.cleaned_data["vt_connected_yellow"]
                resolution.ct_connected_blue = m_form.cleaned_data["ct_connected_blue"]
                resolution.vt_connected_blue = m_form.cleaned_data["vt_connected_blue"]
                resolution.ct_accuracyclass_red = m_form.cleaned_data["ct_accuracyclass_red"]
                resolution.vt_accuracyclass_red = m_form.cleaned_data["vt_accuracyclass_red"]
                resolution.ct_accuracyclass_yellow = m_form.cleaned_data["ct_accuracyclass_yellow"]
                resolution.vt_accuracyclass_yellow = m_form.cleaned_data["vt_accuracyclass_yellow"]
                resolution.ct_accuracyclass_blue = m_form.cleaned_data["ct_accuracyclass_blue"]
                resolution.vt_accuracyclass_blue = m_form.cleaned_data["vt_accuracyclass_blue"]

                resolution.save()
                zerov.status = True
                zerov.save()
                messages.success(
                    request, "Your Inspection Has been successfully saved."
                )
                return redirect("postpaid:my-genstns")
            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)
                # m_form = LpForm(instance=img)

        else:
            m_form = GenerationStationsForm(instance=img)
        context = {
            "form": m_form,
            "target": img,
            # 'users' : region_users,
        }
    else:
        messages.error(request, "Access Denied.")
        return redirect("main:my-dashboard")

    return render(request, "postpaid/genstns/inspect_genstn.html", context)


@login_required(login_url="login")
def dc_search_plantname(request):
    if request.user.is_authenticated:
        meters_list = Generation_stations.objects.filter(
            status=False
        )
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(plant_name__icontains=keyword)
    context = {
        "meters": paged_uploads,
    }
    return render(request, "postpaid/genstns/generation_stations.html", context)


@login_required(login_url="login")
def generation_stations(request):
    if request.user.is_authenticated:
        campaign = request.user.userprofile.campaign
    if campaign == 'genstns':
        stations = Generation_stations.objects.filter(
            status=False
        )
        paginator = Paginator(stations, 30)
        page = request.GET.get("page")
        paged_uploads = paginator.get_page(page)
    else:
        messages.error(request, "Access denied.")
        return redirect("main:my-dashboard")

    context = {"meters": paged_uploads}
    return render(request, "postpaid/genstns/generation_stations.html", context)


# Domestic Not In target
@login_required(login_url="login")
def dc_not_in_target(request):
    # userprofile = get_object_or_404(UserProfile, user=request.user)

    campaign = request.user.userprofile.campaign

    if campaign == "lpx":
        if request.method == "POST":
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = Dc_customersNotInTargetForm(request.POST, request.FILES)

            check = Dc_inspection.objects.filter(dc_meterno=request.POST["dc_meterno"])
            if check:
                messages.error(request, "That Meter has already been inspected.")
                return redirect("postpaid:domestic-customers")

            if m_form.is_valid():
                # if m_form.cleaned_data['meterno'] is None:
                # messages.success(request, 'You need to take the Cordinates.')
                # return redirect('postpaid:mythreephase-list')
                #
                resolution = Dc_inspection()
                resolution.dc_meterno = m_form.cleaned_data["dc_meterno"]
                resolution.dc_accountno = m_form.cleaned_data["dc_meterno"]
                resolution.dc_meteringstatus = m_form.cleaned_data["dc_meteringstatus"]
                resolution.dc_installationstatus = m_form.cleaned_data[
                    "dc_installationstatus"
                ]
                resolution.dc_faultystatus = m_form.cleaned_data["dc_faultystatus"]
                resolution.dc_tamperedstatus = m_form.cleaned_data["dc_tamperedstatus"]
                resolution.dc_bypassstatus = m_form.cleaned_data["dc_bypassstatus"]
                resolution.dc_notokaystatus = m_form.cleaned_data["dc_notokaystatus"]
                resolution.dc_meterimg = m_form.cleaned_data["dc_meterimg"]
                resolution.dc_reading = m_form.cleaned_data["dc_reading"]
                resolution.dc_metertype = m_form.cleaned_data["dc_metertype"]
                resolution.dc_conf_type = m_form.cleaned_data["dc_conf_type"]
                resolution.dc_comment = m_form.cleaned_data["dc_comment"]
                resolution.dc_sealno = m_form.cleaned_data["dc_sealno"]
                resolution.dc_inspector = request.user.userprofile
                resolution.dc_county = request.user.userprofile.county
                resolution.dc_region = request.user.userprofile.region
                resolution.x = m_form.cleaned_data["x"]
                resolution.y = m_form.cleaned_data["y"]

                with transaction.atomic():
                    new_target = Domestic_customers.objects.create(
                        id=time.time(),
                        dc_meterno=resolution.dc_meterno,
                        dc_accountno=resolution.dc_meterno,
                        county=resolution.dc_county,
                        region=resolution.dc_region,
                        status=True,
                        avg_units=0,
                    )
                    new_target.save()

                    resolution.dc = new_target

                    resolution.save()

                messages.success(
                    request, "Your Inspection Has been successfully saved."
                )
                return redirect("postpaid:my-dc")
            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = Dc_customersNotInTargetForm()
        context = {
            "form": m_form,
        }
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

    return render(request, "postpaid/dc/dc_notin_target.html", context)


@login_required(login_url="login")
def publiclighting_anomolous_unbilled(request):
    meters = (
        Public_lighting_inspection.objects.select_related("target", "county")
        .annotate(
            reading_c=Cast("reading", output_field=IntegerField()),
        )
        .filter(reading_c__gte=F("system_reading"))
        # .exclude(dc_meteringstatus="okay")
        .annotate(
            diff=F("reading_c") - F("system_reading"),
        )
        .filter(nextlevel=False, incms=True)
        .order_by("-dtadd")
    )

    # meters_pending = meters.filter(incms_nextlevel=False)
    paginator = Paginator(meters, 30)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    def pending():
        df = read_frame(meters)
        df = df.groupby(by="county", as_index=False, sort=False)[
            "meterno"
        ].count()
        df = px.bar(
            df,
            x=df.county,
            y=df.meterno,
            title="Pending Billing Accounts",
            text_auto=True,
            text=df.meterno,
            labels={"county": "County", "meterno": "Accounts Count"},
        )
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    context = {
        "name": "Pending Billing Accounts",
        "meters": paged_uploads,
        "meters_count": meters.count(),
        "nbar": "myuploads",
        "df": pending(),
    }
    return render(request, "postpaid/publiclighting/publiclighting_anomalous_dashboard.html", context)


@login_required(login_url="login")
def publiclighting_anomolous_dashboard(request):
    meters = (
        Public_lighting_inspection.objects.select_related("target", "county")
        .exclude(meteringstatus="okay")
        .filter(nextlevel=False)
        .order_by("-dtadd")
    )

    # meters_pending = meters.filter(incms_nextlevel=False)
    paginator = Paginator(meters, 30)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    def pending():
        df = read_frame(meters)
        df = df.groupby(by="county", as_index=False, sort=False)[
            "meterno"
        ].count()
        df = px.bar(
            df,
            x=df.county,
            y=df.meterno,
            title="Pending Faulty Accounts",
            text_auto=True,
            text=df.meterno,
            labels={"county": "County", "meterno": "Accounts Count"},
        )
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    context = {
        "name": "Pending Faulty Accounts",
        "meters": paged_uploads,
        "meters_count": meters.count(),
        "nbar": "myuploads",
        "df": pending(),
    }

    return render(request, "postpaid/publiclighting/publiclighting_anomalous_dashboard.html", context)


@login_required(login_url="login")
def highend_anomolous_unbilled_export(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    meters = (
        Threephase_inspection.objects.select_related("threepase", "county")
        .annotate(
            reading_c=Cast("reading", output_field=IntegerField()),
        )
        .filter(reading_c__gte=F("system_reading"))
        # .exclude(dc_meteringstatus="okay")
        .annotate(
            diff=F("reading_c") - F("system_reading"),
        )
        .filter(
            incms_nextlevel=False,
            anomaly_status=True,
            dtadd__gt=datetime.datetime.today() - datetime.timedelta(days=14),
        )
        .order_by("-dtadd")
    )

    writer.writerow(
        [
            "COUNTY",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "METERING STATUS",
            "INSTALLATION STATUS",
            "FAULTY",
            "TAMPERED",
            "BYPASSED",
            "NOTOKAY STATUS",
            "READING",
            "INSPECTOR",
            "DATE INSPECTED",
            "COMMENT",
        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.county,
                meter.meterno,
                meter.accountno,
                meter.meteringstatus,
                meter.installationstatus,
                meter.faultystatus,
                meter.tamperedstatus,
                meter.bypassstatus,
                meter.notokaystatus,
                meter.reading,
                meter.inspector,
                meter.dtadd,
                meter.comment,
            ]
        )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="HIGHEND_CUSTOMERS_UNBILLED.csv" '
    return response


@login_required(login_url="login")
def highend_anomolous_faulty_export(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    meters = (
        Threephase_inspection.objects.select_related("threepase", "county")
        .exclude(meteringstatus="okay")
        .filter(
            incms_nextlevel=False,
            dtadd__gt=datetime.datetime.today() - datetime.timedelta(days=14),
        )
        .order_by("-dtadd")
    )

    writer.writerow(
        [
            "REGION",
            "COUNTY",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "METERING STATUS",
            "INSTALLATION STATUS",
            "FAULTY",
            "TAMPERED",
            "BYPASSED",
            "NOTOKAY STATUS",
            "READING",
            "INSPECTOR",
            "DATE INSPECTED",
            "COMMENT",
        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.region,
                meter.county,
                meter.meterno,
                meter.accountno,
                meter.meteringstatus,
                meter.installationstatus,
                meter.faultystatus,
                meter.tamperedstatus,
                meter.bypassstatus,
                meter.notokaystatus,
                meter.reading,
                meter.inspector,
                meter.dtadd,
                meter.comment,
            ]
        )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="HIGHEND_CUSTOMERS_FAULTY.csv" '
    return response


@login_required(login_url="login")
def highend_anomolous_unbilled(request):
    meters = (
        Threephase_inspection.objects.select_related("threepase", "county")
        .annotate(
            reading_c=Cast("reading", output_field=IntegerField()),
        )
        .filter(reading_c__gte=F("system_reading"))
        # .exclude(dc_meteringstatus="okay")
        .annotate(
            diff=F("reading_c") - F("system_reading"),
        )
        .filter(incms_nextlevel=False, anomaly_status=True)
        .order_by("-dtadd")
    )

    # meters_pending = meters.filter(incms_nextlevel=False)
    paginator = Paginator(meters, 30)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    def pending():
        df = read_frame(meters)
        df = df.groupby(by="county", as_index=False, sort=False)["meterno"].count()
        df = px.bar(
            df,
            x=df.county,
            y=df.meterno,
            title="Pending Billing Accounts",
            text_auto=True,
            text=df.meterno,
            labels={"county": "County", "meterno": "Accounts Count"},
        )
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    context = {
        "name": "Pending Billing Accounts",
        "meters": paged_uploads,
        "meters_count": meters.count(),
        "nbar": "myuploads",
        "df": pending(),
    }
    return render(request, "postpaid/highend/highend_anomalous_dashboard.html", context)


@login_required(login_url="login")
def highend_anomolous_dashboard(request):
    meters = (
        Threephase_inspection.objects.select_related("threepase", "county")
        .exclude(meteringstatus="okay")
        .filter(incms_nextlevel=False)
        .order_by("-dtadd")
    )

    # meters_pending = meters.filter(incms_nextlevel=False)
    paginator = Paginator(meters, 30)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    def pending():
        df = read_frame(meters)
        df = df.groupby(by="county", as_index=False, sort=False)["meterno"].count()
        df = px.bar(
            df,
            x=df.county,
            y=df.meterno,
            title="Pending Faulty Accounts",
            text_auto=True,
            text=df.meterno,
            labels={"county": "County", "meterno": "Accounts Count"},
        )
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    context = {
        "name": "Pending Faulty Accounts",
        "meters": paged_uploads,
        "meters_count": meters.count(),
        "nbar": "myuploads",
        "df": pending(),
    }

    return render(request, "postpaid/highend/highend_anomalous_dashboard.html", context)


@login_required(login_url="login")
def dc_anomolous_faulty_export(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    meters = (
        Dc_inspection.objects.select_related("dc", "dc_county")
        .exclude(dc_meteringstatus="okay")
        .filter(
            incms_nextlevel=False,
            dtadd__gt=datetime.datetime.today() - datetime.timedelta(days=30),
        )
        .order_by("-dtadd")
    )

    writer.writerow(
        [
            "REGION",
            "COUNTY",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "METERING STATUS",
            "INSTALLATION STATUS",
            "FAULTY",
            "TAMPERED",
            "BYPASSED",
            "NOTOKAY STATUS",
            "READING",
            "INSPECTOR",
            "DATE INSPECTED",
            "COMMENT",
        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.dc_region,
                meter.dc_county,
                meter.dc_meterno,
                meter.dc_accountno,
                meter.dc_meteringstatus,
                meter.dc_installationstatus,
                meter.dc_faultystatus,
                meter.dc_tamperedstatus,
                meter.dc_bypassstatus,
                meter.dc_notokaystatus,
                meter.dc_reading,
                meter.dc_inspector,
                meter.dtadd,
                meter.dc_comment,
            ]
        )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="DOMESTIC_CUSTOMERS_FAULTY.csv" '
    return response


@login_required(login_url="login")
def dc_anomolous_unbilled_export(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    meters = (
        Dc_inspection.objects.select_related("dc", "dc_county")
        .annotate(
            dc_reading_c=Cast("dc_reading", output_field=IntegerField()),
        )
        .filter(dc_reading_c__gte=F("system_reading"))
        # .exclude(dc_meteringstatus="okay")
        .annotate(
            diff=F("dc_reading_c") - F("system_reading"),
        )
        .filter(
            incms_nextlevel=False,
            anomaly_status=True,
            dtadd__gt=datetime.datetime.today() - datetime.timedelta(days=14),
        )
        .order_by("-dtadd")
    )

    writer.writerow(
        [
            "REGION",
            "COUNTY",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "METERING STATUS",
            "INSTALLATION STATUS",
            "FAULTY",
            "TAMPERED",
            "BYPASSED",
            "NOTOKAY STATUS",
            "READING",
            "INSPECTOR",
            "DATE INSPECTED",
            "COMMENT",
        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.dc_region,
                meter.dc_county,
                meter.dc_meterno,
                meter.dc_accountno,
                meter.dc_meteringstatus,
                meter.dc_installationstatus,
                meter.dc_faultystatus,
                meter.dc_tamperedstatus,
                meter.dc_bypassstatus,
                meter.dc_notokaystatus,
                meter.dc_reading,
                meter.dc_inspector,
                meter.dtadd,
                meter.dc_comment,
            ]
        )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="DOMESTIC_CUSTOMERS_UNBILLED.csv" '
    return response


@login_required(login_url="login")
def dc_anomolous_dashboard(request):
    meters = (
        Dc_inspection.objects.select_related("dc", "dc_county")
        .exclude(dc_meteringstatus="okay")
        .filter(incms_nextlevel=False)
        .order_by("-dtadd")
    )

    # meters_pending = meters.filter(incms_nextlevel=False)
    paginator = Paginator(meters, 30)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    def pending():
        df = read_frame(meters)
        df = df.groupby(by="dc_county", as_index=False, sort=False)[
            "dc_meterno"
        ].count()
        df = px.bar(
            df,
            x=df.dc_county,
            y=df.dc_meterno,
            title="Pending Faulty Accounts",
            text_auto=True,
            text=df.dc_meterno,
            labels={"dc_county": "County", "dc_meterno": "Accounts Count"},
        )
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    context = {
        "name": "Pending Faulty Accounts",
        "meters": paged_uploads,
        "meters_count": meters.count(),
        "nbar": "myuploads",
        "df": pending(),
    }

    return render(request, "postpaid/dc/dc_anomalous_dashboard.html", context)


@login_required(login_url="login")
def dc_anomolous_unbilled(request):
    meters = (
        Dc_inspection.objects.select_related("dc", "dc_county")
        .annotate(
            dc_reading_c=Cast("dc_reading", output_field=IntegerField()),
        )
        .filter(dc_reading_c__gte=F("system_reading"))
        # .exclude(dc_meteringstatus="okay")
        .annotate(
            diff=F("dc_reading_c") - F("system_reading"),
        )
        .filter(incms_nextlevel=False, anomaly_status=True)
        .order_by("-dtadd")
    )

    # meters_pending = meters.filter(incms_nextlevel=False)
    paginator = Paginator(meters, 30)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    def pending():
        df = read_frame(meters)
        df = df.groupby(by="dc_county", as_index=False, sort=False)[
            "dc_meterno"
        ].count()
        df = px.bar(
            df,
            x=df.dc_county,
            y=df.dc_meterno,
            title="Pending Billing Accounts",
            text_auto=True,
            text=df.dc_meterno,
            labels={"dc_county": "County", "dc_meterno": "Accounts Count"},
        )
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    context = {
        "name": "Pending Billing Accounts",
        "meters": paged_uploads,
        "meters_count": meters.count(),
        "nbar": "myuploads",
        "df": pending(),
    }
    return render(request, "postpaid/dc/dc_anomalous_dashboard.html", context)


@login_required(login_url="login")
def dc_export_uploads(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    meters = Dc_inspection.objects.filter(
        dtadd__gt=datetime.datetime.today() - datetime.timedelta(days=14)
    ).order_by("-dtadd")

    writer.writerow(
        [
            "REGION",
            "COUNTY",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "METERING STATUS",
            "INSTALLATION STATUS",
            "FAULTY",
            "TAMPERED",
            "BYPASSED",
            "NOTOKAY STATUS",
            "READING",
            "INSPECTOR",
            "DATE INSPECTED",
            "COMMENT",
        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.dc_region,
                meter.dc_county,
                meter.dc_meterno,
                meter.dc_accountno,
                meter.dc_meteringstatus,
                meter.dc_installationstatus,
                meter.dc_faultystatus,
                meter.dc_tamperedstatus,
                meter.dc_bypassstatus,
                meter.dc_notokaystatus,
                meter.dc_reading,
                meter.dc_inspector,
                meter.dtadd,
                meter.dc_comment,
            ]
        )

    response["Content-Disposition"] = 'attachment; filename="DOMESTIC_CUSTOMERS.csv" '
    return response


@login_required(login_url="login")
def dc_useranalytics(request):
    if request.user.is_authenticated:
        user = request.user
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)

    inspectors = (
        UserProfile.objects.filter(campaign="dc")
        .values("user_id__stid", "user_id__name", "user_id__mobile", "county__name")
        .annotate(
            the_count=Count("dc_inspector"),
            today=Count("dc_inspector", filter=Q(dc_inspector__dtadd__date=today)),
            yesturday=Count("dc_inspector", filter=Q(dc_inspector__dtadd__date=yesterday)),
            yesturday_1=Count("dc_inspector", filter=Q(dc_inspector__dtadd__date=yesterday_1)),
            yesturday_2=Count("dc_inspector", filter=Q(dc_inspector__dtadd__date=yesterday_2)),
        )
        .order_by("county__name")
    )

    # inspectors = Threephase_inspection.objects.all().select_related('inspector').values('inspector__user_id__stid','inspector__user_id__name','inspector__county__name','inspector__user_id__mobile').annotate(
    #      the_count=Count('id'),
    #      today=Count('id',filter=Q(dtadd__date=today)),
    #      yesturday=Count('id',filter=Q(dtadd__date=yesterday)),
    #      yesturday_1=Count('id',filter=Q(dtadd__date=yesterday_1)),
    #      yesturday_2=Count('id',filter=Q(dtadd__date=yesterday_2)),
    #      #yesturday_2_d=Count('id',filter=Q(dtadd__date=yesterday_2)),
    #      #yesturday_3_d=Count('id',filter=Q(dtadd__date=yesterday_3)),
    #     ).order_by('inspector__county__name')

    context = {
        "analytics": inspectors,
        "nbar": "analytics",
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        # 'county' : county
    }
    return render(request, "postpaid/dc_user_analytics.html", context)


# Domestic DAshboard
@login_required(login_url="login")
def dc_dashboard(request):
    # oveall_target = County.objects.aggregate(Sum("publiclighting_target"))

    oveall_inspected = Dc_inspection.objects.values(
        "dc_meteringstatus", "dc_meterno", "dtadd"
    )
    overall_not_okay = oveall_inspected.exclude(dc_meteringstatus='okay')

    def count_business_days(start_date, end_date):
        # Define a list of weekend days (Saturday and Sunday)
        weekend_days = [5, 6]  # Monday is 0 and Sunday is 6
        # Initialize a counter for business days
        business_days = 0
        target = 0
        # Iterate through each day in the date range
        current_date = start_date
        while current_date <= end_date:
            # Check if the current day is a weekend day
            if current_date.weekday() not in weekend_days:
                business_days += 1
                target += 10230
            # Move to the next day
            current_date += datetime.timedelta(days=1)
        return business_days, target

    # Test the function
    start_date = datetime.date(2023, 9, 11)
    end_date = datetime.date.today()

    result = count_business_days(start_date, end_date)

    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    def metering_status_notokay():
        df = read_frame(overall_not_okay)
        df = df.groupby(by="dc_meteringstatus", as_index=False, sort=False)[
            "dc_meterno"
        ].count()
        values = df.dc_meteringstatus
        names = df.dc_meterno
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Metering Status Not Okay",
            labels={
                "dc_meterno": "Meter Count",
                "dc_meteringstatus": "Metering Status",
            },
        )
        df.update_traces(textposition='inside', textinfo='percent+label')
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    def metering_status():
        df = read_frame(oveall_inspected)
        df = df.groupby(by="dc_meteringstatus", as_index=False, sort=False)[
            "dc_meterno"
        ].count()
        values = df.dc_meteringstatus
        names = df.dc_meterno
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Inspection Metering Status",
            labels={
                "dc_meterno": "Meter Count",
                "dc_meteringstatus": "Metering Status",
            },
        )
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    def target_achievement():
        t_a = oveall_inspected.count()
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Planned ToDate",
                    x=["Planned ToDate"],
                    y=[result[1]],
                ),
                go.Bar(name="Achieved ToDate", x=["Achieved ToDate"], y=[t_a]),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Target vs Achievement",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="No Of Inspections",
                titlefont_size=16,
                tickfont_size=14,
            ),
            xaxis=dict(
                title="Year(2023/24)",
            ),
            legend=dict(
                bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
            ),
            barmode="group",
            bargap=0.15,  # gap between bars of adjacent location coordinates.
            bargroupgap=0.1,  # gap between bars of the same location coordinate.
        )
        fig_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return fig_plot

    def daily_trend():
        df = read_frame(oveall_inspected)
        df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
        df = df.groupby(by="dtadd", as_index=False, sort=False)["dc_meterno"].count()
        df = px.bar(
            df,
            x=df.dtadd,
            y=df.dc_meterno,
            title=f"Daily Overall Inspections.Daily Target = {10, 230}",
            text_auto=True,
            text=df.dc_meterno,
            labels={"dc_meterno": "Meter Count", "dtadd": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    region_analytics = (
        Region.objects.select_related("dc_region")
        .values("name")  # select_related('dc_region')
        .annotate(
            dc_target_acs=(Sum("dc_target", distinct=True)),
            dc_daily_target=(Sum("dc_daily_target", distinct=True)),
            dc_inspected=(Count("dc_region_rtn", distinct=True)),
            dc_insp_faulty=(
                Count(
                    "dc_region_rtn",
                    distinct=True,
                    filter=Q(dc_region_rtn__dc_meteringstatus="faulty"),
                )
            ),
            dc_insp_tampered=(
                Count(
                    "dc_region_rtn",
                    distinct=True,
                    filter=Q(dc_region_rtn__dc_meteringstatus="tampered"),
                )
            ),
            dc_insp_bypassed=(
                Count(
                    "dc_region_rtn",
                    distinct=True,
                    filter=Q(dc_region_rtn__dc_meteringstatus="bypassed"),
                )
            ),
            dc_insp_nometer=(
                Count(
                    "dc_region_rtn",
                    distinct=True,
                    filter=Q(dc_region_rtn__dc_meteringstatus="nometer"),
                )
            ),
            today=Count(
                "dc_region_rtn",
                distinct=True,
                filter=Q(dc_region_rtn__dtadd__date=today),
            ),
            today_1=Count(
                "dc_region_rtn",
                distinct=True,
                filter=Q(dc_region_rtn__dtadd__date=yesterday),
            ),
            today_2=Count(
                "dc_region_rtn",
                distinct=True,
                filter=Q(dc_region_rtn__dtadd__date=yesterday_1),
            ),
            today_3=Count(
                "dc_region_rtn",
                distinct=True,
                filter=Q(dc_region_rtn__dtadd__date=yesterday_2),
            ),
            today_4=Count(
                "dc_region_rtn",
                distinct=True,
                filter=Q(dc_region_rtn__dtadd__date=yesterday_3),
            ),
        )
        .order_by("name")
    )
    county_analytics = (
        County.objects.select_related("dc_county")
        .values("name")
        .annotate(
            dc_target_acs=(Sum("publiclighting_target", distinct=True)),
            dc_daily_target=(Sum("dc_daily_target", distinct=True)),
            dc_inspected=(Count("dc_county_rtn", distinct=True)),
            dc_insp_faulty=(
                Count(
                    "dc_county_rtn",
                    distinct=True,
                    filter=Q(dc_county_rtn__dc_meteringstatus="faulty"),
                )
            ),
            dc_insp_tampered=(
                Count(
                    "dc_county_rtn",
                    distinct=True,
                    filter=Q(dc_county_rtn__dc_meteringstatus="tampered"),
                )
            ),
            dc_insp_bypassed=(
                Count(
                    "dc_county_rtn",
                    distinct=True,
                    filter=Q(dc_county_rtn__dc_meteringstatus="bypassed"),
                )
            ),
            dc_insp_nometer=(
                Count(
                    "dc_county_rtn",
                    distinct=True,
                    filter=Q(dc_county_rtn__dc_meteringstatus="nometer"),
                )
            ),
            today=Count(
                "dc_county_rtn",
                distinct=True,
                filter=Q(dc_county_rtn__dtadd__date=today),
            ),
            today_1=Count(
                "dc_county_rtn",
                distinct=True,
                filter=Q(dc_county_rtn__dtadd__date=yesterday),
            ),
            today_2=Count(
                "dc_county_rtn",
                distinct=True,
                filter=Q(dc_county_rtn__dtadd__date=yesterday_1),
            ),
            today_3=Count(
                "dc_county_rtn",
                distinct=True,
                filter=Q(dc_county_rtn__dtadd__date=yesterday_2),
            ),
            today_4=Count(
                "dc_county_rtn",
                distinct=True,
                filter=Q(dc_county_rtn__dtadd__date=yesterday_3),
            ),
        )
        .order_by("name")
    )

    context = {
        # "oveall_target": oveall_target,
        # "per_insp": per_insp,
        # "oveall_inspected": overall_inspected_count,
        # "overall_faulty": overall_faulty,
        # "overall_tampered": overall_tampered,
        # "overall_bypassed": overall_bypassed,
        # "overall_nometer": overall_nometer,
        "daily_trend_plot": daily_trend(),
        "target_achievement": target_achievement(),
        "metering_status": metering_status(),
        "metering_status_notokay": metering_status_notokay(),
        "region_analytics": region_analytics,
        "county_analytics": county_analytics,
        "yesterday": yesterday,
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,
    }
    return render(request, "postpaid/dc/dc_dashboard.html", context)


# Domestic view dc Inspected
@login_required(login_url="login")
def view_dc_inspeted(request, pk):
    meter = Dc_inspection.objects.get(id=pk)

    context = {
        "meter": meter,
    }
    return render(request, "postpaid/view_inspected_dc.html", context)


# Domestic view search Inspected
@login_required(login_url="login")
def search_meter_dc_inspected(request):
    if request.user.is_authenticated:
        user = request.user.userprofile
    meters_list = Dc_inspection.objects.all()
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(dc_meterno__icontains=keyword)
    context = {
        "meters": paged_uploads,
    }
    return render(request, "postpaid/view_dc_inspected.html", context)


# Domestic view Inspected
@login_required(login_url="login")
def dc_viewinspected(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters = Dc_inspection.objects.all().order_by("-dtadd")
    paginator = Paginator(meters, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()

    context = {
        "meters": paged_uploads,
        "meters_count": meters_count,
        "nbar": "alluploads",
    }
    return render(request, "postpaid/view_dc_inspected.html", context)


# Domestic customers my
@login_required(login_url="login")
def my_dc(request):
    if request.user.is_authenticated:
        user = request.user.userprofile

    meters = Dc_inspection.objects.filter(dc_inspector=user).order_by("-dtadd")
    paginator = Paginator(meters, 30)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)
    paged_uploads_direct = paginator.get_page(page)
    meters_count = meters.count()

    context = {
        "meters": paged_uploads,
        "meters_count": meters_count,
        "nbar": "myuploads",
    }
    return render(request, "postpaid/my_dc.html", context)


# Domestic customers inspect
@login_required(login_url="login")
def inspect_dc(request, pk):
    img = get_object_or_404(Domestic_customers, id=pk)
    # region_users = UserProfile.objects.filter(region=userprofile.region,campaign='lp').exclude(user=request.user)

    campaign = request.user.userprofile.campaign

    if campaign == 'lpx':

        if request.method == "POST":
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = Dc_customersForm(request.POST, request.FILES, instance=img)

            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                resolution = Dc_inspection()
                resolution.dc = img
                resolution.dc_meterno = m_form.cleaned_data["dc_meterno"]
                resolution.dc_accountno = m_form.cleaned_data["dc_accountno"]
                resolution.dc_meteringstatus = m_form.cleaned_data["dc_meteringstatus"]
                resolution.dc_installationstatus = m_form.cleaned_data[
                    "dc_installationstatus"
                ]
                resolution.dc_faultystatus = m_form.cleaned_data["dc_faultystatus"]
                resolution.dc_tamperedstatus = m_form.cleaned_data["dc_tamperedstatus"]
                resolution.dc_bypassstatus = m_form.cleaned_data["dc_bypassstatus"]
                resolution.dc_notokaystatus = m_form.cleaned_data["dc_notokaystatus"]
                resolution.dc_meterimg = m_form.cleaned_data["dc_meterimg"]
                resolution.dc_reading = m_form.cleaned_data["dc_reading"]
                resolution.dc_metertype = m_form.cleaned_data["dc_metertype"]
                resolution.dc_conf_type = m_form.cleaned_data["dc_conf_type"]
                resolution.dc_comment = m_form.cleaned_data["dc_comment"]
                resolution.dc_sealno = m_form.cleaned_data["dc_sealno"]
                resolution.dc_inspector = request.user.userprofile
                resolution.dc_county = request.user.userprofile.county
                resolution.dc_region = request.user.userprofile.region
                resolution.x = m_form.cleaned_data["x"]
                resolution.y = m_form.cleaned_data["y"]
                resolution.save()
                zerov.status = True
                zerov.save()
                messages.success(
                    request, "Your Inspection Has been successfully saved."
                )
                return redirect("postpaid:my-dc")
            else:
                messages.error(
                    request, "There was an error in submitting your inspection."
                )
                print("invalid form")
                print(m_form.errors)
                # m_form = LpForm(instance=img)
        else:
            m_form = Dc_customersForm(instance=img)
        context = {
            "form": m_form,
            "target": img,
        }
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

    return render(request, "postpaid/dc_inspection.html", context)


# Domestic customers search the account by meter number
@login_required(login_url="login")
def dc_search_meter(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters_list = Domestic_customers.objects.filter(status=False)
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(dc_meterno__icontains=keyword)
    context = {
        "meters": paged_uploads,
        "county": user,
    }
    return render(request, "postpaid/dc_target_list.html", context)


# Domestic customers view target list
@login_required(login_url="login")
def domestic_customers(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters = Domestic_customers.objects.filter(status=False, county=user)[0:10]
    paginator = Paginator(meters, 10)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)
    context = {"meters": paged_uploads, "county": user, "nbar": "alluploads"}
    return render(request, "postpaid/dc_target_list.html", context)


@login_required(login_url="login")
def zerobills(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters = Zerobills.objects.all()
    meters_list = meters.filter(status='pending', county=user)
    paginator = Paginator(meters_list, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_pending = meters_list.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_pending,
        'nbar': 'alluploads'}
    return render(request, 'postpaid/zerobills.html', context)


@login_required(login_url='login')
def viewzerobill(request, pk):
    # userprofile = get_object_or_404(UserProfile, user=request.user)
    img = Zerobills.objects.get(id=pk)
    if request.method == 'POST':
        # user_form = UserForm(request.POST, instance=request.user)
        m_form = MeterForm(request.POST, request.FILES, instance=img)

        if m_form.is_valid():
            zerov = m_form.save(commit=False)
            resolution = Zerobillresolved()
            resolution.meterno = m_form.cleaned_data['meterno']
            resolution.accountno = m_form.cleaned_data['accountno']
            resolution.status = m_form.cleaned_data['status']
            resolution.meterimg = m_form.cleaned_data['meterimg']
            resolution.readings = m_form.cleaned_data['readings']
            resolution.comment = m_form.cleaned_data['comment']
            resolution.county = request.user.userprofile.county
            resolution.region = request.user.userprofile.region
            resolution.user = request.user.userprofile
            resolution.save()

            zerov.save()
            messages.success(request, 'Your Resolution Has been successfully saved.')
            return redirect('postpaid:zerobills-list')
    else:
        # user_form = UserForm(instance=request.user)
        m_form = MeterForm(instance=img)
    context = {
        'form': m_form,

    }
    return render(request, 'postpaid/viewzerobill.html', context)


@login_required(login_url="login")
def search_meter(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters_list = Zerobills.objects.filter(status='pending', county=user)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/zerobills.html', context)


@login_required(login_url="login")
def viewresults(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters = Zerobillresolved.objects.all()
    meters_list = meters.filter(status3=False)
    paginator = Paginator(meters_list, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_pending = meters_list.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_pending,
        'nbar': 'alluploads'}
    return render(request, 'postpaid/viewresults.html', context)


@login_required(login_url="login")
def viewuploaded(request, pk):
    meter = Zerobillresolved.objects.get(id=pk)
    form_asign = ResolveForm(request.POST, request.FILES, instance=meter)
    # datetime.datetime.now()
    if request.method == 'POST':
        form_asign = ResolveForm(request.POST, request.FILES, instance=meter)
        if form_asign.is_valid():
            meter = form_asign.save(commit=False)

            meter.status2 = form_asign.cleaned_data['status2']
            meter.user2 = request.user
            meter.dtadd2 = datetime.datetime.now()
            meter.status3 = True
            meter.save()
            messages.success(request, 'Resolution Record saved successfully')
            return redirect('postpaid:results-list')
    else:
        # user_form = UserForm(instance=request.user)
        form_asign = ResolveForm(instance=meter)

    context = {
        'meter': meter,
        'form': form_asign,

    }
    return render(request, 'postpaid/viewuploaded.html', context)


def zerobillanalytics(request, pk=None):
    if request.user.is_authenticated:
        user = request.user
    meters = Zerobillresolved.objects.all()
    metersnon = Zerobills.objects.all()

    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_2 = date.today() - timedelta(days=2)
    yesterday_3 = date.today() - timedelta(days=3)
    yesterday_4 = date.today() - timedelta(days=4)

    meters_d = meters.filter(dtadd__date=today)
    meters_y = meters.filter(dtadd__date=yesterday)
    meters_y_2 = meters.filter(dtadd__date=yesterday_2)
    meters_y_3 = meters.filter(dtadd__date=yesterday_3)
    meters_y_4 = meters.filter(dtadd__date=yesterday_4)

    meters_f = meters.filter(status='faulty')
    meters_d_f = meters.filter(dtadd__date=today, status='faulty')
    meters_y_f = meters.filter(dtadd__date=yesterday, status='faulty')

    meters_fdc = meters.filter(status='disconnected')
    meters_d_fdc = meters.filter(dtadd__date=today, status='disconnected')
    meters_y_fdc = meters.filter(dtadd__date=yesterday, status='disconnected')

    meters_nos = meters.filter(status='notonsite')
    meters_d_nos = meters.filter(dtadd__date=today, status='notonsite')
    meters_y_nos = meters.filter(dtadd__date=yesterday, status='notonsite')

    meters_vp = meters.filter(status='vacantpremises')
    meters_d_vp = meters.filter(dtadd__date=today, status='vacantpremises')
    meters_y_vp = meters.filter(dtadd__date=yesterday, status='vacantpremises')

    meters_ok = meters.filter(status='meterokay')
    meters_d_ok = meters.filter(dtadd__date=today, status='meterokay')
    meters_y_ok = meters.filter(dtadd__date=yesterday, status='meterokay')

    meters_issue = meters.filter(Q(status='tampered') | Q(status='bypasses'))

    meters_is = meters_issue
    meters_d_is = meters_issue.filter(dtadd__date=today)
    meters_y_is = meters_issue.filter(dtadd__date=yesterday)

    meters_id = meters.filter(status='idle')
    meters_d_id = meters.filter(dtadd__date=today, status='idle')
    meters_y_id = meters.filter(dtadd__date=yesterday, status='idle')

    meters_count = meters.count()
    # County analytics
    analytics = County.objects.values('name').annotate(
        pending=(Count('county_zb_target', distinct=True, filter=Q(county_zb_target__status='pending'))),
    ).order_by('name')

    analytics1 = County.objects.values('name').annotate(
        over_r=(Count('county_zb_resolved', distinct=True)),
        over_r_t=(Count('county_zb_resolved', distinct=True, filter=Q(county_zb_resolved__dtadd__date=today))),
        over_r_y=(Count('county_zb_resolved', distinct=True, filter=Q(county_zb_resolved__dtadd__date=yesterday))),

    ).order_by('name')

    # Regional analytics
    analytics_r = Region.objects.values('name').annotate(
        pending=(Count('region_zb_target', distinct=True, filter=Q(region_zb_target__status='pending'))),
    ).order_by('name')

    analytics1_r = Region.objects.values('name').annotate(
        over_r=(Count('region_zb_resolved', distinct=True)),
        over_r_t=(Count('region_zb_resolved', distinct=True, filter=Q(region_zb_resolved__dtadd__date=today))),
        over_r_y=(Count('region_zb_resolved', distinct=True, filter=Q(region_zb_resolved__dtadd__date=yesterday))),

    ).order_by('name')

    # analytics = County.objects.annotate(resolved=Count('county_z_resolved'),pending=Count('county_z_target')).distinct()

    target = metersnon.count()
    overall_r = meters.count()
    overall_t = metersnon.filter(dtadd__date=today).count()
    overall_y = metersnon.filter(dtadd__date=yesterday).count()

    # meters_vended = meters.filter(status = 'vended').count()
    # meters_faulty = meters.filter(status = 'faulty').count()
    # meters_recovered = meters.filter(status = 'recovered').count()    
    # meters_pendingrerec = meters.filter(status = 'pendingrerec').count()
    # meters_notonsite = meters.filter(status = 'notonsite').count()

    # meters_vended_t = meters.filter(status = 'vended', dtadd__date=today).count()
    # meters_recovered_t = meters.filter(status = 'recovered', dtadd__date=today).count()
    # meters_faulty_t = meters.filter(status = 'faulty',dtadd__date=today).count()
    # meters_notonsite_t = meters.filter(status = 'notonsite',dtadd__date=today).count()
    # meters_pendingrerec_t = meters.filter(status = 'pendingrerec',dtadd__date=today).count()
    # meters_t = meters_d.count()

    context = {
        'target': metersnon.count(),
        'analytics': analytics,
        'analytics1': analytics1,
        'overall_t': meters_d.count(),
        'overall_y': meters_y.count(),

        'meters_f': meters_f.count(),
        'meters_d_f': meters_d_f.count(),
        'meters_y_f': meters_y_f.count(),

        'meters_fdc': meters_fdc.count(),
        'meters_d_fdc': meters_d_fdc.count(),
        'meters_y_fdc': meters_y_fdc.count(),

        'meters_nos': meters_nos.count(),
        'meters_d_nos': meters_d_nos.count(),
        'meters_y_nos': meters_y_nos.count(),

        'meters_vp': meters_vp.count(),
        'meters_d_vp': meters_d_vp.count(),
        'meters_y_vp': meters_y_vp.count(),

        'meters_ok': meters_ok.count(),
        'meters_d_ok': meters_d_ok.count(),
        'meters_y_ok': meters_y_ok.count(),

        'meters_is': meters_is.count(),
        'meters_d_is': meters_d_is.count(),
        'meters_y_is': meters_y_is.count(),

        'meters_id': meters_id.count(),
        'meters_d_id': meters_d_id.count(),
        'meters_y_id': meters_y_id.count(),

        'analytics_r': analytics_r,
        'analytics1_r': analytics1_r,

        'meters_count': meters_count,
        'nbar': 'analytics'

    }

    return render(request, 'postpaid/analytics.html', context)


@login_required(login_url="login")
def staffresolutions(request, pk=None):
    if request.user.is_authenticated:
        user = request.user
    today = date.today()
    yesterday = date.today() - timedelta(days=1)

    user_posts = UserProfile.objects.filter(campaign='zerobills').annotate(
        total_posts=Count('Zerobillresolved_user'),
        td=(Count('user_id', filter=Q(Zerovendingresolved_user__dtadd__date=today))),
        ys=(Count('user_id', filter=Q(Zerovendingresolved_user__dtadd__date=yesterday))),
    ).order_by('county')

    context = {
        'analytics': user_posts,
        'nbar': 'analytics'
    }
    return render(request, 'postpaid/staffresolutions.html', context)


@login_required(login_url="login")
def globalreport(request, pk=None):
    if request.user.is_authenticated:
        user = request.user
    meters = Zerobillresolved.objects.all()
    metersnon = Zerobills.objects.all()

    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_2 = date.today() - timedelta(days=2)
    yesterday_3 = date.today() - timedelta(days=3)

    meters_d = meters.filter(dtadd__date=today)
    meters_y = meters.filter(dtadd__date=yesterday)
    meters_y_2 = meters.filter(dtadd__date=yesterday_2)
    meters_y_3 = meters.filter(dtadd__date=yesterday_3)

    meters_f = meters.filter(status='faulty')
    meters_d_f = meters.filter(dtadd__date=today, status='faulty')
    meters_y_f = meters.filter(dtadd__date=yesterday, status='faulty')
    meters_y2_f = meters.filter(dtadd__date=yesterday_2, status='faulty')
    meters_y3_f = meters.filter(dtadd__date=yesterday_3, status='faulty')

    meters_fdc = meters.filter(status='disconnected')
    meters_d_fdc = meters.filter(dtadd__date=today, status='disconnected')
    meters_y_fdc = meters.filter(dtadd__date=yesterday, status='disconnected')
    meters_y2_fdc = meters.filter(dtadd__date=yesterday_2, status='disconnected')
    meters_y3_fdc = meters.filter(dtadd__date=yesterday_3, status='disconnected')

    meters_nos = meters.filter(status='notonsite')
    meters_d_nos = meters.filter(dtadd__date=today, status='notonsite')
    meters_y_nos = meters.filter(dtadd__date=yesterday, status='notonsite')
    meters_y2_nos = meters.filter(dtadd__date=yesterday_2, status='notonsite')
    meters_y3_nos = meters.filter(dtadd__date=yesterday_3, status='notonsite')

    meters_vp = meters.filter(status='vacantpremises')
    meters_d_vp = meters.filter(dtadd__date=today, status='vacantpremises')
    meters_y_vp = meters.filter(dtadd__date=yesterday, status='vacantpremises')
    meters_y2_vp = meters.filter(dtadd__date=yesterday_2, status='vacantpremises')
    meters_y3_vp = meters.filter(dtadd__date=yesterday_3, status='vacantpremises')

    meters_ok = meters.filter(status='meterokay')
    meters_d_ok = meters.filter(dtadd__date=today, status='meterokay')
    meters_y_ok = meters.filter(dtadd__date=yesterday, status='meterokay')
    meters_y2_ok = meters.filter(dtadd__date=yesterday_2, status='meterokay')
    meters_y3_ok = meters.filter(dtadd__date=yesterday_3, status='meterokay')

    meters_id = meters.filter(status='idle')
    meters_d_id = meters.filter(dtadd__date=today, status='idle')
    meters_y_id = meters.filter(dtadd__date=yesterday, status='idle')
    meters_y2_id = meters.filter(dtadd__date=yesterday_2, status='idle')
    meters_y3_id = meters.filter(dtadd__date=yesterday_3, status='idle')

    meters_issue = meters.filter(Q(status='tampered') | Q(status='bypasses'))

    paginator = Paginator(meters, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()

    context = {
        'target': metersnon.count(),

        'overall_t': meters_d.count(),
        'overall_y': meters_y.count(),
        'overall_y2': meters_y_2.count(),
        'overall_y3': meters_y_3.count(),

        'meters_f': meters_f.count(),
        'meters_d_f': meters_d_f.count(),
        'meters_y_f': meters_y_f.count(),
        'meters_y2_f': meters_y2_f.count(),
        'meters_y2_f': meters_y2_f.count(),

        'meters_fdc': meters_fdc.count(),
        'meters_d_fdc': meters_d_fdc.count(),
        'meters_y_fdc': meters_y_fdc.count(),
        'meters_y2_fdc': meters_y2_fdc.count(),
        'meters_y3_fdc': meters_y3_fdc.count(),

        'meters_nos': meters_nos.count(),
        'meters_d_nos': meters_d_nos.count(),
        'meters_y_nos': meters_y_nos.count(),
        'meters_y2_nos': meters_y2_nos.count(),
        'meters_y3_nos': meters_y3_nos.count(),

        'meters_vp': meters_vp.count(),
        'meters_d_vp': meters_d_vp.count(),
        'meters_y_vp': meters_y_vp.count(),
        'meters_y2_vp': meters_y2_vp.count(),
        'meters_y3_vp': meters_y3_vp.count(),

        'meters_ok': meters_ok.count(),
        'meters_d_ok': meters_d_ok.count(),
        'meters_y_ok': meters_y_ok.count(),
        'meters_y2_ok': meters_y2_ok.count(),
        'meters_y3_ok': meters_y3_ok.count(),

        'meters_id': meters_id.count(),
        'meters_d_id': meters_d_id.count(),
        'meters_y_id': meters_y_id.count(),
        'meters_y2_id': meters_y2_id.count(),
        'meters_y3_id': meters_y3_id.count(),

        'yesterday_2': yesterday_2,
        'yesterday_3': yesterday_3,

        'meters_count': meters_count,
        'nbar': 'analytics'

    }

    return render(request, 'postpaid/globalanalysis.html', context)


@login_required(login_url="login")
def regionalreport(request, pk=None):
    if request.user.is_authenticated:
        user = request.user
    meters = Zerobillresolved.objects.all()
    metersnon = Zerobills.objects.all()

    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_2 = date.today() - timedelta(days=2)
    yesterday_3 = date.today() - timedelta(days=3)
    yesterday_4 = date.today() - timedelta(days=4)

    meters_d = meters.filter(dtadd__date=today)
    meters_y = meters.filter(dtadd__date=yesterday)
    meters_y_2 = meters.filter(dtadd__date=yesterday_2)
    meters_y_3 = meters.filter(dtadd__date=yesterday_3)
    meters_y_4 = meters.filter(dtadd__date=yesterday_4)

    paginator = Paginator(meters, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()

    analytics_r = Region.objects.values('name', 'id').annotate(
        pending=(Count('region_zb_target', distinct=True, filter=Q(region_zb_target__status='pending'))),
    ).order_by('name')

    analytics1_r = Region.objects.values('name', 'id').annotate(
        over_r=(Count('region_zb_resolved', distinct=True)),
        over_r_t=(Count('region_zb_resolved', distinct=True, filter=Q(region_zb_resolved__dtadd__date=today))),
        over_r_y=(Count('region_zb_resolved', distinct=True, filter=Q(region_zb_resolved__dtadd__date=yesterday))),

    ).order_by('name')

    meters_t = meters_d.count()

    context = {
        'target': metersnon.count(),

        'overall_t': meters_d.count(),
        'overall_y': meters_y.count(),

        'analytics_r': analytics_r,
        'analytics1_r': analytics1_r,

        'meters_count': meters_count,
        'nbar': 'analytics'

    }

    return render(request, 'postpaid/regionalanalytics.html', context)


@login_required(login_url="login")
def viewcounty(request, pk):
    meter_resolved = Zerobillresolved.objects.filter(region_id=pk)
    meter_target = Zerobills.objects.filter(region_id=pk)
    county = County.objects.filter(id=pk)
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_2 = date.today() - timedelta(days=2)
    yesterday_3 = date.today() - timedelta(days=3)
    yesterday_4 = date.today() - timedelta(days=4)

    analytics = County.objects.filter(region_id=pk).values('name', 'id').annotate(
        pending=(Count('county_zb_target', distinct=True, filter=Q(county_zb_target__status='pending'))),
    ).order_by('name')

    analytics1 = County.objects.filter(region_id=pk).annotate(
        over_r=(Count('county_zb_resolved', distinct=True)),
        over_r_t=(Count('county_zb_resolved', distinct=True, filter=Q(county_zb_resolved__dtadd__date=today))),
        over_r_y=(Count('county_zb_resolved', distinct=True, filter=Q(county_zb_resolved__dtadd__date=yesterday))),

    ).order_by('name')

    context = {
        'analytics': analytics,
        'analytics1': analytics1,
    }
    return render(request, 'postpaid/countyanalytics.html', context)


@login_required(login_url="login")
def viewuser(request, pk):
    if request.user.is_authenticated:
        user = request.user
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    county = County.objects.get(id=pk).name

    user_posts = UserProfile.objects.filter(county_id=pk, campaign='zerobills').annotate(
        total_posts=Count('Zerobillresolved_user'),
        td=(Count('user_id', filter=Q(Zerobillresolved_user__dtadd__date=today))),
        ys=(Count('user_id', filter=Q(Zerobillresolved_user__dtadd__date=yesterday))),
    ).order_by('county')

    context = {
        'analytics': user_posts,
        'nbar': 'analytics',
        'county': county
    }
    return render(request, 'postpaid/useranalytics.html', context)


@login_required(login_url="login")
def exportupload(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=7)
    meters = Zerobillresolved.objects.filter(dtadd__range=[yesterday, today])

    writer.writerow(
        ['METER NUMBER', 'ACCOUNT NUMBER', 'REGION', 'COUNTY', 'DATE RECOVERED', 'STAFF', 'STATUS', 'READINGS'])
    for meter in meters:
        writer.writerow(
            [meter.meterno, meter.accountno, meter.region, meter.county, meter.dtadd, meter.user, meter.status,
             meter.readings])

    response['Content-Disposition'] = 'attachment; filename="ZERO BILL RESOLVED.csv" '
    return response


@login_required(login_url="login")
def search_meter_resolved(request):
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = Threephase_inspection.objects.filter(meterno__icontains=keyword)

    context = {
        'meters': paged_uploads,
        'meters_count': paged_uploads.count(),
        'nbar': 'searchmeter',
    }

    return render(request, 'postpaid/highend/threephase_view_results.html', context)


@login_required(login_url="login")
def kagua_connection(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters = Kaguaconnection.objects.filter(status=False, feeder__county=user)
    paginator = Paginator(meters, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_pending = meters.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_pending,
        'nbar': 'alluploads'}
    return render(request, 'postpaid/kagua_connection.html', context)


@login_required(login_url="login")
def search_connection(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county

        if 'keyword' in request.GET:
            keyword = request.GET["keyword"]
            if keyword:
                paged_uploads = Kaguaconnection.objects.filter(meterno__icontains=keyword, status=False,
                                                               feeder__county=user)

        context = {
            'meters': paged_uploads,
            'meters_count': paged_uploads.count(),
            'nbar': 'searchmeter',
        }

    return render(request, 'postpaid/kagua_connection.html', context)


@login_required(login_url='login')
def viewkagua(request, pk):
    # userprofile = get_object_or_404(UserProfile, user=request.user)
    img = Kaguaconnection.objects.get(id=pk)

    campaign = request.user.userprofile.campaign

    if campaign == 'kagua_connection':

        if request.method == 'POST':
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = KaguaForm(request.POST, request.FILES, instance=img)

            if m_form.is_valid():

                zerov = m_form.save(commit=False)
                resolution = Inspect_connection()
                resolution.meterno = m_form.cleaned_data['meterno']
                resolution.accountno = m_form.cleaned_data['accountno']
                resolution.meteringstatus = m_form.cleaned_data['meteringstatus']
                resolution.installationstatus = m_form.cleaned_data['installationstatus']
                resolution.faultystatus = m_form.cleaned_data['faultystatus']
                resolution.tamperedstatus = m_form.cleaned_data['tamperedstatus']
                resolution.bypassstatus = m_form.cleaned_data['bypassstatus']
                resolution.notokaystatus = m_form.cleaned_data['notokaystatus']
                resolution.meterimg = m_form.cleaned_data['meterimg']
                resolution.reading = m_form.cleaned_data['reading']
                resolution.metertype = m_form.cleaned_data['metertype']
                resolution.comment = m_form.cleaned_data['comment']
                resolution.inspector = request.user.userprofile
                resolution.connection = img
                resolution.feeder_inspected = zerov.feeder
                resolution.county = request.user.userprofile.county
                resolution.region = request.user.userprofile.region
                # resolution.feeder = zerov.feeder

                resolution.save()
                zerov.status = True

                zerov.save()
                messages.success(request, 'Your Inspection Has been successfully saved.')
                return redirect('postpaid:myconnection-list')
            else:

                messages.error(request, 'There was an error in submitting your inspection.')
                m_form = KaguaForm(instance=img)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = KaguaForm(instance=img)
        context = {'form': m_form, }
    else:
        messages.error(request, 'You are not configured to run on this campaign.')
        return redirect('main:my-dashboard')

    return render(request, 'postpaid/kagua_inspection.html', context)


@login_required(login_url="login")
def myconnection(request):
    if request.user.is_authenticated:
        user = request.user.userprofile

    meters = Inspect_connection.objects.filter(inspector=user).order_by('-dtadd')
    meters1 = Not_in_feeder.objects.filter(inspector=user).order_by('-dtadd')
    paginator = Paginator(meters, 30)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_count,
        'meters1': meters1,

        'nbar': 'myuploads'}
    return render(request, 'postpaid/myconnections.html', context)


@login_required(login_url="login")
def kaguaresultslist(request):
    meters = Inspect_connection.objects.all().order_by('-dtadd')
    counties = County.objects.all().order_by('name')
    paginator = Paginator(meters, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_pending = meters.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_pending,
        'counties': counties,
        'nbar': 'alluploads'}
    return render(request, 'postpaid/viewkaguaresults.html', context)


@login_required(login_url="login")
def kagua_analytics_global(request):
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_2 = date.today() - timedelta(days=2)
    yesterday_3 = date.today() - timedelta(days=3)

    feeders_inspected = Inspect_connection.objects.all().select_related('connection').values('connection__feeder__name',
                                                                                             'connection__feeder__county__name',
                                                                                             'connection__feeder_id').annotate(
        the_count=Count('id'),
        the_count_t=Count('connection__feeder_id'),
        today=Count('id', filter=Q(dtadd__date=today)),
        meteringnotokay=Count('id', filter=(~Q(meteringstatus__in=['okay']))),
        installation_not_okay=Count('id', filter=(~Q(installationstatus__in=['okay']))),
        yesturday=Count('id', filter=Q(dtadd__date=yesterday)),
        yesturday_2_d=Count('id', filter=Q(dtadd__date=yesterday_2)),
        yesturday_3_d=Count('id', filter=Q(dtadd__date=yesterday_3)),
    ).order_by('connection__feeder__county__name')

    # feeders = Kaguaconnection.objects.all().select_related('feeder').values('feeder__name').annotate(the_count=Count('feeder_id'))

    context = {
        'feeders': feeders_inspected,
        'yesterday_2': yesterday_2,
        'yesterday_3': yesterday_3,

    }

    return render(request, 'postpaid/kagua_analytics_global.html', context)


@login_required(login_url="login")
def kagua_inspector_analytics(request):
    if request.user.is_authenticated:
        user = request.user
    today = date.today()
    yesterday = date.today() - timedelta(days=1)

    inspectors = Inspect_connection.objects.all().select_related('inspector').values('inspector__user_id__stid',
                                                                                     'inspector__user_id__name',
                                                                                     'inspector__county__name',
                                                                                     'inspector__user_id__mobile').annotate(
        the_count=Count('id'),
        today=Count('id', filter=Q(dtadd__date=today)),
        yesturday=Count('id', filter=Q(dtadd__date=yesterday)),
        # yesturday_2_d=Count('id',filter=Q(dtadd__date=yesterday_2)),
        # yesturday_3_d=Count('id',filter=Q(dtadd__date=yesterday_3)),
    ).order_by('connection__feeder__county__name')

    context = {
        'analytics': inspectors,
        'nbar': 'analytics',
        # 'county' : county
    }
    return render(request, 'postpaid/kagua_user_analytics.html', context)


@login_required(login_url="login")
def not_in_feeder(request):
    sectorname = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = Not_in_feederForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            meter = form.save(commit=False)
            meter.inspector = request.user.userprofile
            meter.county = request.user.userprofile.county
            meter.region = request.user.userprofile.region
            uploaded = Kaguaconnection.objects.filter(meterno=meter.meterno)
            if uploaded.count() > 0:
                messages.error(request, 'That Meter is in that Feeder and Has already been Inspected.')
                return redirect('postpaid:upload-new')
            else:
                meter.save()
            messages.success(request, 'Your record has been uploaded successfully')
            return redirect('postpaid:myconnection-list')
        else:
            messages.error(request, 'Error Uploading the record. Please Try Again')
    else:
        form = Not_in_feederForm(request=request)
    return render(request, 'postpaid/not_in_feeder.html', {'form': form, 'sectorname': sectorname})


@login_required(login_url="login")
def export_kagua_connection(request, pk):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    # meters =Inspect_connection.objects.filter(dtadd__gt=datetime.datetime.today()-datetime.timedelta(days=30), county_id=pk).order_by('-dtadd')
    meters = Inspect_connection.objects.filter(county_id=pk).order_by('-dtadd')

    writer.writerow(
        ['METER NUMBER', 'ACCOUNT NUMBER', 'TYPE', 'FEEDER', 'TX', 'METERING STATUS', 'INSTALLATION STATUS', 'FAULTY',
         'TAMPERED', 'BYPASSED', 'NOTOKAY STATUS', 'READING', 'INSPECTOR', 'DATE INSPECTED', 'COMMENT'])
    for meter in meters:
        writer.writerow(
            [meter.meterno, meter.accountno, meter.metertype, meter.connection.feeder.name, meter.connection.substation,
             meter.meteringstatus, meter.installationstatus, meter.faultystatus, meter.tamperedstatus,
             meter.bypassstatus, meter.notokaystatus, meter.reading, meter.inspector, meter.dtadd, meter.comment])

    response['Content-Disposition'] = 'attachment; filename="KAGUA CONNECTION.csv" '
    return response


@login_required(login_url="login")
def kagua_regional_analytics(request, pk=None):
    if request.user.is_authenticated:
        user = request.user
    meters = Region.objects.all()
    context = {
        'analytics_r': meters,
        'nbar': 'analytics'
    }
    return render(request, 'postpaid/kagua_regional_analysis.html', context)


@login_required(login_url="login")
def kagua_county_analysis(request, pk):
    meter_resolved = Inspect_connection.objects.filter(region_id=pk)
    county = County.objects.filter(id=pk)
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_2 = date.today() - timedelta(days=2)
    yesterday_3 = date.today() - timedelta(days=3)
    yesterday_4 = date.today() - timedelta(days=4)

    analytics = County.objects.filter(region_id=pk).select_related('county').values('name', 'id').annotate(
        resolved=(Count('inspect_connection', distinct=True)),
        not_in_feeder_resolved=(Count('not_in_feeder', distinct=True)),
        resolved_t=(Count('inspect_connection', distinct=True, filter=Q(inspect_connection__dtadd__date=today))),
        resolved_y=(Count('inspect_connection', distinct=True, filter=Q(inspect_connection__dtadd__date=yesterday))),
        resolved_y_2=(
            Count('inspect_connection', distinct=True, filter=Q(inspect_connection__dtadd__date=yesterday_2))),
    ).order_by('name')

    context = {
        'analytics': analytics,
        'yesterday_2': yesterday_2
    }
    return render(request, 'postpaid/kagua_county_analysis.html', context)


@login_required(login_url="login")
def export_kagua_connection_notinfeeder(request, pk):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    # meters =Inspect_connection.objects.filter(dtadd__gt=datetime.datetime.today()-datetime.timedelta(days=30), county_id=pk).order_by('-dtadd')
    meters = Not_in_feeder.objects.filter(county_id=pk).order_by('-dtadd')

    writer.writerow(
        ['METER NUMBER', 'NEIGHBOUR METER', 'FEEDER', 'TX NUMBER', 'TYPE', 'REGION', 'COUNTY', 'METERING STATUS',
         'INSTALLATION STATUS', 'FAULTY', 'TAMPERED', 'BYPASSED', 'NOTOKAY STATUS', 'READING', 'INSPECTOR',
         'DATE INSPECTED', 'COMMENT'])
    for meter in meters:
        writer.writerow(
            [meter.meterno, meter.Neighbour_Meter, meter.feeder, meter.txnumber, meter.metertype, meter.region,
             meter.county, meter.meteringstatus, meter.installationstatus, meter.faultystatus, meter.tamperedstatus,
             meter.bypassstatus, meter.notokaystatus, meter.reading, meter.inspector, meter.dtadd, meter.comment])

    response['Content-Disposition'] = 'attachment; filename="KAGUA CONNECTION NOT IN FEEDER.csv" '
    return response


@login_required(login_url="login")
def kagua_dashboard(request):
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_2 = date.today() - timedelta(days=2)
    yesterday_3 = date.today() - timedelta(days=3)

    feeders_inspected = Inspect_connection.objects.all().select_related('connection').values('connection__feeder__name',
                                                                                             'connection__feeder__county__name',
                                                                                             'connection__feeder_id').annotate(
        the_count=Count('id'),
        the_count_t=Count('connection__feeder_id'),
        today=Count('id', filter=Q(dtadd__date=today)),
        meteringnotokay=Count('id', filter=(~Q(meteringstatus__in=['okay']))),
        installation_not_okay=Count('id', filter=(~Q(installationstatus__in=['okay']))),
        yesturday=Count('id', filter=Q(dtadd__date=yesterday)),
        yesturday_2_d=Count('id', filter=Q(dtadd__date=yesterday_2)),
        yesturday_3_d=Count('id', filter=Q(dtadd__date=yesterday_3)),
    ).order_by('connection__feeder__county__name')
    kagua = Inspect_connection.objects.all()
    county_kagua = kagua.values('meterno', 'county__name')
    meteringstatus_kagua = kagua.values('meterno', 'meteringstatus')
    installationstatus_kagua = kagua.values('meterno', 'installationstatus')

    df = read_frame(kagua)
    county = read_frame(county_kagua)
    df['dtadd'] = pd.to_datetime(df['dtadd']).dt.date
    df = df.groupby(by='dtadd', as_index=False, sort=False)['meterno'].count()
    df = px.bar(df, x=df.dtadd, y=df.meterno, title='Kagua Connection Global Daily Trend', text_auto=True,
                text=df.meterno)
    df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

    county = county.groupby(by='county__name', as_index=False)['meterno'].count().sort_values(by='meterno',
                                                                                              ascending=False)
    county = px.bar(county, x=county.county__name, y=county.meterno,
                    title='Kagua Connection Overall County Achievement', text_auto=True, text=county.meterno)
    county = json.dumps(county, cls=plotly.utils.PlotlyJSONEncoder)

    metering_status = read_frame(meteringstatus_kagua)
    metering_status = metering_status.groupby(by='meteringstatus', as_index=False)['meterno'].count()
    values = metering_status.meteringstatus
    names = metering_status.meterno
    metering_status = px.pie(metering_status, values=names, names=values, title='Kagua Connection Metering Status')
    metering_status = json.dumps(metering_status, cls=plotly.utils.PlotlyJSONEncoder)

    installation_status = read_frame(installationstatus_kagua)
    installation_status = installation_status.groupby(by='installationstatus', as_index=False)['meterno'].count()
    values = installation_status.installationstatus
    names = installation_status.meterno
    installation_status = px.pie(installation_status, values=names, names=values,
                                 title='Kagua Connection Installation Status')
    installation_status = json.dumps(installation_status, cls=plotly.utils.PlotlyJSONEncoder)

    context = {
        'df': df,
        'county': county,
        'metering_status': metering_status,
        'installation_status': installation_status,
        'feeders': feeders_inspected,
        'yesterday_2': yesterday_2,
        'yesterday_3': yesterday_3,
    }

    return render(request, 'postpaid/dashboard.html', context=context)


@login_required(login_url="login")
def threephase_target(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters = Threephase_target.objects.filter(status=False, county=user)[:10]
    paginator = Paginator(meters, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_pending = meters.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_pending,
        'nbar': 'alluploads'}
    return render(request, 'postpaid/highend/threepase_target.html', context)


@login_required(login_url='login')
def inspect_threephase(request, pk):
    # userprofile = get_object_or_404(UserProfile, user=request.user)
    img = Threephase_target.objects.get(id=pk)

    campaign = request.user.userprofile.campaign

    if campaign not in (
            'network_technician', 'network_supervisors', 'network_region', 'contractor_safaricom',
            'contractor_allandick',
            'other'):

        if request.method == 'POST':
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = ThreepahseForm(request.POST, request.FILES, instance=img)

            if m_form.is_valid():

                zerov = m_form.save(commit=False)
                resolution = Threephase_inspection()
                resolution.meterno = m_form.cleaned_data['meterno']
                resolution.accountno = m_form.cleaned_data['accountno']
                resolution.meteringstatus = m_form.cleaned_data['meteringstatus']
                resolution.installationstatus = m_form.cleaned_data['installationstatus']
                resolution.faultystatus = m_form.cleaned_data['faultystatus']
                resolution.tamperedstatus = m_form.cleaned_data['tamperedstatus']
                resolution.bypassstatus = m_form.cleaned_data['bypassstatus']
                resolution.notokaystatus = m_form.cleaned_data['notokaystatus']
                resolution.meterimg = m_form.cleaned_data['meterimg']
                resolution.reading = m_form.cleaned_data['reading']
                resolution.metertype = m_form.cleaned_data['metertype']
                resolution.comment = m_form.cleaned_data['comment']
                resolution.sealno = m_form.cleaned_data['sealno']
                resolution.inspector = request.user.userprofile
                resolution.threepase = img
                resolution.county = request.user.userprofile.county
                resolution.region = request.user.userprofile.region
                # resolution.feeder = zerov.feeder

                resolution.save()
                zerov.status = True
                zerov.save()
                messages.success(request, 'Your Inspection Has been successfully saved.')
                return redirect('postpaid:mythreephase-list')
            else:

                messages.error(request, 'There was an error in submitting your inspection.')
                print('invalid form')
                print(m_form.errors)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = ThreepahseForm(instance=img)
        context = {'form': m_form, }
    else:
        messages.error(request, 'You are not configured to run on this campaign.')
        return redirect('main:my-dashboard')

    return render(request, 'postpaid/threephase_inspection.html', context)


# My High End Inspections
@login_required(login_url="login")
def mythreephase_list(request):
    if request.user.is_authenticated:
        user = request.user.userprofile
    today = date.today()
    meters = (
        Threephase_inspection.objects.select_related("inspector")
        .filter(inspector=user, dtadd__date=today)
        .order_by("-dtadd")
    )
    paginator = Paginator(meters, 30)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()

    context = {
        "meters": paged_uploads,
        "meters_count": meters_count,
        "nbar": "myuploads",
    }
    return render(request, "postpaid/highend/mythreephase_list.html", context)


# view Uploaded High End
@login_required(login_url="login")
def view_uploaded_highend(request, pk):
    meter = Threephase_inspection.objects.get(id=pk)

    context = {
        "meter": meter,
    }
    return render(request, "postpaid/highend/view_uploaded_threephase.html", context)


@login_required(login_url="login")
def threephase_search_meter(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters_list = Threephase_target.objects.filter(status=False, county=user)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/highend/threepase_target.html', context)


@login_required(login_url="login")
def threephase_search_itin(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county

    meters_list = Threephase_target.objects.filter(status=False, county=user)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(itin__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/highend/threepase_target.html', context)


@login_required(login_url="login")
def search_by_sector(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county

    meters_list = Threephase_target.objects.filter(status=False, county=user)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(sector__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/highend/threepase_target.html', context)


@login_required(login_url="login")
def threephase_target_export(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    # meters =Inspect_connection.objects.filter(dtadd__gt=datetime.datetime.today()-datetime.timedelta(days=30), county_id=pk).order_by('-dtadd')
    meters = Threephase_target.objects.filter(status=False, county=user)

    writer.writerow(['METER NUMBER', 'ACCOUNT NUMBER', 'SECTOR', 'ZONE', 'ITINERARY', 'LONGITUDE', 'LATITUDE'])
    for meter in meters:
        writer.writerow([meter.meterno, meter.accountno, meter.sector, meter.zone, meter.itin, meter.lon, meter.lat])

    response['Content-Disposition'] = 'attachment; filename="SME TARGET.csv" '
    return response


@login_required(login_url="login")
def threephase_itins(request, pk):
    if request.user.is_authenticated:
        user = request.user.userprofile.county

    meters_list = Threephase_target.objects.filter(status=False, county=user, itin=pk)
    paginator = Paginator(meters_list, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context = {
        'meters': paged_uploads,
        'nbar': 'alluploads'
    }
    return render(request, 'postpaid/highend/threepase_target.html', context)


# High End Inspection Results
@login_required(login_url="login")
def threephase_results_list(request):
    meters = (
        Threephase_inspection.objects.select_related(
            "threepase", "inspector", "county", "region"
        )
        .all()
        .order_by("-dtadd")
    )
    paginator = Paginator(meters, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)
    context = {
        "meters": paged_uploads,
        "nbar": "alluploads",
    }
    return render(request, "postpaid/highend/threephase_view_results.html", context)


@login_required(login_url="login")
def threephase_dashboard(request):
    overall_inspected_t = Threephase_inspection.objects.select_related(
        "county", "region"
    ).values('meterno', 'meteringstatus', 'dtadd', 'county', 'region')
    overall_not_okay = overall_inspected_t.exclude(meteringstatus='okay')

    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    def count_business_days(start_date, end_date):
        # Define a list of weekend days (Saturday and Sunday)
        weekend_days = [5, 6]  # Monday is 0 and Sunday is 6
        # Initialize a counter for business days
        business_days = 0
        target = 0
        # Iterate through each day in the date range
        current_date = start_date
        while current_date <= end_date:
            # Check if the current day is a weekend day
            if current_date.weekday() not in weekend_days:
                business_days += 1
                target += 1392
            # Move to the next day
            current_date += datetime.timedelta(days=1)
        return business_days, target

    # Test the function
    start_date = datetime.date(2023, 8, 21)
    end_date = datetime.date.today()

    result = count_business_days(start_date, end_date)

    def metering_status_notokay():
        df = read_frame(overall_not_okay)
        df = df.groupby(by="meteringstatus", as_index=False, sort=False)[
            "meterno"
        ].count()
        values = df.meteringstatus
        names = df.meterno
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Metering Status Not Okay",
            labels={
                "meterno": "Meter Count",
                "meteringstatus": "Metering Status",
            },
        )
        df.update_traces(textposition='inside', textinfo='percent+label')
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    def metering_status():
        df = read_frame(overall_inspected_t)
        df = df.groupby(by="meteringstatus", as_index=False, sort=False)[
            "meterno"
        ].count()
        values = df.meteringstatus
        names = df.meterno
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Inspection Metering Status",
            labels={
                "meterno": "Meter Count",
                "meteringstatus": "Metering Status",
            },
        )
        df.update_traces(textposition='inside', textinfo='percent+label')
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    def target_achievement():
        t_a = overall_inspected_t.count()
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Planned ToDate",
                    x=["Planned ToDate"],
                    y=[result[1]],
                ),
                go.Bar(name="Achieved ToDate", x=["Achieved ToDate"], y=[t_a]),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Target vs Achievement",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="No Of Inspections",
                titlefont_size=16,
                tickfont_size=14,
            ),
            xaxis=dict(
                title="Year(2023/24)",
            ),
            legend=dict(
                bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
            ),
            barmode="group",
            bargap=0.15,  # gap between bars of adjacent location coordinates.
            bargroupgap=0.1,  # gap between bars of the same location coordinate.
        )
        fig_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return fig_plot

    def daily_trend():
        df = read_frame(overall_inspected_t)
        df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
        df = df.groupby(by="dtadd", as_index=False, sort=False)["meterno"].count()
        df = px.bar(
            df,
            x=df.dtadd,
            y=df.meterno,
            title=f"Daily Overall Inspections.Daily Target = {1, 392}",
            text_auto=True,
            text=df.meterno,
            labels={"dc_meterno": "Meter Count", "dtadd": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    regional_analytics = (
        Region.objects.select_related("highend_region")
        .values("name")  # select_related('dc_region')
        .annotate(
            hc_target_acs=(Sum("highend_target", distinct=True)),
            dc_daily_target=(Sum("highend_daily_target", distinct=True)),
            hc_inspected=(Count("highend_region", distinct=True)),
            hc_insp_faulty=(
                Count(
                    "highend_region",
                    distinct=True,
                    filter=Q(highend_region__meteringstatus="faulty"),
                )
            ),
            dc_insp_tampered=(
                Count(
                    "highend_region",
                    distinct=True,
                    filter=Q(highend_region__meteringstatus="tampered"),
                )
            ),
            hc_insp_bypassed=(
                Count(
                    "highend_region",
                    distinct=True,
                    filter=Q(highend_region__meteringstatus="bypassed"),
                )
            ),
            hc_insp_nometer=(
                Count(
                    "highend_region",
                    distinct=True,
                    filter=Q(highend_region__meteringstatus="nometer"),
                )
            ),
            hc_today=Count(
                "highend_region",
                distinct=True,
                filter=Q(highend_region__dtadd__date=today),
            ),
            hc_yesturday=Count(
                "highend_region",
                distinct=True,
                filter=Q(highend_region__dtadd__date=yesterday),
            ),
            hc_yesturday_1=Count(
                "highend_region",
                distinct=True,
                filter=Q(highend_region__dtadd__date=yesterday_1),
            ),
            hc_yesturday_2=Count(
                "highend_region",
                distinct=True,
                filter=Q(highend_region__dtadd__date=yesterday_2),
            ),
            hc_yesturday_3=Count(
                "highend_region",
                distinct=True,
                filter=Q(highend_region__dtadd__date=yesterday_3),
            ),
        )
        .order_by()
    )
    county_analytics = (
        County.objects.select_related("highend_county")
        .values("name")  # select_related('dc_region')
        .annotate(
            hc_target_acs=(Sum("highend_target", distinct=True)),
            dc_daily_target=(Sum("highend_daily_target", distinct=True)),
            hc_inspected=(Count("highend_county", distinct=True)),
            hc_insp_faulty=(
                Count(
                    "highend_county",
                    distinct=True,
                    filter=Q(highend_county__meteringstatus="faulty"),
                )
            ),
            dc_insp_tampered=(
                Count(
                    "highend_county",
                    distinct=True,
                    filter=Q(highend_county__meteringstatus="tampered"),
                )
            ),
            hc_insp_bypassed=(
                Count(
                    "highend_county",
                    distinct=True,
                    filter=Q(highend_county__meteringstatus="bypassed"),
                )
            ),
            hc_insp_nometer=(
                Count(
                    "highend_county",
                    distinct=True,
                    filter=Q(highend_county__meteringstatus="nometer"),
                )
            ),
            hc_today=Count(
                "highend_county",
                distinct=True,
                filter=Q(highend_county__dtadd__date=today),
            ),
            hc_yesturday=Count(
                "highend_county",
                distinct=True,
                filter=Q(highend_county__dtadd__date=yesterday),
            ),
            hc_yesturday_1=Count(
                "highend_county",
                distinct=True,
                filter=Q(highend_county__dtadd__date=yesterday_1),
            ),
            hc_yesturday_2=Count(
                "highend_county",
                distinct=True,
                filter=Q(highend_county__dtadd__date=yesterday_2),
            ),
            hc_yesturday_3=Count(
                "highend_county",
                distinct=True,
                filter=Q(highend_county__dtadd__date=yesterday_3),
            ),
        )
        .order_by("name")
    )

    context = {
        "daily_trend_plot": daily_trend(),
        "target_achievement": target_achievement(),
        "metering_status": metering_status(),
        "metering_status_notokay": metering_status_notokay(),

        "regional_analytics": regional_analytics,
        "county_analytics": county_analytics,
        'yesterday': yesterday,
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,
    }

    return render(request, "postpaid/highend/threephase_dashboard.html", context=context)


@login_required(login_url="login")
def threephase_inspector_analytics(request):
    if request.user.is_authenticated:
        user = request.user
    county = request.user.userprofile.region
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    inspectors = Threephase_inspection.objects.select_related('inspector').values('inspector__county__name',
                                                                                  'inspector__user_id__stid',
                                                                                  'inspector__user_id__name',
                                                                                  'inspector__user_id__mobile').filter(
        region=county).annotate(
        the_count=Count("inspector"),
        today=Count("inspector", filter=Q(dtadd__date=today)),
        yesturday=Count(
            "inspector", filter=Q(dtadd__date=yesterday)
        ),
        yesturday_1=Count(
            "inspector", filter=Q(dtadd__date=yesterday_1)
        ),
        yesturday_2=Count(
            "inspector", filter=Q(dtadd__date=yesterday_2)
        ),
        yesturday_3=Count(
            "inspector", filter=Q(dtadd__date=yesterday_3)
        ),
    ).order_by("inspector__county__name")

    # if request.user.is_authenticated:
    #     user = request.user
    # today = date.today()
    # yesterday = date.today() - timedelta(days = 1)
    # yesterday_1 = date.today() - timedelta(days = 2)
    # yesterday_2 = date.today() - timedelta(days = 3)
    #
    # inspectors = UserProfile.objects.filter(campaign='threephase').values('user_id__id', 'user_id__name', 'user_id__mobile','county__name').annotate(
    #     the_count=Count('threephase_inspector'),
    #     today=Count('threephase_inspector', filter=Q(threephase_inspector__dtadd__date=today)),
    #     yesturday=Count('threephase_inspector', filter=Q(threephase_inspector__dtadd__date=yesterday)),
    #     yesturday_1=Count('threephase_inspector', filter=Q(threephase_inspector__dtadd__date=yesterday_1)),
    #     yesturday_2=Count('threephase_inspector', filter=Q(threephase_inspector__dtadd__date=yesterday_2)),
    # ).order_by('county__name')

    # inspectors = Threephase_inspection.objects.all().select_related('inspector').values('inspector__user_id__stid','inspector__user_id__name','inspector__county__name','inspector__user_id__mobile').annotate(
    #      the_count=Count('id'),
    #      today=Count('id',filter=Q(dtadd__date=today)),
    #      yesturday=Count('id',filter=Q(dtadd__date=yesterday)),
    #      yesturday_1=Count('id',filter=Q(dtadd__date=yesterday_1)),
    #      yesturday_2=Count('id',filter=Q(dtadd__date=yesterday_2)),
    #      #yesturday_2_d=Count('id',filter=Q(dtadd__date=yesterday_2)),
    #      #yesturday_3_d=Count('id',filter=Q(dtadd__date=yesterday_3)),
    #     ).order_by('inspector__county__name')

    context = {
        'analytics': inspectors,
        'nbar': 'analytics',
        'yesterday_1': yesterday_1,
        'yesterday_2': yesterday_2,
        # 'county' : county
    }
    return render(request, 'postpaid/threephase_user_analytics.html', context)


@login_required(login_url="login")
def threephase_regional_analytics(request, pk=None):
    if request.user.is_authenticated:
        user = request.user
    meters = Region.objects.all()
    context = {
        'analytics_r': meters,
        'nbar': 'analytics'
    }
    return render(request, 'postpaid/threephase_regional_analysis.html', context)


@login_required(login_url="login")
def threephase_county_analysis(request, pk):
    meter_resolved = Threephase_inspection.objects.filter(region_id=pk)
    county = County.objects.filter(id=pk)
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_2 = date.today() - timedelta(days=2)
    yesterday_3 = date.today() - timedelta(days=3)
    yesterday_4 = date.today() - timedelta(days=4)

    analytics = County.objects.filter(region_id=pk).select_related('county').values('name', 'id').annotate(
        resolved=(Count('threephase_inspection', distinct=True)),
        meteringnotokay=Count('threephase_inspection', filter=(~Q(threephase_inspection__meteringstatus__in=['okay']))),
        installation_not_okay=Count('threephase_inspection',
                                    filter=(~Q(threephase_inspection__installationstatus__in=['okay']))),
        resolved_t=(Count('threephase_inspection', distinct=True, filter=Q(threephase_inspection__dtadd__date=today))),
        resolved_y=(
            Count('threephase_inspection', distinct=True, filter=Q(threephase_inspection__dtadd__date=yesterday))),
        resolved_y_2=(
            Count('threephase_inspection', distinct=True, filter=Q(threephase_inspection__dtadd__date=yesterday_2))),
    ).order_by('name')

    inspectors = UserProfile.objects.filter(campaign='threephase', region_id=pk).values('user_id__stid',
                                                                                        'user_id__name',
                                                                                        'user_id__mobile',
                                                                                        'county__name').annotate(
        the_count=Count('threephase'),
        today=Count('threephase', filter=Q(threephase__dtadd__date=today)),
        yesturday=Count('threephase', filter=Q(threephase__dtadd__date=yesterday)),
        yesturday_2=Count('threephase', filter=Q(threephase__dtadd__date=yesterday_2)),
        yesturday_3=Count('threephase', filter=Q(threephase__dtadd__date=yesterday_3)),
    ).order_by('county__name')

    context = {
        'analytics': analytics,
        'yesterday_2': yesterday_2,
        'yesterday_1': yesterday,
        'inspectors': inspectors,

    }
    return render(request, 'postpaid/threephase_county_analysis.html', context)


@login_required(login_url="login")
def export_threephase_connection(request, pk):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    # meters =Inspect_connection.objects.filter(dtadd__gt=datetime.datetime.today()-datetime.timedelta(days=30), county_id=pk).order_by('-dtadd')
    meters = Threephase_inspection.objects.filter(county_id=pk).order_by('-dtadd')

    writer.writerow(
        ['REGION', 'COUNTY', 'METER NUMBER', 'ACCOUNT NUMBER', 'METERING STATUS', 'INSTALLATION STATUS', 'FAULTY',
         'TAMPERED', 'BYPASSED', 'NOTOKAY STATUS', 'READING', 'INSPECTOR', 'DATE INSPECTED', 'COMMENT'])
    for meter in meters:
        writer.writerow(
            [meter.region, meter.county, meter.meterno, meter.accountno, meter.meteringstatus, meter.installationstatus,
             meter.faultystatus, meter.tamperedstatus, meter.bypassstatus, meter.notokaystatus, meter.reading,
             meter.inspector, meter.dtadd, meter.comment])

    response['Content-Disposition'] = 'attachment; filename="3 PHASE CONNECTION.csv" '
    return response


@login_required(login_url="login")
def threephase_export_uploads(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    meters = Threephase_inspection.objects.filter(
        dtadd__gt=datetime.datetime.today() - datetime.timedelta(days=7)).order_by('-dtadd')

    writer.writerow(
        ['REGION', 'COUNTY', 'METER NUMBER', 'ACCOUNT NUMBER', 'METERING STATUS', 'INSTALLATION STATUS', 'FAULTY',
         'TAMPERED', 'BYPASSED', 'NOTOKAY STATUS', 'READING', 'INSPECTOR', 'DATE INSPECTED', 'COMMENT'])
    for meter in meters:
        writer.writerow(
            [meter.region, meter.county, meter.meterno, meter.accountno, meter.meteringstatus, meter.installationstatus,
             meter.faultystatus, meter.tamperedstatus, meter.bypassstatus, meter.notokaystatus, meter.reading,
             meter.inspector, meter.dtadd, meter.comment])

    response['Content-Disposition'] = 'attachment; filename="3 PHASE CONNECTION.csv" '
    return response


@login_required(login_url='login')
def inspect_telcos(request, pk):
    # userprofile = get_object_or_404(UserProfile, user=request.user)
    img = Telcos_target.objects.get(id=pk)

    campaign = request.user.userprofile.campaign

    if campaign not in (
            "network_technician",
            "network_supervisors",
            "network_region",
            "contractor_safaricom",
            "contractor_allandick",
            "other",
    ):

        if request.method == 'POST':
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = TelcosForm(request.POST, request.FILES, instance=img)

            if m_form.is_valid():

                # if m_form.cleaned_data['meterno'] is None:
                # messages.success(request, 'You need to take the Cordinates.')
                # return redirect('postpaid:mythreephase-list')
                #

                zerov = m_form.save(commit=False)
                resolution = Telcos_inspection()
                resolution.siteid = m_form.cleaned_data['siteid']
                resolution.sitename = m_form.cleaned_data['sitename']
                resolution.meterno = m_form.cleaned_data['meterno']
                resolution.accountno = m_form.cleaned_data['accountno']
                resolution.meteringstatus = m_form.cleaned_data['meteringstatus']
                resolution.installationstatus = m_form.cleaned_data['installationstatus']
                resolution.faultystatus = m_form.cleaned_data['faultystatus']
                resolution.tamperedstatus = m_form.cleaned_data['tamperedstatus']
                resolution.bypassstatus = m_form.cleaned_data['bypassstatus']
                resolution.notokaystatus = m_form.cleaned_data['notokaystatus']
                resolution.telcosimg = m_form.cleaned_data['telcosimg']
                resolution.reading = m_form.cleaned_data['reading']
                resolution.metertype = m_form.cleaned_data['metertype']
                resolution.diimg = m_form.cleaned_data['diimg']
                resolution.phase = m_form.cleaned_data['phase']
                resolution.comment = m_form.cleaned_data['comment']
                resolution.x = m_form.cleaned_data['x']
                resolution.y = m_form.cleaned_data['y']
                resolution.telcos = img
                resolution.county = m_form.cleaned_data['county']
                resolution.inspector = request.user.userprofile
                resolution.system_reading = 0
                resolution.consumption = zerov.consumption
                resolution.units = 0

                resolution.save()
                zerov.status = True
                zerov.save()
                messages.success(request, 'Your Inspection Has been successfully saved.')
                return redirect('postpaid:mytelcos-list')
            else:

                messages.error(request, 'There was an error in submitting your inspection.')
                m_form = TelcosForm(instance=img)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = TelcosForm(instance=img)
        context = {'form': m_form, }
    else:
        messages.error(request, 'You are not configured to run on this campaign.')
        return redirect('main:my-dashboard')

    return render(request, 'postpaid/telcos_inspection.html', context)


@login_required(login_url="login")
def telcos_target(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters = Telcos_target.objects.filter(status=False)
    paginator = Paginator(meters, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_pending = meters.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_pending,
        'nbar': 'alluploads'}
    return render(request, 'postpaid/telcos_target.html', context)


@login_required(login_url="login")
def telcos_search_meter(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters_list = Telcos_target.objects.filter(status=False)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/telcos_target.html', context)


@login_required(login_url="login")
def telcos_search_siteid(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters_list = Telcos_target.objects.filter(status=False)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(siteid__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/telcos_target.html', context)


@login_required(login_url="login")
def mytelcos_list(request):
    if request.user.is_authenticated:
        user = request.user.userprofile

    meters = Telcos_inspection.objects.filter(inspector=user).order_by('-dtadd')
    paginator = Paginator(meters, 30)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_count,
        'nbar': 'myuploads'}
    return render(request, 'postpaid/mytelcos_list.html', context)


@login_required(login_url="login")
def viewtelcos(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters = Telcos_inspection.objects.all().order_by('-dtadd')
    paginator = Paginator(meters, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_pending = meters.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_pending,
        'nbar': 'alluploads'}
    return render(request, 'postpaid/viewtelcos.html', context)


@login_required(login_url="login")
def viewsite(request, pk):
    meter = Telcos_inspection.objects.get(id=pk)

    context = {
        'meter': meter,

    }
    return render(request, 'postpaid/viewsite.html', context)


@login_required(login_url="login")
def telcos_export_uploads(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    meters = Telcos_inspection.objects.filter(
        dtadd__gt=datetime.datetime.today() - datetime.timedelta(days=60)).order_by('-dtadd')

    writer.writerow(['COUNTY', 'SITEID', 'SITE NAME', 'METER NUMBER', 'ACCOUNT NUMBER', 'PHASE', 'METERING STATUS',
                     'INSTALLATION STATUS', 'FAULTY', 'TAMPERED', 'BYPASSED', 'NOTOKAY STATUS', 'READING', 'INSPECTOR',
                     'DATE INSPECTED', 'COMMENT', 'X', 'Y', 'IMAGE_ADD', 'DI_ADD', 'SYSTEM READING'])
    for meter in meters:
        writer.writerow([meter.county, meter.siteid, meter.sitename, meter.meterno, meter.accountno, meter.phase,
                         meter.meteringstatus, meter.installationstatus, meter.faultystatus, meter.tamperedstatus,
                         meter.bypassstatus, meter.notokaystatus, meter.reading, meter.inspector, meter.dtadd,
                         meter.comment, meter.x, meter.y, meter.telcosimg, meter.diimg, meter.telcos.system_reading])

    response['Content-Disposition'] = 'attachment; filename="KAGUA TELCOS  CONNECTION.csv" '
    return response


@login_required(login_url="login")
def telcos_dashboard(request):
    Telcos = Telcos_inspection.objects.filter(telcos__telcos_type='safaricom')
    Target = Telcos_target.objects.filter(telcos_type='safaricom')
    county_telcos = Telcos.values('meterno', 'county__name')
    meteringstatus_telcos = Telcos.values('meterno', 'meteringstatus')
    installationstatus_telcos = Telcos.values('meterno', 'installationstatus')
    daily_target = County.objects.aggregate(total_target=Sum('telcos_target'))['total_target']
    overall_target = County.objects.aggregate(total_target_o=Sum('telcos_target_overall'))['total_target_o']

    yesterday = date.today() - timedelta(days=1)
    today = date.today()
    todays = Telcos.filter(dtadd__date=today).values('meterno', 'county__name', 'county__telcos_target', 'dtadd')
    previous = Telcos.filter(dtadd__date=yesterday).values('meterno', 'county__name', 'county__telcos_target', 'dtadd')

    rebill = Telcos.filter(units__gte=F('telcos__timesonefive') or ~Q(meteringstatus__in="okay"))

    rebilled = Telcos.filter(incms=True)

    county_today = []

    df = read_frame(Telcos)
    county = read_frame(county_telcos)
    df['dtadd'] = pd.to_datetime(df['dtadd']).dt.date
    df = df.groupby(by='dtadd', as_index=False, sort=False)['meterno'].count()
    df = px.bar(df, x=df.dtadd, y=df.meterno,
                title=f'Telcos Daily Overall Trend. Daily Target-{daily_target} Inspections', text_auto=True,
                text=df.meterno)
    df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

    county = county.groupby(by='county__name', as_index=False)['meterno'].count().sort_values(by='meterno',
                                                                                              ascending=False)
    county = px.bar(county, x=county.county__name, y=county.meterno, title='Telcos Overall County Achievement',
                    text_auto=True, text=county.meterno)
    county = json.dumps(county, cls=plotly.utils.PlotlyJSONEncoder)

    def resolution():
        analytics = County.objects.all().select_related('county').values('name').annotate(
            target=Count('telcos_inspection',
                         filter=(Q(telcos_inspection__units__gte=F('telcos_inspection__telcos__timesonefive')))),
            achievement=Count('telcos_inspection', filter=(
                Q(telcos_inspection__incms=True, telcos_inspection__telcos__telcos_type='safaricom'))),

        ).order_by('name')
        analytics = read_frame(analytics)

        fig = px.bar(
            data_frame=analytics,
            x="name",
            y=["target", "achievement"],
            opacity=0.9,
            orientation="v",

        )

        # Change the bar mode
        fig.update_layout(barmode='group')
        fig.update_layout(
            title_text='Accounts > 1.5 x 6 Months Avg Consumption That have been resolved.')
        fig.update_traces(
            texttemplate='%{y}<br>',  # use '%{text}' to show only percentage
            textposition='outside'
        )

        td = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return td

    def todays_achievemnt():
        today = date.today()
        todays = Telcos.filter(dtadd__date=today).values('meterno', 'county__name', 'county__telcos_target', 'dtadd')
        county_today = read_frame(todays)
        count_county_today = read_frame(todays).shape[0]
        count_county_total = read_frame(Target).shape[0]
        per = "{:0.2f}".format((count_county_today / daily_target) * 100)
        # county_today['dtadd'] = pd.to_datetime(county_today['dtadd']).dt.date
        county_today = county_today.groupby(by=['county__name', 'county__telcos_target'], as_index=False)[
            'meterno'].count().sort_values(
            by='meterno', ascending=False)

        fig = go.Figure(data=[
            go.Bar(name='Target', x=county_today.county__name, y=county_today.county__telcos_target),
            go.Bar(name='Achievement', x=county_today.county__name, y=county_today.meterno)
        ])
        # Change the bar mode
        fig.update_layout(barmode='group')
        fig.update_layout(
            title_text=f'Telcos Today"s {today} Achievement-{count_county_today} Inspections. {per}% Achievement')
        fig.update_traces(
            texttemplate='%{y}<br>',  # use '%{text}' to show only percentage
            textposition='outside'
        )
        td = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return td

    def overall_achievemnt():

        todays = Telcos.values('meterno', 'county__name', 'county__telcos_target_overall', 'dtadd')
        county_today = read_frame(todays)
        count_county_today = read_frame(todays).shape[0]
        count_county_total = read_frame(Target).shape[0]
        per = "{:0.2f}".format((count_county_today / overall_target) * 100)
        # county_today['dtadd'] = pd.to_datetime(county_today['dtadd']).dt.date
        county_today = county_today.groupby(by=['county__name', 'county__telcos_target_overall'], as_index=False)[
            'meterno'].count().sort_values(
            by='meterno', ascending=False)

        fig = go.Figure(data=[
            go.Bar(name='Target', x=county_today.county__name, y=county_today.county__telcos_target_overall),
            go.Bar(name='Achievement', x=county_today.county__name, y=county_today.meterno)
        ])
        # Change the bar mode
        fig.update_layout(barmode='group')
        fig.update_layout(
            title_text=f'Telcos Overall {today} Achievement-{count_county_today} Inspections. {per}% Achievement')
        fig.update_traces(
            texttemplate='%{y}<br>',  # use '%{text}' to show only percentage
            textposition='outside'
        )
        td = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return td

    metering_status = read_frame(meteringstatus_telcos)
    metering_status = metering_status.groupby(by='meteringstatus', as_index=False)['meterno'].count()
    values = metering_status.meteringstatus
    names = metering_status.meterno
    metering_status = px.pie(metering_status, values=names, names=values, title='Telcos Metering Status')
    metering_status = json.dumps(metering_status, cls=plotly.utils.PlotlyJSONEncoder)

    installation_status = read_frame(installationstatus_telcos)
    installation_status = installation_status.groupby(by='installationstatus', as_index=False)['meterno'].count()
    values = installation_status.installationstatus
    names = installation_status.meterno
    installation_status = px.pie(installation_status, values=names, names=values,
                                 title='Telcos Installation Status')
    installation_status = json.dumps(installation_status, cls=plotly.utils.PlotlyJSONEncoder)

    today = date.today()
    todays = Telcos.filter(dtadd__date=today).values('meterno', 'county__name', 'dtadd')
    if todays:
        county_today = read_frame(todays)
        count_county_today = read_frame(todays).shape[0]
        # county_today['dtadd'] = pd.to_datetime(county_today['dtadd']).dt.date
        county_today = county_today.groupby(by='county__name', as_index=False)['meterno'].count().sort_values(
            by='meterno', ascending=False)
        county_today = px.bar(county_today, x=county_today.county__name, y=county_today.meterno,
                              title=f'Telcos Todays {today} Achievement-{count_county_today} Inspections',
                              text_auto=True, text=county_today.meterno)
        county_today = json.dumps(county_today, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        county_today = px.bar(title=f'Telcos Todays {today} County Achievement', text_auto=True)

    context = {
        'df': df,
        'county': overall_achievemnt(),
        'metering_status': metering_status,
        'installation_status': installation_status,
        'overall': read_frame(Telcos).shape[0],
        'overall_target': read_frame(Target).shape[0],
        'achievement': "{:0.2f}".format((read_frame(Telcos).shape[0] / read_frame(Target).shape[0]) * 100),
        'county_today': todays_achievemnt(),
        'county_overall': overall_achievemnt(),
        'daily_target': daily_target,
        'per_achievement': "{:0.2f}".format((todays.count() / daily_target) * 100),
        'prev_per_achievement': "{:0.2f}".format((previous.count() / daily_target) * 100),
        'pending_rebill': rebill.count(),
        'est_units': rebill.aggregate(Sum('units')),
        'per_toberebilled': "{:0.2f}".format((rebill.count() / Telcos.count()) * 100),
        'rebilled_accs': rebilled.count(),
        'rebilled_units': rebilled.aggregate(Sum('billed')),
        'county_rebilling': resolution(),

    }
    return render(request, 'postpaid/telcos_dashboard.html', context=context)


@login_required(login_url="login")
def telcos_dashboard_atcc(request):
    Telcos = Telcos_inspection.objects.filter(telcos__telcos_type='atc')
    Target = Telcos_target.objects.filter(telcos_type='atc')
    county_telcos = Telcos.values('meterno', 'county__name')
    meteringstatus_telcos = Telcos.values('meterno', 'meteringstatus')
    installationstatus_telcos = Telcos.values('meterno', 'installationstatus')
    daily_target = County.objects.aggregate(total_target=Sum('telcos_target'))['total_target']
    overall_target = County.objects.aggregate(total_target_o=Sum('telcos_target_overall'))['total_target_o']

    yesterday = date.today() - timedelta(days=1)
    today = date.today()
    todays = Telcos.filter(dtadd__date=today).values('meterno', 'county__name', 'county__telcos_target', 'dtadd')
    previous = Telcos.filter(dtadd__date=yesterday).values('meterno', 'county__name', 'county__telcos_target', 'dtadd')

    rebill = Telcos.filter(units__gte=F('telcos__timesonefive') or ~Q(meteringstatus__in="okay"))

    rebilled = Telcos.filter(incms=True)

    d = rebill.aggregate(Sum('units'))

    rebilled_units = rebilled.aggregate(Sum('billed'))

    analytics = County.objects.all().select_related('county').values('name').annotate(
        target=Count('telcos_inspection',
                     filter=(Q(telcos_inspection__units__gte=F('telcos_inspection__telcos__timesonefive')))),
        achievement=Count('telcos_inspection', filter=(Q(telcos_inspection__incms=True))),

    ).order_by('name')

    for g in analytics:
        p = g.get('name')
        print(p)

    county_today = []

    df = read_frame(Telcos)
    county = read_frame(county_telcos)
    df['dtadd'] = pd.to_datetime(df['dtadd']).dt.date
    df = df.groupby(by='dtadd', as_index=False, sort=False)['meterno'].count()
    df = px.bar(df, x=df.dtadd, y=df.meterno,
                title=f'Telcos Daily Overall Trend. Daily Target-{daily_target} Inspections', text_auto=True,
                text=df.meterno)
    df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

    county = county.groupby(by='county__name', as_index=False)['meterno'].count().sort_values(by='meterno',
                                                                                              ascending=False)
    county = px.bar(county, x=county.county__name, y=county.meterno, title='Telcos Overall County Achievement',
                    text_auto=True, text=county.meterno)
    county = json.dumps(county, cls=plotly.utils.PlotlyJSONEncoder)

    metering_status = read_frame(meteringstatus_telcos)
    metering_status = metering_status.groupby(by='meteringstatus', as_index=False)['meterno'].count()
    values = metering_status.meteringstatus
    names = metering_status.meterno
    metering_status = px.pie(metering_status, values=names, names=values, title='Telcos Metering Status')
    metering_status = json.dumps(metering_status, cls=plotly.utils.PlotlyJSONEncoder)

    installation_status = read_frame(installationstatus_telcos)
    installation_status = installation_status.groupby(by='installationstatus', as_index=False)['meterno'].count()
    values = installation_status.installationstatus
    names = installation_status.meterno
    installation_status = px.pie(installation_status, values=names, names=values,
                                 title='Telcos Installation Status')
    installation_status = json.dumps(installation_status, cls=plotly.utils.PlotlyJSONEncoder)

    def todays_achievemnt():

        county_today = read_frame(todays)
        count_county_today = read_frame(todays).shape[0]
        count_county_total = read_frame(Target).shape[0]
        per = "{:0.2f}".format((count_county_today / daily_target) * 100)
        # county_today['dtadd'] = pd.to_datetime(county_today['dtadd']).dt.date
        county_today = county_today.groupby(by=['county__name', 'county__telcos_target'], as_index=False)[
            'meterno'].count().sort_values(
            by='meterno', ascending=False)

        fig = go.Figure(data=[
            go.Bar(name='Target', x=county_today.county__name, y=county_today.county__telcos_target),
            go.Bar(name='Achievement', x=county_today.county__name, y=county_today.meterno)
        ])
        # Change the bar mode
        fig.update_layout(barmode='group')
        fig.update_layout(
            title_text=f'Telcos Today"s {today} Achievement-{count_county_today} Inspections. {per}% Achievement')
        fig.update_traces(
            texttemplate='%{y}<br>',  # use '%{text}' to show only percentage
            textposition='outside'
        )
        td = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return td

    def resolution():
        analytics = County.objects.all().select_related('county').values('name').annotate(
            target=Count('telcos_inspection',
                         filter=(Q(telcos_inspection__units__gte=F('telcos_inspection__telcos__timesonefive')))),
            achievement=Count('telcos_inspection',
                              filter=(Q(telcos_inspection__incms=True, telcos_inspection__telcos__telcos_type='atc'))),
        ).order_by('name')
        analytics = read_frame(analytics)

        fig = px.bar(
            data_frame=analytics,
            x="name",
            y=["target", "achievement"],
            opacity=0.9,
            orientation="v",

        )

        # Change the bar mode
        fig.update_layout(barmode='group')
        fig.update_layout(
            title_text='Accounts > 1.5 x 6 Months Avg Consumption That have been resolved.')
        fig.update_traces(
            texttemplate='%{y}<br>',  # use '%{text}' to show only percentage
            textposition='outside'
        )

        td = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return td

    def overall_achievemnt():

        todays = Telcos.values('meterno', 'county__name', 'county__atc', 'dtadd')
        county_today = read_frame(todays)
        count_county_today = read_frame(todays).shape[0]
        count_county_total = read_frame(Target).shape[0]
        per = "{:0.2f}".format((count_county_today / overall_target) * 100)
        # county_today['dtadd'] = pd.to_datetime(county_today['dtadd']).dt.date
        county_today = county_today.groupby(by=['county__name', 'county__atc'], as_index=False)[
            'meterno'].count().sort_values(
            by='meterno', ascending=False)

        fig = go.Figure(data=[
            go.Bar(name='Target', x=county_today.county__name, y=county_today.county__atc),
            go.Bar(name='Achievement', x=county_today.county__name, y=county_today.meterno)
        ])
        # Change the bar mode
        fig.update_layout(barmode='group')
        fig.update_layout(
            title_text=f'Telcos Overall {today} Achievement-{count_county_today} Inspections. {per}% Achievement')
        fig.update_traces(
            texttemplate='%{y}<br>',  # use '%{text}' to show only percentage
            textposition='outside'
        )
        td = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return td

    today = date.today()
    todays = Telcos.filter(dtadd__date=today).values('meterno', 'county__name', 'county__telcos_target', 'dtadd')
    if todays:
        county_today = read_frame(todays)
        count_county_today = read_frame(todays).shape[0]
        # county_today['dtadd'] = pd.to_datetime(county_today['dtadd']).dt.date
        county_today = county_today.groupby(by=['county__name', 'county__telcos_target'], as_index=False)[
            'meterno'].count().sort_values(
            by='meterno', ascending=False)

        county_today = px.bar(county_today, x=county_today.county__name, y=county_today.meterno,
                              title=f'Three Phase Todays {today} Achievement-{count_county_today} Inspections',
                              text_auto=True, text=county_today.meterno)
        # county_today = json.dumps(county_today, cls=plotly.utils.PlotlyJSONEncoder)

        # months = [county_today.county__name]

        county_today = json.dumps(county_today, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        county_today = px.bar(title=f'Three Phase Todays {today} County Achievement', text_auto=True)

    context = {
        'df': df,
        'county': overall_achievemnt(),
        'metering_status': metering_status,
        'installation_status': installation_status,
        'overall': read_frame(Telcos).shape[0],
        'overall_target': read_frame(Target).shape[0],
        'achievement': "{:0.2f}".format((read_frame(Telcos).shape[0] / read_frame(Target).shape[0]) * 100),
        'county_today': todays_achievemnt(),
        'county_overall': overall_achievemnt(),
        'daily_target': daily_target,
        'per_achievement': "{:0.2f}".format((todays.count() / daily_target) * 100),
        'prev_per_achievement': "{:0.2f}".format((previous.count() / daily_target) * 100),
        'pending_rebill': rebill.count(),
        'est_units': rebill.aggregate(Sum('units')),
        'per_toberebilled': "{:0.2f}".format((rebill.count() / Telcos.count()) * 100),
        'rebilled_accs': rebilled.count(),
        'rebilled_units': rebilled.aggregate(Sum('billed')),
        'county_rebilling': resolution(),

    }
    return render(request, 'postpaid/telcos_dashboard_atc.html', context=context)


@login_required(login_url="login")
def telcos_inspector_analytics(request):
    if request.user.is_authenticated:
        user = request.user
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)

    inspectors = UserProfile.objects.filter(campaign='telcos').values('user_id__stid', 'user_id__name',
                                                                      'user_id__mobile', 'county__name').annotate(
        the_count=Count('telcos'),
        today=Count('telcos', filter=Q(telcos__dtadd__date=today)),
        yesturday=Count('telcos', filter=Q(telcos__dtadd__date=yesterday)),
        yesturday_1=Count('telcos', filter=Q(telcos__dtadd__date=yesterday_1)),
        yesturday_2=Count('telcos', filter=Q(telcos__dtadd__date=yesterday_2)),
    ).order_by('county__name')

    # inspectors = Threephase_inspection.objects.all().select_related('inspector').values('inspector__user_id__stid','inspector__user_id__name','inspector__county__name','inspector__user_id__mobile').annotate(
    #      the_count=Count('id'),
    #      today=Count('id',filter=Q(dtadd__date=today)),
    #      yesturday=Count('id',filter=Q(dtadd__date=yesterday)),
    #      yesturday_1=Count('id',filter=Q(dtadd__date=yesterday_1)),
    #      yesturday_2=Count('id',filter=Q(dtadd__date=yesterday_2)),
    #      #yesturday_2_d=Count('id',filter=Q(dtadd__date=yesterday_2)),
    #      #yesturday_3_d=Count('id',filter=Q(dtadd__date=yesterday_3)),
    #     ).order_by('inspector__county__name')

    context = {
        'analytics': inspectors,
        'nbar': 'analytics',
        'yesterday_1': yesterday_1,
        'yesterday_2': yesterday_2,
        # 'county' : county
    }
    return render(request, 'postpaid/telcos_user_analytics.html', context)


@login_required(login_url="login")
def search_meter_telcos_resolved(request):
    if request.user.is_authenticated:
        user = request.user.userprofile
    meters_list = Telcos_inspection.objects.all()
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/viewtelcos.html', context)


@login_required(login_url="login")
def telcos_tobe_billed(request):
    if request.user.is_authenticated:
        user = request.user.userprofile
    meters = Telcos_inspection.objects.filter(incms=False)
    meters = meters.filter(units__gte=F('telcos__timesonefive') or ~Q(meteringstatus__in="okay")).order_by('-dtadd')
    paginator = Paginator(meters, 30)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_count,
        'nbar': 'myuploads'}
    return render(request, 'postpaid/telcos_priority.html', context)


@login_required(login_url="login")
def telcos_anomolous(request):
    if request.user.is_authenticated:
        user = request.user.userprofile
    meters = Telcos_inspection.objects.exclude(meteringstatus="okay").order_by('-dtadd')
    meters_pending = meters.filter(nextlevel=False)
    paginator = Paginator(meters_pending, 30)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_count = meters_pending.count()
    county_telcos = meters_pending.values('meterno', 'county__name')

    def pending():
        df = read_frame(meters_pending)
        county = read_frame(county_telcos)

        df = df.groupby(by='county', as_index=False, sort=False)['meterno'].count()
        df = px.bar(df, x=df.county, y=df.meterno,
                    title='Pending Anomalous Accounts', text_auto=True,
                    text=df.meterno)
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    context = {
        'meters': paged_uploads,
        'meters_count': meters_count,
        'nbar': 'myuploads',
        'df': pending()
    }
    return render(request, 'postpaid/telcos_anomolous.html', context)


@login_required(login_url="login")
def telcos_anomalous_export_uploads(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

    meters = Telcos_inspection.objects.exclude(meteringstatus="okay").order_by('-dtadd')
    meters = meters.filter(nextlevel=False)

    writer.writerow(
        ['COUNTY', 'CLIENT', 'SITEID', 'SITE NAME', 'METER NUMBER', 'ACCOUNT NUMBER', 'PHASE', 'METERING STATUS',
         'INSTALLATION STATUS', 'FAULTY', 'TAMPERED', 'BYPASSED', 'NOTOKAY STATUS', 'READING', 'INSPECTOR',
         'DATE INSPECTED', 'COMMENT', 'X', 'Y', 'IMAGE_ADD', 'DI_ADD', 'SYSTEM READING'])
    for meter in meters:
        writer.writerow(
            [meter.county, meter.telcos.telcos_type, meter.siteid, meter.sitename, meter.meterno, meter.accountno,
             meter.phase, meter.meteringstatus, meter.installationstatus, meter.faultystatus, meter.tamperedstatus,
             meter.bypassstatus, meter.notokaystatus, meter.reading, meter.inspector, meter.dtadd, meter.comment,
             meter.x, meter.y, meter.telcosimg, meter.diimg, meter.telcos.system_reading])

    response['Content-Disposition'] = 'attachment; filename="TELCOS ANOMOULOUS PENDING RESOLUTION.csv" '
    return response


@login_required(login_url="login")
def telcos_export_uploads_tobebilled(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    meters = Telcos_inspection.objects.filter(incms=False)
    meters = meters.filter(units__gte=F('telcos__timesonefive') or ~Q(meteringstatus__in="okay"))
    meters = meters.filter(dtadd__gt=datetime.datetime.today() - datetime.timedelta(days=28)).order_by('-dtadd')

    writer.writerow(['COUNTY', 'SITEID', 'SITE NAME', 'METER NUMBER', 'ACCOUNT NUMBER', 'PHASE', 'METERING STATUS',
                     'INSTALLATION STATUS', 'FAULTY', 'TAMPERED', 'BYPASSED', 'NOTOKAY STATUS', 'READING', 'INSPECTOR',
                     'DATE INSPECTED', 'COMMENT', 'X', 'Y', 'IMAGE_ADD', 'DI_ADD', 'SYSTEM READING'])
    for meter in meters:
        writer.writerow([meter.county, meter.siteid, meter.sitename, meter.meterno, meter.accountno, meter.phase,
                         meter.meteringstatus, meter.installationstatus, meter.faultystatus, meter.tamperedstatus,
                         meter.bypassstatus, meter.notokaystatus, meter.reading, meter.inspector, meter.dtadd,
                         meter.comment, meter.x, meter.y, meter.telcosimg, meter.diimg, meter.telcos.system_reading])

    response['Content-Disposition'] = 'attachment; filename="KAGUA TELCOS  CONNECTION TOBEREBILLED.csv" '
    return response


@login_required(login_url="login")
def publiclighting_target(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters = Public_lighting_target.objects.filter(status=False)
    paginator = Paginator(meters, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_pending = meters.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_pending,
        'nbar': 'alluploads'}
    return render(request, 'postpaid/publiclighting/publiclighting_target.html', context)


@login_required(login_url='login')
def inspect_publiclighting(request, pk):
    # userprofile = get_object_or_404(UserProfile, user=request.user)
    img = Public_lighting_target.objects.get(id=pk)

    campaign = request.user.userprofile.campaign

    if campaign not in (
            "network_technician",
            "network_supervisors",
            "network_region",
            "contractor_safaricom",
            "contractor_allandick",
            "other",
    ):

        if request.method == 'POST':
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = PubliclightingForm(request.POST, request.FILES, instance=img)

            if m_form.is_valid():

                # if m_form.cleaned_data['meterno'] is None:
                # messages.success(request, 'You need to take the Cordinates.')
                # return redirect('postpaid:mythreephase-list')
                #

                zerov = m_form.save(commit=False)
                resolution = Public_lighting_inspection_25()
                resolution.meterno = m_form.cleaned_data['meterno']
                resolution.accountno = m_form.cleaned_data['accountno']
                resolution.meteringstatus = m_form.cleaned_data['meteringstatus']
                resolution.installationstatus = m_form.cleaned_data['installationstatus']
                resolution.faultystatus = m_form.cleaned_data['faultystatus']
                resolution.tamperedstatus = m_form.cleaned_data['tamperedstatus']
                resolution.bypassstatus = m_form.cleaned_data['bypassstatus']
                resolution.notokaystatus = m_form.cleaned_data['notokaystatus']
                resolution.public_l_img = m_form.cleaned_data['public_l_img']
                resolution.reading = m_form.cleaned_data['reading']
                resolution.meter_type = m_form.cleaned_data['meter_type']
                resolution.metertype = m_form.cleaned_data['metertype']
                resolution.phase = m_form.cleaned_data['phase']
                resolution.comment = m_form.cleaned_data['comment']
                resolution.x = m_form.cleaned_data['x']
                resolution.y = m_form.cleaned_data['y']
                resolution.meter_readable = m_form.cleaned_data['meter_readable']
                resolution.target = img
                resolution.county = request.user.userprofile.county
                resolution.region = request.user.userprofile.region
                resolution.inspector = request.user.userprofile
                resolution.system_reading = img.system_reading
                resolution.consumption = zerov.consumption
                if resolution.meter_readable == 'yes':
                    resolution.units = resolution.reading - img.system_reading
                else:
                    resolution.units = 0

                resolution.save()
                zerov.status = True
                zerov.save()
                messages.success(request, 'Your Inspection Has been successfully saved.')
                return redirect('postpaid:mypubliclighting-list')
            else:

                print("invalid form")
                print(m_form.errors)
        else:
            # user_form = UserForm(instance=request.user)

            m_form = PubliclightingForm(instance=img)
        context = {'form': m_form, }
    else:
        messages.error(request, 'You are not configured to run on this campaign.')
        return redirect('main:my-dashboard')

    return render(request, 'postpaid/publiclighting/publiclighting_inspection.html', context)


@login_required(login_url="login")
def mypubliclighting_list(request):
    if request.user.is_authenticated:
        user = request.user.userprofile
        user2 = request.user

    meters = Public_lighting_inspection_25.objects.filter(inspector=user).order_by('-dtadd')


    paginator = Paginator(meters, 30)

    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    meters_count = meters.count()

    context = {
        'meters': paged_uploads,

        'meters_count': meters_count,
        'nbar': 'myuploads'}
    return render(request, 'postpaid/publiclighting/mypubliclighting_list.html', context)


@login_required(login_url="login")
def viewpubliclighting(request):
    # if request.user.is_authenticated:
    #     user = request.user.userprofile.county
    meters = Public_lighting_inspection_25.objects.select_related('county', 'target').order_by('-dtadd')
    paginator = Paginator(meters, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    # meters_pending = meters.count()

    context = {
        'meters': paged_uploads,
        # 'meters_count' : meters_pending,
    }
    return render(request, 'postpaid/publiclighting/viewpubliclighting.html', context)

@cache_page(60 * 15)
@login_required(login_url="login")
def publiclighting_dashboard(request):
    overall_inspected_t = Public_lighting_inspection_25.objects.select_related(
        "county", "region"
    ).values('meterno', 'meteringstatus', 'dtadd', 'county', 'region','id')
    overall_not_okay = overall_inspected_t.exclude(meteringstatus='okay')

    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    def count_business_days(start_date, end_date):
        # Define a list of weekend days (Saturday and Sunday)
        weekend_days = [5, 6]  # Monday is 0 and Sunday is 6
        # Initialize a counter for business days
        business_days = 0
        target = 0
        # Iterate through each day in the date range
        current_date = start_date
        while current_date <= end_date:
            # Check if the current day is a weekend day
            if current_date.weekday() not in weekend_days:
                business_days += 1
                target += 1496
            # Move to the next day
            current_date += datetime.timedelta(days=1)
        return business_days, target

    # Test the function
    start_date = datetime.date(2025, 3, 20)
    end_date = datetime.date.today()

    result = count_business_days(start_date, end_date)

    def target_achievement():
        t_a = overall_inspected_t.count()
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Planned ToDate",
                    x=["Planned ToDate"],
                    y=[result[1]],
                ),
                go.Bar(name="Achieved ToDate", x=["Achieved ToDate"], y=[t_a]),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Overall Target vs Achievement",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="No Of Inspections",
                titlefont_size=16,
                tickfont_size=14,
            ),
            xaxis=dict(
                title="Year(2025)",
            ),
            legend=dict(
                bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
            ),
            barmode="group",
            bargap=0.15,  # gap between bars of adjacent location coordinates.
            bargroupgap=0.1,  # gap between bars of the same location coordinate.
        )
        fig_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return fig_plot

    def metering_status():
        df = read_frame(overall_inspected_t)
        df = df.groupby(by="meteringstatus", as_index=False, sort=False)[
            "meterno"
        ].count()
        values = df.meteringstatus
        names = df.meterno
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Inspection Metering Status",
            labels={
                "meterno": "Meter Count",
                "meteringstatus": "Metering Status",
            },
        )
        df.update_traces(textposition='inside', textinfo='percent+label')
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    def metering_status_notokay():
        df = read_frame(overall_not_okay)
        df = df.groupby(by="meteringstatus", as_index=False, sort=False)[
            "meterno"
        ].count()
        values = df.meteringstatus
        names = df.meterno
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Metering Status Not Okay",
            labels={
                "meterno": "Meter Count",
                "meteringstatus": "Metering Status",
            },
        )
        df.update_traces(textposition='inside', textinfo='percent+label')
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    def daily_trend():
        df = read_frame(overall_inspected_t)
        df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
        df = df.groupby(by="dtadd", as_index=False, sort=False)["id"].count()
        df = px.bar(
            df,
            x=df.dtadd,
            y=df.id,
            title=f"Daily Overall Inspections.Daily Target = {1, 496}",
            text_auto=True,
            text=df.id,
            labels={"id": "Meter Count", "dtadd": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    regional_analytics = (
        Region.objects.select_related("region_public_lighting")
        .values("name")  # select_related('dc_region')
        .annotate(
            hc_target_acs=(Sum("publiclighting_target", distinct=True)),
            dc_daily_target=(Sum("publiclighting_daily_target", distinct=True)),
            hc_inspected=(Count("region_public_lighting", distinct=True)),
            hc_insp_faulty=(
                Count(
                    "region_public_lighting",
                    distinct=True,
                    filter=Q(region_public_lighting__meteringstatus="faulty"),
                )
            ),
            dc_insp_tampered=(
                Count(
                    "region_public_lighting",
                    distinct=True,
                    filter=Q(region_public_lighting__meteringstatus="tampered"),
                )
            ),
            hc_insp_bypassed=(
                Count(
                    "region_public_lighting",
                    distinct=True,
                    filter=Q(region_public_lighting__meteringstatus="bypassed"),
                )
            ),
            hc_insp_nometer=(
                Count(
                    "region_public_lighting",
                    distinct=True,
                    filter=Q(region_public_lighting__meteringstatus="NO METER"),
                )
            ),
            hc_today=Count(
                "region_public_lighting",
                distinct=True,
                filter=Q(region_public_lighting__dtadd__date=today),
            ),
            hc_yesturday=Count(
                "region_public_lighting",
                distinct=True,
                filter=Q(region_public_lighting__dtadd__date=yesterday),
            ),
            hc_yesturday_1=Count(
                "region_public_lighting",
                distinct=True,
                filter=Q(region_public_lighting__dtadd__date=yesterday_1),
            ),
            hc_yesturday_2=Count(
                "region_public_lighting",
                distinct=True,
                filter=Q(region_public_lighting__dtadd__date=yesterday_2),
            ),
            hc_yesturday_3=Count(
                "region_public_lighting",
                distinct=True,
                filter=Q(region_public_lighting__dtadd__date=yesterday_3),
            ),
        )
        .order_by()
    )
    county_analytics = (
        County.objects.select_related("county_public_lighting")
        .values("name","region")  # select_related('dc_region')
        .annotate(
            hc_target_acs=(Sum("publiclighting_target_overall", distinct=True)),
            dc_daily_target=(Sum("publiclighting_target", distinct=True)),
            hc_inspected=(Count("county_public_lighting", distinct=True)),
            hc_insp_faulty=(
                Count(
                    "county_public_lighting",
                    distinct=True,
                    filter=Q(county_public_lighting__meteringstatus="faulty"),
                )
            ),
            dc_insp_tampered=(
                Count(
                    "county_public_lighting",
                    distinct=True,
                    filter=Q(county_public_lighting__meteringstatus="tampered"),
                )
            ),
            hc_insp_bypassed=(
                Count(
                    "county_public_lighting",
                    distinct=True,
                    filter=Q(county_public_lighting__meteringstatus="bypassed"),
                )
            ),
            hc_insp_nometer=(
                Count(
                    "county_public_lighting",
                    distinct=True,
                    filter=Q(county_public_lighting__meteringstatus="NO METER"),
                )
            ),
            hc_today=Count(
                "county_public_lighting",
                distinct=True,
                filter=Q(county_public_lighting__dtadd__date=today),
            ),
            hc_yesturday=Count(
                "county_public_lighting",
                distinct=True,
                filter=Q(county_public_lighting__dtadd__date=yesterday),
            ),
            hc_yesturday_1=Count(
                "county_public_lighting",
                distinct=True,
                filter=Q(county_public_lighting__dtadd__date=yesterday_1),
            ),
            hc_yesturday_2=Count(
                "county_public_lighting",
                distinct=True,
                filter=Q(county_public_lighting__dtadd__date=yesterday_2),
            ),
            hc_yesturday_3=Count(
                "county_public_lighting",
                distinct=True,
                filter=Q(county_public_lighting__dtadd__date=yesterday_3),
            ),
        )
        .order_by('region')
    )

    context = {
        'target_achievement': target_achievement(),
        'overall_inspected_t' : f' {"{:,.0f}".format(overall_inspected_t.count())}',
        'metering_status' : metering_status(),
        'metering_status_notokay' : metering_status_notokay(),
        'daily_trend' : daily_trend(),
        'regional_analytics' : regional_analytics,
        'county_analytics': county_analytics,
        'yesterday': yesterday,
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,
    }

    return render(request, 'postpaid/publiclighting/publiclighting_dashboard.html', context=context)


@login_required(login_url="login")
def publiclighting_search_meter(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters_list = Public_lighting_target.objects.filter(status=False)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/publiclighting/publiclighting_target.html', context)


@login_required(login_url="login")
def search_meter_publiclighting_resolved(request):
    if request.user.is_authenticated:
        user = request.user.userprofile
    meters_list = Public_lighting_inspection_25.objects.all()
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/publiclighting/viewpubliclighting.html', context)


@login_required(login_url="login")
def viewinspected(request, pk):
    meter = Public_lighting_inspection_25.objects.get(id=pk)

    context = {
        'meter': meter,

    }
    return render(request, 'postpaid/publiclighting/viewinspected.html', context)


@login_required(login_url="login")
def publiclighting_inspector_analytics(request):
    county = request.user.userprofile.region
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    inspectors = Public_lighting_inspection_25.objects.select_related('inspector').values('inspector__county__name',
                                                                                  'inspector__user_id__stid',
                                                                                  'inspector__user_id__name',
                                                                                  'inspector__user_id__mobile').filter(
        region=county).annotate(
        the_count=Count("inspector"),
        today=Count("inspector", filter=Q(dtadd__date=today)),
        yesturday=Count(
            "inspector", filter=Q(dtadd__date=yesterday)
        ),
        yesturday_1=Count(
            "inspector", filter=Q(dtadd__date=yesterday_1)
        ),
        yesturday_2=Count(
            "inspector", filter=Q(dtadd__date=yesterday_2)
        ),
        yesturday_3=Count(
            "inspector", filter=Q(dtadd__date=yesterday_3)
        ),
    ).order_by("inspector__county__name")


    context = {
        'analytics': inspectors,
        'nbar': 'analytics',
        'yesterday_1': yesterday_1,
        'yesterday_2': yesterday_2,
        # 'county' : county
    }
    return render(request, 'postpaid/publiclighting/publiclighting_user_analytics.html', context)


@login_required(login_url="login")
def publiclighting_direct(request):
    campaign = request.user.userprofile.campaign

    if campaign not in (
            "network_technician",
            "network_supervisors",
            "network_region",
            "contractor_safaricom",
            "contractor_allandick",
            "other",
    ):

        if request.method == 'POST':
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = Publiclighting_direcForm(request.POST, request.FILES)

            if m_form.is_valid():

                # if m_form.cleaned_data['meterno'] is None:
                # messages.success(request, 'You need to take the Cordinates.')
                # return redirect('postpaid:mythreephase-list')
                #

                resolution = m_form.save(commit=False)
                resolution.meterno = m_form.cleaned_data['meterno']
                resolution.accountno = m_form.cleaned_data['accountno']
                resolution.meteringstatus = 'NO METER'
                resolution.installationstatus = 'NO METER'
                resolution.faultystatus = 'NO METER'
                resolution.tamperedstatus = 'NO METER'
                resolution.bypassstatus = 'NO METER'
                resolution.notokaystatus = 'NO METER'
                resolution.public_l_img = m_form.cleaned_data['public_l_img']
                resolution.meter_readable = 'no'
                resolution.reading = 0
                resolution.meter_type = 'NO METER'
                resolution.metertype = 'NO METER'
                resolution.phase = 'NO METER'
                resolution.comment = m_form.cleaned_data['comment']
                resolution.x = m_form.cleaned_data['x']
                resolution.y = m_form.cleaned_data['y']
                resolution.county = request.user.userprofile.county
                resolution.region = request.user.userprofile.region
                resolution.inspector = request.user.userprofile
                resolution.system_reading = 0
                resolution.consumption = 0
                resolution.units = 0

                # with transaction.atomic():
                #
                #     new_target = Public_lighting_target.objects.create(id=time.time(), meterno=resolution.meterno,
                #                                                        accountno=resolution.accountno,
                #                                                        customer='COUNTY GOVT',
                #                                                        supplylocation=f'{resolution.y},{resolution.x}',
                #                                                        county=resolution.county,
                #                                                        region=request.user.userprofile.region,
                #                                                        status=True, system_reading=0, consumption=0)
                #     new_target.save()
                #
                #     resolution.target = new_target

                resolution.save()

                messages.success(request, 'Your Inspection Has been successfully saved.')
                return redirect('postpaid:mypubliclighting-list')
            else:

                messages.error(request, 'There was an error in submitting your inspection.')
                print('invalid form')
                print(m_form.errors)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = Publiclighting_direcForm()
        context = {'form': m_form, }
    else:
        messages.error(request, 'You are not configured to run on this campaign.')
        return redirect('main:my-dashboard')

    # if request.method == 'POST':
    #     form = Public_lightint_direct_supplyForm(request.POST)
    #
    #     if form.is_valid():
    #         regis = form.save(commit=False)
    #         regis.accountno = form.cleaned_data['accountno']
    #         regis.installationstatus = form.cleaned_data['installationstatus']
    #         regis.notokaystatus = form.cleaned_data['notokaystatus']
    #         regis.location = form.cleaned_data['location']
    #         regis.notokaystatus = form.cleaned_data['notokaystatus']
    #         regis.x = form.cleaned_data['x']
    #         regis.y = form.cleaned_data['y']
    #         regis.county = request.user.userprofile.county
    #         regis.region = request.user.userprofile.region
    #         regis.inspector = request.user
    #
    #         regis.save()
    #         messages.success(request, 'The Streetlight Direct Inspection saved successfully.')
    #         return redirect('postpaid:mypubliclighting-list')
    #     else:
    #         print('invalid form')
    #         print(form.errors)
    # else:
    #     form = Public_lightint_direct_supplyForm()
    # context = {
    #     'form': form,
    #
    # }
    return render(request, 'postpaid/publiclighting/public_direct.html', context)


@login_required(login_url="login")
def exportupload_publiclighting(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

    meters = Public_lighting_inspection_25.objects.select_related('county','inspector').filter(region=request.user.userprofile.region)
    # meters =meters.filter(dtadd__gt=datetime.datetime.today()-datetime.timedelta(days=14)).order_by('-dtadd')

    writer.writerow(
        ['COUNTY', 'METER NUMBER', 'ACCOUNT NUMBER', 'PHASE', 'METERING STATUS', 'INSTALLATION STATUS', 'FAULTY',
         'TAMPERED', 'BYPASSED', 'NOTOKAY STATUS', 'READING', 'INSPECTOR', 'DATE INSPECTED', 'COMMENT', 'X', 'Y',
         'IMAGE_ADD'])
    for meter in meters:
        writer.writerow(
            [meter.county, meter.meterno, meter.accountno, meter.phase, meter.meteringstatus, meter.installationstatus,
             meter.faultystatus, meter.tamperedstatus, meter.bypassstatus, meter.notokaystatus, meter.reading,
             meter.inspector, meter.dtadd, meter.comment, meter.x, meter.y, meter.public_l_img])

    response['Content-Disposition'] = 'attachment; filename="PUBLIC LIGHTING INSPECTION.csv" '
    return response


@login_required(login_url="login")
def exportupload_publiclighting_wothoutmeter(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    meters = Public_lightint_direct_supply.objects.all()
    # meters =meters.filter(dtadd__gt=datetime.datetime.today()-datetime.timedelta(days=14)).order_by('-dtadd')

    writer.writerow(['COUNTY', 'LOCATION', 'ACCOUNT/METER NUMBER', 'INSTALLATION STATUS', 'NOTOKAY STATUS', 'INSPECTOR',
                     'DATE INSPECTED', 'COMMENT', 'X', 'Y'])
    for meter in meters:
        writer.writerow([meter.county, meter.location, meter.accountno, meter.installationstatus, meter.notokaystatus,
                         meter.inspector, meter.dtadd, meter.comment, meter.x, meter.y])

    response['Content-Disposition'] = 'attachment; filename="KAGUA PUBLIC LIGHTING NOT IN SYSTEM.csv" '
    return response


@login_required(login_url="login")
def telcos_dashboard_atc(request):
    safaricom = Telcos_target.objects.filter(telcos_type='safaricom')
    safaricom_resolved = Telcos_inspection.objects.filter(telcos__telcos_type='safaricom')
    safaricom_target = safaricom.count()
    safaricom_achieved = safaricom.filter(status=True).count()
    safaricom_per = "{:0.2f}".format((safaricom_achieved / safaricom_target) * 100)
    safaricome_resolved_ntokay = safaricom_resolved.exclude(meteringstatus='okay')
    safaricom_resolved_resolved = safaricome_resolved_ntokay.filter(nextlevel=False)

    atc = Telcos_target.objects.filter(telcos_type='atc')
    atc_resolved = Telcos_inspection.objects.filter(telcos__telcos_type='atc')
    atc_target = atc.count()
    atc_achieved = atc.filter(status=True).count()
    atc_per = "{:0.2f}".format((atc_achieved / atc_target) * 100)
    atc_resolved_ntokay = atc_resolved.exclude(meteringstatus='okay')
    atc_resolved_resolved = atc_resolved_ntokay.filter(nextlevel=False)

    atlas = Telcos_target.objects.filter(telcos_type='atlas')
    atlas_resolved = Telcos_inspection.objects.filter(telcos__telcos_type='atlas')
    atlas_target = atlas.count()
    atlas_achieved = atlas.filter(status=True).count()
    atlas_per = "{:0.2f}".format((atlas_achieved / atlas_target) * 100)
    atlas_resolved_ntokay = atlas_resolved.exclude(meteringstatus='okay')
    atlas_resolved_resolved = atlas_resolved_ntokay.filter(nextlevel=False)

    cctv = Telcos_target.objects.filter(telcos_type='cctv')
    cctv_resolved = Telcos_inspection.objects.filter(telcos__telcos_type='cctv')
    cctv_target = cctv.count()
    cctv_achieved = cctv.filter(status=True).count()
    cctv_per = "{:0.2f}".format((cctv_achieved / cctv_target) * 100)
    cctv_resolved_ntokay = cctv_resolved.exclude(meteringstatus='okay')
    cctv_resolved_resolved = cctv_resolved_ntokay.filter(nextlevel=False)

    metering_status = ['faulty', 'tampered', 'bypassed']

    telcos_analytics = Telcos_target.objects.values('region__name').annotate(
        safaricom=(Count('id', filter=Q(telcos_type='safaricom'))),
        atc=(Count('id', distinct=True, filter=Q(telcos_type='atc'))),
        atlas=(Count('id', distinct=True, filter=Q(telcos_type='atlas'))),
        cctv=(Count('id', distinct=True, filter=Q(telcos_type='cctv'))),
        # Resolved
        safaricom_resolved=(Count('id', distinct=True, filter=Q(telcos_type='safaricom', status=True))),
        atc_resolved=(Count('id', distinct=True, filter=Q(telcos_type='atc', status=True))),
        atlas_resolved=(Count('id', distinct=True, filter=Q(telcos_type='atlas', status=True))),
        cctv_resolved=(Count('id', distinct=True, filter=Q(telcos_type='cctv', status=True))),
        # # Metering status not okay
        safaricom_faulty=(Count('id', distinct=True, filter=Q(telcos_type='safaricom', status=True,
                                                              telcos_target__meteringstatus__in=metering_status))),
        atc_faulty=(Count('id', distinct=True,
                          filter=Q(telcos_type='atc', status=True, telcos_target__meteringstatus__in=metering_status))),
        atlas_faulty=(Count('id', distinct=True, filter=Q(telcos_type='atlas', status=True,
                                                          telcos_target__meteringstatus__in=metering_status))),
        cctv_faulty=(Count('id', distinct=True, filter=Q(telcos_type='cctv', status=True,
                                                         telcos_target__meteringstatus__in=metering_status))),
        # # Metering status not okay resolved
        safaricom_faulty_resolved=(Count('id', distinct=True,
                                         filter=Q(telcos_type='safaricom', status=True, telcos_target__nextlevel=False,
                                                  telcos_target__meteringstatus__in=metering_status))),
        atc_faulty_resolved=(Count('id', distinct=True,
                                   filter=Q(telcos_type='atc', status=True, telcos_target__nextlevel=False,
                                            telcos_target__meteringstatus__in=metering_status))),
        atlas_faulty_resolved=(Count('id', distinct=True,
                                     filter=Q(telcos_type='atlas', status=True, telcos_target__nextlevel=False,
                                              telcos_target__meteringstatus__in=metering_status))),
        cctv_faulty_resolved=(Count('id', distinct=True,
                                    filter=Q(telcos_type='cctv', status=True, telcos_target__nextlevel=False,
                                             telcos_target__meteringstatus__in=metering_status))),

    ).order_by('region__name')

    context = {
        'safaricom_target': safaricom_target,
        'safaricom_achieved': safaricom_achieved,
        'safaricom_per': safaricom_per,
        'safaricome_resolved_ntokay': safaricome_resolved_ntokay.count(),
        'safaricom_resolved_resolved': safaricom_resolved_resolved.count(),

        'atc_target': atc_target,
        'atc_achieved': atc_achieved,
        'atc_per': atc_per,
        'atc_resolved_ntokay': atc_resolved_ntokay.count(),
        'atc_resolved_resolved': atc_resolved_resolved.count(),

        'atlas_target': atlas_target,
        'atlas_achieved': atlas_achieved,
        'atlas_per': atlas_per,
        'atlas_resolved_ntokay': atlas_resolved_ntokay.count(),
        'atlas_resolved_resolved': atlas_resolved_resolved.count(),

        'cctv_target': cctv_target,
        'cctv_achieved': cctv_achieved,
        'cctv_per': cctv_per,
        'cctv_resolved_ntokay': cctv_resolved_ntokay.count(),
        'cctv_resolved_resolved': cctv_resolved_resolved.count(),

        # NAIROBI
        'analytics': telcos_analytics,

    }
    return render(request, 'postpaid/telcos_dashboard_atc.html', context)


@login_required(login_url="login")
def publiclighting_not_in_target(request):
    # userprofile = get_object_or_404(UserProfile, user=request.user)

    campaign = request.user.userprofile.campaign

    if campaign not in (
            "network_technician",
            "network_supervisors",
            "network_region",
            "contractor_safaricom",
            "contractor_allandick",
            "other",
    ):

        if request.method == 'POST':
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = Publiclighting_not_in_targetForm(request.POST, request.FILES)

            check = Public_lighting_inspection_25.objects.filter(meterno=request.POST['meterno'])
            if check:
                messages.error(request, 'That Meter has already been inspected.')
                return redirect('postpaid:publiclighting-target')

            if m_form.is_valid():

                # if m_form.cleaned_data['meterno'] is None:
                # messages.success(request, 'You need to take the Cordinates.')
                # return redirect('postpaid:mythreephase-list')
                #

                resolution = m_form.save(commit=False)
                resolution.meterno = m_form.cleaned_data['meterno']
                resolution.accountno = m_form.cleaned_data['accountno']
                resolution.meteringstatus = m_form.cleaned_data['meteringstatus']
                resolution.installationstatus = m_form.cleaned_data['installationstatus']
                resolution.faultystatus = m_form.cleaned_data['faultystatus']
                resolution.tamperedstatus = m_form.cleaned_data['tamperedstatus']
                resolution.bypassstatus = m_form.cleaned_data['bypassstatus']
                resolution.notokaystatus = m_form.cleaned_data['notokaystatus']
                resolution.public_l_img = m_form.cleaned_data['public_l_img']
                resolution.meter_readable = m_form.cleaned_data['meter_readable']
                resolution.reading = m_form.cleaned_data['reading']
                resolution.meter_type = m_form.cleaned_data['meter_type']
                resolution.metertype = m_form.cleaned_data['metertype']
                resolution.phase = m_form.cleaned_data['phase']
                resolution.comment = m_form.cleaned_data['comment']
                resolution.x = m_form.cleaned_data['x']
                resolution.y = m_form.cleaned_data['y']
                resolution.county = request.user.userprofile.county
                resolution.region = request.user.userprofile.region
                resolution.inspector = request.user.userprofile
                resolution.system_reading = 0
                resolution.consumption = 0
                resolution.units = 0

                with transaction.atomic():

                    new_target = Public_lighting_target.objects.create(id=time.time(), meterno=resolution.meterno,
                                                                       accountno=resolution.accountno,
                                                                       customer='COUNTY GOVT',
                                                                       supplylocation=f'{resolution.y},{resolution.x}',
                                                                       county=resolution.county,
                                                                       region=request.user.userprofile.region,
                                                                       status=True, system_reading=0, consumption=0)
                    new_target.save()

                    resolution.target = new_target

                    resolution.save()

                messages.success(request, 'Your Inspection Has been successfully saved.')
                return redirect('postpaid:mypubliclighting-list')
            else:

                messages.error(request, 'There was an error in submitting your inspection.')
                print('invalid form')
                print(m_form.errors)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = Publiclighting_not_in_targetForm()
        context = {'form': m_form, }
    else:
        messages.error(request, 'You are not configured to run on this campaign.')
        return redirect('main:my-dashboard')

    return render(request, 'postpaid/publiclighting/publiclighting_mot_in_target.html', context)


@login_required(login_url="login")
def lp_target(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters = Largepower_accounts.objects.filter(status=False)[:10]
    paginator = Paginator(meters, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_pending = meters.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_pending,
        'nbar': 'alluploads'}
    return render(request, 'postpaid/lp_target.html', context)


@login_required(login_url="login")
def lp_search_srn(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters_list = Largepower_accounts.objects.filter(status=False)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(srn__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/lp_target.html', context)


@login_required(login_url="login")
def lp_search_meterno(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters_list = Largepower_accounts.objects.filter(status=False)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/lp_target.html', context)


@login_required(login_url='login')
def inspect_lp(request, pk):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    img = Largepower_accounts.objects.get(id=pk)
    # region_users = UserProfile.objects.filter(region=userprofile.region,campaign='lp').exclude(user=request.user)

    campaign = request.user.userprofile.campaign

    if campaign == 'lpx':

        if request.method == 'POST':
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = LpForm(request.POST, request.FILES, instance=img)

            if m_form.is_valid():

                zerov = m_form.save(commit=False)
                resolution = Largepower_inspection()
                resolution.meterno = m_form.cleaned_data['meterno']
                resolution.accountno = m_form.cleaned_data['accountno']
                resolution.target = img
                resolution.x = m_form.cleaned_data['x']
                resolution.y = m_form.cleaned_data['y']
                resolution.inspector = request.user.userprofile
                resolution.smartmeter = m_form.cleaned_data['smartmeter']
                resolution.type_of_industry = m_form.cleaned_data['type_of_industry']
                resolution.meterbox_enclosure_seal_b4 = m_form.cleaned_data['meterbox_enclosure_seal_b4']
                resolution.meterbox_enclosure_seal_after = m_form.cleaned_data['meterbox_enclosure_seal_after']
                resolution.meterbox_terminal_seal_b4 = m_form.cleaned_data['meterbox_terminal_seal_b4']
                resolution.meterbox_terminal_seal_after = m_form.cleaned_data['meterbox_terminal_seal_after']
                resolution.testblock_seal_b4 = m_form.cleaned_data['testblock_seal_b4']
                resolution.testblock_seal_after = m_form.cleaned_data['testblock_seal_after']
                resolution.meterbody_seal_b4 = m_form.cleaned_data['meterbody_seal_b4']
                resolution.meterbody_seal_after = m_form.cleaned_data['meterbody_seal_after']
                resolution.ctchamber_seal_b4 = m_form.cleaned_data['ctchamber_seal_b4']
                resolution.ctchamber_seal_after = m_form.cleaned_data['ctchamber_seal_after']
                resolution.mpcc = m_form.cleaned_data['mpcc']
                resolution.metervoltage = m_form.cleaned_data['metervoltage']
                resolution.ctratio_ci = m_form.cleaned_data['ctratio_ci']
                resolution.ctratio_programed = m_form.cleaned_data['ctratio_programed']
                resolution.ctratio_installedsite = m_form.cleaned_data['ctratio_installedsite']
                resolution.ctratio_img = m_form.cleaned_data['ctratio_img']
                resolution.ctratio_ci_match = m_form.cleaned_data['ctratio_ci_match']
                resolution.ctratio_ci_match_rsn = m_form.cleaned_data['ctratio_ci_match_rsn']
                resolution.vtratio = m_form.cleaned_data['vtratio']
                resolution.amrrecovered = m_form.cleaned_data['amrrecovered']
                resolution.total_180 = m_form.cleaned_data['total_180']
                resolution.total_180_img = m_form.cleaned_data['total_180_img']
                resolution.max_kva_960 = m_form.cleaned_data['max_kva_960']
                resolution.max_kw_150 = m_form.cleaned_data['max_kw_150']
                resolution.t1_181 = m_form.cleaned_data['t1_181']
                resolution.t2_182 = m_form.cleaned_data['t2_182']
                resolution.r_energy = m_form.cleaned_data['r_energy']
                resolution.reverse_consumption = m_form.cleaned_data['reverse_consumption']
                resolution.reverse_consumption_rsn = m_form.cleaned_data['reverse_consumption_rsn']
                resolution.current_red = m_form.cleaned_data['current_red']
                resolution.current_yellow = m_form.cleaned_data['current_yellow']
                resolution.current_blue = m_form.cleaned_data['current_blue']
                resolution.voltage_red = m_form.cleaned_data['voltage_red']
                resolution.voltage_yellow = m_form.cleaned_data['voltage_yellow']
                resolution.voltage_blue = m_form.cleaned_data['voltage_blue']
                resolution.moduleinstalled = m_form.cleaned_data['moduleinstalled']
                resolution.modulecomm_ci = m_form.cleaned_data['modulecomm_ci']
                resolution.modulecom_not_rsn = m_form.cleaned_data['modulecom_not_rsn']
                resolution.civector_img = m_form.cleaned_data['civector_img']
                resolution.sim_serial = m_form.cleaned_data['sim_serial']
                resolution.sim_provider = m_form.cleaned_data['sim_provider']
                resolution.zera_test = m_form.cleaned_data['zera_test']
                resolution.error_register = m_form.cleaned_data['error_register']
                resolution.loadbalance = m_form.cleaned_data['loadbalance']
                resolution.redphase_zera = m_form.cleaned_data['redphase_zera']
                resolution.redphase_meter = m_form.cleaned_data['redphase_meter']
                resolution.redphase_clamp = m_form.cleaned_data['redphase_clamp']
                resolution.yellowphase_zera = m_form.cleaned_data['yellowphase_zera']
                resolution.yellowphase_meter = m_form.cleaned_data['yellowphase_meter']
                resolution.yellowphase_clamp = m_form.cleaned_data['yellowphase_clamp']
                resolution.bluephase_zera = m_form.cleaned_data['bluephase_zera']
                resolution.bluephase_meter = m_form.cleaned_data['bluephase_meter']
                resolution.bluephase_clamp = m_form.cleaned_data['bluephase_clamp']
                resolution.powerfactor_value = m_form.cleaned_data['powerfactor_value']
                resolution.remarks = m_form.cleaned_data['remarks']
                resolution.commit_inspection = m_form.cleaned_data['commit_inspection']
                resolution.arethereanomalies = m_form.cleaned_data['arethereanomalies']
                resolution.anomalies_list = m_form.cleaned_data['anomalies_list']
                resolution.anomalies_addressed_insp = m_form.cleaned_data['anomalies_addressed_insp']
                resolution.anomalies_addressed_insp_list = m_form.cleaned_data['anomalies_addressed_insp_list']
                resolution.fallback_req = m_form.cleaned_data['fallback_req']
                resolution.fallback_activities = m_form.cleaned_data['fallback_activities']
                resolution.commit_annomalies = m_form.cleaned_data['commit_annomalies']
                resolution.oktoworkwith = m_form.cleaned_data["oktoworkwith"]
                resolution.total_180_incms = 0
                resolution.save()
                zerov.status = True
                zerov.save()
                messages.success(request, 'Your Inspection Has been successfully saved.')
                return redirect('postpaid:my-lp')
            else:
                messages.error(request, 'There was an error in submitting your inspection.')
                print('invalid form')
                print(m_form.errors)
                # m_form = LpForm(instance=img)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = LpForm(instance=img)
        context = {
            'form': m_form,
            'target': img,
            # 'users' : region_users,

        }
    else:
        messages.error(request, 'You are not configured to run on this campaign.')
        return redirect('postpaid:lp-target')

    return render(request, 'postpaid/lp_inspection.html', context)


@login_required(login_url="login")
def my_lp(request):
    if request.user.is_authenticated:
        user = request.user.userprofile

    meters = Largepower_inspection.objects.filter(inspector=user).order_by('-dtadd')

    paginator = Paginator(meters, 30)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    paged_uploads_direct = paginator.get_page(page)
    meters_count = meters.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_count,
        'nbar': 'myuploads'}
    return render(request, 'postpaid/my_lp.html', context)


@login_required(login_url="login")
def lp_viewinspected(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters = Largepower_inspection.objects.all().order_by('-dtadd')
    paginator = Paginator(meters, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()

    context = {
        'meters': paged_uploads,
        'meters_count': meters_count,
        'nbar': 'alluploads'}
    return render(request, 'postpaid/view_lp_inspected.html', context)


@login_required(login_url="login")
def search_meter_lp_inspected(request):
    if request.user.is_authenticated:
        user = request.user.userprofile
    meters_list = Largepower_inspection.objects.all()
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {
        'meters': paged_uploads,
    }
    return render(request, 'postpaid/view_lp_inspected.html', context)


@login_required(login_url="login")
def view_lp_inspeted(request, pk):
    meter = Largepower_inspection.objects.get(id=pk)

    context = {
        'meter': meter,

    }
    return render(request, 'postpaid/view_inspected_lp.html', context)


@login_required(login_url="login")
def lp_dashboard(request):
    overall_target = Largepower_accounts.objects.all()
    overall_insp = Largepower_inspection.objects.all()
    overall_inspected = overall_target.filter(status=True).count()
    overall_pending = overall_target.filter(status=False).count()
    # public_per = "{:0.2f}".format((public_inspected / public_target.count()) * 100)

    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)

    overall_today = overall_insp.filter(dtadd__date=today)
    overall_previous_day = overall_insp.filter(dtadd__date=yesterday)

    regional_analytics = Largepower_accounts.objects.values('region__name').annotate(
        lp_target=(Count('id')),
        lp_inspected=(Count('id', distinct=True, filter=Q(status=True))),
        lp_inspected_pending=(Count('id', distinct=True, filter=Q(status=False))),
        lp_today=Count('id', filter=Q(lp_insp_target__dtadd__date=today)),
        lp_yesturday=Count('id', filter=Q(lp_insp_target__dtadd__date=yesterday)),
        # lp_yesturday_1=Count('id', filter=Q(lp_target__dtadd__date=yesterday_1)),

    ).order_by('region__name')

    county_analytics = Largepower_accounts.objects.values('county__name').annotate(
        lp_target=(Count('id')),
        lp_inspected=(Count('id', distinct=True, filter=Q(status=True))),
        lp_inspected_pending=(Count('id', distinct=True, filter=Q(status=False))),
        lp_today=Count('id', filter=Q(lp_insp_target__dtadd__date=today)),
        lp_yesturday=Count('id', filter=Q(lp_insp_target__dtadd__date=yesterday)),
    ).order_by('county__name')

    context = {

        'overall_target': overall_target.count(),
        'overall_inspected': overall_inspected,
        'overall_pending': overall_pending,
        'overall_today': overall_today.count(),
        'overall_previous': overall_previous_day.count(),
        'regional_analytics': regional_analytics,
        'county_analysis': county_analytics

    }

    return render(request, 'postpaid/lp_dashboard.html', context=context)


@login_required(login_url="login")
def exportupload_lp(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    meters = Largepower_inspection.objects.all()
    # meters =meters.filter(dtadd__gt=datetime.datetime.today()-datetime.timedelta(days=14)).order_by('-dtadd')

    writer.writerow(['SRN', 'ACCOUNT NUMBER', 'METER NUMBER', 'DIFFERENT METER NUMBER', 'CUSTOMER NAME', 'INDUSTRY',
                     'SMART METERING SUPPLY', 'METERBOX ENCLOSURE SL B4', 'METERBOX ENCLOSURE SL FINAL',
                     'METER TERMINAL SL B4', 'METER TERMINAL SL FINAL', 'TEST BLOCK SL B4', 'TEST BLOCK SL FINAL',
                     'METER BODY SL B4', 'METER BODY SL FINAL', 'CT CHAMBER SL B4', 'CT CHAMBER SL AFTER', 'MPCC',
                     'VOLTAGE@SITE', 'CT RATIO C&I', 'CT RATIO PROG', 'CT RATIO PROG IMG', 'CT RATIO CT INSTALLD',
                     'CT RATIO & INSTALLED MISMATCH', 'RSN FOR MISMATCH', 'PROG VT RATIO', 'AMR', 'TOTAL(1.8.0)',
                     'TOTAL(1.8.0) IMG', 'REVERS(2.8.0)', 'KVA(9.6.0)', 'KW(1.5.0)', 'KWH(1.8.1)', 'KWH(1.8.2)',
                     'RED PH V', 'YELLOW PH V', 'BLUE PH V', 'RED PH C', 'YELLOW PH C', 'BLUE PH C', 'REVERSE CONSP',
                     'RSN REVERS CONSP', 'MODULE INST', 'ZERA TEST', 'ERROR REG', 'RED PH ZERA', 'RED PH METER',
                     'RED PH AMCODER', 'YELLOW PH ZERA', 'YELLOW PH METER', 'YELLOW PH AMCODER', 'BLUE PH ZERA',
                     'BLUE PH METER', 'BLUE PH AMCODER', 'LOAD BAL', 'POWER FACT', 'ANOMALY DETECT', 'ANOMALY LIST',
                     'ANOMALY RECTFD', 'ANOMALY RECTFD LIST', 'REQ FALLBACK', 'REQ FALLBACK LIST', 'INSPECTOR'])
    for meter in meters:
        writer.writerow(
            [meter.target.srn, meter.target.accountno, meter.target.meterno, meter.meterno, meter.target.customer_name,
             meter.type_of_industry, meter.smartmeter, meter.meterbox_enclosure_seal_b4,
             meter.meterbox_terminal_seal_b4, meter.meterbox_terminal_seal_after, meter.testblock_seal_b4,
             meter.meterbody_seal_b4, meter.meterbody_seal_after, meter.ctchamber_seal_b4, meter.ctchamber_seal_after,
             meter.mpcc, meter.metervoltage, meter.ctratio_ci, meter.ctratio_programed, meter.ctratio_img,
             meter.ctratio_installedsite, meter.ctratio_ci_match, meter.ctratio_ci_match_rsn, meter.vtratio,
             meter.amrrecovered, meter.total_180, meter.total_180_img, meter.r_energy, meter.max_kva_960,
             meter.max_kw_150, meter.t1_181, meter.t2_182, meter.voltage_red, meter.voltage_yellow, meter.voltage_blue,
             meter.current_red, meter.current_yellow, meter.current_blue, meter.reverse_consumption,
             meter.reverse_consumption_rsn, meter.moduleinstalled, meter.zera_test, meter.error_register,
             meter.redphase_zera, meter.redphase_meter, meter.redphase_clamp, meter.yellowphase_zera,
             meter.yellowphase_meter, meter.yellowphase_clamp, meter.bluephase_zera, meter.bluephase_meter,
             meter.bluephase_clamp, meter.loadbalance, meter.powerfactor_value, meter.arethereanomalies,
             meter.anomalies_list, meter.anomalies_addressed_insp, meter.anomalies_addressed_insp_list,
             meter.fallback_req, meter.fallback_activities, meter.inspector])

    response['Content-Disposition'] = 'attachment; filename=LARGE_POWER_INSPECTIONS.csv" '
    return response


@login_required(login_url="login")
def lp_not_in_target(request):
    # userprofile = get_object_or_404(UserProfile, user=request.user)

    campaign = request.user.userprofile.campaign

    if campaign == 'lpx':

        if request.method == 'POST':
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = LpForm(request.POST, request.FILES)
            n_form = LPAccountsForm(request.POST, request.FILES)

            print(request.POST['meterno'])

            check = Largepower_inspection.objects.filter(meterno=request.POST['meterno'])
            # check = get_object_or_404(Largepower_inspection, meterno=request.POST['meterno'])

            if check:
                messages.error(request, 'That Account has already been inspected.')
                return redirect('postpaid:lp-target')

            if m_form.is_valid() and n_form.is_valid():

                # if m_form.cleaned_data['meterno'] is None:
                # messages.success(request, 'You need to take the Cordinates.')
                # return redirect('postpaid:mythreephase-list')
                #
                resolution1 = n_form.save(commit=False)
                resolution = m_form.save(commit=False)

                resolution1.srn = n_form.cleaned_data['srn']
                resolution1.meterno = n_form.cleaned_data['meterno']
                resolution1.accountno = n_form.cleaned_data['accountno']
                resolution1.customer_name = n_form.cleaned_data['customer_name']
                resolution1.id = time.time()
                resolution1.region = request.user.userprofile.region
                resolution1.county = request.user.userprofile.county
                resolution1.asigned = request.user.userprofile
                resolution1.status = True

                resolution.srn = resolution1.srn
                resolution.meterno = resolution1.meterno
                resolution.accountno = resolution1.accountno
                resolution.customer_name = resolution1.customer_name

                resolution.x = m_form.cleaned_data['x']
                resolution.y = m_form.cleaned_data['y']
                resolution.inspector = request.user.userprofile
                resolution.smartmeter = m_form.cleaned_data['smartmeter']
                resolution.type_of_industry = m_form.cleaned_data['type_of_industry']
                resolution.meterbox_enclosure_seal_b4 = m_form.cleaned_data['meterbox_enclosure_seal_b4']
                resolution.meterbox_enclosure_seal_after = m_form.cleaned_data['meterbox_enclosure_seal_after']
                resolution.meterbox_terminal_seal_b4 = m_form.cleaned_data['meterbox_terminal_seal_b4']
                resolution.meterbox_terminal_seal_after = m_form.cleaned_data['meterbox_terminal_seal_after']
                resolution.testblock_seal_b4 = m_form.cleaned_data['testblock_seal_b4']
                resolution.testblock_seal_after = m_form.cleaned_data['testblock_seal_after']
                resolution.meterbody_seal_b4 = m_form.cleaned_data['meterbody_seal_b4']
                resolution.meterbody_seal_after = m_form.cleaned_data['meterbody_seal_after']
                resolution.ctchamber_seal_b4 = m_form.cleaned_data['ctchamber_seal_b4']
                resolution.ctchamber_seal_after = m_form.cleaned_data['ctchamber_seal_after']
                resolution.mpcc = m_form.cleaned_data['mpcc']
                resolution.metervoltage = m_form.cleaned_data['metervoltage']
                resolution.ctratio_ci = m_form.cleaned_data['ctratio_ci']
                resolution.ctratio_programed = m_form.cleaned_data['ctratio_programed']
                resolution.ctratio_installedsite = m_form.cleaned_data['ctratio_installedsite']
                resolution.ctratio_img = m_form.cleaned_data['ctratio_img']
                resolution.ctratio_ci_match = m_form.cleaned_data['ctratio_ci_match']
                resolution.ctratio_ci_match_rsn = m_form.cleaned_data['ctratio_ci_match_rsn']
                resolution.vtratio = m_form.cleaned_data['vtratio']
                resolution.amrrecovered = m_form.cleaned_data['amrrecovered']
                resolution.total_180 = m_form.cleaned_data['total_180']
                resolution.total_180_img = m_form.cleaned_data['total_180_img']
                resolution.max_kva_960 = m_form.cleaned_data['max_kva_960']
                resolution.max_kw_150 = m_form.cleaned_data['max_kw_150']
                resolution.t1_181 = m_form.cleaned_data['t1_181']
                resolution.t2_182 = m_form.cleaned_data['t2_182']
                resolution.r_energy = m_form.cleaned_data['r_energy']
                resolution.reverse_consumption = m_form.cleaned_data['reverse_consumption']
                resolution.reverse_consumption_rsn = m_form.cleaned_data['reverse_consumption_rsn']
                resolution.current_red = m_form.cleaned_data['current_red']
                resolution.current_yellow = m_form.cleaned_data['current_yellow']
                resolution.current_blue = m_form.cleaned_data['current_blue']
                resolution.voltage_red = m_form.cleaned_data['voltage_red']
                resolution.voltage_yellow = m_form.cleaned_data['voltage_yellow']
                resolution.voltage_blue = m_form.cleaned_data['voltage_blue']
                resolution.moduleinstalled = m_form.cleaned_data['moduleinstalled']
                resolution.modulecomm_ci = m_form.cleaned_data['modulecomm_ci']
                resolution.modulecom_not_rsn = m_form.cleaned_data['modulecom_not_rsn']
                resolution.civector_img = m_form.cleaned_data['civector_img']
                resolution.sim_serial = m_form.cleaned_data['sim_serial']
                resolution.sim_provider = m_form.cleaned_data['sim_provider']
                resolution.zera_test = m_form.cleaned_data['zera_test']
                resolution.error_register = m_form.cleaned_data['error_register']
                resolution.loadbalance = m_form.cleaned_data['loadbalance']
                resolution.redphase_zera = m_form.cleaned_data['redphase_zera']
                resolution.redphase_meter = m_form.cleaned_data['redphase_meter']
                resolution.redphase_clamp = m_form.cleaned_data['redphase_clamp']
                resolution.yellowphase_zera = m_form.cleaned_data['yellowphase_zera']
                resolution.yellowphase_meter = m_form.cleaned_data['yellowphase_meter']
                resolution.yellowphase_clamp = m_form.cleaned_data['yellowphase_clamp']
                resolution.bluephase_zera = m_form.cleaned_data['bluephase_zera']
                resolution.bluephase_meter = m_form.cleaned_data['bluephase_meter']
                resolution.bluephase_clamp = m_form.cleaned_data['bluephase_clamp']
                resolution.powerfactor_value = m_form.cleaned_data['powerfactor_value']
                resolution.remarks = m_form.cleaned_data['remarks']
                resolution.commit_inspection = m_form.cleaned_data['commit_inspection']
                resolution.arethereanomalies = m_form.cleaned_data['arethereanomalies']
                resolution.anomalies_list = m_form.cleaned_data['anomalies_list']
                resolution.anomalies_addressed_insp = m_form.cleaned_data['anomalies_addressed_insp']
                resolution.anomalies_addressed_insp_list = m_form.cleaned_data['anomalies_addressed_insp_list']
                resolution.fallback_req = m_form.cleaned_data['fallback_req']
                resolution.fallback_activities = m_form.cleaned_data['fallback_activities']
                resolution.commit_annomalies = m_form.cleaned_data['commit_annomalies']
                resolution.oktoworkwith = m_form.cleaned_data["oktoworkwith"]
                resolution.total_180_incms = 0

                with transaction.atomic():
                    resolution1.save()
                    resolution.target = resolution1
                    resolution.save()

                messages.success(request, 'Your Inspection Has been successfully saved.')
                return redirect('postpaid:my-lp')
            else:

                messages.error(request, 'There was an error in submitting your inspection.')
                print('invalid form')
                print(m_form.errors)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = LpForm()
            n_form = LPAccountsForm()
        context = {'form': m_form, 'n_form': n_form, }
    else:
        messages.error(request, 'You are not configured to run on this campaign.')
        return redirect('main:my-dashboard')

    return render(request, 'postpaid/lp_notin_target.html', context)


@login_required(login_url="login")
def lp_inspector_analytics(request):
    if request.user.is_authenticated:
        user = request.user
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)

    inspectors = UserProfile.objects.filter(campaign='lp').values('user_id__id', 'user_id__name', 'user_id__mobile',
                                                                  'county__name').annotate(
        the_count=Count('lp_inspected_by'),
        today=Count('lp_inspected_by', filter=Q(lp_inspected_by__dtadd__date=today)),
        yesturday=Count('lp_inspected_by', filter=Q(lp_inspected_by__dtadd__date=yesterday)),
        yesturday_1=Count('lp_inspected_by', filter=Q(lp_inspected_by__dtadd__date=yesterday_1)),
        yesturday_2=Count('lp_inspected_by', filter=Q(lp_inspected_by__dtadd__date=yesterday_2)),
    ).order_by('county__name')

    # inspectors = Threephase_inspection.objects.all().select_related('inspector').values('inspector__user_id__stid','inspector__user_id__name','inspector__county__name','inspector__user_id__mobile').annotate(
    #      the_count=Count('id'),
    #      today=Count('id',filter=Q(dtadd__date=today)),
    #      yesturday=Count('id',filter=Q(dtadd__date=yesterday)),
    #      yesturday_1=Count('id',filter=Q(dtadd__date=yesterday_1)),
    #      yesturday_2=Count('id',filter=Q(dtadd__date=yesterday_2)),
    #      #yesturday_2_d=Count('id',filter=Q(dtadd__date=yesterday_2)),
    #      #yesturday_3_d=Count('id',filter=Q(dtadd__date=yesterday_3)),
    #     ).order_by('inspector__county__name')

    context = {
        'analytics': inspectors,
        'nbar': 'analytics',
        'yesterday_1': yesterday_1,
        'yesterday_2': yesterday_2,
        # 'county' : county
    }
    return render(request, 'postpaid/lp_user_analytics.html', context)
