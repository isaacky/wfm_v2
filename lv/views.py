from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Substation, Lvinspection,Poledefects,MaintainLVinspection,SubstationInspection,\
    TxFailure,Commission_substation, Poledefects_maintenance, Lv_defaults, Substation_defaults,SubstationMaintenance,LoadChecks
from user.models import UserProfile
from main.models import Region,County
from mediumv.models import Mv_poledefects,Mvinspection,Mvmaitenance
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .forms import LvinspectionForm, PoledefectsForm,LvinspectionApproveForm,TxFailureForm,MaintainLVinspectionForm,SubstationInspectionForm, \
    LvmaintenanceApproveForm,LvfailureApproveForm,SubstationApproveForm, Commission_substationForm, MaintainPoleApproveForm, CommissionApproveForm,\
    Poledefects_maintenanceForm,SubstationForm,GlobalSubstationForm,MaintainSubstationinspectionForm,SubstationMaintenanceApproveForm,LoadChecksForm
from django.http import HttpResponse
from django_pandas.io import read_frame
from django.db.models import F, Q,Count,Sum
from django.db.models.functions import Coalesce
from itertools import chain
from django_pandas.io import read_frame
import numpy as np
from django.db import transaction
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd
import datetime
from django.utils import formats
from datetime import timedelta, time, date,datetime
import csv
from django.utils import timezone

@login_required(login_url="login")
def global_loadchecks_filter(request):
    lvinspections = LoadChecks.objects.values('id', 'substation__ssn', 'substation__name', 'dtupdate','region', 'county', 'save_status', 'aprv_status',
    'region__name', 'county__name', 'inspectedby__user_id__stid', 'primary_voltage', 'tx_rating',
    'number_of_circuits', 'voltage_ll_ry','voltage_ll_yb', 'voltage_ll_br', 'voltage_ln_rn','voltage_ln_yn', 'voltage_ln_bn', 'phase_loads_r', 'phase_loads_y', 'phase_loads_b',
    'phase_loads_r_2', 'phase_loads_y_2', 'phase_loads_b_2','phase_loads_r_3', 'phase_loads_y_3', 'phase_loads_b_3', 'phase_loads_r_4','phase_loads_y_4', 'phase_loads_b_4', 'phase_loads_r_5',
    'phase_loads_y_5', 'phase_loads_b_5').filter(save_status=True).order_by('-dtupdate')



    # todays filter lvinspections.filter(Q(dtupdate__date=today))

    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(region=keyword)
        title = keyword
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(county=keyword)
        title = keyword
    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = keyword

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = keyword

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = keyword

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title' : title

    }
    return render(request, 'lv/loadchecks/global_loadchecks.html', context)

@login_required(login_url="login")
def global_loadchecks(request):
    today = date.today()
    lvinspections = LoadChecks.objects.values('id', 'substation__ssn', 'substation__name', 'dtupdate','region', 'county', 'save_status', 'aprv_status',
    'region__name', 'county__name', 'inspectedby__user_id__stid', 'primary_voltage', 'tx_rating',
    'number_of_circuits', 'voltage_ll_ry','voltage_ll_yb', 'voltage_ll_br', 'voltage_ln_rn','voltage_ln_yn', 'voltage_ln_bn', 'phase_loads_r', 'phase_loads_y', 'phase_loads_b',
    'phase_loads_r_2', 'phase_loads_y_2', 'phase_loads_b_2','phase_loads_r_3', 'phase_loads_y_3', 'phase_loads_b_3', 'phase_loads_r_4','phase_loads_y_4', 'phase_loads_b_4', 'phase_loads_r_5',
    'phase_loads_y_5', 'phase_loads_b_5').filter(dtupdate__date=today, save_status=True).order_by('-dtupdate')

    title = f' {today} Load Checks Inspections'


    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context = {
        'data': lvinspections,
        'regions': Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title': today

    }
    return render(request, 'lv/loadchecks/global_loadchecks.html', context)

@login_required(login_url="login")
def county_loadchecks_pages(request):
    county = request.user.userprofile.county
    today = date.today()
    lvinspections = LoadChecks.objects.values('id', 'substation__ssn', 'substation__name', 'dtupdate','region', 'county', 'save_status', 'aprv_status',
    'region__name', 'county__name', 'inspectedby__user_id__stid', 'primary_voltage', 'tx_rating',
    'number_of_circuits', 'voltage_ll_ry','voltage_ll_yb', 'voltage_ll_br', 'voltage_ln_rn','voltage_ln_yn', 'voltage_ln_bn', 'phase_loads_r', 'phase_loads_y', 'phase_loads_b',
    'phase_loads_r_2', 'phase_loads_y_2', 'phase_loads_b_2','phase_loads_r_3', 'phase_loads_y_3', 'phase_loads_b_3', 'phase_loads_r_4','phase_loads_y_4', 'phase_loads_b_4', 'phase_loads_r_5',
    'phase_loads_y_5', 'phase_loads_b_5').filter(
        county=county, dtupdate__date=today, save_status=True).order_by('-dtupdate')

    title = f' {today} Load Checks Inspections'


    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'title' : title

    }
    return render(request, 'lv/loadchecks/county_load_checks.html', context)

@login_required(login_url="login")
def county_loadchecks_pages_filter(request):
    county = request.user.userprofile.county
    lvinspections = LoadChecks.objects.values('id', 'substation__ssn', 'substation__name', 'dtupdate', 'region','county', 'save_status', 'aprv_status',
    'region__name', 'county__name', 'inspectedby__user_id__stid','primary_voltage', 'tx_rating','number_of_circuits', 'voltage_ll_ry', 'voltage_ll_yb', 'voltage_ll_br',
    'voltage_ln_rn', 'voltage_ln_yn', 'voltage_ln_bn', 'phase_loads_r','phase_loads_y', 'phase_loads_b','phase_loads_r_2', 'phase_loads_y_2', 'phase_loads_b_2',
    'phase_loads_r_3', 'phase_loads_y_3', 'phase_loads_b_3','phase_loads_r_4', 'phase_loads_y_4', 'phase_loads_b_4','phase_loads_r_5','phase_loads_y_5', 'phase_loads_b_5').filter(
        county=county,save_status=True).order_by('-dtupdate')

    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'
    if 'aprvstatus' in request.GET:
        keyword = request.GET["aprvstatus"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_status=keyword)
        # elif keyword == 'Approved':
        #     lvinspections = lvinspections.filter(aprv_status=keyword)
        title = f' {keyword} SSN Commissions'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'title' : title

    }
    return render(request, 'lv/loadchecks/county_load_checks.html', context)
@login_required(login_url="login")
def loadchecks_update(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')
    sub_inspection = get_object_or_404(LoadChecks, id=pk)

    if request.method == 'POST':
        sub_form = LoadChecksForm(request.POST, instance=sub_inspection)
        if sub_form.is_valid():
            poled = sub_form.save(commit=False)
            poled.substation = sub_inspection.substation
            poled.primary_voltage = sub_form.cleaned_data['primary_voltage']
            poled.tx_rating = sub_form.cleaned_data['tx_rating']
            poled.number_of_circuits = sub_form.cleaned_data['number_of_circuits']
            poled.voltage_ll_ry = sub_form.cleaned_data['voltage_ll_ry']
            poled.voltage_ll_yb = sub_form.cleaned_data['voltage_ll_yb']
            poled.voltage_ll_br = sub_form.cleaned_data['voltage_ll_br']
            poled.voltage_ln_rn = sub_form.cleaned_data['voltage_ln_rn']
            poled.voltage_ln_yn = sub_form.cleaned_data['voltage_ln_yn']
            poled.voltage_ln_bn = sub_form.cleaned_data['voltage_ln_bn']
            poled.phase_loads_r = sub_form.cleaned_data['phase_loads_r']
            poled.phase_loads_y = sub_form.cleaned_data['phase_loads_y']
            poled.phase_loads_b = sub_form.cleaned_data['phase_loads_b']
            poled.phase_loads_r_2 = sub_form.cleaned_data['phase_loads_r_2']
            poled.phase_loads_y_2 = sub_form.cleaned_data['phase_loads_y_2']
            poled.phase_loads_b_2 = sub_form.cleaned_data['phase_loads_b_2']
            poled.phase_loads_r_3 = sub_form.cleaned_data['phase_loads_r_3']
            poled.phase_loads_y_3 = sub_form.cleaned_data['phase_loads_y_3']
            poled.phase_loads_b_3 = sub_form.cleaned_data['phase_loads_b_3']
            poled.phase_loads_r_4 = sub_form.cleaned_data['phase_loads_r_4']
            poled.phase_loads_y_4 = sub_form.cleaned_data['phase_loads_y_4']
            poled.phase_loads_b_4 = sub_form.cleaned_data['phase_loads_b_4']
            poled.phase_loads_r_5 = sub_form.cleaned_data['phase_loads_r_5']
            poled.phase_loads_y_5 = sub_form.cleaned_data['phase_loads_y_5']
            poled.phase_loads_b_5 = sub_form.cleaned_data['phase_loads_b_5']
            poled.county = request.user.userprofile.county
            poled.region = request.user.userprofile.region
            poled.inspectedby = request.user.userprofile

            if request.POST.get("finalsubmission"):
                with transaction.atomic():
                    poled.save_status = True
                    poled.save()
                messages.success(request, 'The Loaod Checks was submitted successfully.')
                return redirect('lv:loadchecks-my')

            elif request.POST.get("draft"):
                poled.save_status = False
                poled.save()
                messages.success(request, 'The Load Checks Inspection was saved as a draft successfully.')
                return redirect('lv:loadchecks-my')
        else:
            print('invalid form')
            print(sub_form.errors)
    else:
        sub_form = LoadChecksForm(instance=sub_inspection)

    context={
        'substation_id': sub_inspection.id,
        'sub_form': sub_form,
        'ssn' : sub_inspection.substation.name
    }
    return render(request, 'lv/loadchecks/load_checks_new.html', context)

@login_required(login_url="login")
def loadchecks_my(request):
    myloadchecks = LoadChecks.objects.select_related('substation', 'inspectedby').order_by('-dtupdate').values(
        'id', 'substation__ssn', 'substation__name', 'dtupdate', 'save_status', 'aprv_status').filter(
        inspectedby=request.user.userprofile).order_by('-dtupdate')
    paginator = Paginator(myloadchecks, 100)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context = {
        'title': 'My Load Checks',
        'data': paged_uploads
    }
    return render(request, 'lv/network_myinspections.html', context)
@login_required(login_url="login")
def load_checks_new(request, pk=None):
    campaign = request.user.userprofile.campaign
    ssn = get_object_or_404(Substation, id=pk)
    any_pending = LoadChecks.objects.filter(save_status=False, inspectedby=request.user.userprofile)

    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')

    if any_pending:
        messages.error(request, 'You have an inspection that is saved as draft. Submit and click on new Inspection.')
        return redirect('lv:loadchecks-my')
    new_inspection = LoadChecks.objects.create(substation=ssn, inspectedby=request.user.userprofile)
    if new_inspection:
        messages.success(request, 'A Draft of the New Inspection was saved successfully. Open to continue with the inspection')
        return redirect('lv:loadchecks-my')

    context = {
        'data': ssn,
        'inspection_id' : new_inspection.id,

    }
    return render(request,'lv/ssn_dashboard.html', context)

@login_required(login_url="login")
def ssn_print(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)


    ssn = Substation.objects.select_related("county","region","make")
    writer.writerow(
        [
            "SSN",
            "NAME",
            "GNUMBER",
            "COUNTY",
            "REGION",
            "INTERNAL CODE",
            "FEEDEROFELEMENT",
            "DA",
            "RATING",
            "VOLTAGE",
            "YOM",
            "MAKE"

        ]
    )
    for meter in ssn:
        writer.writerow(
            [
                meter.ssn,
                meter.name,
                meter.gnumber,
                meter.county,
                meter.region,
                meter.internalcode,
                meter.feederofelement,
                meter.da,
                meter.rating,
                meter.voltage,
                meter.yom,
                meter.make

            ]
        )

    response["Content-Disposition"] = (
        'attachment; filename="SUBSTATIONS.csv" '
    )
    return response

@login_required(login_url="login")
def polemaintenance_delete(request, pk):
    lv  = Poledefects_maintenance.objects.get(id=pk)

    if request.method =='POST':
        lv.delete()
        messages.success(request, 'The Pole Maintenance Inspection was deleted successfully')
        return redirect('lv:poledefects-maintenance-my')
    context = {'object' : lv}
    return render(request, 'lv/poledefects/delete_polemaintenance.html', context)

@login_required(login_url="login")
def global_lv_today(request):
    today = date.today()
    lvinspections = list(Lvinspection.objects.values(
        'dtupdate','latitude','longitude','substation__name','inspectedby__user__stid','retention_req',
        'traceclear_span','conductors_uprate_span','pme_missing_poles','lv_overdistance_l','illegal_connections_l','poshomills_onsingle_p_n'
    ).filter(dtupdate__date=today,aprv_status=True))
    # lvmaintenance = MaintainLVinspection.objects.values('dtupdate')
    # substation = Substation.objects.all()
    # result_list = lvinspections.union(lvmaintenance)




    context = {
    'lvinspections' : lvinspections
    }
    return render(request, "lv/lvinspections/global_lv_today.html", context)

@login_required(login_url="login")
def lv_delete_pole(request, pk):
    lv = Poledefects.objects.get(id=pk)

    if request.method == "POST":
        with transaction.atomic():
            lv.delete()
        messages.success(request, "The Pole Inspection was deleted successfully")
        return redirect("lv:lvinspection-my")
    context = {"object": lv}
    return render(request, "lv/poledelete_confirmation.html", context)

@login_required(login_url="login")
def region_lvinspections(request):
    region = request.user.userprofile.region
    #DATE_RANGE = datetime.datetime.today() - datetime.timedelta(days=360)
    oveall_inspected = Lvinspection.objects.select_related('substation','region').values(
       "id", "dtupdate",'substation__name','county__name','aprv_dt','region','county'
    ).filter(aprv_status=True, region=region)
    oveall_maintenance = MaintainLVinspection.objects.select_related('lvinspection__county','lvinspection__region').values(
        "id", "dtupdate", 'lvinspection__substation__name', 'lvinspection__county__name', 'aprv_dt'
    ).filter(aprv_status=True,lvinspection__region=region)
    overall_substation = SubstationInspection.objects.select_related('county','region').values('id','dtupdate').filter(aprv_status=True,region=region)
    ovearll_txfailure = TxFailure.objects.select_related('county','region').values('id').filter(aprv_status=True,region=region)
    overall_commission = Commission_substation.objects.select_related('county','region').values('id').filter(aprv_status=True,region=region)
    poledefects = Poledefects.objects.select_related('county','region').values('region','county','id','defect_type').filter(status=False,region=region)
    overall_pole_maint = Poledefects_maintenance.objects.select_related('county','region').values('id').filter(aprv_status=True,region=region)
    overall_substation_main = SubstationMaintenance.objects.select_related('county','region').values('id', 'dtupdate').filter(
        aprv_status=True,region=region)
    ssn = Substation.objects.select_related('region').filter(region=region)
    overall_mv = Mvinspection.objects.select_related('feeder','county').values('id','dtupdate').filter(aprv_status=True,feeder__region=region)

    def PoleDefects_analysis():
        df = read_frame(poledefects)
        df = df.groupby(by='defect_type', as_index=False, sort=False)['id'].count()
        names = df.defect_type
        values = df.id
        df = px.pie(df, values=values, names=names, title='Defects Type Analysis')
        df.update_traces(textposition='inside', textinfo='percent+label')
        df.update_layout(margin=dict(l=20, r=20, b=20), ),
        df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df

    def poledefects_region_trend():
        df = read_frame(poledefects)
        df = df.groupby(by="county", as_index=False, sort=False)["id"].count()
        df = px.bar(
            df,
            x=df.county,
            y=df.id,
            title="County Pole Defects",
            text_auto=True,
            text=df.id,
            labels={"id": "COUNT", "county": "COUNTIES"},
        )
        df_region_trend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_region_trend

    def region_trend():
        df = read_frame(oveall_inspected)
        df["dtupdate"] = pd.to_datetime(df["dtupdate"]).dt.date
        df = df.groupby(by="county", as_index=False, sort=False)["id"].count()
        df = px.bar(
            df,
            x=df.county,
            y=df.id,
            title="County LV Inspection",
            text_auto=True,
            text=df.id,
            labels={"id": "INSPECTIONS", "county": "COUNTIES"},
        )
        df_region_trend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_region_trend

    def daily_trend():
        df = read_frame(oveall_inspected)
        df["dtupdate"] = pd.to_datetime(df["dtupdate"]).dt.date
        df = df.groupby(by="dtupdate", as_index=False, sort=False)["id"].count()
        df = px.bar(
            df,
            x=df.dtupdate,
            y=df.id,
            title=f"Daily Overall LV Inspections",
            text_auto=True,
            text=df.id,
            labels={"id": "Lv Count", "dtupdate": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    def daily_trend_maintenace():
        df = read_frame(oveall_maintenance)
        df["dtupdate"] = pd.to_datetime(df["dtupdate"]).dt.date
        df = df.groupby(by="dtupdate", as_index=False, sort=False)["id"].count()
        df = px.bar(
            df,
            x=df.dtupdate,
            y=df.id,
            title=f"Daily Overall LV Maintenance",
            text_auto=True,
            text=df.id,
            labels={"id": "Lv Count", "dtupdate": "Date"},
        )
        df_daily_m = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daily_m

    oveall_inspected1 = {}
    oveall_maintenance1 = {}
    datefrom = []
    dateto = []
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            oveall_inspected1 = oveall_inspected.filter(substation__ssn__icontains=keyword)
            oveall_maintenance1 = oveall_maintenance.filter(lvinspection__substation__ssn__icontains=keyword)

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        if datefrom and dateto:
            oveall_inspected1 = oveall_inspected.filter(dtupdate__gte=datefrom,dtupdate__lte=dateto)
            oveall_maintenance1 = oveall_maintenance.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)


    context ={
    'lvdaily' : daily_trend,
    'region_trend' : region_trend(),
    'data': oveall_inspected1,
    'data1':oveall_maintenance1,
    'lvglobal_count' : oveall_inspected, #oveall_inspected.filter(dtupdate__gte=DATE_RANGE).count(),
    'lv_maintenance_global_count': oveall_maintenance, #oveall_maintenance.filter(dtupdate__gte=DATE_RANGE).count(),
    'overall_substation' : overall_substation,
    'ovearll_txfailure' : ovearll_txfailure,
    'overall_commission' : overall_commission,
    'overall_pole_maint' : overall_pole_maint,
    'daily_trend_maintenace' : daily_trend_maintenace,
    'datefrom' : datefrom,
    'dateto' : dateto,
    'poledefects' : poledefects,
    'poledefects_region_trend' : poledefects_region_trend,
    'PoleDefects_analysis' : PoleDefects_analysis,
    'overall_substation_main' : overall_substation_main,
    'ssn' : ssn,
    'overall_mv' : overall_mv,
    'region' : region

    }
    return render(request, 'lv/lv_region.html', context)
    

@login_required(login_url="login")
def county_pole_defects_pages_filter(request):
    county = request.user.userprofile.county
    lvinspections = Poledefects.objects.select_related('region', 'county', 'substation', 'inspectedby','lvinspection').values(
        'id', 'substation__ssn', 'substation__name', 'dtupdate', 'region', 'county', 'location',
        'region__name', 'county__name', 'inspectedby__user_id__stid',
        'defect_type', 'pole_type', 'location', 'status', 'x', 'y').filter(county=county).order_by('-dtupdate')

    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'
    if 'maintained' in request.GET:
        keyword = request.GET["maintained"]
        if keyword:
            lvinspections = lvinspections.filter(status=keyword)
        # elif keyword == 'Approved':
        #     lvinspections = lvinspections.filter(aprv_status=keyword)
        title = f' {keyword} Pole Defects'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'title' : title

    }
    return render(request, 'lv/poledefects/county_pole_defects_pages.html', context)

@login_required(login_url="login")
def county_pole_defects_pages(request):
    county = request.user.userprofile.county
    today = date.today()
    lvinspections = Poledefects.objects.select_related('region', 'county', 'substation', 'inspectedby','lvinspection').values(
        'id', 'substation__ssn', 'substation__name', 'dtupdate', 'region', 'county', 'location',
        'region__name', 'county__name', 'inspectedby__user_id__stid',
        'defect_type', 'pole_type', 'location', 'status', 'x', 'y').filter(county=county, dtupdate__date=today).order_by('-dtupdate')



    title = f' {today} Pole Defects'


    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(inspection__substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'title' : title

    }
    return render(request, 'lv/poledefects/county_pole_defects_pages.html', context)
    

@login_required(login_url="login")
def substation_maintenance_print(request, pk=None):
    lvinspection = get_object_or_404(SubstationMaintenance, id=pk)
    context ={
        'lvinspection' : lvinspection,
    }

    return render(request, 'lv/substation/substation_maintenance_print.html', context)
    
@login_required(login_url="login")
def county_substation_maintenance_pages_filter(request):
    county = request.user.userprofile.county
    lvinspections = SubstationMaintenance.objects.select_related('aprv_by', 'inspectedby', 'inspection').values(
        'id', 'inspection__substation__ssn', 'inspection__substation__name', 'dtupdate', 'region', 'county',
        'save_status', 'aprv_status', 'region__name', 'county__name',
        'inspectedby__user_id__stid', 'aprv_by__user_id__stid', 'fusesize', 'sizeoflvconductor', 'noofcircuits_added',
        'hvearth_intact', 'neutralearth_intact', 'surgediverters_replaced', 'lvleads_size', 'txloading',
        'c_tx_structure', 'c_fuse_carriers_replaced', 'c_fuse_bar', 'txwiring', 'maintenance_notes', 'txposition'
    ).filter(county=county,save_status=True).order_by('-dtupdate')

    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(inspection__substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'
    if 'aprvstatus' in request.GET:
        keyword = request.GET["aprvstatus"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_status=keyword)
        # elif keyword == 'Approved':
        #     lvinspections = lvinspections.filter(aprv_status=keyword)
        title = f' {keyword} Substation Maintenances'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'title' : title

    }
    return render(request, 'lv/substation/county_substation_maintenance_pages.html', context)

@login_required(login_url="login")
def county_substation_maintenance_pages(request):
    county = request.user.userprofile.county
    today = date.today()
    lvinspections = SubstationMaintenance.objects.select_related('aprv_by', 'inspectedby', 'inspection').values(
        'id', 'inspection__substation__ssn', 'inspection__substation__name', 'dtupdate', 'region', 'county',
        'save_status', 'aprv_status', 'region__name', 'county__name',
        'inspectedby__user_id__stid', 'aprv_by__user_id__stid', 'fusesize', 'sizeoflvconductor', 'noofcircuits_added',
        'hvearth_intact', 'neutralearth_intact', 'surgediverters_replaced', 'lvleads_size', 'txloading',
        'c_tx_structure', 'c_fuse_carriers_replaced', 'c_fuse_bar', 'txwiring', 'maintenance_notes', 'txposition'
    ).filter(county=county, dtupdate__date=today, save_status=True).order_by('-dtupdate')

    title = f' {today} Substation Maintenances'


    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(inspection__substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'title' : title

    }
    return render(request, 'lv/substation/county_substation_maintenance_pages.html', context)
    

@login_required(login_url="login")
def global_poledefects_filter(request):
    lvinspections = Poledefects.objects.select_related('region', 'county', 'substation', 'inspectedby', 'lvinspection').values(
        'id', 'substation__ssn', 'substation__name', 'dtupdate', 'region', 'county','location',
        'region__name', 'county__name', 'inspectedby__user_id__stid',
        'defect_type', 'pole_type', 'location', 'status', 'x', 'y').order_by('-dtupdate')

    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(region=keyword)
        title = f'region {keyword}'
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(county=keyword)
        title = f'county {keyword}'
    if 'maintained' in request.GET:
        keyword = request.GET["maintained"]
        if keyword:
            lvinspections = lvinspections.filter(status=keyword)
        # elif keyword == 'Approved':
        #     lvinspections = lvinspections.filter(aprv_status=keyword)
        title = f' {keyword} Pole Defects'

    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'Pole Defects {keyword}'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title' : title

    }
    return render(request, 'lv/poledefects/global_pole_defects.html', context)

@login_required(login_url="login")
def global_pole_defects(request):
    today = date.today()
    lvinspections = Poledefects.objects.select_related('region', 'county', 'substation', 'inspectedby', 'lvinspection').values(
        'id', 'substation__ssn', 'substation__name', 'dtupdate', 'region', 'county','location',
        'region__name', 'county__name', 'inspectedby__user_id__stid',
        'defect_type', 'pole_type', 'location', 'status', 'x', 'y').filter(dtupdate__date=today).order_by('-dtupdate')

    title = f' {today} Pole Defects'

    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(region=keyword)
        title = f'region {keyword}'
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(county=keyword)
        title = f'county {keyword}'
    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'insspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title' : title

    }
    return render(request, 'lv/poledefects/global_pole_defects.html', context)
    

@login_required(login_url="login")
def county_substation_inspection_pages_filter(request):
    county = request.user.userprofile.county
    lvinspections = SubstationInspection.objects.select_related('region', 'county', 'substation', 'inspectedby','aprv_by').values(
        'id', 'substation__ssn', 'substation__name', 'dtupdate', 'region', 'county', 'save_status', 'aprv_status',
        'region__name', 'county__name', 'inspectedby__user_id__stid', 'aprv_by__user_id__stid',
        'serialno', 'voltage', 'kvarating', 'gnumber', 'make__name', 'yom', 'location', 'fusesize', 'sizeoflvconductor',
        'noofcircuits', 'hvearth_intact', 'hvearth_values', 'neutralearth_intact', 'neutralvearth_values',
        'surgearrestors', 'surgearrestors_values', 'arcinghorns', 'arcinghorns', 'gapset_values', 'lvleads_size',
        'txloading', 'txloading_yes', 'load_distributionby', 'c_tx_structure', 'c_fuse_carriers', 't_fuse_bar',
        'c_fuse_bar', 'txwiring', 'c_txwiring'
    ).filter(county=county,save_status=True).order_by('-dtupdate')



    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'
    if 'aprvstatus' in request.GET:
        keyword = request.GET["aprvstatus"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_status=keyword)
        # elif keyword == 'Approved':
        #     lvinspections = lvinspections.filter(aprv_status=keyword)
        title = f' {keyword} Substation Inspections'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'title' : title

    }
    return render(request, 'lv/substation/county_substation_inspection_pages.html', context)

@login_required(login_url="login")
def county_substation_inspection_pages(request):
    county = request.user.userprofile.county
    today = date.today()
    lvinspections = SubstationInspection.objects.select_related('region', 'county', 'substation', 'inspectedby','aprv_by').values(
        'id', 'substation__ssn', 'substation__name', 'dtupdate', 'region', 'county', 'save_status', 'aprv_status',
        'region__name', 'county__name', 'inspectedby__user_id__stid', 'aprv_by__user_id__stid',
        'serialno', 'voltage', 'kvarating', 'gnumber', 'make__name', 'yom', 'location', 'fusesize', 'sizeoflvconductor',
        'noofcircuits', 'hvearth_intact', 'hvearth_values', 'neutralearth_intact', 'neutralvearth_values',
        'surgearrestors', 'surgearrestors_values', 'arcinghorns', 'arcinghorns', 'gapset_values', 'lvleads_size',
        'txloading', 'txloading_yes', 'load_distributionby', 'c_tx_structure', 'c_fuse_carriers', 't_fuse_bar',
        'c_fuse_bar', 'txwiring', 'c_txwiring'
    ).filter(county=county, dtupdate__date=today, save_status=True).order_by('-dtupdate')


    title = f' {today} Substation Inspections'


    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'title' : title

    }
    return render(request, 'lv/substation/county_substation_inspection_pages.html', context)
    

@login_required(login_url="login")
def county_commission_pages_filter(request):
    county = request.user.userprofile.county
    lvinspections = Commission_substation.objects.values('id', 'substation__ssn', 'substation__name', 'dtupdate','region', 'county', 'save_status', 'aprv_status',
    'region__name', 'county__name','inspectedby__user_id__stid', 'aprv_by__user_id__stid','dt_commission', 'control_center', 'ptw_no', 'typeofchange',
    'typeofload', 'dcs_reference', 'rerec_reference','internalorder', 'make__name', 'gnumber','yom', 'kvarating', 'voltage', 'txweight', 'txstatus',
    'htisolation', 'noofcircuits', 'lvprotection', 'txprotection','surged_red', 'surged_yellow', 'surged_blue','arcinghorns_single', 'arcinghorns_dublex', 'nooftappositions',
    'voltagetappingsetattap', 'earthval_at_structure_ht','earthval_at_structure_sd', 'lv_onespanaway').filter(
        county=county,save_status=True).order_by('-dtupdate')

    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'
    if 'aprvstatus' in request.GET:
        keyword = request.GET["aprvstatus"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_status=keyword)
        # elif keyword == 'Approved':
        #     lvinspections = lvinspections.filter(aprv_status=keyword)
        title = f' {keyword} SSN Commissions'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'title' : title

    }
    return render(request, 'lv/commission/county_commission_pages.html', context)
    
@login_required(login_url="login")
def county_commission_pages(request):
    county = request.user.userprofile.county
    today = date.today()
    lvinspections = Commission_substation.objects.values('id', 'substation__ssn', 'substation__name', 'dtupdate','region', 'county', 'save_status', 'aprv_status',
    'region__name', 'county__name', 'inspectedby__user_id__stid','aprv_by__user_id__stid', 'dt_commission', 'control_center',
    'ptw_no', 'typeofchange','typeofload', 'dcs_reference', 'rerec_reference','internalorder', 'make__name', 'gnumber', 'yom', 'kvarating',
    'voltage', 'txweight', 'txstatus','htisolation', 'noofcircuits', 'lvprotection', 'txprotection','surged_red', 'surged_yellow', 'surged_blue',
    'arcinghorns_single', 'arcinghorns_dublex', 'nooftappositions','voltagetappingsetattap', 'earthval_at_structure_ht',
    'earthval_at_structure_sd', 'lv_onespanaway').filter(
        county=county, dtupdate__date=today, save_status=True).order_by('-dtupdate')

    title = f' {today} Commission Inspections'


    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'title' : title

    }
    return render(request, 'lv/commission/county_commission_pages.html', context)
    

@login_required(login_url="login")
def global_commissions_filter(request):
    lvinspections = Commission_substation.objects.values('id', 'substation__ssn','substation__name','dtupdate','region','county', 'save_status','aprv_status','region__name','county__name',
       'inspectedby__user_id__stid','aprv_by__user_id__stid','dt_commission','control_center','ptw_no','typeofchange','typeofload','dcs_reference','rerec_reference','internalorder','make__name','gnumber',
       'yom','kvarating','voltage','txweight','txstatus','htisolation','noofcircuits','lvprotection','txprotection','surged_red','surged_yellow','surged_blue','arcinghorns_single','arcinghorns_dublex','nooftappositions','voltagetappingsetattap','earthval_at_structure_ht','earthval_at_structure_sd','lv_onespanaway').filter(
        aprv_status=True).order_by('-dtupdate')
    #print(lvinspections[0]['dtupdate'].date())
    #print(datetime.now().date())
    today = today = timezone.now().date()

    # todays filter lvinspections.filter(Q(dtupdate__date=today))

    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(region=keyword)
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(county=keyword)
    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)


    paginator = Paginator(lvinspections, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)


    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name')

    }
    return render(request, 'lv/commission/global_commissions.html', context)
@login_required(login_url="login")
def global_commissions(request):
    today = date.today()
    lvinspections = Commission_substation.objects.values('id', 'substation__ssn','substation__name','dtupdate','region','county', 'save_status','aprv_status','region__name','county__name',
       'inspectedby__user_id__stid','aprv_by__user_id__stid','dt_commission','control_center','ptw_no','typeofchange','typeofload','dcs_reference','rerec_reference','internalorder','make','gnumber',
       'yom','kvarating','voltage','txweight','txstatus','htisolation','noofcircuits','lvprotection','txprotection','surged_red','surged_yellow','surged_blue','arcinghorns_single','arcinghorns_dublex','nooftappositions','voltagetappingsetattap','earthval_at_structure_ht','earthval_at_structure_sd','lv_onespanaway').filter(
        aprv_status=True,dtupdate__date=today).order_by('-dtupdate')
    #print(lvinspections[0]['dtupdate'].date())
    #print(datetime.now().date())
    today = today = timezone.now().date()

    # todays filter lvinspections.filter(Q(dtupdate__date=today))

    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(region=keyword)
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(county=keyword)
    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)


    paginator = Paginator(lvinspections, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)


    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name')

    }
    return render(request, 'lv/commission/global_commissions.html', context)
    

@login_required(login_url="login")
def county_failure_pages_filter(request):
    county = request.user.userprofile.county
    lvinspections = TxFailure.objects.select_related('region', 'county', 'substation', 'userprofile').values(
        'id', 'substation__ssn', 'voltage', 'kvarating', 'gnumber', 'make', 'yom', 'tx_position', 'incidence_no',
        'dt_failure', 'failure_type', 'tx_status', 'weathercond',
        'hvearth_values', 'neutralvearth_values', 'surgearrestors_values', 'expulsionondirectlink', 'causeoffailure',
        'substation__name', 'dtupdate', 'region', 'county', 'save_status', 'aprv_status', 'region__name',
        'county__name',
        'inspectedby__user_id__stid', 'aprv_by__user_id__stid'
    ).filter(county=county,save_status=True).order_by('-dtupdate')


    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'
    if 'aprvstatus' in request.GET:
        keyword = request.GET["aprvstatus"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_status=keyword)
        # elif keyword == 'Approved':
        #     lvinspections = lvinspections.filter(aprv_status=keyword)
        title = f' {keyword} TX Failures'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'title' : title

    }
    return render(request, 'lv/txfailure/county_failure_pages.html', context)
    
@login_required(login_url="login")
def county_failure_pages(request):
    county = request.user.userprofile.county
    today = date.today()
    lvinspections = TxFailure.objects.select_related('region', 'county', 'substation', 'userprofile').values(
        'id', 'substation__ssn', 'voltage', 'kvarating', 'gnumber', 'make', 'yom', 'tx_position', 'incidence_no',
        'dt_failure', 'failure_type', 'tx_status', 'weathercond',
        'hvearth_values', 'neutralvearth_values', 'surgearrestors_values', 'expulsionondirectlink', 'causeoffailure',
        'substation__name', 'dtupdate', 'region', 'county', 'save_status', 'aprv_status', 'region__name',
        'county__name',
        'inspectedby__user_id__stid', 'aprv_by__user_id__stid'
    ).filter(county=county,dtupdate__date=today,save_status=True).order_by('-dtupdate')



    title = f' {today} TX Failures'


    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'title' : title

    }
    return render(request, 'lv/txfailure/county_failure_pages.html', context)

@login_required(login_url="login")
def county_lvmaintenance_pages_filter(request):
    county = request.user.userprofile.county
    lvinspections = MaintainLVinspection.objects.values(
        'id', 'lvinspection__substation__ssn', 'lvinspection__substation__name', 'dtupdate', 'lvinspection__region',
        'lvinspection__county', 'save_status', 'aprv_status', 'lvinspection__region__name',
        'lvinspection__county__name',
        'inspectedby__user_id__stid', 'aprv_by__user_id__stid', 'retention_req', 'traceclear_span',
        'conductors_uprate_span', 'pme_missing_poles', 'lv_overdistance_l', 'illegal_connections_l',
        'jumper_rehab_sect', 'reconducturing_pvc_l', 'poshomills_onsingle_p_n', 'inspect_notes', 'txposition'
    ).filter(lvinspection__county=county,save_status=True).order_by('-dtupdate')




    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(lvinspection__substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'
    if 'aprvstatus' in request.GET:
        keyword = request.GET["aprvstatus"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_status=keyword)
        # elif keyword == 'Approved':
        #     lvinspections = lvinspections.filter(aprv_status=keyword)
        title = f' {keyword} LV Maintenance Inspections'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'title' : title

    }
    return render(request, 'lv/lvmaitenance/county_lvmaintenance_pages.html', context)
@login_required(login_url="login")
def county_lvmaintenance_pages(request):
    county = request.user.userprofile.county
    today = date.today()
    lvinspections = MaintainLVinspection.objects.values(
        'id', 'lvinspection__substation__ssn', 'lvinspection__substation__name', 'dtupdate', 'lvinspection__region',
        'lvinspection__county', 'save_status', 'aprv_status', 'lvinspection__region__name',
        'lvinspection__county__name','lvinspection__kvarating',
        'inspectedby__user_id__stid', 'aprv_by__user_id__stid', 'retention_req', 'traceclear_span',
        'conductors_uprate_span', 'pme_missing_poles', 'lv_overdistance_l', 'illegal_connections_l',
        'jumper_rehab_sect', 'reconducturing_pvc_l', 'poshomills_onsingle_p_n', 'inspect_notes', 'txposition'
    ).filter(lvinspection__county=county, dtupdate__date=today, save_status=True).order_by('-dtupdate')

    title = f' {today} LV Maintenance Inspections'


    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(lvinspection__substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'title' : title

    }
    return render(request, 'lv/lvmaitenance/county_lvmaintenance_pages.html', context)
    

@login_required(login_url="login")
def county_lv_pages_filter(request):
    county = request.user.userprofile.county
    lvinspections = Lvinspection.objects.values('id', 'substation__ssn', 'substation__name', 'dtupdate', 'region',
     'county', 'save_status', 'aprv_status', 'region__name', 'county__name','inspectedby__user_id__stid', 'aprv_by__user_id__stid', 'retention_req',
    'traceclear_span', 'conductors_uprate_span', 'pme_missing_poles','lv_overdistance_l', 'illegal_connections_l', 'jumper_rehab_sect', 'reconducturing_pvc_l',
      'poshomills_onsingle_p_n', 'inspect_notes').filter(county=county,save_status=True).order_by('-dtupdate')

    if 'aprvstatus' in request.GET:
        keyword = request.GET["aprvstatus"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_status=keyword)
        # elif keyword == 'Approved':
        #     lvinspections = lvinspections.filter(aprv_status=keyword)
        title = f' {keyword} LV Inspections'
    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto} LV Inspections'

    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title' : title

    }
    return render(request, 'lv/lvinspections/county_lv_pages.html', context)

@login_required(login_url="login")
def county_lv_pages(request):
    county = request.user.userprofile.county
    today = date.today()
    lvinspections = Lvinspection.objects.values('id', 'substation__ssn', 'substation__name', 'dtupdate', 'region',
     'county', 'save_status', 'aprv_status', 'region__name', 'county__name','inspectedby__user_id__stid', 'aprv_by__user_id__stid', 'retention_req',
    'traceclear_span', 'conductors_uprate_span', 'pme_missing_poles','lv_overdistance_l', 'illegal_connections_l', 'jumper_rehab_sect', 'reconducturing_pvc_l',
      'poshomills_onsingle_p_n', 'inspect_notes').filter(county=county,dtupdate__date=today,save_status=True).order_by('-dtupdate')

    title = f' {today} LV Inspections'


    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title' : title

    }
    return render(request, 'lv/lvinspections/county_lv_pages.html', context)
    

@login_required(login_url="login")
def substation_inspection_print(request, pk=None):
    lvinspection = get_object_or_404(SubstationInspection, id=pk)
    context ={
        'lvinspection' : lvinspection,
    }

    return render(request, 'lv/substation/substation_inspection_print.html', context)

@login_required(login_url="login")
def substation_maintenance_approve(request, pk=None):
    lv_inspection = get_object_or_404(SubstationMaintenance, id=pk)

    if request.method == 'POST':
        form = SubstationMaintenanceApproveForm(request.POST, instance=lv_inspection)

        if form.is_valid():
            regis = form.save(commit=False)
            regis.aprv_notes = form.cleaned_data['aprv_notes']
            regis.aprv_key = form.cleaned_data['aprv_key']
            regis.aprv_by = request.user.userprofile
            regis.aprv_status = True
            regis.aprv_dt = date.today()
            regis.save()
            messages.success(request, 'The Substation Maintenance Report was Approved/Declined successfully.')
            return redirect('lv:county-substation-maintenance-pages')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = SubstationMaintenanceApproveForm(instance=lv_inspection)

    context = {
        'lvinspection': lv_inspection,
        'form' : form
    }
    return render(request, 'lv/substation/substation_maitenance_approve.html', context)

@login_required(login_url="login")
def substation_maintenance_pending_app(request):
    county = request.user.userprofile.county
    sub_maintenance_pending_app = SubstationMaintenance.objects.select_related('county','inspection').filter(county=county,aprv_status='False')#.values('id','dtadd','substation')

    context ={
        'data' : sub_maintenance_pending_app,
        'title':'Substation Maintenance Inspections Pending Approval',
        'county': county,

    }
    return render(request, 'lv/county_substation_maintenance.html', context)

@login_required(login_url="login")
def substation_maintenance_update(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')
    inspection = get_object_or_404(SubstationMaintenance, id=pk)

    if request.method == 'POST':
        sub_form = MaintainSubstationinspectionForm(request.POST, instance=inspection)
        if sub_form.is_valid():
            poled = sub_form.save(commit=False)
            poled.inspection = inspection.inspection
            poled.fusesize = sub_form.cleaned_data['fusesize']
            poled.sizeoflvconductor = sub_form.cleaned_data['sizeoflvconductor']
            poled.noofcircuits_added = sub_form.cleaned_data['noofcircuits_added']
            poled.hvearth_intact = sub_form.cleaned_data['hvearth_intact']
            poled.neutralearth_intact = sub_form.cleaned_data['neutralearth_intact']
            poled.surgediverters_replaced = sub_form.cleaned_data['surgediverters_replaced']
            poled.lvleads_size = sub_form.cleaned_data['lvleads_size']
            poled.txloading = sub_form.cleaned_data['txloading']
            poled.c_tx_structure = sub_form.cleaned_data['c_tx_structure']
            poled.c_fuse_carriers_replaced = sub_form.cleaned_data['c_fuse_carriers_replaced']
            poled.c_fuse_bar = sub_form.cleaned_data['c_fuse_bar']
            poled.txwiring = sub_form.cleaned_data['txwiring']
            poled.maintenance_notes = sub_form.cleaned_data['maintenance_notes']
            poled.latitude = sub_form.cleaned_data['latitude']
            poled.longitude = sub_form.cleaned_data['longitude']
            poled.txposition = sub_form.cleaned_data['txposition']
            poled.other_defects = sub_form.cleaned_data['other_defects']
            poled.inspectedby = request.user.userprofile
            poled.county = request.user.userprofile.county
            poled.region = request.user.userprofile.region


            if request.POST.get("finalsubmission"):
                with transaction.atomic():
                    poled.save_status = True
                    poled.save()
                messages.success(request, 'The Substation Maintenance was submitted successfully.')
                return redirect('lv:substation-maintenance-my')

            if request.POST.get("draft"):
                poled.save_status = False
                poled.save()
                messages.success(request, 'The Substation Maintenance was submitted successfully.')
                return redirect('lv:substation-maintenance-my')


        else:
            print('invalid form')
            print(sub_form.errors)
    else:
        sub_form = MaintainSubstationinspectionForm(instance=inspection)

    context={

        'sub_form': sub_form,
        'lv' : inspection
    }
    return render(request, 'lv/substation/substation_maintenance_update.html', context)

@login_required(login_url="login")
def substation_maintenance_delete(request, pk):
    lv  = get_object_or_404(SubstationMaintenance, id=pk)
    if request.method =='POST':
        lv.delete()
        messages.success(request, 'The Substation Maintenance was deleted successfully')
        return redirect('lv:substation-maintenance-my')
    context = {'object' : lv}
    return render(request, 'lv/substation/sub_maintenance_delete_confirmation.html', context)
    

@login_required(login_url="login")
def substation_maintenance_my(request):
    mysubmaintenance = SubstationMaintenance.objects.select_related('inspection','inspectedby').filter(inspectedby=request.user.userprofile).order_by('-dtadd')
    #
    # paginator = Paginator(mycommissions, 20)
    # page = request.GET.get('page')
    # paged_uploads = paginator.get_page(page)

    context ={
        'title': 'My Substation Maintenance',
        'data' : mysubmaintenance
    }
    return render(request,'lv/network_myinspections.html', context)

@login_required(login_url="login")
def county_substation_maintenance_list(request):
    county = request.user.userprofile.county
    lv = SubstationMaintenance.objects.select_related('county','inspection').filter(county=county, aprv_status=True)

    context ={
        'county' : county,
        'data' : lv,
        'title':'List Of Approved Substation Maitenance Inspections',
    }
    return render(request, 'lv/county_substation_maintenance.html', context)
    

@login_required(login_url="login")
def global_substation_maintenance_filter(request):
    lvinspections = SubstationMaintenance.objects.select_related('aprv_by', 'inspectedby', 'inspection').values(
        'id','inspection', 'inspection__substation__ssn', 'inspection__substation__name', 'dtupdate', 'region', 'county',
        'save_status', 'aprv_status', 'region__name', 'county__name',
        'inspectedby__user_id__stid', 'aprv_by__user_id__stid', 'fusesize', 'sizeoflvconductor', 'noofcircuits_added',
        'hvearth_intact', 'neutralearth_intact', 'surgediverters_replaced', 'lvleads_size', 'txloading',
        'c_tx_structure', 'c_fuse_carriers_replaced', 'c_fuse_bar', 'txwiring', 'maintenance_notes','txposition','other_defects'
    ).filter(aprv_status=True).order_by('-dtupdate')

    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(region=keyword)
        title = f'region {keyword}'
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(county=keyword)
        title = f'county {keyword}'
    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title' : title

    }
    return render(request, 'lv/substation/substation_maintenance_global.html', context)

@login_required(login_url="login")
def global_substation_maintenance(request):
    today = date.today()
    lvinspections = SubstationMaintenance.objects.select_related('aprv_by','inspectedby','inspection').values(
        'id','inspection', 'inspection__substation__ssn','inspection__substation__name','dtupdate','region','county', 'save_status','aprv_status','region__name','county__name',
        'inspectedby__user_id__stid','aprv_by__user_id__stid','fusesize','sizeoflvconductor','noofcircuits_added','hvearth_intact','neutralearth_intact','surgediverters_replaced','lvleads_size','txloading','c_tx_structure','c_fuse_carriers_replaced','c_fuse_bar','txwiring','maintenance_notes','txposition','other_defects'
    ).filter(aprv_status=True,dtupdate__date=today).order_by('-dtupdate')
    #print(lvinspections[0]['dtupdate'].date())
    #print(datetime.now().date())
    today = today = timezone.now().date()

    # todays filter lvinspections.filter(Q(dtupdate__date=today))


    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(lvinspection__region=keyword)
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(lvinspection__county=keyword)
    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(lvinspection__substation__ssn__icontains=keyword)

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)


    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title' : today

    }
    return render(request, 'lv/substation/substation_maintenance_global.html', context)

@login_required(login_url="login")
def global_substation_edit(request, pk=None):
    ssn = get_object_or_404(Substation, id=pk)

    campaign = request.user.userprofile.campaign

    if request.method == "POST":
        m_form = GlobalSubstationForm(request.POST, request.FILES, instance=ssn)

        if m_form.is_valid():
            zerov = m_form.save(commit=False)
            zerov.ssn = m_form.cleaned_data["ssn"]
            zerov.name = m_form.cleaned_data["name"]
            zerov.gnumber = m_form.cleaned_data["gnumber"]
            zerov.originofelement = m_form.cleaned_data["originofelement"]
            zerov.feederofelement = m_form.cleaned_data["feederofelement"]
            zerov.physicallocation = m_form.cleaned_data["physicallocation"]
            zerov.da = m_form.cleaned_data["da"]
            zerov.lenghth = m_form.cleaned_data["lenghth"]
            zerov.rating = m_form.cleaned_data["rating"]
            zerov.volatge = m_form.cleaned_data["voltage"]
            zerov.yom = m_form.cleaned_data["yom"]
            zerov.make = m_form.cleaned_data["make"]
            zerov.county = m_form.cleaned_data["county"]
            zerov.region = m_form.cleaned_data["region"]
            zerov.createdby = request.user.userprofile
            zerov.save()
            messages.success(
                request, "The Substation Has been successfully saved."
            )
            return redirect("lv:global_ssn")
        else:
            print("invalid form")
            print(m_form.errors)

    else:
        # user_form = UserForm(instance=request.user)

        m_form = GlobalSubstationForm(instance=ssn)
    context = {
        "form": m_form,
    }

    return render(request, "lv/global_substation_new.html", context)
    

@login_required(login_url="login")
def global_sssn_search(request):
    lvinspections = Substation.objects.all()


    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(ssn__icontains=keyword)


    paginator = Paginator(lvinspections, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    context = {

        'ssn': paged_uploads,

    }
    return render(request, 'lv/global_ssn.html', context)
    

@login_required(login_url="login")
def global_ssn(request):
    ssn = Substation.objects.select_related('county','region','make')
    paginator = Paginator(ssn, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    context ={

        'ssn' : paged_uploads,

    }
    return render(request, 'lv/global_ssn.html', context)

@login_required(login_url="login")
def global_substation_filter(request):
    lvinspections = SubstationInspection.objects.select_related('region', 'county', 'substation', 'inspectedby',
                                                                'aprv_by').values(
        'id', 'substation__ssn', 'substation__name', 'dtupdate', 'region', 'county', 'save_status', 'aprv_status',
        'region__name', 'county__name', 'inspectedby__user_id__stid', 'aprv_by__user_id__stid',
        'serialno', 'voltage', 'kvarating', 'gnumber', 'make__name', 'yom', 'location', 'fusesize', 'sizeoflvconductor',
        'noofcircuits', 'hvearth_intact', 'hvearth_values', 'neutralearth_intact', 'neutralvearth_values',
        'surgearrestors', 'surgearrestors_values', 'arcinghorns', 'arcinghorns', 'gapset_values', 'lvleads_size',
        'txloading', 'txloading_yes', 'load_distributionby', 'c_tx_structure', 'c_fuse_carriers', 't_fuse_bar',
        'c_fuse_bar', 'txwiring', 'c_txwiring', 'hv_b_r','hv_r_y','hv_y_b','lv_b_n','lv_r_n','lv_y_n','insul_lve','insul_hv_lv','insul_hv_e'
    ).filter(
        aprv_status=True).order_by('-dtupdate')

    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(region=keyword)
        title = f'region {keyword}'
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(county=keyword)
        title = f'county {keyword}'
    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'inspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title' : title

    }
    return render(request, 'lv/substation/substation_global.html', context)

@login_required(login_url="login")
def global_ssnfailures_filter(request):
    lvinspections = TxFailure.objects.select_related('region','county','substation','userprofile').values(
        'id','substation__da','substation__feederofelement', 'substation__ssn','voltage','kvarating','gnumber','make','yom','tx_position','incidence_no','dt_failure','failure_type','tx_status','weathercond',
        'hvearth_values','neutralvearth_values','surgearrestors_values','expulsionondirectlink','causeoffailure','substation__name','dtupdate','region','county', 'save_status','aprv_status','region__name','county__name',
        'inspectedby__user_id__stid','aprv_by__user_id__stid'
    ).filter(aprv_status=True).order_by('-dtupdate')

    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(region=keyword)
        title = f'region {keyword}'
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(county=keyword)
        title = f'county {keyword}'
    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = f'SSN {keyword}'

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = f'insspector {keyword}'

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = f'approver {keyword}'

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title' : title

    }
    return render(request, 'lv/txfailure/global_txfailure.html', context)
@login_required(login_url="login")
def global_lvmaintenance_filter(request):
    lvinspections = MaintainLVinspection.objects.values(
        'id','lvinspection','lvinspection__substation__da','lvinspection__substation__feederofelement', 'lvinspection__substation__ssn','lvinspection__substation__name','dtupdate','lvinspection__region','lvinspection__county', 'save_status','aprv_status','lvinspection__region__name','lvinspection__county__name',
        'inspectedby__user_id__stid','aprv_by__user_id__stid','retention_req','traceclear_span','conductors_uprate_span','pme_missing_poles','lv_overdistance_l','illegal_connections_l','jumper_rehab_sect','reconducturing_pvc_l','poshomills_onsingle_p_n','inspect_notes','txposition','other_defects'
    ).filter(aprv_status=True).order_by('-dtupdate')
    #print(lvinspections[0]['dtupdate'].date())
    #print(datetime.now().date())
    today = today = timezone.now().date()

    # todays filter lvinspections.filter(Q(dtupdate__date=today))


    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(lvinspection__region=keyword)
        title = keyword
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(lvinspection__county=keyword)
        title = keyword
    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(lvinspection__substation__ssn__icontains=keyword)
        title = keyword

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = keyword

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = keyword

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'


    paginator = Paginator(lvinspections, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)


    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title': title

    }
    return render(request, 'lv/lvmaitenance/lvmaintenance_global.html', context)

@login_required(login_url="login")
def global_lv_filter(request):
    lvinspections = Lvinspection.objects.values('id','substation__make__name','substation__da','substation__feederofelement','substation__rating', 'substation__ssn','substation__name','dtupdate','region','county', 'save_status','aprv_status','region__name','county__name',
       'inspectedby__user_id__stid','aprv_by__user_id__stid','retention_req','traceclear_span','conductors_uprate_span','pme_missing_poles','lv_overdistance_l',
          'illegal_connections_l','jumper_rehab_sect','reconducturing_pvc_l','poshomills_onsingle_p_n','inspect_notes').filter(
        aprv_status=True).order_by('-dtupdate')



    # todays filter lvinspections.filter(Q(dtupdate__date=today))

    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(region=keyword)
        title = keyword
    if 'county' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date() + timedelta(days=1)
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(county=keyword,dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = keyword
    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)
        title = keyword

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)
        title = keyword

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)
        title = keyword

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)
        title = f'{datefrom} To {dateto}'

    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title' : title

    }
    return render(request, 'lv/lvinspections/lvinspections_global.html', context)
    

@login_required(login_url="login")
def global_ssnfailures(request):
    today = date.today()
    lvinspections = TxFailure.objects.select_related('region','county','substation','userprofile').values(
        'id','substation__da','substation__feederofelement', 'substation__ssn','voltage','kvarating','gnumber','make','yom','tx_position','incidence_no','dt_failure','failure_type','tx_status','weathercond',
        'hvearth_values','neutralvearth_values','surgearrestors_values','expulsionondirectlink','causeoffailure','substation__name','dtupdate','region','county', 'save_status','aprv_status','region__name','county__name',
        'inspectedby__user_id__stid','aprv_by__user_id__stid'
    ).filter(aprv_status=True,dtupdate__date=today).order_by('-dtupdate')


    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(region=keyword)
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(county=keyword)
    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)


    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title' : today

    }
    return render(request, 'lv/txfailure/global_txfailure.html', context)
    

@login_required(login_url="login")
def polemaintenance_pending_app(request):
    county = request.user.userprofile.county
    polemaintenance_pending_app = Poledefects_maintenance.objects.select_related('county').filter(county=county,aprv_status='False')#.values('id','dtadd','substation')


    context ={
        'data' : polemaintenance_pending_app,
        'title':'Pole Defects Maintenance Pending Approval',
        'county': county,


    }
    return render(request, 'lv/county_poledefects.html', context)

@login_required(login_url="login")
def polemaintenance_approve(request, pk=None):
    polemaintenance = get_object_or_404(Poledefects_maintenance, id=pk)
    poledefect = get_object_or_404(Poledefects, poledefect=polemaintenance.poledefect)


    if request.method == 'POST':
        form = MaintainPoleApproveForm(request.POST, instance=polemaintenance)

        if form.is_valid():
            regis = form.save(commit=False)
            regis.aprv_notes = form.cleaned_data['aprv_notes']
            regis.aprv_key = form.cleaned_data['aprv_key']
            regis.aprv_by = request.user.userprofile
            regis.aprv_status = True
            regis.aprv_dt = date.today()
            regis.save()
            poledefect.status = True
            poledefect.save()
            messages.success(request, 'The Pole Maintenance Report was Approved/Declined successfully.')
            return redirect('lv:county-poledefects')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = MaintainPoleApproveForm(instance=polemaintenance)

    context = {
        'lvinspection': polemaintenance,
        'form' : form
    }
    return render(request, 'lv/poledefects/polemaintenance_approve.html', context)
@login_required(login_url="login")
def poledefects_maintenance_new(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')
    poledefect = get_object_or_404(Poledefects, id=pk)
    any_pending = Poledefects_maintenance.objects.filter(save_status=False, inspectedby=request.user.userprofile)

    if any_pending:
        messages.error(request, 'You have an inspection that is saved as draft. Submit and click on new Inspection.')
        return redirect('lv:poledefects-maintenance-my')

    new_maintenance = Poledefects_maintenance.objects.create(poledefect=poledefect, inspectedby=request.user.userprofile)
    if new_maintenance:
        messages.success(request, 'A Draft of the New Pole Defect Maintebnance was saved successfully. Open to continue with the inspection')
        return redirect('lv:poledefects-maintenance-my')

    context = {
        'data': poledefect,
        'inspection_id' : new_maintenance.id,

    }
    return render(request,'lv/lvFailure_inspect.html', context)

@login_required(login_url="login")
def poledefects_maintain_update(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')
    maintainpole = get_object_or_404(Poledefects_maintenance, id=pk)

    if request.method == 'POST':
        pole_m_form = Poledefects_maintenanceForm(request.POST, request.FILES,instance=maintainpole)
        if pole_m_form.is_valid():
            m_form = pole_m_form.save(commit=False)
            m_form.poledefect = maintainpole.poledefect
            m_form.pole_type = pole_m_form.cleaned_data['pole_type']
            m_form.x = pole_m_form.cleaned_data['x']
            m_form.y = pole_m_form.cleaned_data['y']
            m_form.location = pole_m_form.cleaned_data['location']
            m_form.county = request.user.userprofile.county
            m_form.region = request.user.userprofile.region
            m_form.inspectedby = request.user.userprofile
            m_form.maintain_notes = pole_m_form.cleaned_data['maintain_notes']
            if request.POST.get("finalsubmission"):
                m_form.save_status = True
                m_form.save()
                messages.success(request, 'The Pole Maintenance Inspection was submitted successfully.')
                return redirect('lv:poledefects-maintenance-my')

            elif request.POST.get("draft"):
                m_form.save_status = False
                m_form.save()
                messages.success(request, 'The Pole Makintenance Inspection was saved as a draft successfully.')
                return redirect('lv:poledefects-maintenance-my')

        else:
            print('invalid form')
            print(pole_m_form.errors)

    else:
        lv_form = Poledefects_maintenanceForm(instance=maintainpole)

    context = {
        'maintainpole' : maintainpole,
        'lv_form': lv_form,
       # 'maintain_form' : maintain_form,


    }
    return render(request, 'lv/poledefects/maintain_poledefect.html', context)

@login_required(login_url="login")
def lvmaintenance_print(request, pk=None):
    lvmaintenance = get_object_or_404(MaintainLVinspection, id=pk)


    context ={
        'lvinspection' : lvmaintenance,

    }

    return render(request, 'lv/lvmaitenance/lvmaintenance_print.html', context)

@login_required(login_url="login")
def county_tx_today_failure(request):
    today = date.today()
    failures_today = list(TxFailure.objects.values(
        'dtupdate','latitude','longitude','substation__name','inspectedby__user__stid','causeoffailure',

    ).filter(dtupdate__date=today, county=request.user.userprofile.county))
    # lvmaintenance = MaintainLVinspection.objects.values('dtupdate')
    # substation = Substation.objects.all()
    # result_list = lvinspections.union(lvmaintenance)

    context = {
    'failures_today' : failures_today
    }
    return render(request, "lv/txfailure/failure_daily_visibility.html", context)

@login_required(login_url="login")
def county_lv_today(request):
    today = date.today()
    lvinspections = list(Lvinspection.objects.values(
        'dtupdate','latitude','longitude','substation__name','inspectedby__user__stid','retention_req',
        'traceclear_span','conductors_uprate_span','pme_missing_poles','lv_overdistance_l','illegal_connections_l','poshomills_onsingle_p_n'
    ).filter(dtupdate__date=today,county=request.user.userprofile.county))
    # lvmaintenance = MaintainLVinspection.objects.values('dtupdate')
    # substation = Substation.objects.all()
    # result_list = lvinspections.union(lvmaintenance)




    context = {
    'lvinspections' : lvinspections
    }
    return render(request, "lv/lvinspections/county_lv_today_map.html", context)

@login_required(login_url="login")
def global_substation(request):
    today = date.today()
    lvinspections = SubstationInspection.objects.select_related('region','county','substation','inspectedby','aprv_by').values(
        'id', 'substation__ssn','substation__name','dtupdate','region','county', 'save_status','aprv_status','region__name','county__name','inspectedby__user_id__stid','aprv_by__user_id__stid',
        'serialno','voltage','kvarating','gnumber','make__name','yom','location','fusesize','sizeoflvconductor','noofcircuits','hvearth_intact','hvearth_values','neutralearth_intact','neutralvearth_values',
        'surgearrestors','surgearrestors_values','arcinghorns','arcinghorns','gapset_values','lvleads_size','txloading','txloading_yes','load_distributionby','c_tx_structure','c_fuse_carriers','t_fuse_bar','c_fuse_bar','txwiring','c_txwiring',
        'hv_b_r','hv_r_y','hv_y_b','lv_b_n','lv_r_n','lv_y_n','insul_lve','insul_hv_lv','insul_hv_e'
    ).filter(
        aprv_status=True,dtupdate__date=today).order_by('-dtupdate')
    #print(lvinspections[0]['dtupdate'].date())
    #print(datetime.now().date())
    today = today = timezone.now().date()

    # todays filter lvinspections.filter(Q(dtupdate__date=today))


    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(region=keyword)
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(county=keyword)
    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)


    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title' : today

    }
    return render(request, 'lv/substation/substation_global.html', context)
@login_required(login_url="login")
def global_lv_useranalytics(request):
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    inspectors = (
        UserProfile.objects.filter(campaign="network_technician")
        .values("user_id__stid", "user_id__name", "user_id__mobile", "county__name")
        .annotate(
            the_count=Count("lv_inspected_by"),
            today=Count("lv_inspected_by", filter=Q(lv_inspected_by__dtadd__date=today)),
            yesturday=Count(
                "lv_inspected_by", filter=Q(lv_inspected_by__dtadd__date=yesterday)
            ),
            yesturday_1=Count(
                "lv_inspected_by", filter=Q(lv_inspected_by__dtadd__date=yesterday_1)
            ),
            yesturday_2=Count(
                "lv_inspected_by", filter=Q(lv_inspected_by__dtadd__date=yesterday_2)
            ),
            yesturday_3=Count(
                "lv_inspected_by", filter=Q(lv_inspected_by__dtadd__date=yesterday_3)
            ),
        )
        .order_by("lv_inspected_by")
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
        "yesterday_3": yesterday_3,
        # 'county' : county
    }
    return render(request, "lv/lvinspections/global_staff_analytics.html", context)
@login_required(login_url="login")
def global_lvmaintenance(request):
    today = date.today()
    lvinspections = MaintainLVinspection.objects.select_related('aprv_by','inspectedby','lvinspection').values(
        'id','lvinspection','lvinspection__substation__da','lvinspection__substation__feederofelement', 'lvinspection__substation__ssn','lvinspection__substation__name','dtupdate','lvinspection__region','lvinspection__county', 'save_status','aprv_status','lvinspection__region__name','lvinspection__county__name',
        'inspectedby__user_id__stid','aprv_by__user_id__stid','retention_req','traceclear_span','conductors_uprate_span','pme_missing_poles','lv_overdistance_l','illegal_connections_l','jumper_rehab_sect','reconducturing_pvc_l','poshomills_onsingle_p_n','inspect_notes','txposition','other_defects'
    ).filter(aprv_status=True,dtupdate__date=today).order_by('-dtupdate')



    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(lvinspection__region=keyword)
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(lvinspection__county=keyword)
    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(lvinspection__substation__ssn__icontains=keyword)

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)


    paginator = Paginator(lvinspections, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)


    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title' : today

    }
    return render(request, 'lv/lvmaitenance/lvmaintenance_global.html', context)
@login_required(login_url="login")
def todays_visibility(request):
    lvinspections = list(Lvinspection.objects.values('dtupdate','latitude','longitude','substation__name'))
    # lvmaintenance = MaintainLVinspection.objects.values('dtupdate')
    # substation = Substation.objects.all()
    # result_list = lvinspections.union(lvmaintenance)


    context = {
    'lvinspections' : lvinspections
    }
    return render(request, "lv/general/today_visibility.html", context)

@login_required(login_url="login")
def inspector_analytics_dashbord(request, pk=None):
    user = get_object_or_404(UserProfile, id=pk)
    lvinspections = Lvinspection.objects.select_related('inspectedby').filter(aprv_status=True, inspectedby=user).order_by('-dtupdate')

    # df = read_frame(lvinspections)
    # df = df.groupby(by=['defect_type', 'pole_type'], as_index=False, sort=False)['id'].count()
    # json_records = df.reset_index().to_json(orient='records')
    # data = []
    # data = json.loads(json_records)
    #
    # df_defaults = read_frame(lvfaults)
    # # df_defaults = df_defaults.groupby(by='county',as_index=False, sort=False).agg([np.sum])
    # df_defaults = df_defaults.groupby(["county"]).agg(
    #     {'vegline': 'sum', 'poorsags': 'sum', 'uprate_cond': 'sum',
    #      'pme': 'sum', 'con_illegal': 'sum', 'jumper_rehab': 'sum', 'overdistance': 'sum', 'lvreconductor': 'sum',
    #      'poshomill': 'sum'})
    # json_records1 = df_defaults.reset_index().to_json(orient='records')
    # data1 = []
    # data1 = json.loads(json_records1)

    def lvinspection_daily_trend():
        df = read_frame(lvinspections)
        df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
        df = df.groupby(by="dtadd", as_index=False, sort=False)["id"].count()
        df = px.bar(
            df,
            x=df.dtadd,
            y=df.id,
            title="Daily Overall Inspections.",
            text_auto=True,
            text=df.id,
            labels={"id": "Count", "dtadd": "Date"},
        )
        df.update_layout(
            margin=dict(l=20, r=20, b=20),
            title_text=f'', title_x=0.5, font={'size': 12},
            # title=("Target vs Achievement"),
            xaxis_tickfont_size=14,
            yaxis_range=[0, 6],
            yaxis=dict(
                title="No Of Inspections",
                titlefont_size=16,
                tickfont_size=14,
                range=[0, 5]
            ),
            xaxis=dict(
                title="Period",
            ),
            legend=dict(
                bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
            ),
            barmode="group",
            bargap=0.15,  # gap between bars of adjacent location coordinates.
            bargroupgap=0.1,  # gap between bars of the same location coordinate.
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df_daolytrend

    context = {
        'user' : user,
        "lvinspection_daily_trend": lvinspection_daily_trend,
        "nbar": "analytics",
        'title3' : 'Summarized Daily LV Inspections',
        'lvinspections' : lvinspections
    }
    return render(request, "lv/lvinspections/inspector_analytics.html", context)

@login_required(login_url="login")
def county_lvinspection_useranalytics(request):
    if request.user.is_authenticated:
        user = request.user
    county = request.user.userprofile.county
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    inspectors = (
        UserProfile.objects.values("user_id__stid", "user_id__name", "user_id__mobile", "county__name","id")
        .filter(campaign="network_technician",county=county)
        .annotate(
            the_count=Count("lv_inspected_by"),
            today=Count("lv_inspected_by", distinct=True, filter=Q(lv_inspected_by__dtadd__date=today)),
            yesturday=Count(
                "lv_inspected_by", distinct=True, filter=Q(lv_inspected_by__dtadd__date=yesterday)
            ),
            yesturday_1=Count(
                "lv_inspected_by", distinct=True, filter=Q(lv_inspected_by__dtadd__date=yesterday_1)
            ),
            yesturday_2=Count(
                "lv_inspected_by",distinct=True, filter=Q(lv_inspected_by__dtadd__date=yesterday_2)
            ),
            yesturday_3=Count(
                "lv_inspected_by",distinct=True, filter=Q(lv_inspected_by__dtadd__date=yesterday_3)
            ),
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
        "yesterday_3": yesterday_3,
        # 'county' : county
    }
    return render(request, "lv/lvinspections/County_Lvinspection_inspector_analytics.html", context)

@login_required(login_url="login")
def county_lv_useranalytics(request):
    if request.user.is_authenticated:
        user = request.user
    county = request.user.userprofile.county
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    yesterday_1 = date.today() - timedelta(days=2)
    yesterday_2 = date.today() - timedelta(days=3)
    yesterday_3 = date.today() - timedelta(days=4)

    inspectors = (
        UserProfile.objects.filter(campaign="network_technician",county=county)
        .values("user_id__stid", "user_id__name", "user_id__mobile", "county__name")
        .annotate(
            the_count=Count("lv_inspected_by"),
            today=Count("lv_inspected_by", filter=Q(lv_inspected_by__dtadd__date=today)),
            yesturday=Count(
                "lv_inspected_by", filter=Q(lv_inspected_by__dtadd__date=yesterday)
            ),
            yesturday_1=Count(
                "lv_inspected_by", filter=Q(lv_inspected_by__dtadd__date=yesterday_1)
            ),
            yesturday_2=Count(
                "lv_inspected_by", filter=Q(lv_inspected_by__dtadd__date=yesterday_2)
            ),
            yesturday_3=Count(
                "lv_inspected_by", filter=Q(lv_inspected_by__dtadd__date=yesterday_3)
            ),
        )
        .order_by("lv_inspected_by")
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
        "yesterday_3": yesterday_3,
        # 'county' : county
    }
    return render(request, "lv/lvinspections/county_staff_analytics.html", context)
@login_required(login_url="login")
def global_substation_inspections(request):
    DATE_RANGE = datetime.datetime.today() - datetime.timedelta(days=360)
    oveall_inspected = SubstationInspection.objects.select_related('county').values(
       "id", "dtupdate",'substation__name','county__name','aprv_dt', 'region'
    ).filter(aprv_status=True)
    # oveall_maintenance = MaintainLVinspection.objects.select_related('lvinspection__county').values(
    #     "id", "dtupdate", 'lvinspection__substation__name', 'lvinspection__county__name', 'aprv_dt'
    # ).filter(aprv_status=True)




    def region_trend():
        df = read_frame(oveall_inspected)
        df["dtupdate"] = pd.to_datetime(df["dtupdate"]).dt.date
        df = df.groupby(by="region", as_index=False, sort=False)["id"].count()
        df = px.bar(
            df,
            x=df.region,
            y=df.id,
            title="Regional Substation Inspection",
            text_auto=True,
            text=df.id,
            labels={"id": "INSPECTIONS", "region": "REGIONS"},
        )
        df_region_trend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_region_trend

    def daily_trend():
        df = read_frame(oveall_inspected)
        df["dtupdate"] = pd.to_datetime(df["dtupdate"]).dt.date
        df = df.groupby(by="dtupdate", as_index=False, sort=False)["id"].count()
        df = px.bar(
            df,
            x=df.dtupdate,
            y=df.id,
            title=f"Daily Overall Substation Inspections",
            text_auto=True,
            text=df.id,
            labels={"id": "Inspections Count", "dtupdate": "Date"},
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daolytrend

    def daily_trend_maintenace():
        df = read_frame(oveall_inspected)
        df["dtupdate"] = pd.to_datetime(df["dtupdate"]).dt.date
        df = df.groupby(by="dtupdate", as_index=False, sort=False)["id"].count()
        df = px.bar(
            df,
            x=df.dtupdate,
            y=df.id,
            title=f"Daily Overall LV Maintenance",
            text_auto=True,
            text=df.id,
            labels={"id": "Lv Count", "dtupdate": "Date"},
        )
        df_daily_m = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)

        return df_daily_m

    oveall_inspected1 = {}
    oveall_maintenance1 = {}
    datefrom = []
    dateto = []
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            oveall_inspected1 = oveall_inspected.filter(substation__ssn__icontains=keyword)
            oveall_maintenance1 = oveall_maintenance.filter(lvinspection__substation__ssn__icontains=keyword)

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        if datefrom and dateto:
            oveall_inspected1 = oveall_inspected.filter(dtupdate__gte=datefrom,dtupdate__lte=dateto)
            oveall_maintenance1 = oveall_inspected.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)


    context ={
    'daily_trend' : daily_trend,
    'data': oveall_inspected1,
    'data1':oveall_maintenance1,
    'substation_global_count' : oveall_inspected.filter(dtupdate__gte=DATE_RANGE).count(),
    'substation_maintenance_global_count': oveall_inspected.filter(dtupdate__gte=DATE_RANGE).count(),
    'daily_trend_maintenace' : daily_trend_maintenace,
    'datefrom' : datefrom,
    'dateto' : dateto,
    'region_trend' : region_trend,

    }
    return render(request, 'lv/substation_global.html', context)
@login_required(login_url="login")
def lvinspection_range_export(request):
    response = HttpResponse(content_type="text/csv")
    writer = csv.writer(response)
    datefrom = request.GET.get('datefrom')
    dateto = request.GET.get('dateto')

    meters = Lvinspection.objects.select_related('county','inspectedby')
    meters =meters.filter(dtupdate__gte=datefrom,dtupdate__lte=dateto, aprv_status=True).order_by('-dtadd')

    writer.writerow(
        [
            "COUNTY",
            "SUBSATION",
            "POORSAGS",
            "RETENTION",
            "LINE VEG",
            'TRACE CLEARANCE SPANS',
            'CONDUCTOR UPRATING',
            'CONDUCTOR LENGTH',
            'PME INSTALLED',
            'PME MISSING',
            'OVERDISTANCE LV',
            'DISTANCE FROM TX',
            'ILLEGAL CONNECTIONS',
            'APRX LENGTH',
            'JUMPER REHAB SECTIONS',
            'LV RECONDUCTERING WITH PVC',
            'LENGTH',
            'NO OF CIRCUITS',
            'POSHOMILLS ON SINGLE PHASE',
            'INSPECTION NOTES'
            'DATE INSEPECTED',
            'INSPECTED BY',
            'DATE APPROVED',
            'APPROVED BY',
            'APPROVAL NOTES'



        ]
    )
    for meter in meters:
        writer.writerow(
            [
                meter.county,
                meter.substation,
                meter.poor_sags_cl_cond,
                meter.retention_req,
                meter.lvline_veg,
                meter.traceclear_span,
                meter.conductors_uprate,
                meter.conductors_uprate_span,
                meter.pme_installed,
                meter.pme_missing_poles,
                meter.lv_overdistance,
                meter.lv_overdistance_l,
                meter.illegal_connections,
                meter.illegal_connections_l,
                meter.jumper_rehab_sect,
                meter.reconducturing_pvc,
                meter.reconducturing_pvc_l,
                meter.circuits,
                meter.poshomills_onsingle_p,
                meter.inspect_notes,
                formats.date_format(meter.dtupdate,'SHORT_DATE_FORMAT'),
                meter.inspectedby,
                formats.date_format(meter.aprv_dt, 'SHORT_DATE_FORMAT'),
                meter.aprv_by,
                meter.aprv_notes

            ]
        )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="LVINSPECTIONS.csv" '
    return response
@login_required(login_url="login")
def substation_edit(request, pk=None):
    ssn = get_object_or_404(Substation, id=pk)

    campaign = request.user.userprofile.campaign

    if campaign == "network_supervisors":
        if request.method == "POST":
            m_form = SubstationForm(request.POST, request.FILES,instance=ssn)

            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.ssn = m_form.cleaned_data["ssn"]
                zerov.name = m_form.cleaned_data["name"]
                zerov.gnumber = m_form.cleaned_data["gnumber"]
                zerov.originofelement = m_form.cleaned_data["originofelement"]
                zerov.feederofelement = m_form.cleaned_data["feederofelement"]
                zerov.physicallocation = m_form.cleaned_data["physicallocation"]
                zerov.da = m_form.cleaned_data["da"]
                zerov.lenghth = m_form.cleaned_data["lenghth"]
                zerov.rating = m_form.cleaned_data["rating"]
                zerov.volatge = m_form.cleaned_data["voltage"]
                zerov.yom = m_form.cleaned_data["yom"]
                zerov.make = m_form.cleaned_data["make"]
                zerov.county =request.user.userprofile.county
                zerov.region = request.user.userprofile.region
                zerov.createdby = request.user.userprofile
                zerov.save()
                messages.success(
                    request, "The Substation Has been successfully saved."
                )
                return redirect("lv:county_ssn")
            else:
                print("invalid form")
                print(m_form.errors)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = SubstationForm(instance=ssn)
        context = {
            "form": m_form,
        }
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

    return render(request, "lv/substation_new.html", context)
@login_required(login_url="login")
def ssn_new(request):
    # userprofile = get_object_or_404(UserProfile, user=request.user)

    campaign = request.user.userprofile.campaign

    if campaign == "network_supervisors":
        if request.method == "POST":
            m_form = SubstationForm(request.POST, request.FILES)

            if m_form.is_valid():
                zerov = m_form.save(commit=False)
                zerov.ssn = m_form.cleaned_data["ssn"]
                zerov.name = m_form.cleaned_data["name"]
                zerov.gnumber = m_form.cleaned_data["gnumber"]
                zerov.originofelement = m_form.cleaned_data["originofelement"]
                zerov.feederofelement = m_form.cleaned_data["feederofelement"]
                zerov.physicallocation = m_form.cleaned_data["physicallocation"]
                zerov.da = m_form.cleaned_data["da"]
                zerov.lenghth = m_form.cleaned_data["lenghth"]
                zerov.rating = m_form.cleaned_data["rating"]
                zerov.volatge = m_form.cleaned_data["voltage"]
                zerov.yom = m_form.cleaned_data["yom"]
                zerov.make = m_form.cleaned_data["make"]
                zerov.county =request.user.userprofile.county
                zerov.region = request.user.userprofile.region
                zerov.createdby = request.user.userprofile
                zerov.save()
                messages.success(
                    request, "The Substation Has been successfully saved."
                )
                return redirect("lv:county_ssn")
            else:
                print("invalid form")
                print(m_form.errors)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = SubstationForm()
        context = {
            "form": m_form,
        }
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

    return render(request, "lv/substation_new.html", context)
@login_required(login_url="login")
def county_ssn(request):
    county = request.user.userprofile.county
    ssn = Substation.objects.select_related('county').filter(county=county)
    paginator = Paginator(ssn, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    context ={

        'ssn' : paged_uploads,
        'county' : county,
    }
    return render(request, 'lv/county_ssn.html', context)
@login_required(login_url="login")
def poledefects_maintenance_my(request):
    mypolemaintenance = Poledefects_maintenance.objects.select_related('poledefect__substation','inspectedby').filter(inspectedby=request.user.userprofile).order_by('-dtadd')

    context ={
        'title': 'My Pole Defects Maintenance',
        'data' : mypolemaintenance
    }
    return render(request,'lv/network_myinspections.html', context)
@login_required(login_url="login")
def poledefects_maintain(request,pk=None):
    new_maintenance = get_object_or_404(Poledefects, id=pk)

    pole_form = Poledefects_maintenanceForm()

    if request.method == 'POST':
        pole_form = Poledefects_maintenanceForm(request.POST)
        if pole_form.is_valid():
            poled = pole_form.save(commit=False)
            poled.pole_type = pole_form.cleaned_data['pole_type']
            poled.x = pole_form.cleaned_data['x']
            poled.y = pole_form.cleaned_data['y']
            poled.location = pole_form.cleaned_data['location']
            poled.county = request.user.userprofile.county
            poled.poledefect = new_maintenance
            poled.inspectedby = request.user.userprofile
            poled.substation = new_maintenance.substation
            poled.save()
            new_maintenance.status = True
            new_maintenance.save()

            messages.success(request, 'The Pole Defect Maintenance was saved successfully.')
            return redirect('lv:poledefects-maintenance-my')
        else:
            print('invalid form')
            print(pole_form.errors)
            # print(Lvinsp_form.errors)
    else:
        pole_form = Poledefects_maintenanceForm()
        # lv_form = LvinspectionForm(instance=new_inspection)

    context = {
        'lvinspections' : new_maintenance,
        'pole_form' : pole_form,

    }
    return render(request,'lv/poledefects_maintain.html', context)

@login_required(login_url="login")
def search_by_ssn_global(request):
    # sb_list = Substation.objects.filter(county=request.user.userprofile.county)
    sb_list = Lvinspection.objects.select_related('county').values('ssn','id','name','physicallocation','originofelement','feederofelement','county__name').filter(aprv_status=True)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            sb_list = sb_list.filter(ssn__icontains=keyword)

    context = {
         'data' : sb_list,
    }
    return  render(request, 'lv/substation_search.html', context)
@login_required(login_url="login")
def global_lvinspections(request):
    #DATE_RANGE = datetime.datetime.today() - datetime.timedelta(days=360)
    oveall_inspected = Lvinspection.objects.select_related('county').values(
       "id", "dtupdate",'substation__name','county__name','aprv_dt','region'
    ).filter(aprv_status=True)
    oveall_maintenance = MaintainLVinspection.objects.select_related('lvinspection__county').values(
        "id", "dtupdate", 'lvinspection__substation__name', 'lvinspection__county__name', 'aprv_dt'
    ).filter(aprv_status=True)
    overall_substation = SubstationInspection.objects.select_related('county').values('id','dtupdate').filter(aprv_status=True)
    ovearll_txfailure = TxFailure.objects.select_related('county').values('id').filter(aprv_status=True)
    overall_commission = Commission_substation.objects.select_related('county').values('id').filter(aprv_status=True)
    poledefects = Poledefects.objects.select_related('county').values('region','id','defect_type').filter(status=False)
    overall_pole_maint = Poledefects_maintenance.objects.select_related('county').values('id').filter(aprv_status=True)
    overall_substation_main = SubstationMaintenance.objects.select_related('county').values('id', 'dtupdate').filter(
        aprv_status=True)
    ssn = Substation.objects.all()
    overall_mv = Mvinspection.objects.select_related('feeder','county').values('id','dtupdate').filter(aprv_status=True)
    overall_mv_maintenance = Mvmaitenance.objects.select_related('mvinspection', 'county').values('id', 'dtupdate').filter(
        aprv_status=True)
    load_checks = LoadChecks.objects.select_related('county','region').values('id', 'dtupdate').filter(
        save_status=True)

    # def PoleDefects_analysis():
    #     df = read_frame(poledefects)
    #     df = df.groupby(by='defect_type', as_index=False, sort=False)['id'].count()
    #     names = df.defect_type
    #     values = df.id
    #     df = px.pie(df, values=values, names=names, title='Defects Type Analysis')
    #     df.update_traces(textposition='inside', textinfo='percent+label')
    #     df.update_layout(margin=dict(l=20, r=20, b=20), ),
    #     df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
    #     return df

    # def poledefects_region_trend():
    #     df = read_frame(poledefects)
    #     df = df.groupby(by="region", as_index=False, sort=False)["id"].count()
    #     df = px.bar(
    #         df,
    #         x=df.region,
    #         y=df.id,
    #         title="Regional Pole Defects",
    #         text_auto=True,
    #         text=df.id,
    #         labels={"id": "COUNT", "region": "REGIONS"},
    #     )
    #     df_region_trend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
    #
    #     return df_region_trend

    # def region_trend():
    #     df = read_frame(oveall_inspected)
    #     df["dtupdate"] = pd.to_datetime(df["dtupdate"]).dt.date
    #     df = df.groupby(by="region", as_index=False, sort=False)["id"].count()
    #     df = px.bar(
    #         df,
    #         x=df.region,
    #         y=df.id,
    #         title="Regional LV Inspection",
    #         text_auto=True,
    #         text=df.id,
    #         labels={"id": "INSPECTIONS", "region": "REGIONS"},
    #     )
    #     df_region_trend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
    #
    #     return df_region_trend

    # def daily_trend():
    #     df = read_frame(oveall_inspected)
    #     df["dtupdate"] = pd.to_datetime(df["dtupdate"]).dt.date
    #     df = df.groupby(by="dtupdate", as_index=False, sort=False)["id"].count()
    #     df = px.bar(
    #         df,
    #         x=df.dtupdate,
    #         y=df.id,
    #         title=f"Daily Overall LV Inspections",
    #         text_auto=True,
    #         text=df.id,
    #         labels={"id": "Lv Count", "dtupdate": "Date"},
    #     )
    #     df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
    #
    #     return df_daolytrend

    # def daily_trend_maintenace():
    #     df = read_frame(oveall_maintenance)
    #     df["dtupdate"] = pd.to_datetime(df["dtupdate"]).dt.date
    #     df = df.groupby(by="dtupdate", as_index=False, sort=False)["id"].count()
    #     df = px.bar(
    #         df,
    #         x=df.dtupdate,
    #         y=df.id,
    #         title=f"Daily Overall LV Maintenance",
    #         text_auto=True,
    #         text=df.id,
    #         labels={"id": "Lv Count", "dtupdate": "Date"},
    #     )
    #     df_daily_m = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
    #
    #     return df_daily_m

    oveall_inspected1 = {}
    oveall_maintenance1 = {}
    datefrom = []
    dateto = []
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            oveall_inspected1 = oveall_inspected.filter(substation__ssn__icontains=keyword)
            oveall_maintenance1 = oveall_maintenance.filter(lvinspection__substation__ssn__icontains=keyword)

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        if datefrom and dateto:
            oveall_inspected1 = oveall_inspected.filter(dtupdate__gte=datefrom,dtupdate__lte=dateto)
            oveall_maintenance1 = oveall_maintenance.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)


    context ={
    # 'lvdaily' : daily_trend,
    # 'region_trend' : region_trend(),
    'data': oveall_inspected1,
    'data1':oveall_maintenance1,
    'lvglobal_count' : oveall_inspected, #oveall_inspected.filter(dtupdate__gte=DATE_RANGE).count(),
    'lv_maintenance_global_count': oveall_maintenance, #oveall_maintenance.filter(dtupdate__gte=DATE_RANGE).count(),
    'overall_substation' : overall_substation,
    'ovearll_txfailure' : ovearll_txfailure,
    'overall_commission' : overall_commission,
    'overall_pole_maint' : overall_pole_maint,
    # 'daily_trend_maintenace' : daily_trend_maintenace,
    'datefrom' : datefrom,
    'dateto' : dateto,
    'poledefects' : poledefects,
    # 'poledefects_region_trend' : poledefects_region_trend,
    # 'PoleDefects_analysis' : PoleDefects_analysis,
    'ssn' : ssn,
    'overall_substation_main' : overall_substation_main,
    'overall_mv' : overall_mv,
    'overall_mv_maintenance' : overall_mv_maintenance,
    'load_checks' : load_checks

    }
    return render(request, 'lv/lv_global.html', context)
    
@login_required(login_url="login")
def global_mv(request):



    context ={


    }
    return render(request, 'lv/mv_global.html', context)
    
@login_required(login_url="login")
def global_lv(request):
    today = date.today()
    lvinspections = Lvinspection.objects.values('id','substation__make__name','substation__da','substation__feederofelement', 'substation__ssn','substation__rating','substation__name','dtupdate','region','county', 'save_status','aprv_status','region__name','county__name',
       'inspectedby__user_id__stid','aprv_by__user_id__stid','retention_req','traceclear_span','conductors_uprate_span','pme_missing_poles','lv_overdistance_l',
          'illegal_connections_l','jumper_rehab_sect','reconducturing_pvc_l','poshomills_onsingle_p_n','inspect_notes').filter(
        aprv_status=True,dtupdate__date=today).order_by('-dtupdate')
    #print(lvinspections[0]['dtupdate'].date())
    #print(datetime.now().date())
    today = today = timezone.now().date()

    # todays filter lvinspections.filter(Q(dtupdate__date=today))


    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(region=keyword)
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(county=keyword)
    if 'ssn' in request.GET:
        keyword = request.GET["ssn"]
        if keyword:
            lvinspections = lvinspections.filter(substation__ssn__icontains=keyword)

    if 'staff' in request.GET:
        keyword = request.GET["staff"]
        if keyword:
            lvinspections = lvinspections.filter(inspectedby__user_id__stid=keyword)

    if 'approver' in request.GET:
        keyword = request.GET["approver"]
        if keyword:
            lvinspections = lvinspections.filter(aprv_by__user_id__stid=keyword)

    if 'datefrom' in request.GET and 'dateto' in request.GET:
        datefrom = request.GET["datefrom"]
        dateto = request.GET["dateto"]
        datefrom = datetime.strptime(datefrom, '%Y-%m-%d')
        dateto = datetime.strptime(dateto, '%Y-%m-%d')
        dateto = dateto.date()+timedelta(days=1)
        if datefrom and dateto:
           lvinspections = lvinspections.filter(dtupdate__gte=datefrom, dtupdate__lte=dateto)


    paginator = Paginator(lvinspections, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)


    context ={
        'data' : lvinspections,
        'regions' : Region.objects.all().order_by('name'),
        'counties': County.objects.all().order_by('name'),
        'title': today

    }
    return render(request, 'lv/lvinspections/lvinspections_global.html', context)
@login_required(login_url="login")
def region_analysis(request):
    region =  request.user.userprofile.region


    context ={
        'region' : region


    }
    return render(request, 'lv/regional_analysis.html', context)
    
@login_required(login_url="login")
def substation_maintenance_new(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')
    lv_inspection = SubstationInspection.objects.filter(substation=pk, aprv_status=True).order_by('-dtupdate').first()


    if not lv_inspection:
        messages.error(request, 'There is no available Substation inspection to be maintained. Do an Inspection First')
        return redirect('lv:substation-search')
    any_pending = SubstationMaintenance.objects.filter(save_status=False, inspectedby=request.user.userprofile)

    if any_pending:
        messages.error(request, 'You have an inspection that is saved as draft. Submit and click on new Inspection.')
        return redirect('lv:substation-maintenance-my')
    new_inspection = SubstationMaintenance.objects.create(inspection=lv_inspection, inspectedby=request.user.userprofile)
    if new_inspection:
        messages.success(request, 'A Draft of the New Inspection was saved successfully. Open to continue with the inspection')
        return redirect('lv:substation-maintenance-my')


    return render(request, 'lv/lvmaitenance/lvmaintenance.html')
    
@login_required(login_url="login")
def commission_print(request, pk=None):
    lvinspection = get_object_or_404(Commission_substation, id=pk)
    context ={
        'lvinspection' : lvinspection,
    }

    return render(request, 'lv/commission_print.html', context)
@login_required(login_url="login")
def commission_approve(request, pk=None):
    lv_inspection = get_object_or_404(Commission_substation, id=pk)

    if request.method == 'POST':
        form = CommissionApproveForm(request.POST, instance=lv_inspection)

        if form.is_valid():
            regis = form.save(commit=False)
            regis.aprv_notes = form.cleaned_data['aprv_notes']
            regis.aprv_key = form.cleaned_data['aprv_key']
            regis.aprv_by = request.user.userprofile
            regis.aprv_status = True
            regis.save()
            messages.success(request, 'The Commission Report was Approved/Declined successfully.')
            return redirect('lv:county-commission-pages')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = CommissionApproveForm(instance=lv_inspection)

    context = {
        'lvinspection': lv_inspection,
        'form' : form
    }
    return render(request, 'lv/commission_approve.html', context)
@login_required(login_url="login")
def commission_pending_app(request):
    county = request.user.userprofile.county
    failure_pending_app = Commission_substation.objects.select_related('county','substation').filter(county=county,aprv_status='False')#.values('id','dtadd','substation')
    paginator = Paginator(failure_pending_app, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)


    context ={
        'data' : paged_uploads,
        'title':'Commission Inspections Pending Approval',
        'county': county,


    }
    return render(request, 'lv/county_commission.html', context)
@login_required(login_url="login")
def county_commission_list(request):
    county = request.user.userprofile.county
    lv = Commission_substation.objects.select_related('county','substation').filter(county=county, aprv_status=True)
    paginator = Paginator(lv, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)


    context ={
        'county' : county,
        'data' : paged_uploads,
        'title':'List Of Approved Commission Inspections',
    }
    return render(request, 'lv/county_commission.html', context)
@login_required(login_url="login")
def commission_update(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')
    sub_inspection = get_object_or_404(Commission_substation, id=pk)

    if request.method == 'POST':
        sub_form = Commission_substationForm(request.POST, instance=sub_inspection)
        if sub_form.is_valid():
            poled = sub_form.save(commit=False)
            poled.substation = sub_inspection.substation
            poled.longitude = sub_form.cleaned_data['longitude']
            poled.latitude = sub_form.cleaned_data['latitude']
            poled.location = sub_form.cleaned_data['location']
            poled.dt_commission = sub_form.cleaned_data['dt_commission']
            poled.control_center = sub_form.cleaned_data['control_center']
            poled.ptw_no = sub_form.cleaned_data['ptw_no']
            poled.typeofchange = sub_form.cleaned_data['typeofchange']
            poled.typeofload = sub_form.cleaned_data['typeofload']
            poled.dcs_reference = sub_form.cleaned_data['dcs_reference']
            poled.rerec_reference = sub_form.cleaned_data['rerec_reference']
            poled.internalorder = sub_form.cleaned_data['internalorder']
            poled.lastmile_reference = sub_form.cleaned_data['lastmile_reference']
            poled.make = sub_form.cleaned_data['make']
            poled.gnumber = sub_form.cleaned_data['gnumber']
            poled.yom = sub_form.cleaned_data['yom']
            poled.kvarating = sub_form.cleaned_data['kvarating']
            poled.voltage = sub_form.cleaned_data['voltage']
            poled.txweight = sub_form.cleaned_data['txweight']
            poled.txstatus = sub_form.cleaned_data['txstatus']
            poled.refurbishedby = sub_form.cleaned_data['refurbishedby']
            poled.kplcworkshop = sub_form.cleaned_data['kplcworkshop']
            poled.htisolation = sub_form.cleaned_data['htisolation']
            poled.noofcircuits = sub_form.cleaned_data['noofcircuits']
            poled.lvprotection = sub_form.cleaned_data['lvprotection']
            poled.txprotection = sub_form.cleaned_data['txprotection']
            poled.surged_red = sub_form.cleaned_data['surged_red']
            poled.surged_yellow = sub_form.cleaned_data['surged_yellow']
            poled.surged_blue = sub_form.cleaned_data['surged_blue']
            poled.arcinghorns_single = sub_form.cleaned_data['arcinghorns_single']
            poled.arcinghorns_dublex = sub_form.cleaned_data['arcinghorns_dublex']
            poled.nooftappositions = sub_form.cleaned_data['nooftappositions']
            poled.voltagetappingsetattap = sub_form.cleaned_data['voltagetappingsetattap']
            poled.earthval_at_structure_ht = sub_form.cleaned_data['earthval_at_structure_ht']
            poled.earthval_at_structure_sd = sub_form.cleaned_data['earthval_at_structure_sd']
            poled.lv_onespanaway = sub_form.cleaned_data['lv_onespanaway']
            poled.hv_b_r = sub_form.cleaned_data['hv_b_r']
            poled.hv_r_y = sub_form.cleaned_data['hv_r_y']
            poled.hv_y_b = sub_form.cleaned_data['hv_y_b']
            poled.lv_b_n = sub_form.cleaned_data['lv_b_n']
            poled.lv_r_n = sub_form.cleaned_data['lv_r_n']
            poled.lv_y_n = sub_form.cleaned_data['lv_y_n']
            poled.insul_lve = sub_form.cleaned_data['insul_lve']
            poled.insul_hv_lv = sub_form.cleaned_data['insul_hv_lv']
            poled.insul_hv_e = sub_form.cleaned_data['insul_hv_e']
            poled.volt_b_r = sub_form.cleaned_data['volt_b_r']
            poled.volt_r_y = sub_form.cleaned_data['volt_r_y']
            poled.volt_y_b = sub_form.cleaned_data['volt_y_b']
            poled.volt_b_n = sub_form.cleaned_data['volt_b_n']
            poled.volt_r_n = sub_form.cleaned_data['volt_r_n']
            poled.volt_y_n = sub_form.cleaned_data['volt_y_n']
            poled.htfuse_b = sub_form.cleaned_data['htfuse_b']
            poled.htfuse_r = sub_form.cleaned_data['htfuse_r']
            poled.htfuse_y = sub_form.cleaned_data['htfuse_y']
            poled.phasetotation = sub_form.cleaned_data['phasetotation']
            poled.comments = sub_form.cleaned_data['comments']
            poled.county = request.user.userprofile.county
            poled.region = request.user.userprofile.region
            poled.inspectedby = request.user.userprofile

            if request.POST.get("finalsubmission"):
                poled.save_status = True
                poled.save()
                messages.success(request, 'The COmmission Inspection was submitted successfully.')
                return redirect('lv:commission-my')

            elif request.POST.get("draft"):
                poled.save_status = False
                poled.save()
                messages.success(request, 'The Substation Inspection was saved as a draft successfully.')
                return redirect('lv:commission-my')
        else:
            print('invalid form')
            print(sub_form.errors)
    else:
        sub_form = Commission_substationForm(instance=sub_inspection)

    context={
        'substation_id': sub_inspection.id,
        'sub_form': sub_form,
        'ssn' : sub_inspection.substation.ssn
    }
    return render(request, 'lv/commission/commission_update.html', context)

@login_required(login_url="login")
def commission_delete(request, pk):
    lv  = Commission_substation.objects.get(id=pk)
    if request.method =='POST':
        lv.delete()
        messages.success(request, 'The Commission Inspection was deleted successfully')
        return redirect('lv:commission-my')
    context = {'object' : lv}
    return render(request, 'lv/substation_delete_confirmation.html', context)
@login_required(login_url="login")
def commission_my(request):
    mycommissions = Commission_substation.objects.select_related('substation','inspectedby').filter(inspectedby=request.user.userprofile).order_by('-dtadd')

    paginator = Paginator(mycommissions, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context ={
        'title': 'My TX Commissions',
        'data' : paged_uploads
    }
    return render(request,'lv/network_myinspections.html', context)
@login_required(login_url="login")
def commission_new(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')

    any_pending = Commission_substation.objects.filter(save_status=False, inspectedby=request.user.userprofile)
    ssn = get_object_or_404(Substation, id=pk)

    if any_pending:
        messages.error(request, 'You have an inspection that is saved as draft. Submit and click on new Inspection.')
        return redirect('lv:commission-my')
    new_inspection = Commission_substation.objects.create(substation=ssn, inspectedby=request.user.userprofile, region=request.user.userprofile.region)
    if new_inspection:
        messages.success(request, 'A Draft of the New Inspection was saved successfully. Open to continue with the inspection')
        return redirect('lv:commission-my')


    return render(request, 'lv/lvmaitenance/lvmaintenance.html')
@login_required(login_url="login")
def substation_print(request, pk=None):
    lvinspection = get_object_or_404(SubstationInspection, id=pk)
    context ={
        'lvinspection' : lvinspection,
    }

    return render(request, 'lv/substation/sustation_inspection_print.html', context)
@login_required(login_url="login")
def substation_approve(request, pk=None):
    lv_inspection = get_object_or_404(SubstationInspection, id=pk)

    if request.method == 'POST':
        form = SubstationApproveForm(request.POST, instance=lv_inspection)

        if form.is_valid():
            regis = form.save(commit=False)
            regis.aprv_notes = form.cleaned_data['aprv_notes']
            regis.aprv_key = form.cleaned_data['aprv_key']
            regis.aprv_by = request.user.userprofile
            regis.aprv_status = True
            regis.aprv_dt = date.today()
            regis.save()
            messages.success(request, 'The Substation Report was Approved/Declined successfully.')
            return redirect('lv:county-substation-inspection-pages')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = SubstationApproveForm(instance=lv_inspection)

    context = {
        'lvinspection': lv_inspection,
        'form' : form
    }
    return render(request, 'lv/substation/substation_inspection_approve.html', context)
@login_required(login_url="login")
def substations_pending_app(request):
    county = request.user.userprofile.county
    failure_pending_app = SubstationInspection.objects.select_related('county','substation').filter(county=county,aprv_status='False',save_status=True)#.values('id','dtadd','substation')
    paginator = Paginator(failure_pending_app, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)


    context ={
        'data' : paged_uploads,
        'title':'Substation Inspections Pending Approval',
        'county': county,


    }
    return render(request, 'lv/county_substation.html', context)
@login_required(login_url="login")
def county_substation_list(request):
    county = request.user.userprofile.county
    lv = SubstationInspection.objects.select_related('county','substation').filter(county=county, aprv_status=True)
    paginator = Paginator(lv, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)


    context ={
        'county' : county,
        'data' : paged_uploads,
        'title':'List Of Approved Substation Inspections',
    }
    return render(request, 'lv/county_substation.html', context)
@login_required(login_url="login")
def substation_delete(request, pk):
    lv  = SubstationInspection.objects.get(id=pk)
    if request.method =='POST':
        lv.delete()
        messages.success(request, 'The Substation Inspection was deleted successfully')
        return redirect('lv:substation-my')
    context = {'object' : lv}
    return render(request, 'lv/substation_delete_confirmation.html', context)
@login_required(login_url="login")
def lvfailure_delete(request, pk):
    lv  = TxFailure.objects.get(id=pk)
    if request.method =='POST':
        lv.delete()
        messages.success(request, 'The TX Failure Inspection was deleted successfully')
        return redirect('lv:lvfailure-my')
    context = {'object' : lv}
    return render(request, 'lv/txfailure_delete_confirmation.html', context)
@login_required(login_url="login")
def txfailure_print(request, pk=None):
    lvinspection = get_object_or_404(TxFailure, id=pk)
    context ={
        'lvinspection' : lvinspection,
    }

    return render(request, 'lv/txfailure_print.html', context)
@login_required(login_url="login")
def lvfailure_approve(request, pk=None):
    lv_inspection = get_object_or_404(TxFailure, id=pk)

    if request.method == 'POST':
        form = LvfailureApproveForm(request.POST, instance=lv_inspection)

        if form.is_valid():
            regis = form.save(commit=False)
            regis.aprv_notes = form.cleaned_data['aprv_notes']
            regis.aprv_key = form.cleaned_data['aprv_key']
            regis.aprv_by = request.user.userprofile
            regis.aprv_status = True
            regis.save()
            messages.success(request, 'The TX Failure Report was Approved/Declined successfully.')
            return redirect('lv:lvfailure_approve')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = LvfailureApproveForm(instance=lv_inspection)

    context = {
        'lvinspection': lv_inspection,
        'form' : form
    }
    return render(request, 'lv/lvfailure_approve.html', context)
@login_required(login_url="login")
def lvmaintenance_delete(request, pk):
    lv  = MaintainLVinspection.objects.get(id=pk)
    if request.method =='POST':
        lv.delete()
        messages.success(request, 'The Maintenance Inspection was deleted successfully')
        return redirect('lv:lvmaintenance-my')
    context = {'object' : lv}
    return render(request, 'lv/lvmaintenance_delete_confirmation.html', context)
@login_required(login_url="login")
def lvmaintenance_update(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')
    inspection = get_object_or_404(Lvinspection, id=pk)
    maintenance = MaintainLVinspection.objects.filter(lvinspection=inspection).order_by('-dtadd').first()
    if request.method == 'POST':
        sub_form = MaintainLVinspectionForm(request.POST, instance=maintenance)
        if sub_form.is_valid():
            poled = sub_form.save(commit=False)
            poled.lvinspection = inspection
            poled.retention_req = sub_form.cleaned_data['retention_req']
            poled.traceclear_span = sub_form.cleaned_data['traceclear_span']
            poled.conductors_uprate_span = sub_form.cleaned_data['conductors_uprate_span']
            poled.pme_missing_poles = sub_form.cleaned_data['pme_missing_poles']
            poled.lv_overdistance_l = sub_form.cleaned_data['lv_overdistance_l']
            poled.illegal_connections_l = sub_form.cleaned_data['illegal_connections_l']
            poled.jumper_rehab_sect = sub_form.cleaned_data['jumper_rehab_sect']
            poled.reconducturing_pvc_l = sub_form.cleaned_data['reconducturing_pvc_l']
            poled.poshomills_onsingle_p_n = sub_form.cleaned_data['poshomills_onsingle_p_n']
            poled.inspect_notes = sub_form.cleaned_data['inspect_notes']
            poled.inspectedby = request.user.userprofile


            if request.POST.get("finalsubmission"):
                with transaction.atomic():
                    poled.save_status = True
                    poled.save()
                    lv_d = Lv_defaults.objects.create(
                        lvinspection=inspection,
                        county=request.user.userprofile.county,
                        region=request.user.userprofile.region,
                        poorsags= -poled.retention_req,
                        vegline= -poled.traceclear_span,
                        uprate_cond= -poled.conductors_uprate_span,
                        pme= -poled.pme_missing_poles,
                        con_illegal= -poled.illegal_connections_l,
                        jumper_rehab= -poled.jumper_rehab_sect,
                        poshomill= -poled.poshomills_onsingle_p_n,
                        overdistance= -poled.lv_overdistance_l,
                        lvreconductor= -poled.reconducturing_pvc_l,
                        inspectedby=request.user.userprofile,
                        substation=inspection.substation
                    )
                    lv_d.save()
                messages.success(request, 'The LV Maintenance was submitted successfully.')
                return redirect('lv:lvmaintenance-my')

            if request.POST.get("draft"):
                poled.save_status = False
                poled.save()
                messages.success(request, 'The LV Maintenance was submitted successfully.')
                return redirect('lv:lvmaintenance-my')


        else:
            print('invalid form')
            print(sub_form.errors)
    else:
        sub_form = MaintainLVinspectionForm(instance=maintenance)

    context={

        'sub_form': sub_form,
        'lv' : inspection
    }

    return render(request, 'lv/lvmaitenance/lvmaintenance.html', context)

@login_required(login_url="login")
def lvinspection_delete(request, pk):
    lv  = Lvinspection.objects.get(id=pk)
    lv_defaults = Lv_defaults.objects.filter(lvinspection=lv)
    if request.method =='POST':
        with transaction.atomic():
            lv.delete()
            lv_defaults.delete()
        messages.success(request, 'The Inspection was deleted successfully')
        return redirect('lv:lvinspection-my')
    context = {'object' : lv}
    return render(request, 'lv/lvdelete_confirmation.html', context)
@login_required(login_url="login")
def county_lvmaintenance_pending(request):
    county = request.user.userprofile.county
    lv = MaintainLVinspection.objects.select_related('lvinspection__county').filter(lvinspection__county=county, save_status=True, aprv_status=False)

    context ={
        'county' : county,
        'title':'List Of Pending Approval LV Maintenance Inspections',
        'data': lv,

    }
    return render(request, 'lv/county_lvmaintenance.html', context)

@login_required(login_url="login")
def lvmaintenance_approve(request, pk=None):
    lv_inspection = get_object_or_404(MaintainLVinspection, id=pk)

    if request.method == 'POST':
        form = LvmaintenanceApproveForm(request.POST, instance=lv_inspection)

        if form.is_valid():
            regis = form.save(commit=False)
            regis.aprv_notes = form.cleaned_data['aprv_notes']
            regis.aprv_key = form.cleaned_data['aprv_key']
            regis.aprv_by = request.user.userprofile
            regis.aprv_status = True
            regis.aprv_dt = date.today()
            regis.save()
            messages.success(request, 'The LV Maintenance was Approved/Declined successfully.')
            return redirect('lv:county-lvmaintenance-pages')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = LvmaintenanceApproveForm(instance=lv_inspection)

    context = {
        'lvinspection': lv_inspection,
        'form' : form
    }
    return render(request, 'lv/lvmaitenance/lvmaintenance_approve.html', context)

@login_required(login_url="login")
def lvfailure_my(request):
    myfailures = TxFailure.objects.select_related('substation','inspectedby').filter(inspectedby=request.user.userprofile).order_by('-dtadd')

    paginator = Paginator(myfailures, 100)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context ={
        'title': 'My TX Failure Inspections',
        'data' : paged_uploads
    }
    return render(request,'lv/network_myinspections.html', context)

@login_required(login_url="login")
def lvinspection_my(request):
    
    mylvinspections = Lvinspection.objects.select_related('substation','inspectedby').order_by('-dtupdate').values('id','substation__ssn','substation__name','dtupdate','save_status','aprv_status').filter(inspectedby=request.user.userprofile)
    paginator = Paginator(mylvinspections, 100)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context ={
        'title': 'My LV Inspections',
        'data' : paged_uploads
    }
    return render(request, 'lv/network_myinspections.html', context)
@login_required(login_url="login")
def lvmaintenance_my(request):
    mymaintenance = MaintainLVinspection.objects.select_related('substation','inspectedby').values('id','lvinspection__substation__ssn','lvinspection__substation__name','dtupdate','save_status','aprv_status','lvinspection').filter(inspectedby=request.user.userprofile).order_by('-dtadd')

    paginator = Paginator(mymaintenance, 100)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context ={
        'title': 'My LV Maintenance',
        'data': paged_uploads
    }
    return render(request,'lv/network_myinspections.html', context)
@login_required(login_url="login")
def network_myinspections(request):
    mylvinspections = Lvinspection.objects.select_related('substation','inspectedby').values('id','substation__ssn','substation__name','dtupdate','save_status','aprv_status').filter(inspectedby=request.user.userprofile).order_by('-dtadd')

    paginator = Paginator(mylvinspections, 100)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context={
        'title': 'My LV Inspections',
        'data' : paged_uploads,
    }
    return render(request, 'lv/network_myinspections.html', context)
@login_required(login_url="login")
def lvmaintenance_new(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')
    lv_inspection = Lvinspection.objects.filter(substation=pk, aprv_status=True).order_by('-dtupdate').first()

    if not lv_inspection:
        messages.error(request, 'There is no available LV inspection to be maintained. Do an Inspection First')
        return redirect('lv:substation-search')
    any_pending = MaintainLVinspection.objects.filter(save_status=False, inspectedby=request.user.userprofile)

    if any_pending:
        messages.error(request, 'You have an inspection that is saved as draft. Submit and click on new Inspection.')
        return redirect('lv:lvmaintenance-my')
    new_inspection = MaintainLVinspection.objects.create(lvinspection=lv_inspection, inspectedby=request.user.userprofile)
    if new_inspection:
        messages.success(request, 'A Draft of the New Inspection was saved successfully. Open to continue with the inspection')
        return redirect('lv:lvmaintenance-my')


    return render(request, 'lv/lvmaitenance/lvmaintenance.html', context)
@login_required(login_url="login")
def txfailure_approve(request, pk=None):
    lv_inspection = get_object_or_404(Lvinspection, id=pk)

    if request.method == 'POST':
        form = LvinspectionApproveForm(request.POST, instance=lv_inspection)

        if form.is_valid():
            regis = form.save(commit=False)
            regis.aprv_notes = form.cleaned_data['aprv_notes']
            regis.aprv_key = form.cleaned_data['aprv_key']
            regis.aprv_by = request.user.userprofile
            regis.aprv_status = True
            regis.save()
            messages.success(request, 'The LV Inspection was Approved/Declined successfully.')
            return redirect('lv:lvinspections-pending-apprv')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = LvinspectionApproveForm(instance=lv_inspection)

    context = {
        'lvinspection': lv_inspection,
        'form' : form
    }
    return render(request, 'lv/lvinspection_approve.html', context)
@login_required(login_url="login")
def txfailure_pending_app(request):
    county = request.user.userprofile.county
    failure_pending_app = TxFailure.objects.select_related('county','substation').filter(county=county,aprv_status='False')#.values('id','dtadd','substation')
    paginator = Paginator(failure_pending_app, 100)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)


    context ={
        'data' : paged_uploads,
        'title':'TX Failure Pending Approval',
        'county': county,


    }
    return render(request, 'lv/county_txfailure.html', context)
@login_required(login_url="login")
def substation_update(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')
    sub_inspection = get_object_or_404(SubstationInspection, id=pk)

    if request.method == 'POST':
        sub_form = SubstationInspectionForm(request.POST, instance=sub_inspection)
        if sub_form.is_valid():
            poled = sub_form.save(commit=False)
            poled.substation = sub_inspection.substation
            poled.longitude = sub_form.cleaned_data['longitude']
            poled.latitude = sub_form.cleaned_data['latitude']
            poled.serialno = sub_form.cleaned_data['serialno']
            poled.voltage = sub_form.cleaned_data['voltage']
            poled.kvarating = sub_form.cleaned_data['kvarating']
            poled.gnumber = sub_form.cleaned_data['gnumber']
            poled.make = sub_form.cleaned_data['make']
            poled.yom = sub_form.cleaned_data['yom']
            poled.location = sub_form.cleaned_data['location']
            poled.fusesize = sub_form.cleaned_data['fusesize']
            poled.sizeoflvconductor = sub_form.cleaned_data['sizeoflvconductor']
            poled.noofcircuits = sub_form.cleaned_data['noofcircuits']
            poled.c_1_R = sub_form.cleaned_data['c_1_R']
            poled.c_1_Y = sub_form.cleaned_data['c_1_Y']
            poled.c_1_B = sub_form.cleaned_data['c_1_B']
            poled.c_1_bn = sub_form.cleaned_data['c_1_bn']
            poled.c_1_rn = sub_form.cleaned_data['c_1_rn']
            poled.c_1_yn = sub_form.cleaned_data['c_1_yn']
            poled.c2_1_R = sub_form.cleaned_data['c2_1_R']
            poled.c2_1_Y = sub_form.cleaned_data['c2_1_Y']
            poled.c2_1_B = sub_form.cleaned_data['c2_1_B']
            poled.c2_1_bn = sub_form.cleaned_data['c2_1_bn']
            poled.c2_1_rn = sub_form.cleaned_data['c2_1_rn']
            poled.c2_1_yn = sub_form.cleaned_data['c2_1_yn']
            poled.c2_2_R = sub_form.cleaned_data['c2_2_R']
            poled.c2_2_Y = sub_form.cleaned_data['c2_2_Y']
            poled.c2_2_B = sub_form.cleaned_data['c2_2_B']
            poled.c2_2_bn = sub_form.cleaned_data['c2_2_bn']
            poled.c2_2_rn = sub_form.cleaned_data['c2_2_rn']
            poled.c2_2_yn = sub_form.cleaned_data['c2_2_yn']
            poled.c3_1_R = sub_form.cleaned_data['c3_1_R']
            poled.c3_1_Y = sub_form.cleaned_data['c3_1_Y']
            poled.c3_1_B = sub_form.cleaned_data['c3_1_B']
            poled.c3_1_bn = sub_form.cleaned_data['c3_1_bn']
            poled.c3_1_rn = sub_form.cleaned_data['c3_1_rn']
            poled.c3_1_yn = sub_form.cleaned_data['c3_1_yn']
            poled.c3_2_R = sub_form.cleaned_data['c3_2_R']
            poled.c3_2_Y = sub_form.cleaned_data['c3_2_Y']
            poled.c3_2_B = sub_form.cleaned_data['c3_2_B']
            poled.c3_2_bn = sub_form.cleaned_data['c3_2_bn']
            poled.c3_2_rn = sub_form.cleaned_data['c3_2_rn']
            poled.c3_2_yn = sub_form.cleaned_data['c3_2_yn']
            poled.c3_3_R = sub_form.cleaned_data['c3_3_R']
            poled.c3_3_Y = sub_form.cleaned_data['c3_3_Y']
            poled.c3_3_B = sub_form.cleaned_data['c3_3_B']
            poled.c3_3_bn = sub_form.cleaned_data['c3_3_bn']
            poled.c3_3_rn = sub_form.cleaned_data['c3_3_rn']
            poled.c3_3_yn = sub_form.cleaned_data['c3_3_yn']
            poled.hvearth_intact = sub_form.cleaned_data['hvearth_intact']
            poled.hvearth_values = sub_form.cleaned_data['hvearth_values']
            poled.neutralearth_intact = sub_form.cleaned_data['neutralearth_intact']
            poled.neutralvearth_values = sub_form.cleaned_data['neutralvearth_values']
            poled.surgearrestors = sub_form.cleaned_data['surgearrestors']
            poled.surgearrestors_values = sub_form.cleaned_data['surgearrestors_values']
            poled.arcinghorns = sub_form.cleaned_data['arcinghorns']
            poled.gapset_values = sub_form.cleaned_data['gapset_values']
            poled.sizeoflvconductor = sub_form.cleaned_data['sizeoflvconductor']
            poled.lvleads_size = sub_form.cleaned_data['lvleads_size']
            poled.txloading = sub_form.cleaned_data['txloading']
            poled.txloading_yes = sub_form.cleaned_data['txloading_yes']
            poled.load_distributionby = sub_form.cleaned_data['load_distributionby']
            poled.c_tx_structure = sub_form.cleaned_data['c_tx_structure']
            poled.c_fuse_carriers = sub_form.cleaned_data['c_fuse_carriers']
            poled.t_fuse_bar = sub_form.cleaned_data['t_fuse_bar']
            poled.c_fuse_bar = sub_form.cleaned_data['c_fuse_bar']
            poled.c_txwiring = sub_form.cleaned_data['c_txwiring']
            poled.inspect_notes = sub_form.cleaned_data['inspect_notes']
            poled.hv_b_r = sub_form.cleaned_data['hv_b_r']
            poled.hv_r_y = sub_form.cleaned_data['hv_r_y']
            poled.hv_y_b = sub_form.cleaned_data['hv_y_b']
            poled.lv_b_n = sub_form.cleaned_data['lv_b_n']
            poled.lv_r_n = sub_form.cleaned_data['lv_r_n']
            poled.lv_y_n = sub_form.cleaned_data['lv_y_n']
            poled.insul_lve = sub_form.cleaned_data['insul_lve']
            poled.insul_hv_lv = sub_form.cleaned_data['insul_hv_lv']
            poled.insul_hv_e = sub_form.cleaned_data['insul_hv_e']
            poled.county = request.user.userprofile.county
            poled.region = request.user.userprofile.region
            poled.inspectedby = request.user.userprofile

            if request.POST.get("finalsubmission"):
                with transaction.atomic():
                    poled.save_status = True
                    poled.save()
                    hvearthintact = 0
                    neutralearth_intact = 0
                    surgearrestors = 0
                    arcinghorns = 0
                    txloading = 0
                    c_tx_structure = 0
                    c_fuse_carriers = 0
                    c_fuse_bar = 0

                    if poled.hvearth_intact == 'no':
                        hvearthintact = 1
                    if poled.neutralearth_intact == 'no':
                            neutralearth_intact = 1
                    if poled.surgearrestors == 'no':
                        surgearrestors = 1
                    if poled.arcinghorns == 'yes':
                        arcinghorns = 1
                    if poled.txloading == 'yes':
                            txloading = 1
                    if poled.c_tx_structure != 'okay':
                        c_tx_structure = 1
                    if poled.c_fuse_carriers == 'needreplacement':
                        c_fuse_carriers = 1
                    if poled.c_fuse_bar != 'okay':
                        c_fuse_bar = 1
                    lv_d = Substation_defaults.objects.create(
                        substation_inspection=sub_inspection,
                        county=request.user.userprofile.county,
                        region=request.user.userprofile.region,
                        arcinghones= arcinghorns,
                        hvearthintact=hvearthintact,
                        neutralearthintact =neutralearth_intact,
                        surgearresters = surgearrestors,
                        txloading=txloading,
                        txstructure=c_tx_structure,
                        fusecarriers=c_fuse_carriers,
                        fusebar=c_fuse_bar,
                        substation=sub_inspection.substation,
                        inspectedby=request.user.userprofile
                    )
                    lv_d.save()
                messages.success(request, 'The Substation Inspection was submitted successfully.')
                return redirect('lv:substation-my')

            elif request.POST.get("draft"):
                poled.save_status = False
                poled.save()
                messages.success(request, 'The Substation Inspection was saved as a draft successfully.')
                return redirect('lv:substation-my')
        else:
            print('invalid form')
            print(sub_form.errors)
    else:
        sub_form = SubstationInspectionForm(instance=sub_inspection)

    context={
        'substation_id': sub_inspection.id,
        'sub_form': sub_form,
        'ssn' : sub_inspection.substation.ssn
    }
    return render(request, 'lv/substation/substation_inspection_new.html', context)
@login_required(login_url="login")
def substation_my(request):
    substations = SubstationInspection.objects.filter(inspectedby=request.user.userprofile).order_by('-dtadd')

    paginator = Paginator(substations, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context ={
        'data': paged_uploads,
        'title' :'My Substation Inspections'
    }
    return render(request,'lv/network_myinspections.html', context)
@login_required(login_url="login")
def substation_new(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')
    ssn = get_object_or_404(Substation, id=pk)
    any_pending = SubstationInspection.objects.filter(save_status=False, inspectedby=request.user.userprofile)

    if any_pending:
        messages.error(request, 'You have an inspection that is saved as draft. Submit and click on new Inspection.')
        return redirect('lv:substation-my')
    new_inspection = SubstationInspection.objects.create(substation=ssn, inspectedby=request.user.userprofile)
    if new_inspection:
        messages.success(request, 'A Draft of the New Inspection was saved successfully. Open to continue with the inspection')
        return redirect('lv:substation-my')

    context = {
        'data': ssn,
        'inspection_id' : new_inspection.id,

    }
    return render(request,'lv/network_myinspections.html', context)
@login_required(login_url="login")
def county_poledefects_list(request):
    county = request.user.userprofile.county
    lv = Poledefects.objects.filter(county=county, status=False)
    pending = Poledefects_maintenance.objects.filter(aprv_status=False)


    context ={
        'county' : county,
        'data' : lv,
        'data_count': lv.count(),
        'pending' : pending,
        'title':'List Of Pole Defects in the county',
    }
    return render(request, 'lv/county_poledefects.html', context)
@login_required(login_url="login")
def county_txfailure_list(request):
    county = request.user.userprofile.county
    lv = TxFailure.objects.select_related('county','substation').filter(county=county, aprv_status=True)
    paginator = Paginator(lv, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)


    context ={
        'county' : county,
        'data' : paged_uploads,
        'title':'List Of Approved Transformer Failure Inspections',
    }
    return render(request, 'lv/county_txfailure.html', context)
@login_required(login_url="login")
def county_lvmaintenance_list(request):
    county = request.user.userprofile.county
    lv = MaintainLVinspection.objects.select_related('lvinspection__county').filter(lvinspection__county=county, save_status=True, aprv_status=True)

    context ={
        'county' : county,
        'title':'List Of Approved LV Maintenance Inspections',
        'data': lv,

    }
    return render(request, 'lv/county_lvmaintenance.html', context)

@login_required(login_url="login")
def county_lvinspections_dashboard(request):
    #county = UserProfile.objects.select_related('county').get(user=request.user).county
    county = request.user.userprofile.county
    lvfaults = Lv_defaults.objects.select_related('county').filter(county=county)
    pole_defects = Poledefects.objects.select_related('county').filter(county=county, status=False).order_by('defect_type')
    lvinspections = Lvinspection.objects.select_related('county').filter(aprv_status=True,county=county)


    df = read_frame(pole_defects)
    df = df.groupby(by=['defect_type','pole_type'], as_index=False, sort=False)['id'].count()
    json_records = df.reset_index().to_json(orient='records')
    data = []
    data = json.loads(json_records)
    
    # 
    df_defaults = read_frame(lvfaults)
    #df_defaults = df_defaults.groupby(by='county',as_index=False, sort=False).agg([np.sum])
    df_defaults = df_defaults.groupby(["county"]).agg(
        {'vegline': 'sum', 'poorsags': 'sum','uprate_cond': 'sum',
         'pme': 'sum','con_illegal': 'sum','jumper_rehab': 'sum','overdistance': 'sum','lvreconductor': 'sum','poshomill': 'sum'})
    json_records1 = df_defaults.reset_index().to_json(orient='records')
    data1 = []
    data1 = json.loads(json_records1)
    
    def lvinspection_daily_trend():
        df = read_frame(lvinspections)
        df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
        df = df.groupby(by="dtadd", as_index=False, sort=False)["id"].count()
        df = px.bar(
            df,
            x=df.dtadd,
            y=df.id,
            title="Daily Overall Inspections.",
            text_auto=True,
            text=df.id,
            labels={"id": "Count", "dtadd": "Date"},
        )
        df.update_layout(
            margin=dict(l=20, r=20, b=20),
            title_text=f'', title_x=0.5, font={'size': 12},
            # title=("Target vs Achievement"),
            xaxis_tickfont_size=14,
            yaxis_range=[0, 6],
            yaxis=dict(
                title="No Of Inspections",
                titlefont_size=16,
                tickfont_size=14,
                range=[0, 20]
            ),
            xaxis=dict(
                title="Period",
            ),
            legend=dict(
                bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
            ),
            barmode="group",
            bargap=0.15,  # gap between bars of adjacent location coordinates.
            bargroupgap=0.1,  # gap between bars of the same location coordinate.
        )
        df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
        return df_daolytrend



    # df_lvinspections = read_frame(lvinspections)
    # #df_defaults = df_defaults.groupby(by='county',as_index=False, sort=False).agg([np.sum])
    # df_lvinspections = df_lvinspections.groupby(by='substation', as_index=False, sort=False)['id'].count()
    # print(df_lvinspections)
    # json_records3 = df_lvinspections.reset_index().to_json(orient='records')
    # data3 = []
    # data3 = json.loads(json_records3)



    context ={
        'county' : county,
        # 'poorsags' : lvfaults.aggregate(p=Sum('poorsags')).get('p'),
        # 'vegline': lvfaults.aggregate(Vline=Sum('vegline'))['Vline'],
        # 'uprate_cond': lvfaults.aggregate(Ucond=Sum('uprate_cond'))['Ucond'],
        # 'pme': lvfaults.aggregate(P_me=Sum('pme'))['P_me'],
        # 'con_illegal' : lvfaults.aggregate(ICon=Sum('con_illegal'))['ICon'],
        # 'jumper_rehab': lvfaults.aggregate(JR=Sum('jumper_rehab'))['JR'],
        # 'overdistance': lvfaults.aggregate(OD=Sum('overdistance'))['OD'],
        # 'lvreconductor': lvfaults.aggregate(LvR=Sum('lvreconductor'))['LvR'],
        # 'poshomill': lvfaults.aggregate(PM=Sum('poshomill'))['PM'],
        'pole_defects' : data,
        'lv_def': data1,
        'title':'List Of Total Defects on the Network',
        'title2': 'List Of Pole Defects on the Network',
        'title3': 'Daily Summarized LV Inspections',
        'lvinspection_daily_trend' : lvinspection_daily_trend
    }
    return render(request, 'lv/lvinspections/county_lvinspections_dashbboard.html', context)
    
@login_required(login_url="login")
def county_lvinspections_list(request):
    county = UserProfile.objects.select_related('county').get(user=request.user).county
    # county = request.user.userprofile.county
    lv = Lvinspection.objects.select_related('substation','inspectedby__user').values('id','dtupdate','substation__name','inspectedby__user_id__stid','aprv_status','save_status').filter(county=county, save_status=True, aprv_status=True).order_by('-dtupdate')


    paginator = Paginator(lv, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context ={
        'county' : county,
        'data' : paged_uploads,
        'title':'List Of Approved LV Inspections',
    }
    return render(request, 'lv/lvinspections/county_lvinspections.html', context)
@login_required(login_url="login")
def ssn_txfailure(request, pk=None):
    txfailures = TxFailure.objects.filter(substation__ssn=pk, aprv_status=True)

    paginator = Paginator(txfailures, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context={
        'txfailures' : paged_uploads,
        'ssn' : pk,

    }
    return render(request, 'lv/ssn_txfailures.html', context)
@login_required(login_url="login")
def ssn_lvmaintenance(request, pk=None):
    lvmaintenance = MaintainLVinspection.objects.filter(lvinspection__substation__ssn=pk, aprv_status=True)
    paginator = Paginator(lvmaintenance, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context={
        'lvmaintenance' : paged_uploads,
        'ssn' : pk,

    }
    return render(request, 'lv/ssn_lvmaintenance.html', context)
@login_required(login_url="login")
def ssn_lvinspections(request, pk=None):
    lvinspections = Lvinspection.objects.filter(substation__ssn=pk, aprv_status=True)
    paginator = Paginator(lvinspections, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context={
        'lvinspections' : paged_uploads,
        'ssn' : pk,

    }
    return render(request, 'lv/ssn_lvinspections.html', context)
@login_required(login_url="login")
def lvinspection_maintain_update(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')
    maintain_insp = get_object_or_404(MaintainLVinspection, id=pk)
    lv_inspection  = get_object_or_404(Lvinspection, id=maintain_insp.lvinspection.id)
    maintain_form = MaintainLVinspectionForm()
    defect_poles = Poledefects.objects.filter(lvinspection=maintain_insp.lvinspection)

    if request.method == 'POST':
        lv_m_form = MaintainLVinspectionForm(request.POST)
        if lv_m_form.is_valid():
            m_form = lv_m_form.save(commit=False)
            m_form.lvinspection = maintain_insp.lvinspection
            m_form.retention_req = lv_m_form.cleaned_data['retention_req']
            m_form.retention_req_status = lv_m_form.cleaned_data['retention_req_status']
            m_form.traceclear_span = lv_m_form.cleaned_data['traceclear_span']
            m_form.traceclear_span_status = lv_m_form.cleaned_data['traceclear_span_status']
            m_form.conductors_uprate_status = lv_m_form.cleaned_data['conductors_uprate_status']
            m_form.conductors_uprate_span = lv_m_form.cleaned_data['conductors_uprate_span']
            m_form.pme_missing_poles = lv_m_form.cleaned_data['pme_missing_poles']
            m_form.pme_missing_poles_status = lv_m_form.cleaned_data['pme_missing_poles_status']
            m_form.lv_overdistance_l = lv_m_form.cleaned_data['lv_overdistance_l']
            m_form.lv_overdistance_l_status = lv_m_form.cleaned_data['lv_overdistance_l_status']
            m_form.illegal_connections_l = lv_m_form.cleaned_data['illegal_connections_l']
            m_form.illegal_connections_l_status = lv_m_form.cleaned_data['illegal_connections_l_status']
            m_form.reconducturing_pvc_l = lv_m_form.cleaned_data['reconducturing_pvc_l']
            m_form.reconducturing_pvc_l_status = lv_m_form.cleaned_data['reconducturing_pvc_l_status']
            m_form.poshomills_onsingle_p_n = lv_m_form.cleaned_data['poshomills_onsingle_p_n']
            m_form.poshomills_onsingle_p_n_status = lv_m_form.cleaned_data['poshomills_onsingle_p_n_status']
            m_form.inspect_notes = lv_m_form.cleaned_data['inspect_notes']
            m_form.txposition = lv_m_form.cleaned_data['txposition']
            m_form.other_defects = lv_m_form.cleaned_data['other_defects']
            m_form.inspectedby = request.user.userprofile
            m_form.save()
            messages.success(request, 'The LV Maintenance was saved successfully.')
            return redirect('lv:lvmaintenance-my',lv_inspection)
        else:
            print('invalid form')
            print(lv_m_form.errors)

    else:
        lv_form = LvinspectionForm(instance=maintain_insp)

    context = {
        'lv_inspection' : lv_inspection,
        'lv_form': lv_form,
        'maintain_form' : maintain_form,
        'defect_poles' : defect_poles,

    }
    return render(request, 'lv/lv_maintenance.html', context)

# @login_required(login_url="login")
# def lvmaintenance_new(request, pk=None):
#     ssn = get_object_or_404(Substation, id=pk)
#     any_pending = MaintainLVinspection.objects.filter(save_status=False, inspectedby=request.user.userprofile)
#     lvinspection = Lvinspection.objects.filter(substation=ssn,aprv_status=True).order_by('-dtadd')[0]
#     # poledefects = Poledefects.objects.filter(lvinspection=lvmaintenance.lvinspection)
#
#
#     if any_pending:
#         messages.error(request, 'You have an inspection that is saved as draft. Submit and click on new Inspection.')
#         return redirect('lv:lvmaintenance-my', pk)
#     new_inspection = MaintainLVinspection.objects.create(lvinspection=lvinspection, inspectedby=request.user.userprofile)
#     if new_inspection:
#         messages.success(request, 'A Draft of the New Inspection was saved successfully. Open to continue with the inspection')
#         return redirect('lv:lvmaintenance-my', pk)
#
#     context = {
#         'data': ssn,
#         'inspection_id' : new_inspection.id,
#
#     }
#     return render(request,'lv/lvFailure_inspect.html', context)
@login_required(login_url="login")
def poledefects_list(request, pk=None):
    poledefects_list = Poledefects.objects.filter(lvinspection__substation=pk, status=False)
    paginator = Paginator(poledefects_list, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context={
        'poledefects_list' : paged_uploads,
        'ssn' : pk,

    }
    return render(request, 'lv/poledefects/ssn_poledefects.html', context)
@login_required(login_url="login")
def poledefects_new(request):
    new_inspection = Lvinspection.objects.filter(inspectedby=request.user.userprofile).order_by('id').last()

    lv_form = LvinspectionForm()

    if request.method == 'POST':
        pole_form = PoledefectsForm(request.POST)


        if pole_form.is_valid():
            poled = pole_form.save(commit=False)
            poled.defect_type = pole_form.cleaned_data['defect_type']
            poled.x = pole_form.cleaned_data['x']
            poled.y = pole_form.cleaned_data['y']
            poled.location = pole_form.cleaned_data['location']
            poled.county = request.user.userprofile.county
            poled.region = request.user.userprofile.region
            poled.lvinspection = new_inspection
            poled.inspectedby = request.user.userprofile
            poled.substation = new_inspection.substation
            poled.save()

            # lv_form = Lvinsp_form.save(commit=False)
            # lv_form.substation = new_inspection.substation
            # lv_form.longitude = Lvinsp_form.cleaned_data['longitude']
            # lv_form.latitude = Lvinsp_form.cleaned_data['latitude']
            # lv_form.poles_leaning = 0
            # lv_form.poles_rotten = 0
            # lv_form.poor_sags_cl_cond = Lvinsp_form.cleaned_data['poor_sags_cl_cond']
            # lv_form.midspanpole_req = Lvinsp_form.cleaned_data['midspanpole_req']
            # lv_form.retention_req = Lvinsp_form.cleaned_data['retention_req']
            # lv_form.lvline_veg = Lvinsp_form.cleaned_data['lvline_veg']
            # lv_form.traceclear_span = Lvinsp_form.cleaned_data['traceclear_span']
            # lv_form.conductors_uprate = Lvinsp_form.cleaned_data['conductors_uprate']
            # lv_form.conductors_uprate_span = Lvinsp_form.cleaned_data['conductors_uprate_span']
            # lv_form.pme_installed = Lvinsp_form.cleaned_data['pme_installed']
            # lv_form.pme_missing_poles = Lvinsp_form.cleaned_data['pme_missing_poles']
            # lv_form.lv_overdistance = Lvinsp_form.cleaned_data['lv_overdistance']
            # lv_form.lv_overdistance_l = Lvinsp_form.cleaned_data['lv_overdistance_l']
            # lv_form.illegal_connections = Lvinsp_form.cleaned_data['illegal_connections']
            # lv_form.illegal_connections_l = Lvinsp_form.cleaned_data['illegal_connections_l']
            # lv_form.jumper_rehab_sect = Lvinsp_form.cleaned_data['jumper_rehab_sect']
            # lv_form.reconducturing_pvc = Lvinsp_form.cleaned_data['reconducturing_pvc']
            # lv_form.reconducturing_pvc_l = Lvinsp_form.cleaned_data['reconducturing_pvc_l']
            # lv_form.circuits = Lvinsp_form.cleaned_data['circuits']
            # lv_form.c1_r = Lvinsp_form.cleaned_data['c1_r']
            # lv_form.c1_b = Lvinsp_form.cleaned_data['c1_b']
            # lv_form.c1_y = Lvinsp_form.cleaned_data['c1_y']
            # lv_form.c2_1r = Lvinsp_form.cleaned_data['c2_1r']
            # lv_form.c2_1b = Lvinsp_form.cleaned_data['c2_1b']
            # lv_form.c2_1y = Lvinsp_form.cleaned_data['c2_1y']
            # lv_form.c2_2r = Lvinsp_form.cleaned_data['c2_2r']
            # lv_form.c2_2b = Lvinsp_form.cleaned_data['c2_2b']
            # lv_form.c2_2y = Lvinsp_form.cleaned_data['c2_2y']
            # lv_form.c3_1r = Lvinsp_form.cleaned_data['c3_1r']
            # lv_form.c3_1b = Lvinsp_form.cleaned_data['c3_1b']
            # lv_form.c3_1y = Lvinsp_form.cleaned_data['c3_1y']
            # lv_form.c3_2r = Lvinsp_form.cleaned_data['c3_2r']
            # lv_form.c3_2b = Lvinsp_form.cleaned_data['c3_2b']
            # lv_form.c3_2y = Lvinsp_form.cleaned_data['c3_2y']
            # lv_form.c3_3r = Lvinsp_form.cleaned_data['c3_3r']
            # lv_form.c3_3b = Lvinsp_form.cleaned_data['c3_3b']
            # lv_form.c3_3y = Lvinsp_form.cleaned_data['c3_3y']
            # lv_form.inspect_notes = Lvinsp_form.cleaned_data['inspect_notes']
            # lv_form.save_status = Lvinsp_form.cleaned_data['save_status']
            #
            # lv_form.county = request.user.userprofile.county
            # lv_form.inspectedby = request.user
            #
            # lv_form.save()

            # if lv_form.save_status == False:
            #     if poled.neutralearth_intact is None or lv_form.neutralearth_intact is None \
            #             or lv_form.surgdearth_intact is None or lv_form.surgd_connected is None or lv_form.c_tx_structure is None or lv_form.c_fuse_carriers is None:
            #         messages.error(request, 'All Fields are Required When doing a Final Submission.')
            #         return redirect('lvinspections:lvinspection-update', new_inspection.id)
            #     lv_form.save_status = True
            #     lv_form.save()
            messages.success(request, 'The Pole Defect was saved successfully.')
            return redirect('lv:lvinspection-update', new_inspection.id)
        else:
            print('invalid form')
            print(pole_form.errors)
            # print(Lvinsp_form.errors)
    else:
        pole_form = PoledefectsForm()
        # lv_form = LvinspectionForm(instance=new_inspection)


    context = {
        'lvinspections' : new_inspection,
        'pole_form' : pole_form,
        'lv_form': lv_form,
    }
    return render(request,'lv/poledefect_capture.html', context)
@login_required(login_url="login")
def lvfailure_update(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')
    inspection = get_object_or_404(TxFailure, id=pk)

    if request.method == 'POST':
         form = TxFailureForm(request.POST, instance=inspection)


         if form.is_valid():
            f_rep = form.save(commit=False)
            f_rep.substation = inspection.substation
            f_rep.longitude = form.cleaned_data['longitude']
            f_rep.latitude = form.cleaned_data['latitude']
            f_rep.serialno = form.cleaned_data['serialno']
            f_rep.voltage = form.cleaned_data['voltage']
            f_rep.kvarating = form.cleaned_data['kvarating']
            f_rep.txweight = form.cleaned_data['txweight']
            f_rep.gnumber = form.cleaned_data['gnumber']
            f_rep.make = form.cleaned_data['make']
            f_rep.yom = form.cleaned_data['yom']
            f_rep.location = form.cleaned_data['location']
            f_rep.tx_position = form.cleaned_data['tx_position']
            f_rep.incidence_no = form.cleaned_data['incidence_no']
            f_rep.failure_type = form.cleaned_data['failure_type']
            f_rep.tx_status = form.cleaned_data['tx_status']
            f_rep.refubby = form.cleaned_data['refubby']
            f_rep.workshop = form.cleaned_data['workshop']
            f_rep.contractor = form.cleaned_data['contractor']
            f_rep.weathercond = form.cleaned_data['weathercond']
            f_rep.hvearth_intact = form.cleaned_data['hvearth_intact']
            f_rep.hvearth_values_missing = form.cleaned_data["hvearth_values_missing"]
            f_rep.hvearth_values = form.cleaned_data['hvearth_values']
            f_rep.neutralearth_intact = form.cleaned_data['neutralearth_intact']
            f_rep.neutralvearth_values = form.cleaned_data['neutralvearth_values']
            f_rep.surgearrestors = form.cleaned_data['surgearrestors']
            f_rep.surgearrestors_values = form.cleaned_data['surgearrestors_values']
            f_rep.surge_arrestors_missing = form.cleaned_data["surge_arrestors_missing"]
            f_rep.tx_isolation = form.cleaned_data['tx_isolation']
            f_rep.expulsionondirectlink = form.cleaned_data['expulsionondirectlink']
            f_rep.powderondirectlink = form.cleaned_data['powderondirectlink']
            f_rep.c_lvleads = form.cleaned_data['c_lvleads']
            f_rep.c_fusecarriers = form.cleaned_data['c_fusecarriers']
            f_rep.d_fusecarriers = form.cleaned_data['d_fusecarriers']
            f_rep.shortet_lv_c_1 = form.cleaned_data['shortet_lv_c_1']
            f_rep.shortet_lv_c_2 = form.cleaned_data['shortet_lv_c_2']
            f_rep.shortet_lv_c_3 = form.cleaned_data['shortet_lv_c_3']
            f_rep.fuse_size_c_1 = form.cleaned_data['fuse_size_c_1']
            f_rep.fuse_size_c_2 = form.cleaned_data['fuse_size_c_2']
            f_rep.fuse_size_c_3 = form.cleaned_data['fuse_size_c_3']
            f_rep.hvlv_m_ohms = form.cleaned_data['hvlv_m_ohms']
            f_rep.hvearth_m_ohms = form.cleaned_data['hvearth_m_ohms']
            f_rep.lvearth_m_ohms = form.cleaned_data['lvearth_m_ohms']
            f_rep.R_Y = form.cleaned_data['R_Y']
            f_rep.Y_B = form.cleaned_data['Y_B']
            f_rep.B_R = form.cleaned_data['B_R']
            f_rep.r_n = form.cleaned_data['r_n']
            f_rep.y_n = form.cleaned_data['y_n']
            f_rep.b_n = form.cleaned_data['b_n']
            f_rep.recommendations = form.cleaned_data['recommendations']
            f_rep.county = request.user.userprofile.county
            f_rep.region = request.user.userprofile.region
            f_rep.inspectedby = request.user.userprofile
            if request.POST.get("finalsubmission"):
                f_rep.save_status = True
                f_rep.save()
                messages.success(request, 'The Tx Failure  Inspection was submitted successfully.')
                return redirect('lv:lvfailure-my')

            elif request.POST.get("draft"):
                f_rep.save_status = False
                f_rep.save()
                messages.success(request, 'The TX Failure Inspection was saved as a draft successfully.')
                return redirect('lv:lvfailure-my')

         else:
            print('invalid form')
            print(form.errors)
    else:
        form = TxFailureForm(instance=inspection)
    context={
        'form' : form,
        'data' : inspection.substation.ssn,
        'tx_f_id': inspection.id,

    }

    return render(request, 'lv/lvFailure_inspect.html', context)

@login_required(login_url="login")
def lvfailure_new(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')
    ssn = get_object_or_404(Substation, id=pk)
    lv = Lvinspection.objects.filter(substation=ssn, aprv_status=True, dtupdate__gt=datetime.today() - timedelta(hours=48))
    any_pending = TxFailure.objects.filter(save_status=False, inspectedby=request.user.userprofile)

    if any_pending:
        messages.error(request, 'You have an inspection that is saved as draft. Submit and click on new Inspection.')
        return redirect('lv:lvfailure-my')
    if not lv:
        messages.error(request, 'There is no Approved LV Inspection that is not more than 48hrs old for that substation.')
        return redirect('main:my-dashboard')
    new_inspection = TxFailure.objects.create(substation=ssn, inspectedby=request.user.userprofile)
    if new_inspection:
        messages.success(request, 'A Draft of the New Inspection was saved successfully. Open to continue with the inspection')
        return redirect('lv:lvfailure-my')

    context = {
        'data': ssn,
        'inspection_id' : new_inspection.id,

    }
    return render(request,'lv/lvFailure_inspect.html', context)
@login_required(login_url="login")
def lvinspection_maintenance(request,pk=None):
    substation = get_object_or_404(Substation, id=pk)
    lvs = Lvinspection.objects.filter(county__substation__ssn=substation, aprv_status=True)

    context ={
        'data' : lvs,
        'title':'List Of Approved LV INmspections',
    }
    return render(request, 'lv/ssn_maintenace_qry.html', context)
@login_required(login_url="login")
def lv_inspections_county(request):
    county = request.user.userprofile.county
    lv = Lvinspection.objects.filter(county=county)
    lvinspections_apprvd = lv.filter(aprv_status='True')
    lvinspections_pending_app = lv.filter(aprv_status='False')

    context ={
        'county' : county,
        'data' : lvinspections_apprvd,
        'title':'List Of Approved LV INmspections',
        'count' : lvinspections_apprvd.count(),
        'count_pending' : lvinspections_pending_app.count()
    }
    return render(request, 'lv/lvinspections/county_lvinspections.html', context)
@login_required(login_url="login")
def lvinspection_approve(request, pk=None):
    lv_inspection = get_object_or_404(Lvinspection, id=pk,save_status=True)
    poledefects = Poledefects.objects.filter(lvinspection=lv_inspection)

    if request.method == 'POST':
        form = LvinspectionApproveForm(request.POST, instance=lv_inspection)

        if form.is_valid():
            regis = form.save(commit=False)
            regis.aprv_notes = form.cleaned_data['aprv_notes']
            regis.aprv_key = form.cleaned_data['aprv_key']
            regis.aprv_by = request.user.userprofile
            regis.aprv_status = True
            regis.aprv_dt =  date.today()
            regis.save()
            messages.success(request, 'The LV Inspection was Approved/Declined successfully.')
            return redirect('lv:county-lv-pages')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = LvinspectionApproveForm(instance=lv_inspection)

    context = {
        'lvinspection': lv_inspection,
        'form' : form,
        'poledefects' : poledefects,
    }
    return render(request, 'lv/lvinspection_approve.html', context)
@login_required(login_url="login")
def lv_inspections_approve(request,pk=None):
    lvinspection = get_object_or_404(Lvinspection, id=pk)

    context ={
        'lvinspection' : lvinspection,

    }
    return render(request, 'lv/lvinspection_approve.html', context)
@login_required(login_url="login")
def lv_inspections_pending_app(request):
    county = request.user.userprofile.county
    lvinspections_pending_app = Lvinspection.objects.select_related('substation','inspectedby__user').values('id','dtupdate','substation__name','inspectedby__user_id__stid','aprv_status','save_status').filter(county=county, save_status=True, aprv_status=False).order_by('-dtupdate')

    # paginator = Paginator(lvinspections_pending_app, 20)
    # page = request.GET.get("page")
    # paged_uploads = paginator.get_page(page)

    context ={
        # 'data' : paged_uploads,
        'title':'LV Inspections Pending Approval',
        'county': county,
        'data' : lvinspections_pending_app


    }
    return render(request, 'lv/lvinspections/county_lvinspections.html', context)
@login_required(login_url="login")
def county_analysis(request):
    campaign = request.user.userprofile.campaign
    county = request.user.userprofile.county
    if campaign == 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')

    #DATE_RANGE = datetime.datetime.today() - datetime.timedelta(days=180)
    poledefects_list = Poledefects.objects.select_related('county').filter(county=county,status=False).values('dtadd','id','defect_type')
    lvinspections = Lvinspection.objects.select_related('county').filter(county=county,aprv_status=True).values('id','dtadd')
    lvmaintenance = MaintainLVinspection.objects.filter(lvinspection__county=county, aprv_status=True).values('id', 'dtadd')
    lvfailure = TxFailure.objects.select_related('county').filter(county=county, aprv_status=True).values('id','dtadd')
    lvsubstation = SubstationInspection.objects.select_related('county').filter(county=county, aprv_status=True).values('id', 'dtadd')
    commission = Commission_substation.objects.select_related('county').filter(county=county, aprv_status=True).values(
        'id', 'dtadd')

    # def PoleDefects_analysis():
    #     df = read_frame(poledefects_list)
    #     df = df.groupby(by='defect_type', as_index=False, sort=False)['id'].count()
    #     names = df.defect_type
    #     values = df.id
    #     df = px.pie(df, values=values, names=names, title=f'Total Defects-{poledefects_list.count()}')
    #     df.update_traces(textposition='inside', textinfo='percent+label')
    #     df.update_layout(margin=dict(l=20, r=20, b=20), ),
    #     df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
    #     return df

    # def lvinspection_daily_trend():
    #     df = read_frame(lvinspections)
    #     df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
    #     df = df.groupby(by="dtadd", as_index=False, sort=False)["id"].count()
    #     df = px.bar(
    #         df,
    #         x=df.dtadd,
    #         y=df.id,
    #         title="Daily Overall Inspections.",
    #         text_auto=True,
    #         text=df.id,
    #         labels={"id": "Count", "dtadd": "Date"},
    #     )
    #     df.update_layout(
    #         margin=dict(l=20, r=20, b=20),
    #         title_text=f'Lv Inspections- {lvinspections.count()}', title_x=0.5, font={'size': 12},
    #         # title=("Target vs Achievement"),
    #         xaxis_tickfont_size=14,
    #         yaxis_range=[0, 6],
    #         yaxis=dict(
    #             title="No Of Inspections",
    #             titlefont_size=16,
    #             tickfont_size=14,
    #             range=[0, 5]
    #         ),
    #         xaxis=dict(
    #             title="Period",
    #         ),
    #         legend=dict(
    #             bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
    #         ),
    #         barmode="group",
    #         bargap=0.15,  # gap between bars of adjacent location coordinates.
    #         bargroupgap=0.1,  # gap between bars of the same location coordinate.
    #     )
    #     df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
    #     return df_daolytrend

    # def lvmaintenance_daily_trend():
    #     df = read_frame(lvmaintenance)
    #     df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
    #     df = df.groupby(by="dtadd", as_index=False, sort=False)["id"].count()
    #     df = px.bar(
    #         df,
    #         x=df.dtadd,
    #         y=df.id,
    #         title="Daily Overall Maintenance.",
    #         text_auto=True,
    #         text=df.id,
    #         labels={"id": "Count", "dtadd": "Date"},
    #     )
    #     df.update_layout(
    #         margin=dict(l=20, r=20, b=20),
    #         title_text=f'Lv Maintenance Inspections- {lvmaintenance.count()}', title_x=0.5, font={'size': 12},
    #         # title=("Target vs Achievement"),
    #         xaxis_tickfont_size=14,
    #         yaxis_range=[0, 6],
    #         yaxis=dict(
    #             title="No Of Inspections",
    #             titlefont_size=16,
    #             tickfont_size=14,
    #             range=[0, 5]
    #         ),
    #         xaxis=dict(
    #             title="Period",
    #         ),
    #         legend=dict(
    #             bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
    #         ),
    #         barmode="group",
    #         bargap=0.15,  # gap between bars of adjacent location coordinates.
    #         bargroupgap=0.1,  # gap between bars of the same location coordinate.
    #     )
    #     df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
    #     return df_daolytrend

    
    # def lvfailure_daily_trend():
    #     df = read_frame(lvfailure)
    #     df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
    #     df = df.groupby(by="dtadd", as_index=False, sort=False)["id"].count()
    #     df = px.bar(
    #         df,
    #         x=df.dtadd,
    #         y=df.id,
    #         title="Daily Overall Tx Failure.",
    #         text_auto=True,
    #         text=df.id,
    #         labels={"id": "Count", "dtadd": "Date"},
    #     )
    #     df.update_layout(
    #         margin=dict(l=20, r=20, b=20),
    #         title_text=f'Lv Failure Inspections- {lvfailure.count()}', title_x=0.5, font={'size': 12},
    #         # title=("Target vs Achievement"),
    #         xaxis_tickfont_size=14,
    #         yaxis_range=[0, 6],
    #         yaxis=dict(
    #             title="No Of Inspections",
    #             titlefont_size=16,
    #             tickfont_size=14,
    #             range=[0, 5]
    #         ),
    #         xaxis=dict(
    #             title="Period",
    #         ),
    #         legend=dict(
    #             bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
    #         ),
    #         barmode="group",
    #         bargap=0.15,  # gap between bars of adjacent location coordinates.
    #         bargroupgap=0.1,  # gap between bars of the same location coordinate.
    #     )
    #     df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
    #     return df_daolytrend

    # def lvsubstation_daily_trend():
    #     df = read_frame(lvsubstation)
    #     df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
    #     df = df.groupby(by="dtadd", as_index=False, sort=False)["id"].count()
    #     df = px.bar(
    #         df,
    #         x=df.dtadd,
    #         y=df.id,
    #         title="Daily Overall Substtation Inspections.",
    #         text_auto=True,
    #         text=df.id,
    #         labels={"id": "Count", "dtadd": "Date"},
    #     )
    #     df.update_layout(
    #         margin=dict(l=20, r=20, b=20),
    #         title_text=f'Lv Substation Inspections- {lvsubstation.count()}', title_x=0.5, font={'size': 12},
    #         # title=("Target vs Achievement"),
    #         xaxis_tickfont_size=14,
    #         yaxis_range=[0, 6],
    #         yaxis=dict(
    #             title="No Of Inspections",
    #             titlefont_size=16,
    #             tickfont_size=14,
    #             range=[0, 5]
    #         ),
    #         xaxis=dict(
    #             title="Period",
    #         ),
    #         legend=dict(
    #             bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
    #         ),
    #         barmode="group",
    #         bargap=0.15,  # gap between bars of adjacent location coordinates.
    #         bargroupgap=0.1,  # gap between bars of the same location coordinate.
    #     )
    #     df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
    #     return df_daolytrend

    # def commission_daily_trend():
    #     df = read_frame(commission)
    #     df["dtadd"] = pd.to_datetime(df["dtadd"]).dt.date
    #     df = df.groupby(by="dtadd", as_index=False, sort=False)["id"].count()
    #     df = px.bar(
    #         df,
    #         x=df.dtadd,
    #         y=df.id,
    #         title="Daily Overall Commission Inspections.",
    #         text_auto=True,
    #         text=df.id,
    #         labels={"id": "Count", "dtadd": "Date"},
    #     )
    #     df.update_layout(
    #         margin=dict(l=20, r=20, b=20),
    #         title_text=f'Lv Commission Inspections- {commission.count()}', title_x=0.5, font={'size': 12},
    #         # title=("Target vs Achievement"),
    #         xaxis_tickfont_size=14,
    #         yaxis_range=[0, 6],
    #         yaxis=dict(
    #             title="No Of Inspections",
    #             titlefont_size=16,
    #             tickfont_size=14,
    #             range=[0, 5]
    #         ),
    #         xaxis=dict(
    #             title="Period",
    #         ),
    #         legend=dict(
    #             bgcolor="rgba(255, 255, 255, 0)", bordercolor="rgba(255, 255, 255, 0)"
    #         ),
    #         barmode="group",
    #         bargap=0.15,  # gap between bars of adjacent location coordinates.
    #         bargroupgap=0.1,  # gap between bars of the same location coordinate.
    #     )
    #     df_daolytrend = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
    #     return df_daolytrend

    context ={

        # 'poledefects' : PoleDefects_analysis,
        'county':county,
        # 'lvinspections': lvinspection_daily_trend,
        # 'lvmaintenance': lvmaintenance_daily_trend,
        # 'lvfailure_daily_trend' : lvfailure_daily_trend,
        # 'lvsubstation_daily_trend' : lvsubstation_daily_trend,
        # 'commission_daily_trend': commission_daily_trend
    }

    return render(request, 'lv/county_analysiss.html', context)
    
@login_required(login_url="login")
def lvinspection_print(request, pk=None):
    lvinspection = get_object_or_404(Lvinspection, id=pk)
    poledefects = Poledefects.objects.filter(lvinspection=lvinspection)

    context ={
        'lvinspection' : lvinspection,
        'poledefects' : poledefects
    }

    return render(request, 'lv/lv_inspection_print.html', context)
@login_required(login_url="login")
def lvinspection_update(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')
    lvinspection = get_object_or_404(Lvinspection, id=pk)
    poledefects = Poledefects.objects.filter(lvinspection=lvinspection)
    pole_form = PoledefectsForm()

    if request.method == 'POST':
        lv_form = LvinspectionForm(request.POST, instance=lvinspection)

        if lv_form.is_valid():
            poled = lv_form.save(commit=False)
            poled.substation = lvinspection.substation
            poled.longitude = lv_form.cleaned_data['longitude']
            poled.latitude = lv_form.cleaned_data['latitude']
            poled.poor_sags_cl_cond = lv_form.cleaned_data['poor_sags_cl_cond']
            poled.retention_req = lv_form.cleaned_data['retention_req']
            poled.retention_maintanance = lv_form.cleaned_data['retention_maintanance']
            poled.lvline_veg = lv_form.cleaned_data['lvline_veg']
            poled.traceclear_span = lv_form.cleaned_data['traceclear_span']
            poled.trace_maintanance = lv_form.cleaned_data['trace_maintanance']
            poled.conductors_uprate = lv_form.cleaned_data['conductors_uprate']
            poled.conductors_uprate_span = lv_form.cleaned_data['conductors_uprate_span']
            poled.upratingconduct_maintanance = lv_form.cleaned_data['upratingconduct_maintanance']
            poled.pme_installed = lv_form.cleaned_data['pme_installed']
            poled.pme_missing_poles = lv_form.cleaned_data['pme_missing_poles']
            poled.pme_maintanance = lv_form.cleaned_data['pme_maintanance']
            poled.lv_overdistance = lv_form.cleaned_data['lv_overdistance']
            poled.lv_overdistance_l = lv_form.cleaned_data['lv_overdistance_l']
            poled.lvoverdistance_maintanance = lv_form.cleaned_data['lvoverdistance_maintanance']
            poled.illegal_connections = lv_form.cleaned_data['illegal_connections']
            poled.illegal_connections_l = lv_form.cleaned_data['illegal_connections_l']
            poled.illegalconn_maintanance = lv_form.cleaned_data['illegalconn_maintanance']
            poled.jumper_rehab_sect = lv_form.cleaned_data['jumper_rehab_sect']
            poled.jumperrehab_maintanance = lv_form.cleaned_data['jumperrehab_maintanance']
            poled.reconducturing_pvc = lv_form.cleaned_data['reconducturing_pvc']
            poled.reconducturing_pvc_l = lv_form.cleaned_data['reconducturing_pvc_l']
            poled.reconductering_maintanance = lv_form.cleaned_data['reconductering_maintanance']
            poled.poshomills_onsingle_p = lv_form.cleaned_data['poshomills_onsingle_p']
            poled.poshomills_onsingle_p_n = lv_form.cleaned_data['poshomills_onsingle_p_n']
            poled.poshomill_maintenance = lv_form.cleaned_data['poshomill_maintenance']
            poled.circuits = lv_form.cleaned_data['circuits']
            poled.c1_r = lv_form.cleaned_data['c1_r']
            poled.c1_b = lv_form.cleaned_data['c1_b']
            poled.c1_y = lv_form.cleaned_data['c1_y']
            poled.c2_1r = lv_form.cleaned_data['c2_1r']
            poled.c2_1b = lv_form.cleaned_data['c2_1b']
            poled.c2_1y = lv_form.cleaned_data['c2_1y']
            poled.c2_2r = lv_form.cleaned_data['c2_2r']
            poled.c2_2b = lv_form.cleaned_data['c2_2b']
            poled.c2_2y = lv_form.cleaned_data['c2_2y']
            poled.c3_1r = lv_form.cleaned_data['c3_1r']
            poled.c3_1b = lv_form.cleaned_data['c3_1b']
            poled.c3_1y = lv_form.cleaned_data['c3_1y']
            poled.c3_2r = lv_form.cleaned_data['c3_2r']
            poled.c3_2b = lv_form.cleaned_data['c3_2b']
            poled.c3_2y = lv_form.cleaned_data['c3_2y']
            poled.c3_3r = lv_form.cleaned_data['c3_3r']
            poled.c3_3b = lv_form.cleaned_data['c3_3b']
            poled.c3_3y = lv_form.cleaned_data['c3_3y']
            poled.inspect_notes = lv_form.cleaned_data['inspect_notes']
            poled.county = request.user.userprofile.county
            poled.region = request.user.userprofile.region
            poled.inspectedby = request.user.userprofile



            if request.POST.get("finalsubmission"):
                with transaction.atomic():
                    poled.save_status = True
                    poled.save()
                    lv_d = Lv_defaults.objects.create(
                        lvinspection=lvinspection,
                        county=request.user.userprofile.county,
                        region = request.user.userprofile.region,
                        poorsags = poled.retention_req,
                        vegline = poled.traceclear_span,
                        uprate_cond = poled.conductors_uprate_span,
                        pme =poled.pme_missing_poles,
                        con_illegal = poled.illegal_connections_l,
                        jumper_rehab = poled.jumper_rehab_sect,
                        poshomill = poled.poshomills_onsingle_p_n,
                        overdistance = poled.lv_overdistance_l,
                        lvreconductor = poled.reconducturing_pvc_l,
                        inspectedby=request.user.userprofile,
                        substation=lvinspection.substation
                    )
                    lv_d.save()
                messages.success(request, 'The LV  Inspection was submitted successfully.')
                return redirect('lv:lvinspection-my')

            elif request.POST.get("draft"):
                poled.save_status = False
                poled.save()
                messages.success(request, 'The LV Inspection was saved as a draft successfully.')
                return redirect('lv:lvinspection-my')

            messages.success(request, 'The LV Inspection was saved successfully.')
            return redirect('lv:lvinspection-my')
        else:
            print('invalid form')
            print(lv_form.errors)
    else:
        lv_form = LvinspectionForm(instance=lvinspection)


    context ={
        'lv': lvinspection.id,
        'lv_form': lv_form,
        'poledefects' : poledefects,
        'pole_form' : pole_form

    }

    return render(request,'lv/lv_inspection_new.html', context)
@login_required(login_url="login")
def lvinspection_new(request, pk=None):
    campaign = request.user.userprofile.campaign
    ssn = get_object_or_404(Substation, id=pk)
    any_pending = Lvinspection.objects.filter(save_status=False, inspectedby=request.user.userprofile)

    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')

    if any_pending:
        messages.error(request, 'You have an inspection that is saved as draft. Submit and click on new Inspection.')
        return redirect('lv:lvinspection-my')
    new_inspection = Lvinspection.objects.create(substation=ssn, inspectedby=request.user.userprofile)
    if new_inspection:
        messages.success(request, 'A Draft of the New Inspection was saved successfully. Open to continue with the inspection')
        return redirect('lv:lvinspection-my')

    context = {
        'data': ssn,
        'inspection_id' : new_inspection.id,

    }
    return render(request,'lv/ssn_dashboard.html', context)

@login_required(login_url="login")
def substation_search(request):
    if request.user.is_authenticated:
        user = request.user

    return render(request, 'lv/substation_search.html',)
@login_required(login_url="login")
def search_by_ssn(request):
    # sb_list = Substation.objects.filter(county=request.user.userprofile.county)
    sb_list = Substation.objects.select_related('county').values('ssn','id','name','physicallocation','originofelement','feederofelement','county__name').filter(county=request.user.userprofile.county)
    if 'keyword' in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            sb_list = sb_list.filter(ssn__icontains=keyword)

    context = {
         'data' : sb_list,
    }
    return  render(request, 'lv/substation_search.html', context)
@login_required(login_url="login")
def ssn_detail(request, pk=None):
    # ssn = get_object_or_404(Substation, id=pk)
    ssn1 = Substation.objects.select_related('county').values('id','ssn','name','physicallocation','originofelement','feederofelement','county__name').get(id=pk)
    lv_inspections = Lvinspection.objects.filter(substation=pk, aprv_status=True, aprv_key='approved').order_by('-dtupdate')
    lv_maintenance = MaintainLVinspection.objects.filter(lvinspection__substation=pk, aprv_status=True, aprv_key='approved').order_by(
        '-dtupdate')
    substation_inspections = SubstationInspection.objects.filter(substation=pk, aprv_status=True,
                                                         aprv_key='approved').order_by(
        '-dtupdate')

    lvfaults = Lv_defaults.objects.filter(substation=pk)
    substationfaults = Substation_defaults.objects.filter(substation=pk)


    pole_defects = Poledefects.objects.select_related('county').filter(substation=pk, status=False).order_by(
        'defect_type')


    df_poledefects = read_frame(pole_defects)
    df_poledefects = df_poledefects.groupby(by=['defect_type', 'pole_type'], as_index=False, sort=False)['id'].count()
    json_records_poled = df_poledefects.reset_index().to_json(orient='records')
    data_pd = []
    data_pd = json.loads(json_records_poled)



    df_defaults = read_frame(lvfaults)
    # df_defaults = df_defaults.groupby(by='county',as_index=False, sort=False).agg([np.sum])
    df_defaults = df_defaults.groupby(["county"]).agg(
        {'vegline': 'sum', 'poorsags': 'sum', 'uprate_cond': 'sum',
         'pme': 'sum', 'con_illegal': 'sum', 'jumper_rehab': 'sum', 'overdistance': 'sum', 'lvreconductor': 'sum',
         'poshomill': 'sum'})
    json_records1 = df_defaults.reset_index().to_json(orient='records')
    data1 = []
    data1 = json.loads(json_records1)

    sub_defaults = read_frame(substationfaults)
    # df_defaults = df_defaults.groupby(by='county',as_index=False, sort=False).agg([np.sum])
    sub_defaults = sub_defaults.groupby(["county"]).agg(
        {'hvearthintact': 'sum', 'surgearresters': 'sum', 'arcinghones': 'sum',
         'txloading': 'sum', 'txstructure': 'sum', 'fusecarriers': 'sum', 'fusebar': 'sum','neutralearthintact': 'sum'})
    json_records_sub = sub_defaults.reset_index().to_json(orient='records')
    data_sub = []
    data_sub = json.loads(json_records_sub)

    p = Poledefects.objects.filter(substation_id=ssn1['id'],status=False).values('dtadd','id').annotate(all_defects=Coalesce(Count('defect_type'),0)).order_by('defect_type')

    # # lv_maintenance= MaintainLVinspection.objects.select_related('substation').filter(lvinspection__substation__ssn=ssn1['ssn'])
    # substation = SubstationInspection.objects.select_related('inspectedby').filter(inspectedby=request.user.userprofile).order_by('-dtadd')[:3]
    # failure = TxFailure.objects.select_related('inspectedby').filter(inspectedby=request.user.userprofile).order_by('-dtadd')[:3]

    def PoleDefects_analysis():
        x = p.values_list('defect_type', flat=True)
        y = p.values_list('all_defects', flat=True)
        fig = px.pie(values=y, names=x, title='Pole Defects', labels={
                "defect_type": "DEFECT TYPE",

            },)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(margin=dict(l=20, r=20,  b=20),),
        fig_plot = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return fig_plot

    def lvinspections():
        df = read_frame(lv_inspections)
        by_month = pd.to_datetime(df['dtadd']).dt.to_period('M').value_counts().sort_index()
        by_month.index = pd.PeriodIndex(by_month.index)
        df_month = by_month.rename_axis('month').reset_index(name='counts')
        fig = go.Figure(data=go.Bar(x=df_month['month'].astype(dtype=str),
                                    y=df_month['counts'],
                                    text="counts",
                                    ))
        # fig.update_layout({"title": 'Tweets about Malioboro from Jan 2020 to Jan 2021',
        #                    "xaxis": {"title": "Months"},
        #                    "yaxis": {"title": "Total tweets"},
        #                    "showlegend": False})
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            margin=dict(l=20, r=20, b=20),
            title_text='Lv Inspections(Last 12 Months)', title_x=0.5, font={'size': 12},
            # title=("Target vs Achievement"),
            xaxis_tickfont_size=14,
            yaxis_range=[0, 6],
            yaxis=dict(
                title="No Of Inspections",
                titlefont_size=16,
                tickfont_size=14,
                range=[0, 5]
            ),
            xaxis=dict(
                title="Period",
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

    def lvmaintenance():
        df = read_frame(MaintainLVinspection.objects.filter(lvinspection__substation=ssn1['id'], aprv_status=True, aprv_key='approved').values('dtadd','id'))
        by_month = pd.to_datetime(df['dtadd']).dt.to_period('M').value_counts().sort_index()
        by_month.index = pd.PeriodIndex(by_month.index)
        df_month = by_month.rename_axis('month').reset_index(name='counts')
        fig = go.Figure(data=go.Bar(x=df_month['month'].astype(dtype=str),
                                    y=df_month['counts'],
                                    text="counts",
                                    ))
        # fig.update_layout({"title": 'Tweets about Malioboro from Jan 2020 to Jan 2021',
        #                    "xaxis": {"title": "Months"},
        #                    "yaxis": {"title": "Total tweets"},
        #                    "showlegend": False})
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            margin=dict(l=20, r=20, b=20),
            title_text='Lv Maintenance(Last 12 Months)', title_x=0.5, font={'size': 12},
            # title=("Target vs Achievement"),
            xaxis_tickfont_size=14,
            yaxis_range=[0, 6],
            yaxis=dict(
                title="No Of Inspections",
                titlefont_size=16,
                tickfont_size=14,
                range=[0, 5]
            ),
            xaxis=dict(
                title="Period",
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

    def txfailure():
        df = read_frame(TxFailure.objects.filter(substation=ssn1['id'], aprv_status=True, aprv_key='approved').values('dtadd','id'))
        by_month = pd.to_datetime(df['dtadd']).dt.to_period('M').value_counts().sort_index()
        by_month.index = pd.PeriodIndex(by_month.index)
        df_month = by_month.rename_axis('month').reset_index(name='counts')
        fig = go.Figure(data=go.Bar(x=df_month['month'].astype(dtype=str),
                                    y=df_month['counts'],
                                    text="counts",
                                    ))
        # fig.update_layout({"title": 'Tweets about Malioboro from Jan 2020 to Jan 2021',
        #                    "xaxis": {"title": "Months"},
        #                    "yaxis": {"title": "Total tweets"},
        #                    "showlegend": False})
        fig.update_traces(
            texttemplate="%{y}<br>",  # use '%{text}' to show only percentage
            textposition="outside",
        )
        fig.update_layout(
            margin=dict(l=20, r=20, b=20),
            title_text='TX Failures (Last 12 Months)', title_x=0.5, font={'size': 12},
            # title=("Target vs Achievement"),
            xaxis_tickfont_size=14,
            yaxis_range=[0, 6],
            yaxis=dict(
                title="No Of Failures",
                titlefont_size=16,
                tickfont_size=14,
                range=[0, 5]
            ),
            xaxis=dict(
                title="Period",
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



    context ={
        'data': ssn1,
        'lv_def': data1,
        'lv_inspections': lv_inspections,
        # 'p':p,
        'df_f_plot': txfailure(),
        'poledefects' : PoleDefects_analysis(),

        # 'lv_maintenance' : lvmaintenance,
        # 'substation' : substation,
        'failure' : txfailure(),
        'df': PoleDefects_analysis(),
        'df_lv': lvinspections(),
        'df_m_plot': lvmaintenance(),
        'title' : 'LV defaults on the Substation',
        'pole_defects': data_pd,
        'poledefects' : pole_defects,
        'data_sub' : data_sub,
        'lv_maintenance' : lv_maintenance,
        'substation_inspections' : substation_inspections
    }

    return render(request,'lv/lvinspections/ssn_dashboard.html', context)