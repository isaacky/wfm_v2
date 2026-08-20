from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
import csv
import datetime
from datetime import timedelta, date
from .models import  Debtlist, Revenuerecollection
from user.models import Account,UserProfile
from main.models import County, Region
from .forms import MeterForm, DebtListForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import F, Q
from django.db.models import Count,Sum
from django.db import models
from django_pandas.io import read_frame
import plotly
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from plotly.subplots import make_subplots

@login_required(login_url="login")
def search_zone_zone(request):
    if request.user.is_authenticated:
        county = request.user.userprofile.county

    today = date.today()
    meters_list = Debtlist.objects.select_related().values('zone').filter(county=request.user.userprofile.county,
                                                                     status=False,
                                                                     dt_asigned__lt=today).annotate(
        total_accounts=Count('accountno'),
        total_balance=Sum('totalbalance'),
        total_balance_new=Sum('totalbalance_new'),
        target_accounts = Count('id', distinct=True, filter=Q(target_acc=True))
    ).order_by('zone')

    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(zone__icontains=keyword)
    m_form = DebtListForm(request=request)
    context = {
        'meters' : paged_uploads,
        'title': 'County-target-list',
        'm_form' : m_form
    }
    return  render(request, 'revenue/target_asigning_zone_page.html', context)
@login_required(login_url="login")
def asign_accounts_zone(request):
    today = date.today()
    meters = Debtlist.objects.select_related('county').filter(county=request.user.userprofile.county, status=False, dt_asigned__lt=today).order_by('zone')
    objectlist = UserProfile.objects.filter(county=request.user.userprofile.county, campaign='revenue')
    paginator = Paginator(meters, 40)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    if request.method == 'POST':
        form = DebtListForm(request.POST,request=request)
        staff = request.POST.get('asigned_to')
        ids = request.POST.getlist('z')
        if ids == [] or staff == '':
            messages.error(request, 'The collector or Accounts cannot be blank.')
            return redirect('revenue:debt-list-zone')


        if form.is_valid():
            idz = meters.filter(zone__in=ids)
            for id in idz:
                rev_accounts = Debtlist.objects.get(pk=int(id.id))
                rev_accounts.asigned_to = form.cleaned_data['asigned_to']
                rev_accounts.asigned_by = request.user.userprofile
                rev_accounts.dt_asigned = today
                rev_accounts.save()
            messages.success(request, 'Accounts Allocated successfully successfully.')
            return redirect('revenue:debt-list-zone')
        else:
            print('invalid form')
            print(form.errors)

        # messages.success(request, 'Accounts Allocated successfully successfully.')
        # return redirect('revenue:debtlist_by_itin')

    else:
        m_form = DebtListForm(request=request)
    m_form = DebtListForm(request=request)
    context={
        'm_form' : m_form,
        'meters': paged_uploads,
        'title': 'County-target-list',
        'objectlist' : objectlist
    }
    return render(request, "revenue/target_asigning_zone_page.html", context)

@login_required(login_url="login")
def debtlist_by_zone(request):
    today = date.today()
    meters = Debtlist.objects.select_related().values('zone').filter(county=request.user.userprofile.county, status=False,
                                                              dt_asigned__lt=today).annotate(
        total_accounts=Count('accountno'),
        total_balance=Sum('totalbalance'),
        total_balance_new=Sum('totalbalance_new'),
        target_accounts = Count('id', distinct=True, filter=Q(target_acc=True))
    ).order_by('zone')

    paginator = Paginator(meters,40)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    m_form = DebtListForm(request=request)

    context = {
        'meters' : paged_uploads,
        'm_form' : m_form
}
    return render(request, 'revenue/target_asigning_zone_page.html', context)

@login_required(login_url="login")
def search_asigned_itin(request):
    today = date.today()
    meters_list = Debtlist.objects.select_related('county','asigned_to').filter(asigned_to=request.user.userprofile.id, status=False,
                                                              dt_asigned=today).order_by('itin')
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(itin__icontains=keyword)
    m_form = DebtListForm(request=request)
    context = {
        'meters' : paged_uploads,
        'm_form' : m_form
    }
    return  render(request, 'revenue/mydebtlist.html', context)

@login_required(login_url="login")
def search_asigned_meter(request):
    today = date.today()
    meters_list = Debtlist.objects.select_related('county','asigned_to').filter(asigned_to=request.user.userprofile.id, status=False,
                                                              dt_asigned=today).order_by('itin')
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    m_form = DebtListForm(request=request)
    context = {
        'meters' : paged_uploads,
        'm_form' : m_form
    }
    return  render(request, 'revenue/mydebtlist.html', context)

@login_required(login_url="login")
def search_itin_itn(request):
    if request.user.is_authenticated:
        county = request.user.userprofile.county

    today = date.today()
    meters_list = Debtlist.objects.select_related().values('itin').filter(county=request.user.userprofile.county,
                                                                     status=False,
                                                                     dt_asigned__lt=today).annotate(
        total_accounts=Count('accountno'),
        total_balance=Sum('totalbalance'),
        total_balance_new=Sum('totalbalance_new'),
        target_accounts = Count('id', distinct=True, filter=Q(target_acc=True))
    ).order_by('itin')

    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(itin__icontains=keyword)
    m_form = DebtListForm(request=request)
    context = {
        'meters' : paged_uploads,
        'title': 'County-target-list',
        'm_form' : m_form
    }
    return  render(request, 'revenue/target_asignng_itin_page.html', context)



@login_required(login_url="login")
def asign_accounts_itin(request):
    today = date.today()
    meters = Debtlist.objects.select_related('county').filter(county=request.user.userprofile.county, status=False, dt_asigned__lt=today).order_by('itin')
    objectlist = UserProfile.objects.filter(county=request.user.userprofile.county, campaign='revenue')
    paginator = Paginator(meters, 40)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    if request.method == 'POST':
        form = DebtListForm(request.POST,request=request)
        staff = request.POST.get('asigned_to')
        ids = request.POST.getlist('z')
        if ids == [] or staff == '':
            messages.error(request, 'The collector or Accounts cannot be blank.')
            return redirect('revenue:debt-list-itin')


        if form.is_valid():
            idz = meters.filter(itin__in=ids)
            for id in idz:
                rev_accounts = Debtlist.objects.get(pk=int(id.id))
                rev_accounts.asigned_to = form.cleaned_data['asigned_to']
                rev_accounts.asigned_by = request.user.userprofile
                rev_accounts.dt_asigned = today
                rev_accounts.save()
            messages.success(request, 'Accounts Allocated successfully successfully.')
            return redirect('revenue:debt-list-itin')
        else:
            print('invalid form')
            print(form.errors)

        # messages.success(request, 'Accounts Allocated successfully successfully.')
        # return redirect('revenue:debtlist_by_itin')

    else:
        m_form = DebtListForm(request=request)
    m_form = DebtListForm(request=request)
    context={
        'm_form' : m_form,
        'meters': paged_uploads,
        'title': 'County-target-list',
        'objectlist' : objectlist
    }
    return render(request, "revenue/target_asignng_itin_page.html", context)
    

@login_required(login_url="login")
def debtlist_by_itin(request):
    today = date.today()
    meters = Debtlist.objects.select_related().values('itin').filter(county=request.user.userprofile.county, status=False,
                                                              dt_asigned__lt=today).annotate(
        total_accounts=Count('accountno'),
        total_balance=Sum('totalbalance'),
        total_balance_new=Sum('totalbalance_new'),
        target_accounts = Count('id', distinct=True, filter=Q(target_acc=True))
    ).order_by('itin')

    paginator = Paginator(meters,40)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    m_form = DebtListForm(request=request)

    context = {
        'meters' : paged_uploads,
        'm_form' : m_form
}
    return render(request, 'revenue/target_asignng_itin_page.html', context)
    

@login_required(login_url="login")
def exportupload_all_collections(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    meters = (
        Revenuerecollection.objects.select_related('target').order_by("-dtadd")
    )

    writer.writerow(
        [
            "REGION",
            "COUNTY",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "NAME",
            "SECTOR",
            "ZONE",
            "ITIN",
            "TOTAL BALANCE",
            "PAID",
            "COLLECTION STATIS",
            "READING",
            "COLLECTORS",
            "COLLECTORS_NAME",
            "DATE COLLECTED",
            "COMMENTS"


        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.target.region,
                meter.target.county,
                meter.meterno,
                meter.accountno,
                meter.target.name,
                meter.target.sector,
                meter.target.zone,
                meter.target.itin,
                meter.target.totalbalance,
                meter.amountpaid,
                meter.collection_status,
                meter.reading,
                meter.collector,
                meter.collector.user.name,
                meter.dtadd,
                meter.comment



            ]
        )

    response["Content-Disposition"] = (
        'attachment; filename="REVENUE COLLECTION.csv" '
    )
    return response

@login_required(login_url="login")
def search_by_staff_number(request):
    # if request.user.is_authenticated:
    #     county = request.user.userprofile
    # print(county)
    # user = UserProfile.objects.get(user__stid =16314)
    # print(user.id)
    meters_list = Debtlist.objects.prefetch_related('asigned_to')
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            # user = UserProfile.objects.select_related('user').get(user__stid=keyword)
            paged_uploads = meters_list.filter(asigned_to__user__stid=keyword)
    context = {
        'meters' : paged_uploads,
        'title': 'County-target-list',
    }
    return  render(request, 'revenue/target_asignments_page.html', context)
    

@login_required(login_url="login")
def export_my_debtlist(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    today = date.today()
    meters = (
        Debtlist.objects.select_related("county")
        .filter(
            asigned_to=request.user.userprofile.id, status=False,
            dt_asigned=today
        )
        .order_by("-itin")
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
            "TOTAL BALANCE",
            "PAID",
            "LONGITUDE",
            "LATITUDE"

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
                meter.location,
                meter.name,
                meter.totalbalance,
                meter.amount_paid,
                meter.xcood,
                meter.ycood


            ]
        )

    response["Content-Disposition"] = (
        'attachment; filename="MY_DEBTLIST_TARGET.csv" '
    )
    return response

@login_required(login_url="login")
def debt_list_mytarget(request):
    today = date.today()
    meters = Debtlist.objects.select_related('county','asigned_to').filter(asigned_to=request.user.userprofile.id, status=False,
                                                              dt_asigned=today).order_by('itin')
    paginator = Paginator(meters,40)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context = {
        'meters' : paged_uploads,
        'title' : 'County-target-list',

}
    return render(request, 'revenue/mydebtlist.html', context)

@login_required(login_url="login")
def asigned_accounts(request):
    today = date.today()
    meters = Debtlist.objects.select_related('county').filter(county=request.user.userprofile.county, dt_asigned=today)
    meters_list = meters
    paginator = Paginator(meters_list,40)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context = {
        'meters' : paged_uploads,
         'title': 'County-target-asignments',
    }
    return render(request, 'revenue/target_asignments_page.html', context)

@login_required(login_url="login")
def asign_accounts(request):
    today = date.today()
    meters = Debtlist.objects.select_related('county').filter(county=request.user.userprofile.county, status=False, dt_asigned__lt=today).order_by('itin')
    objectlist = UserProfile.objects.filter(county=request.user.userprofile.county, campaign='revenue')
    paginator = Paginator(meters, 40)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    if request.method == 'POST':
        form = DebtListForm(request.POST,request=request)
        staff = request.POST.get('asigned_to')
        ids = request.POST.getlist('z')
        if ids == [] or staff == '':
            messages.error(request, 'The collector or Accounts cannot be blank.')
            return redirect('revenue:debt-list')
        if form.is_valid():
            for id in ids:
                rev_accounts = Debtlist.objects.get(pk=int(id))
                rev_accounts.asigned_to = form.cleaned_data['asigned_to']
                rev_accounts.asigned_by = request.user.userprofile
                rev_accounts.dt_asigned = today
                rev_accounts.save()
            messages.success(request, 'Accounts Allocated successfully successfully.')
            return redirect('revenue:debt-list')
        else:
            print('invalid form')
            print(form.errors)

        # messages.success(request, 'Accounts Allocated successfully successfully.')
        # return redirect('revenue:asign-accounts')

    else:
        m_form = DebtListForm(request=request)
    m_form = DebtListForm(request=request)
    context={
        'm_form' : m_form,
        'meters': paged_uploads,
        'title': 'County-target-list',
        'objectlist' : objectlist
    }
    return render(request, "revenue/target_allocation.html", context)


@cache_page(60 * 15)
@login_required(login_url="login")
def collections_dashboard_region(request, pk):
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)
    target = Region.objects.filter(id=pk)
    for t in target:
        nm = t.name
    paid_amount_customer = target.aggregate(Sum("collection_amount_paid"))
    paid_amount_customer_count = target.aggregate(Sum("collection_paid_count"))
    paid_amount = target.aggregate(Sum("collection_target"))
    paid_amount_count = target.aggregate(Sum("collection_target_count"))
    total_balance_new = target.aggregate(Sum("totalbalance_new"))
    oveall_inspected = Revenuerecollection.objects.select_related('region', 'county').values("collection_status",
                                                                                             "dtadd", "id", "accountno",
                                                                                             "amountpaid").filter(region_id=pk)

    # print(paid_amount['collection_target__sum'])
    # print(oveall_inspected.aggregate(Sum("amountpaid")))

    def target_achievement_paid_count():
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Planned",
                    x=["Planned"],
                    y=[paid_amount_count['collection_target_count__sum']],
                ),
                go.Bar(name="Achieved", x=["Achieved"], y=[paid_amount_customer_count['collection_paid_count__sum']]),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Target vs Achievement No Of Accounts(INCMS)",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="Accounts",
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
    def target_achievement_collected_amount():
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Target Balance",
                    x=["Planned"],
                    y=[paid_amount['collection_target__sum']],
                ),
                go.Bar(name="Current Balance", x=["Current Balance"], y=[total_balance_new['totalbalance_new__sum']]),
                go.Bar(name="Achieved", x=["Achieved"], y=[paid_amount_customer['collection_amount_paid__sum']]),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Target vs Achieved in Shillings(INCMS)",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="Amount(KSH)",
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

    def target_achievement():
        t_a = oveall_inspected.aggregate(Sum("amountpaid"))
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Planned",
                    x=["Planned"],
                    y=[paid_amount['collection_target__sum']],
                ),
                go.Bar(name="Achieved", x=["Achieved"], y=[t_a['amountpaid__sum']]),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Regions Target vs Achievement in Shillings",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="Amount(KSH)",
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

    def target_achievement_count():
        t_a = oveall_inspected.count()
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Planned",
                    x=["Planned"],
                    y=[paid_amount_count['collection_target_count__sum']],
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
            title="Regions Target vs Achievement No Of Accounts",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="Accounts",
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

    def collection_status():
        df = read_frame(oveall_inspected)
        df = df.groupby(by="collection_status", as_index=False, sort=False)[
            "accountno"
        ].count()
        values = df.collection_status
        names = df.accountno
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Regional Collection Statuses",
            labels={
                "accountno": "Meter Count",
                "collection_status": "Collection Status",
            },
        )
        df.update_traces(textposition="inside", textinfo="percent+label")
        df_collection_status = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df_collection_status

    def daily_trend():
        df = read_frame(oveall_inspected)
        df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
        df = df.groupby(by="dtadd", as_index=False, sort=False)["amountpaid"].sum()
        df = px.bar(
            df,
            x=df.dtadd,
            y=df.amountpaid,
            title=f"Regional Daily Overall Collections Amount.",
            text_auto=True,
            text=df.amountpaid,
            labels={"amountpaid": "Collection Amount", "dtadd": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    county_analytics = Revenuerecollection.objects.select_related('region','county') \
        .values('county__name', 'county__collection_target', 'region_id','county__collection_amount_paid','county__totalbalance_new').filter(region_id=pk) \
        .annotate(
        collected=Sum('amountpaid'),
        collected_visted=Count('id'),
        collected_collected=Count('id', filter=Q(collection_status="paid")),
        collected_today_accounts=Count('id', filter=Q(dtadd__date=today)),
        collected_today_amount=Sum('amountpaid', filter=Q(dtadd__date=today)),
        collected_today_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=today))),
        collected_yesturday_accounts=Count('id', filter=Q(dtadd__date=yesterday)),
        collected_yesturday_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday))),
        collected_yesturday_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday)),

        collected_yesturday_1_accounts=Count('id', filter=Q(dtadd__date=yesterday_1)),
        collected_yesturday_1_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday_1))),
        collected_yesturday_1_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday_1)),

        collected_yesturday_2_accounts=Count('id', filter=Q(dtadd__date=yesterday_2)),
        collected_yesturday_2_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday_2))),
        collected_yesturday_2_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday_2)),

        collected_yesturday_3_accounts=Count('id', filter=Q(dtadd__date=yesterday_3)),
        collected_yesturday_3_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday_3))),
        collected_yesturday_3_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday_3)),
    ).order_by('region_id')

    region_analytics = Revenuerecollection.objects.select_related('region')\
        .values('region__name','region__collection_target','region','region__collection_amount_paid','region__totalbalance_new',).filter(region_id=pk)\
       .annotate(
        collected=Sum('amountpaid'),
        collected_visted=Count('id'),
        collected_collected=Count('id', filter=Q(collection_status="paid")),
        collected_today_accounts=Count('id', filter=Q(dtadd__date=today)),
        collected_today_amount=Sum('amountpaid', filter=Q(dtadd__date=today)),
        collected_today_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=today))),
        collected_yesturday_accounts=Count('id', filter=Q(dtadd__date=yesterday)),
        collected_yesturday_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday))),
        collected_yesturday_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday)),

        collected_yesturday_1_accounts=Count('id', filter=Q(dtadd__date=yesterday_1)),
        collected_yesturday_1_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday_1))),
        collected_yesturday_1_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday_1)),

        collected_yesturday_2_accounts=Count('id', filter=Q(dtadd__date=yesterday_2)),
        collected_yesturday_2_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday_2))),
        collected_yesturday_2_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday_2)),

        collected_yesturday_3_accounts=Count('id', filter=Q(dtadd__date=yesterday_3)),
        collected_yesturday_3_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday_3))),
        collected_yesturday_3_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday_3)),
    ).order_by('region__name')

    inspectors = Revenuerecollection.objects.select_related('collector')\
        .values('collector__user_id__stid','collector__user_id__name','collector__user_id__mobile','collector__county__name')\
        .filter(region_id=pk).annotate(
        the_count=Count("collector"),
        total_sum=Sum("amountpaid"),
        today=Count("collector", filter=Q(dtadd__date=today)),
        today_sum=Sum("amountpaid", filter=Q(dtadd__date=today)),
        yesturday=Count(
            "collector", filter=Q(dtadd__date=yesterday)
        ),
        yesturday_sum=Sum("amountpaid", filter=Q(dtadd__date=yesterday)),
        yesturday_1=Count(
            "collector", filter=Q(dtadd__date=yesterday_1)
        ),
        yesturday_1_sum=Sum("amountpaid", filter=Q(dtadd__date=yesterday_1)),
        yesturday_2=Count(
            "collector", filter=Q(dtadd__date=yesterday_2)
        ),
        yesturday_2_sum=Sum("amountpaid", filter=Q(dtadd__date=yesterday_2)),
        yesturday_3=Count(
            "collector", filter=Q(dtadd__date=yesterday_3)
        ),
        yesturday_3_sum=Sum("amountpaid", filter=Q(dtadd__date=yesterday_3)),
    ).order_by('collector__county__name')

    context = {
        "yesterday": yesterday,
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,
        "county_analytics": county_analytics,
        "daily_trend_plot": daily_trend(),
        "target_achievement": target_achievement(),
        "collection_status": collection_status(),
        "target_achievement_count": target_achievement_count(),
        "target" : nm,
        "inspectors" : inspectors,
        "region_analytics" : region_analytics,
        'target_achievement_collected_amount': target_achievement_collected_amount(),
        'target_achievement_paid_count': target_achievement_paid_count()
    }

    return render(request, "revenue/regional_dashboard.html", context)


@cache_page(60 * 15)
@login_required(login_url="login")
def collections_dashboard(request):

    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)
    target= Region.objects.all()
    paid_amount = target.aggregate(Sum("collection_target"))
    paid_amount_customer = target.aggregate(Sum("collection_amount_paid"))
    paid_amount_customer_count = target.aggregate(Sum("collection_paid_count"))
    paid_amount_count = target.aggregate(Sum("collection_target_count"))
    total_balance_new = target.aggregate(Sum("totalbalance_new"))
    oveall_inspected = Revenuerecollection.objects.select_related('region', 'county').values("collection_status", "dtadd","id","accountno","amountpaid")
    # print(paid_amount['collection_target__sum'])
    # print(oveall_inspected.aggregate(Sum("amountpaid")))

    def target_achievement_collected_amount():
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Target Balance",
                    x=["Planned"],
                    y=[paid_amount['collection_target__sum']],
                ),
                go.Bar(name="Current Balance", x=["Current Balance"], y=[total_balance_new['totalbalance_new__sum']]),
                go.Bar(name="Achieved", x=["Achieved"], y=[paid_amount_customer['collection_amount_paid__sum']]),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Target vs Achieved in Shillings(INCMS)",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="Amount(KSH)",
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


    def target_achievement():
        t_a = oveall_inspected.aggregate(Sum("amountpaid"))
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Planned",
                    x=["Planned"],
                    y=[paid_amount['collection_target__sum']],
                ),
                go.Bar(name="Achieved", x=["Achieved"], y=[t_a['amountpaid__sum']]),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Target vs Achievement in Shillings(Collectors)",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="Amount(KSH)",
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

    def target_achievement_count():
        t_a = oveall_inspected.count()
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Planned",
                    x=["Planned"],
                    y=[paid_amount_count['collection_target_count__sum']],
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
            title="Target vs Achievement No Of Accounts(Collectors)",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="Accounts",
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

    def target_achievement_paid_count():
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Planned",
                    x=["Planned"],
                    y=[paid_amount_count['collection_target_count__sum']],
                ),
                go.Bar(name="Achieved", x=["Achieved"], y=[paid_amount_customer_count['collection_paid_count__sum']]),
            ]
        )

        fig.update_layout(barmode="group")
        fig.update_layout(title_text="Overall Target vs Achievement")
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            title="Target vs Achievement No Of Accounts(INCMS)",
            xaxis_tickfont_size=14,
            yaxis=dict(
                title="Accounts",
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

    def collection_status():
        df = read_frame(oveall_inspected)
        df = df.groupby(by="collection_status", as_index=False, sort=False)[
            "accountno"
        ].count()
        values = df.collection_status
        names = df.accountno
        df = px.pie(
            df,
            values=names,
            names=values,
            title="Collection Statuses",
            labels={
                "accountno": "Meter Count",
                "collection_status": "Collection Status",
            },
        )
        df.update_traces(textposition="inside", textinfo="percent+label")
        df_collection_status = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df_collection_status

    def daily_trend():
        df = read_frame(oveall_inspected)
        df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
        df = df.groupby(by="dtadd", as_index=False, sort=False)["amountpaid"].sum()
        df = px.bar(
            df,
            x=df.dtadd,
            y=df.amountpaid,
            title=f"Daily Overall Collections Amount.(Collectors)",
            text_auto=True,
            text=df.amountpaid,
            labels={"amountpaid": "Collection Amount", "dtadd": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    region_analytics = Revenuerecollection.objects.select_related('region')\
        .values('region__name','region__collection_target','region','region__collection_amount_paid','region__totalbalance_new',)\
       .annotate(
        collected=Sum('amountpaid'),
        collected_visted=Count('id'),
        collected_collected=Count('id', filter=Q(collection_status="paid")),
        collected_today_accounts=Count('id', filter=Q(dtadd__date=today)),
        collected_today_amount=Sum('amountpaid', filter=Q(dtadd__date=today)),
        collected_today_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=today))),
        collected_yesturday_accounts=Count('id', filter=Q(dtadd__date=yesterday)),
        collected_yesturday_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday))),
        collected_yesturday_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday)),

        collected_yesturday_1_accounts=Count('id', filter=Q(dtadd__date=yesterday_1)),
        collected_yesturday_1_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday_1))),
        collected_yesturday_1_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday_1)),

        collected_yesturday_2_accounts=Count('id', filter=Q(dtadd__date=yesterday_2)),
        collected_yesturday_2_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday_2))),
        collected_yesturday_2_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday_2)),

        collected_yesturday_3_accounts=Count('id', filter=Q(dtadd__date=yesterday_3)),
        collected_yesturday_3_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday_3))),
        collected_yesturday_3_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday_3)),
    ).order_by('region__name')




    county_analytics = Revenuerecollection.objects.select_related('region')\
        .values('county__name','county__collection_target','region_id','county__collection_amount_paid','county__totalbalance_new')\
       .annotate(
        collected=Sum('amountpaid'),
        collected_visted=Count('id'),
        collected_collected=Count('id', filter=Q(collection_status="paid")),
        collected_today_accounts=Count('id', filter=Q(dtadd__date=today)),
        collected_today_amount=Sum('amountpaid', filter=Q(dtadd__date=today)),
        collected_today_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=today))),
        collected_yesturday_accounts=Count('id', filter=Q(dtadd__date=yesterday)),
        collected_yesturday_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday))),
        collected_yesturday_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday)),

        collected_yesturday_1_accounts=Count('id', filter=Q(dtadd__date=yesterday_1)),
        collected_yesturday_1_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday_1))),
        collected_yesturday_1_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday_1)),

        collected_yesturday_2_accounts=Count('id', filter=Q(dtadd__date=yesterday_2)),
        collected_yesturday_2_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday_2))),
        collected_yesturday_2_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday_2)),

        collected_yesturday_3_accounts=Count('id', filter=Q(dtadd__date=yesterday_3)),
        collected_yesturday_3_paid=Count('id', filter=(Q(collection_status="paid") & Q(dtadd__date=yesterday_3))),
        collected_yesturday_3_amount=Sum('amountpaid', filter=Q(dtadd__date=yesterday_3)),
    ).order_by('region_id')

    context = {
        "yesterday": yesterday,
        "yesterday_1": yesterday_1,
        "yesterday_2": yesterday_2,
        "yesterday_3": yesterday_3,
        "region_analytics" : region_analytics,
        "county_analytics": county_analytics,
        "daily_trend_plot": daily_trend(),
        "target_achievement": target_achievement(),
        "collection_status" : collection_status(),
        "target_achievement_count" : target_achievement_count(),
        'target_achievement_collected_amount' : target_achievement_collected_amount(),
        'target_achievement_paid_count' : target_achievement_paid_count()
    }
    return render(request, "revenue/collections_dashboard.html", context)
    
@login_required(login_url="login")
def county_collector_useranalytics(request):
    if request.user.is_authenticated:
        user = request.user
    county = request.user.userprofile.county
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    inspectors = Revenuerecollection.objects.select_related('collector').values('collector__user_id__stid','collector__user_id__name','collector__user_id__mobile','collector__county__name').filter(county=county).annotate(
        the_count=Count("collector"),
        total_sum=Sum("amountpaid"),
        today=Count("collector", filter=Q(dtadd__date=today)),
        today_sum=Sum("amountpaid", filter=Q(dtadd__date=today)),
        yesturday=Count(
            "collector", filter=Q(dtadd__date=yesterday)
        ),
        yesturday_sum=Sum("amountpaid", filter=Q(dtadd__date=yesterday)),
        yesturday_1=Count(
            "collector", filter=Q(dtadd__date=yesterday_1)
        ),
        yesturday_1_sum=Sum("amountpaid", filter=Q(dtadd__date=yesterday_1)),
        yesturday_2=Count(
            "collector", filter=Q(dtadd__date=yesterday_2)
        ),
        yesturday_2_sum=Sum("amountpaid", filter=Q(dtadd__date=yesterday_2)),
        yesturday_3=Count(
            "collector", filter=Q(dtadd__date=yesterday_3)
        ),
        yesturday_3_sum=Sum("amountpaid", filter=Q(dtadd__date=yesterday_3)),
    ).order_by('collector__county__name')


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
    return render(request, "revenue/inspector_analytics.html", context)
@login_required(login_url="login")
def search_collected_meter(request):
    meters_list = Revenuerecollection.objects.all()
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    context = {
        'meters' : paged_uploads,
    }
    return  render(request, 'revenue/viewresults.html', context)
@login_required(login_url="login")
def export_county_debtlist(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    county = request.user.userprofile.county
    meters = (
        Debtlist.objects.select_related("county")
        .filter(
           county=county, status=False
        )
        .order_by("-itin")
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
            "TOTAL BALANCE",
            "OVERDUE",
            "LONGITUDE",
            "LATITUDE"

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
                meter.location,
                meter.name,
                meter.totalbalance,
                meter.overdue_amount,
                meter.xcood,
                meter.ycood


            ]
        )

    response["Content-Disposition"] = (
        'attachment; filename="COUNTY_PENDING_DEBTLIST_TARGET.csv" '
    )
    return response

@login_required(login_url="login")
def debtlist(request):
    today = date.today()
    meters = Debtlist.objects.select_related('county').filter(county=request.user.userprofile.county, status=False,
                                                              dt_asigned__lt=today).order_by('itin')
    paginator = Paginator(meters,40)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    m_form = DebtListForm(request=request)

    context = {
        'meters' : paged_uploads,
        'm_form' : m_form
}
    return render(request, 'revenue/target_asigning_page.html', context)
  
@login_required(login_url='login')
def viewdebtaccount(request,pk):
    #userprofile = get_object_or_404(UserProfile, user=request.user)
  
    img  = Debtlist.objects.get(id=pk)
    if request.method == 'POST':
        #user_form = UserForm(request.POST, instance=request.user)
        m_form = MeterForm(request.POST, request.FILES, instance=img)
        if m_form.is_valid():
            
            zerov = m_form.save(commit=False)
            resolution=Revenuerecollection()
            resolution.meterno = m_form.cleaned_data['meterno']
            resolution.accountno = m_form.cleaned_data['accountno']
            resolution.collection_status = m_form.cleaned_data['collection_status']
            resolution.amountpaid = m_form.cleaned_data['amountpaid']
            resolution.reading = m_form.cleaned_data['reading']
            resolution.comment = m_form.cleaned_data['comment']
            resolution.county = request.user.userprofile.county
            resolution.region = request.user.userprofile.region
            resolution.xcood = zerov.xcood
            resolution.ycood = zerov.ycood
            resolution.sector = zerov.sector
            resolution.zone = zerov.zone
            resolution.totalbalance = zerov.totalbalance
            resolution.target = zerov
            resolution.collector = request.user.userprofile
            resolution.save()
            zerov.status = True
            zerov.save()

            
            messages.success(request, 'Your Resolution Has been successfully saved.')
            return redirect('revenue:debt-list-mytarget')
    else:
        #messages.error(request, 'There was an error in submitting your resolution, Please try again.')
        m_form = MeterForm(instance=img)
    context = {
        'form': m_form,
        'img' : img,
        
    }
    return render(request, 'revenue/viewdebtlistaccount.html', context)


@login_required(login_url="login")
def viewresults(request):
    today = date.today()
    meters = Revenuerecollection.objects.select_related('county','collector').filter(dtadd__date=today).order_by('-dtadd')
    meters_list = meters
    paginator = Paginator(meters_list,40)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context = {
        'meters' : paged_uploads,
        'nbar' : 'alluploads'}
    return render(request, 'revenue/viewresults.html', context)

@login_required(login_url="login")
def globalreport(request, pk=None):
    if request.user.is_authenticated:
        user = request.user
    meters = Revenuerecollection.objects.all()
    meters_paid_o = Revenuerecollection.objects.filter(status='paid')
    meters_disconnected_o = Revenuerecollection.objects.filter(status='disconnected')
    meters_founddisc_o = Revenuerecollection.objects.filter(status='fdc')
    metersnon = Debtlist.objects.all()

    today = date.today()
    yesterday = date.today() - timedelta(days = 1)
    yesterday_2 = date.today() - timedelta(days = 2)
    yesterday_3 = date.today() - timedelta(days = 3)

    meters_d = meters.filter(dtadd__date=today)
    meters_y = meters.filter(dtadd__date=yesterday)
    meters_y_2 = meters.filter(dtadd__date=yesterday_2)
    meters_y_3 = meters.filter(dtadd__date=yesterday_3)
    
    meters_paid_d = meters_paid_o.filter(dtadd__date=today)
    meters_paid_y = meters_paid_o.filter(dtadd__date=yesterday)
    meters_paid_y_2 = meters_paid_o.filter(dtadd__date=yesterday_2)
    meters_paid_y_3 = meters_paid_o.filter(dtadd__date=yesterday_3)
    
    meters_disc_d = meters_disconnected_o.filter(dtadd__date=today)
    meters_disc_y = meters_disconnected_o.filter(dtadd__date=yesterday)
    meters_disc_y_2 = meters_disconnected_o.filter(dtadd__date=yesterday_2)
    meters_disc_y_3 = meters_disconnected_o.filter(dtadd__date=yesterday_3)
    
    meters_fdc_d = meters_founddisc_o.filter(dtadd__date=today)
    meters_fdc_y = meters_founddisc_o.filter(dtadd__date=yesterday)
    meters_fdc_y_2 = meters_founddisc_o.filter(dtadd__date=yesterday_2)
    meters_fdc_y_3 = meters_founddisc_o.filter(dtadd__date=yesterday_3)
    
    revenue_all = Revenuerecollection.objects.aggregate(revenue_all=Sum('amountpaid')),
    # revenue_td = meters_d.aggregate(collected_all=Sum('amountpaid')),
    # revenue_y = meters_y.aggregate(collected_all=Sum('amountpaid')),
    # revenue_y2 = meters_y_2.aggregate(collected_all=Sum('amountpaid')),
    # revenue_y3 = meters_y_3.aggregate(collected_all=Sum('amountpaid'))
    
    context = {
	    'target': metersnon.count(),
        'achieved_All': meters.count(),
        'achieved_t': meters_d.count(),
        'achieved_y': meters_y.count(),
        'achieved_y_2': meters_y_2.count(),
        'achieved_y_3': meters_y_3.count(),
        'meters_paid_o' : meters_paid_o.count(),
        'meters_paid_d' : meters_paid_d.count(),
        'meters_paid_y' : meters_paid_y.count(),
        'meters_paid_y_2' : meters_paid_y_2.count(),
        'meters_paid_y_3' : meters_paid_y_3.count(),
        'meters_disc_o' : meters_disconnected_o.count(),
        'meters_disc_d' : meters_disc_d.count(),
        'meters_disc_y' : meters_disc_y.count(),
        'meters_disc_y_2' : meters_disc_y_2.count(),
        'meters_disc_y_3' : meters_disc_y_3.count(),
        'meters_fdc_o' : meters_founddisc_o.count(),
        'meters_fdc_d' : meters_fdc_d.count(),
        'meters_fdc_y' : meters_fdc_y.count(),
        'meters_fdc_y_2' : meters_fdc_y_2.count(),
        'meters_fdc_y_3' : meters_fdc_y_3.count(),
        
        'target_amt': Debtlist.objects.aggregate(total_price=Sum('totalbalance')),
        # 'revenue_all' : Revenuerecollection.objects.aggregate(revenue_all=Sum('amountpaid')),
        # 'revenue_td' : meters_d.aggregate(collected_all=Sum('amountpaid')),
        # 'revenue_y' : meters_y.aggregate(collected_all=Sum('amountpaid')),     
        # 'revenue_y2' : revenue_y2,
        # 'revenue_y3' : revenue_y3,
        
        'overall_t' : meters_d.count(),
        'overall_y' : meters_y.count(),
        'overall_y_2' : meters_y_2.count(),
        'overall_y_3' : meters_y_3.count(),
        
        'yesterday_2' :  yesterday_2,
        'yesterday_3' :  yesterday_3,
        'nbar' : 'analytics'
        
        }

    return render(request, 'revenue/globalanalytics.html', context)  

@login_required(login_url="login")
def regionalreport(request, pk=None):
    if request.user.is_authenticated:
        user = request.user

    today = date.today()
    yesterday = date.today() - timedelta(days = 1)
    yesterday_2 = date.today() - timedelta(days = 2)

    r = Region.objects.values('name','id').annotate(
        target=Count('region_debt_list',distinct=True),
        actioned=Count('region_rev_action',distinct=True),
        #actioned_t=Count('region_rev_action__dtadd', distinct=True,filter=Q(dtadd__date=today)),
        ).annotate(
            actioned_t = Count('region_rev_action',distinct=True, filter=Q(region_rev_action__dtadd__date=today))
        ).annotate(
            actioned_y = Count('region_rev_action',distinct=True, filter=Q(region_rev_action__dtadd__date=yesterday))
        ).annotate(
             actioned_y_2 = Count('region_rev_action',distinct=True, filter=Q(region_rev_action__dtadd__date=yesterday_2))
        ).order_by('name')

    context = {

        'analytics' : r,
        'nbar' : 'analytics',
        'yesterday_2':yesterday_2 
        
        }

    return render(request, 'revenue/regionalanalytics.html', context)

@login_required(login_url="login")
def viewcounty(request, pk):

    today = date.today()
    yesterday = date.today() - timedelta(days = 1)
    
    collection = Revenuerecollection.objects.filter(region_id=pk)
  
    analytics_r = Debtlist.objects.values('county__name','county__id').annotate(
        c_target = Sum('totalbalance'),
        c_target_accounts = Count('id')
        ).filter(region_id=pk,status='pending').order_by('county__name')
    
    analytics1_r = collection.values('county__name','county__id').annotate(
        c_collection_total = Count('id'),
        c_collection_total_accounts_p = Count('id',filter=Q(status='paid')),
        c_collection_total_accounts_disc = Count('id',filter=Q(status='disconnected')),
        c_collection_total_accounts_fdc = Count('id',filter=Q(status='fdc')),
        # today
        c_collection_td_accounts=(Count('id', filter=Q(dtadd__date=today))),
        c_collection_td_accounts_p = Count('id',filter=Q(dtadd__date=today,status='paid')),
        c_collection_td_accounts_disc = Count('id',filter=Q(dtadd__date=today,status='disconnected')),
        c_collection_td_accounts_fdc = Count('id',filter=Q(dtadd__date=today,status='fdc')),
        # yesturday
        c_collection_y_accounts=(Count('id', filter=Q(dtadd__date=yesterday))),
        c_collection_y_accounts_p = Count('id',filter=Q(dtadd__date=yesterday,status='paid')),
        c_collection_y_accounts_disc = Count('id',filter=Q(dtadd__date=yesterday,status='disconnected')),
        c_collection_y_accounts_fdc = Count('id',filter=Q(dtadd__date=yesterday,status='fdc')),
        ).order_by('region__name')


    context = {
               'analytics' : analytics_r,
               'analytics1' : analytics1_r,
        }
    return render(request, 'revenue/countyanalytics.html', context) 

@login_required(login_url="login")
def viewuser(request, pk):
    if request.user.is_authenticated:
        user = request.user
    today = date.today()
    yesterday = date.today() - timedelta(days = 1)
    county = County.objects.get(id=pk).name
    resolved = Revenuerecollection.objects.filter(county_id=pk)
    target = Debtlist.objects.filter(county_id=pk)
 
    
    analytics_r = Debtlist.objects.values('staff','staff__name','staff__mobile').annotate(
        #c_target = Sum('totalbalance')
        c_target_accounts = Count('id')
        ).filter(county_id=pk).order_by('staff')
    
    analytics1_r = resolved.values('staff__stid','staff__name','staff__stid','staff__mobile').annotate(
        c_collection_total = Count('id'),
        c_collection_total_accounts_p = Count('id',filter=Q(status='paid')),
        c_collection_total_accounts_disc = Count('id',filter=Q(status='disconnected')),
        c_collection_total_accounts_fdc = Count('id',filter=Q(status='fdc')),
         # today
        c_collection_td_accounts=(Count('id', filter=Q(dtadd__date=today))),
        c_collection_td_accounts_p = Count('id',filter=Q(dtadd__date=today,status='paid')),
        c_collection_td_accounts_disc = Count('id',filter=Q(dtadd__date=today,status='disconnected')),
        c_collection_td_accounts_fdc = Count('id',filter=Q(dtadd__date=today,status='fdc')),
        # yesturday
        c_collection_y_accounts=(Count('id', filter=Q(dtadd__date=yesterday))),
        c_collection_y_accounts_p = Count('id',filter=Q(dtadd__date=yesterday,status='paid')),
        c_collection_y_accounts_disc = Count('id',filter=Q(dtadd__date=yesterday,status='disconnected')),
        c_collection_y_accounts_fdc = Count('id',filter=Q(dtadd__date=yesterday,status='fdc')),
        ).order_by('staff__stid')
    
    context = {   
        'analytics' : analytics_r,
        'analytics1' : analytics1_r,
        'nbar' : 'analytics' ,
        'county' : county       
        }
    return render(request, 'revenue/useranalytics.html', context) 

@login_required(login_url="login")
def search_meter(request):
    if request.user.is_authenticated:
        county = request.user.userprofile.county
    today = date.today()
    meters_list = Debtlist.objects.select_related('county').filter(county=county, status=False,
                                                              dt_asigned__lt=today)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(meterno__icontains=keyword)
    m_form = DebtListForm(request=request)
    context = {
        'meters' : paged_uploads,
        'title': 'County-target-list',
        'm_form' : m_form
    }
    return  render(request, 'revenue/target_asigning_page.html', context)

@login_required(login_url="login")
def search_itin(request):
    if request.user.is_authenticated:
        county = request.user.userprofile.county

    today = date.today()
    meters_list = Debtlist.objects.select_related('county').filter(county=county, status=False,
                                                              dt_asigned__lt=today)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            paged_uploads = meters_list.filter(itin__icontains=keyword)
    m_form = DebtListForm(request=request)
    context = {
        'meters' : paged_uploads,
        'title': 'County-target-list',
        'm_form' : m_form
    }
    return  render(request, 'revenue/target_allocation.html', context)


@login_required(login_url="login")
def viewdebtlistitins(request, pk):
    if request.user.is_authenticated:
        county = request.user.userprofile.county

    meters_list = Debtlist.objects.select_related('county').filter(status=False, county=county,itin=pk)
    paginator = Paginator(meters_list,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context = {
        'meters' : paged_uploads,
        'nbar' : 'alluploads'
        }
    return render(request, 'revenue/mydebtlist.html', context)

@login_required(login_url="login")
def exportupload(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)

    today = date.today()
    meters = (
        Revenuerecollection.objects.select_related("county")
        .filter(
            county=request.user.userprofile.county
        )
        .order_by("-dtadd")
    )

    writer.writerow(
        [

            "COUNTY",
            "METER NUMBER",
            "ACCOUNT NUMBER",
            "NAME",
            "SECTOR",
            "ZONE",
            "ITIN",
            "TOTAL BALANCE",
            "PAID",
            "COLLECTION STATIS",
            "READING",
            "COLLECTORS",
            "COLLECTORS_NAME",
            "DATE COLLECTED",
            "COMMENTS",
            "TARGET ACC",


        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.target.county,
                meter.meterno,
                meter.accountno,
                meter.target.name,
                meter.target.sector,
                meter.target.zone,
                meter.target.itin,
                meter.target.totalbalance,
                meter.amountpaid,
                meter.collection_status,
                meter.reading,
                meter.collector,
                meter.collector.user.name,
                meter.dtadd,
                meter.comment,
                meter.target.target_acc



            ]
        )

    response["Content-Disposition"] = (
        'attachment; filename="REVENUE COLLECTION.csv" '
    )
    return response

@login_required(login_url="login")
def my_actioned(request):
    if request.user.is_authenticated:
        user = request.user.userprofile
    today = date.today()   
    meters = Revenuerecollection.objects.filter(collector=user,dtadd__date=today).order_by('-dtadd')
    paid = Revenuerecollection.objects.filter(collector=user, collection_status='paid',dtadd__date=today)
    paid_amount = meters.aggregate(Sum("amountpaid"))
    fdc = Revenuerecollection.objects.filter(collector=user, collection_status='fdc',dtadd__date=today)
    disconnected = Revenuerecollection.objects.filter(collector=user, collection_status='disconnected',dtadd__date=today)
    meters_list = meters
    paginator = Paginator(meters_list,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)




    context = {
        'meters' : paged_uploads,
        'paid' : paid.count(),
        'fdc' : fdc.count(),
        'disconnected' : disconnected.count(),
        'paid_amount' : paid_amount,
        'nbar' : 'alluploads'}
    return render(request, 'revenue/my_achievement.html', context)