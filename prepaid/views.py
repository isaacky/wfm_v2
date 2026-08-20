from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import csv
import json
import datetime
from datetime import timedelta, date
from .models import  Tid_meters,Tid_inspection
from user.models import Account,UserProfile
from main.models import County, Region
from .forms import TidForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import F, Q, Sum, Count
from django_pandas.io import read_frame
import plotly
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


@login_required(login_url="login")
def threephase_target(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters = Retr.objects.filter(status=False, county=user)[:10]
    paginator = Paginator(meters,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_pending = meters.count()

    context = {
        'meters' : paged_uploads,
        'meters_count' : meters_pending,
        'nbar' : 'alluploads'}
    return render(request, 'prepaid/retrofits/retrofit_target.html', context)

@login_required(login_url="login")
def tid_export_inspected_region(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    county = request.user.userprofile.region

    meters = (
        Tid_inspection.objects
        .filter(
            region=county,
            dtadd__gt=datetime.datetime.today() - datetime.timedelta(days=30),
        )
        .order_by("-dtadd")
    )

    writer.writerow(
        [
            "COUNTY",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "DATE UPDATED",
            "STAFf UPDATED"
        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.county,
                meter.meterno,
                meter.accountno,
                meter.dtadd,
                meter.inspector
            ]
        )

    response["Content-Disposition"] = (
        'attachment; filename="TID_PENDING_UPGRADE_REGION_LAST30DAYS.csv" '
    )
    return response
@login_required(login_url="login")
def tid_pending_upgrade_all(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)


    meters = (
        Tid_meters.objects.select_related("county","region")
        .filter(
            status=False,

        )
        .order_by("-customer_name")
    )

    writer.writerow(
        [
            "REGION",
            "COUNTY",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "CUSTOMER NAME"

        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.region,
                meter.county,
                meter.meterno,
                meter.accountno,
                meter.customer_name

            ]
        )

    response["Content-Disposition"] = (
        'attachment; filename="TID_UPGRADE_REGION.csv" '
    )
    return response

@login_required(login_url="login")
def tid_pending_upgrade(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    today = date.today()
    yesterday = date.today() - timedelta(days=14)
    county = request.user.userprofile.county
    meters = (
        Tid_meters.objects.select_related("county")
        .filter(
            county=county,
            status=False
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
            "TECH CENTER",
            "OFFICE NAME",
            "ITIN",
            "CUSTOMER NAME",
            "LAST VEND",
            "MOBILE VEND",
            "SUPPLY ADDRESS",
            "LATITUDE",
            "LONGITUDE"
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
                meter.tech_center,
                meter.office_name,
                meter.itin,
                meter.customer_name,
                meter.mobile_incms,
                meter.mobile_vend,
                meter.supply_address,
                meter.latitude,
                meter.longitute
            ]
        )

    response["Content-Disposition"] = (
        'attachment; filename="TID_PENDING_UPGRADE.csv" '
    )
    return response

@login_required(login_url="login")
def county_tid_useranalytics(request):
    if request.user.is_authenticated:
        user = request.user
    county = request.user.userprofile.region
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    inspectors = Tid_inspection.objects.select_related('inspector').values('inspector__county__name','inspector__user_id__stid','inspector__user_id__name','inspector__user_id__mobile').filter(region=county).annotate(
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
        'county' : county
    }
    return render(request, "prepaid/tid/inspector_analytics.html", context)
    
    


@login_required(login_url="login")
def tid_upgrade_dashboard(request):
    # oveall_target = County.objects.aggregate(Sum("publiclighting_target"))

    oveall_upgraded = Tid_inspection.objects.values(
        "meteringstatus", "tidstatus", "dtadd","meterno","region__name"
    )
    overall_not_okay = oveall_upgraded.exclude(meteringstatus="okay")

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
    start_date = datetime.date(2023, 10, 28)
    end_date = datetime.date.today()

    result = count_business_days(start_date, end_date)

    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    def non_consent():
        df = read_frame(oveall_upgraded)
        df = df.groupby(by="tidstatus", as_index=False, sort=False)[
            "meterno"
        ].count()
        values = df.tidstatus
        names = df.meterno
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Upgrade status",
            labels={
                "meterno": "Meter Count",
                "tidstatus": "Upgrade Status",
            },
        )
        df.update_traces(textposition="inside", textinfo="percent+label")
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df



    def metering_status():
        df = read_frame(oveall_upgraded)
        df = df.groupby(by="meteringstatus", as_index=False, sort=False)[
            "meterno"
        ].count()
        values = df.meteringstatus
        names = df.meterno
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Upgraded Meter Metering Status",
            labels={
                "newmeter": "Meter Count",
                "meteringstatus": "Metering Status",
            },
        )
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    def target_achievement():
        t_a = oveall_upgraded.count()
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Planned ToDate",
                    x=["Planned ToDate"],
                    y=[120003],
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
                title="No Of Upgrades",
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
        df = read_frame(oveall_upgraded)
        df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
        df = df.groupby(by="dtadd", as_index=False, sort=False)["meterno"].count()
        df = px.bar(
            df,
            x=df.dtadd,
            y=df.meterno,
            title=f"Daily Overall Meter Upgrade.Daily Target = {0}",
            text_auto=True,
            text=df.meterno,
            labels={"meterno": "Meter Count", "dtadd": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    # df = read_frame(oveall_upgraded)
    # df = df.groupby(by=['region__name', 'tidstatus'], as_index=False, sort=False)['meterno'].count()
    # json_records = df.reset_index().to_json(orient='records')
    # data = []
    # data = json.loads(json_records)
    # print(data)



    region_analytics = (
        Region.objects.select_related('tid_region')
        .values("name")  # select_related('dc_region')
        .annotate(
            tid_upgraded=(Count("tid_region", distinct=True)),
            tid_target=(Sum("tid_overall_target", distinct=True)),
            tid_failed=(Count("tid_region", distinct=True,filter=Q(tid_region__tidstatus='failed'))
            ),
            diff=F('tid_target')-F('tid_upgraded'),
            today=Count(
                "tid_region",
                distinct=True,
                filter=Q(tid_region__dtadd__date=today),
            ),
            today_1=Count(
                "tid_region",
                distinct=True,
                filter=Q(tid_region__dtadd__date=yesterday),
            ),
            today_2=Count(
                "tid_region",
                distinct=True,
                filter=Q(tid_region__dtadd__date=yesterday_1),
            ),
            today_3=Count(
                "tid_region",
                distinct=True,
                filter=Q(tid_region__dtadd__date=yesterday_2),
            ),
            today_4=Count(
                "tid_region",
                distinct=True,
                filter=Q(tid_region__dtadd__date=yesterday_3),
            ),
        )
        .order_by("name")
    )

    county_analytics = (
        County.objects.select_related("tid_county")
        .values("name","region_id")
        .annotate(
            tid_upgraded=(Count("tid_county", distinct=True)),
            tid_target=(Sum("tid_overall_target", distinct=True)),
            tid_failed=(Count("tid_county", distinct=True, filter=Q(tid_county__tidstatus='failed'))
                        ),
            diff=F('tid_target') - F('tid_upgraded'),
            today=Count(
                "tid_county",
                distinct=True,
                filter=Q(tid_county__dtadd__date=today),
            ),
            today_1=Count(
                "tid_county",
                distinct=True,
                filter=Q(tid_county__dtadd__date=yesterday),
            ),
            today_2=Count(
                "tid_county",
                distinct=True,
                filter=Q(tid_county__dtadd__date=yesterday_1),
            ),
            today_3=Count(
                "tid_county",
                distinct=True,
                filter=Q(tid_county__dtadd__date=yesterday_2),
            ),
            today_4=Count(
                "tid_county",
                distinct=True,
                filter=Q(tid_county__dtadd__date=yesterday_3),
            ),
        )
        .order_by("region_id")
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
        "region_analytics": region_analytics,
        "county_analytics": county_analytics,
        "yesterday": yesterday,
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,

    }
    return render(request, "prepaid/tid/tid_dashboard.html", context)
    

@login_required(login_url="login")
def upgraded_list(request):
    meters = (
        Tid_inspection.objects.select_related("tid").order_by("-dtadd")
    )
    paginator = Paginator(meters, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {
        "meters": paged_uploads,
        "nbar": "alluploads",
    }
    return render(request, "prepaid/tid/upgraded_meters.html", context)

@login_required(login_url="login")
def mytidupgrade_list(request):
    if request.user.is_authenticated:
        user = request.user.userprofile
    today = date.today()
    meters = (
        Tid_inspection.objects.select_related("inspector")
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
    return render(request, "prepaid/tid/mytidupgrades.html", context)
    
@login_required(login_url="login")
def upgrade_tidmeter(request, pk):
    # userprofile = get_object_or_404(UserProfile, user=request.user)
    img = Tid_meters.objects.get(id=pk)
    if request.method == "POST":
        # user_form = UserForm(request.POST, instance=request.user)
        m_form = TidForm(request.POST, request.FILES, instance=img)
        if m_form.is_valid():
            zerov = m_form.save(commit=False)
            resolution = Tid_inspection()
            resolution.meterno = m_form.cleaned_data["meterno"]
            resolution.accountno = m_form.cleaned_data["accountno"]
            resolution.meteringstatus = m_form.cleaned_data["meteringstatus"]
            resolution.faultystatus = m_form.cleaned_data["faultystatus"]
            resolution.tamperedstatus = m_form.cleaned_data["tamperedstatus"]
            resolution.bypassstatus = m_form.cleaned_data["bypassstatus"]
            resolution.meterimg = m_form.cleaned_data["meterimg"]
            resolution.tidstatus = m_form.cleaned_data["tidstatus"]
            resolution.comment = m_form.cleaned_data["comment"]
            resolution.sealno = m_form.cleaned_data["sealno"]
            resolution.inspector = request.user.userprofile
            resolution.tid = img
            resolution.county = request.user.userprofile.county
            resolution.region = request.user.userprofile.region

            resolution.save()
            zerov.status = True
            zerov.save()
            messages.success(
                request, "Your TID Meter Upgrade Has been successfully saved."
            )
            return redirect("prepaid:mytidupgrade-list")
        else:
            messages.error(
                request, "There was an error in submitting your inspection."
            )
            # m_form = ThreepahseForm(instance=img)
            print("invalid form")
            print(m_form.errors)

    else:
        # user_form = UserForm(instance=request.user)

        m_form = TidForm(instance=img)
    context = {
        "form": m_form,
    }

    return render(request, "prepaid/tid/tidupgrade.html", context)

@login_required(login_url="login")
def tid_search_meter(request):
    if request.user.is_authenticated:
        user = request.user.userprofile.county
    meters_list = Tid_meters.objects.filter(status=False)
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {
        "meters": paged_uploads,
    }
    return render(request, "prepaid/tid/targetlist.html", context)
    

@login_required(login_url="login")
def star_tid_customers(request):
    # if request.user.is_authenticated:
    #     user = request.user.userprofile
    county = get_object_or_404(UserProfile, user=request.user).county
    meters = Tid_meters.objects.select_related("county").filter(
        status=False, county=county
    )[
        :10
    ]  # filter(status=False, county=county)[:10]
    # paginator = Paginator(meters, 10)
    # page = request.GET.get("page")
    # paged_uploads = paginator.get_page(page)
    context = {"meters": meters, "county": county, "nbar": "alluploads"}
    return render(request, "prepaid/tid/targetlist.html", context)

