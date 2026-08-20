from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Mvinspection, Mv_poledefects, Mvmaitenance,Mv_defaults, Poledefects_maintenance
from main.models import Feeder, Feeder_sections
from user.models import UserProfile
from django.contrib import messages

from django.db.models import Count, F, Max, Value
from django.db.models.functions import Coalesce

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .forms import (
    MvinspectionForm,
    MvPoledefectsForm,
    MvinspectionApproveForm,
    MvmaintenanceForm, MvmaintenanceApproveForm,Poledefects_maintenanceForm
)
from main.models import Region,County
from django_pandas.io import read_frame
from django.db.models import F, Q
from django.db.models import Count, Sum, FloatField
from itertools import chain
from django_pandas.io import read_frame
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd
import datetime
from django.db import transaction
from datetime import timedelta, time, date,datetime

# views.py
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render
from .models import Mvinspection, Mv_poledefects
from collections import defaultdict


def mvinspection_with_defects_view(request):
    """
    Equivalent of the provided SQL:
      - LEFT JOINs county, feeder, feeder_section, approved/inspected users
      - LEFT JOIN defects and groups by inspection + defect dimensions
      - COALESCE for missing polefitting_type/defect_type -> 'UNKNOWN'
      - COUNT(p.id) as defect_count
      - Ordered by dtadd DESC, feeder_name, feeder_section_name, polefitting_type, defect_type
    Returns JSON list of dicts.
    """

    # ---- Annotations (aliases & coalesce) ----
    # NOTE: If your reverse relation from MvInspection -> MvPoleDefect is not "poledefects",
    # replace "poledefects__..." with the actual related name, e.g., "mvpoledefect_set__..."
    qs = (
        mv.objects
        .select_related('county', 'inspectedby__user', 'feeder', 'feeder_section')
        .annotate(
            county_name=F('county__name'),
            inspected_by_staffID=F('inspectedby__user__stid'),
            feeder_name=F('feeder__name'),
            feeder_section_name=F('feeder_section__name'),
            polefitting_type=Coalesce(F('poledefects__polefitting_type'), Value('UNKNOWN')),
            defect_type=Coalesce(F('poledefects__defect_type'), Value('UNKNOWN')),
        )
        # GROUP BY is implicit in Django when you call .values(...) with .annotate(...)
        .values(
            # ---- All selected inspection fields (i.*) ----
            'id',
            'feeder_section_id',
            'feeder_id',
            'no_poleswithoutstays',
            'no_rottentxstructure',
            'no_leaningtxstructure',
            'no_sagstoretention',
            'no_sectionstodoublejumper',
            'no_replacefusemounts',
            'no_bypassedhtfuses',
            'no_spurtaplins',
            'no_faultyabswitces',
            'no_installabswitces',
            'no_overhangingtrees',
            'no_tracemaint',
            'no_upratingconductors',
            'no_autoclosures',
            'no_autoclosuresfaulty',
            'no_faultyhvcable',
            'no_structureswithouttx',
            'no_jumpercableswithoutlugs',
            'no_disconnsurged',
            'no_txmissingearthing',
            'no_ssnnumberless',
            'no_wayleaveinfrng',
            'no_leakingpininsul',
            'no_leakingsuspinsul',
            'comments',
            'save_status',
            'aprv_status',
            'aprv_by_id',
            'aprv_notes',
            'aprv_dt',
            'aprv_key',
            'dtadd',
            'dtupdate',
            'inspectedby_id',
            'county_id',

            # ---- Enriched names (annotations) ----
            'county_name',
            'inspected_by_staffID',
            'feeder_name',
            'feeder_section_name',

            # ---- Grouping dimensions from defects (coalesced) ----
            'polefitting_type',
            'defect_type',
        )
        .annotate(
            # COUNT(p.id) AS defect_count
            defect_count=Count('poledefects__id')
        )
        .order_by(
            '-dtadd',            # i.dtadd DESC
            'feeder_name',
            'feeder_section_name',
            'polefitting_type',
            'defect_type',
        )
    )

    # Return as JSON list
    return JsonResponse(list(qs), safe=False)


def inspection_list(request):
    """
    List all inspections, with related names and grouped defect counts
    (polefitting_type x defect_type) per inspection.
    """
    # Base queryset of inspections with names (avoid N+1 queries)
    inspections_qs = (
        Mvinspection.objects
        .select_related('feeder', 'feeder_section', 'county', 'inspectedby', 'aprv_by')
        .order_by('-dtadd')
    )

    # Optional filters via query params
    feeder_id = request.GET.get('feeder')
    county_id = request.GET.get('county')
    if feeder_id:
        inspections_qs = inspections_qs.filter(feeder_id=feeder_id)
    if county_id:
        inspections_qs = inspections_qs.filter(county_id=county_id)

    # Paginate inspections
    paginator = Paginator(inspections_qs, 25)  # 25 per page
    page_number = request.GET.get('page')
    inspections_page = paginator.get_page(page_number)

    # Compute grouped counts across the inspections currently on page (efficient)
    page_inspection_ids = [i.id for i in inspections_page.object_list]

    grouped = (
        Mv_poledefects.objects
        .filter(mvinspection_id__in=page_inspection_ids)
        .values('mvinspection_id', 'polefitting_type', 'defect_type')
        .annotate(defect_count=Count('id'))
        .order_by('mvinspection_id', 'polefitting_type', 'defect_type')
    )

    # Build mapping: inspection_id -> list of grouped rows
    # Each item: { 'polefitting_type': ..., 'defect_type': ..., 'defect_count': ... }
    grouped_map = {iid: [] for iid in page_inspection_ids}
    for row in grouped:
        grouped_map[row['mvinspection_id']].append({
            'polefitting_type': row['polefitting_type'] or 'UNKNOWN',
            'defect_type': row['defect_type'] or 'UNKNOWN',
            'defect_count': row['defect_count'],
        })

    context = {
        'inspections': inspections_page,
        'grouped_counts': grouped_map,  # dict keyed by inspection id
    }
    return render(request, 'inspections/inspection_list.html', context)

@login_required(login_url="login")
def global_mv_maintenance_filter(request):
    lvinspections = Mvmaitenance.objects.select_related('mvinspection','county','feeder','inspectedby','aprv_by').values(
        'id', 'feeder__name','feeder_section','dtupdate','feeder__region__name','feeder__region','county', 'save_status','aprv_status','feeder__region__name','county__name','inspectedby__user_id__stid','aprv_by__user_id__stid',
        'no_poleswithoutstays','no_rottentxstructure','no_leaningtxstructure','no_sagstoretention','no_sectionstodoublejumper','no_replacefusemounts','no_bypassedhtfuses','no_spurtaplins','no_faultyabswitces','no_installabswitces','no_overhangingtrees','no_tracemaint','no_upratingconductors','no_autoclosures',
        'no_autoclosuresfaulty','no_faultyhvcable','no_structureswithouttx','no_jumpercableswithoutlugs','no_disconnsurged','no_txmissingearthing','no_ssnnumberless','no_wayleaveinfrng','comments'
    ).filter(
        aprv_status=True).order_by('-dtupdate')

    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(feeder__region=keyword)
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(county=keyword)
    if 'feeder' in request.GET:
        keyword = request.GET["feeder"]
        if keyword:
            lvinspections = lvinspections.filter(feeder__name__icontains=keyword)

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
    }
    return render(request, 'mediumv/mv_maintenance_global.html', context)

@login_required(login_url="login")
def global_mv_maintenance(request):
    today = date.today()
    lvinspections = Mvmaitenance.objects.select_related('mvinspection','county','feeder','inspectedby','aprv_by').values(
        'id', 'feeder','feeder_section','dtupdate','feeder__region','county', 'save_status','aprv_status','feeder__region__name','county__name','inspectedby__user_id__stid','aprv_by__user_id__stid',
        'no_poleswithoutstays','no_rottentxstructure','no_leaningtxstructure','no_sagstoretention','no_sectionstodoublejumper','no_replacefusemounts','no_bypassedhtfuses','no_spurtaplins','no_faultyabswitces','no_installabswitces','no_overhangingtrees','no_tracemaint','no_upratingconductors','no_autoclosures',
        'no_autoclosuresfaulty','no_faultyhvcable','no_structureswithouttx','no_jumpercableswithoutlugs','no_disconnsurged','no_txmissingearthing','no_ssnnumberless','no_wayleaveinfrng','comments'
    ).filter(
        aprv_status=True,dtupdate__date=today).order_by('-dtupdate')

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
    return render(request, 'mediumv/mv_maintenance_global.html', context)
@login_required(login_url="login")
def mediumv_delete_pole(request, pk):
    lv = Mv_poledefects.objects.get(id=pk)

    if request.method == "POST":
        with transaction.atomic():
            lv.delete()
        messages.success(request, "The Pole Inspection was deleted successfully")
        return redirect("mediumv:mv-inspections-my")
    context = {"object": lv}
    return render(request, "lv/poledelete_confirmation.html", context)
    

@login_required(login_url="login")
def global_mv_filter(request):
    lvinspections = Mvinspection.objects.select_related('county','feeder','inspectedby','aprv_by').values(
        'id', 'feeder__name','feeder__section_feeder__name','dtupdate','feeder__region__name','feeder__region','county', 'save_status','aprv_status','feeder__region__name','county__name','inspectedby__user_id__stid','aprv_by__user_id__stid',
        'no_poleswithoutstays','no_rottentxstructure','no_leaningtxstructure','no_sagstoretention','no_sectionstodoublejumper','no_replacefusemounts','no_bypassedhtfuses','no_spurtaplins','no_faultyabswitces','no_installabswitces','no_overhangingtrees','no_tracemaint','no_upratingconductors','no_autoclosures',
        'no_autoclosuresfaulty','no_faultyhvcable','no_structureswithouttx','no_jumpercableswithoutlugs','no_disconnsurged','no_txmissingearthing','no_ssnnumberless','no_wayleaveinfrng','comments'
    ).filter(
        aprv_status=True).order_by('-dtupdate')

    if 'region' in request.GET:
        keyword = request.GET["region"]
        if keyword:
            lvinspections = lvinspections.filter(feeder__region=keyword)
    if 'county' in request.GET:
        keyword = request.GET["county"]
        if keyword:
            lvinspections = lvinspections.filter(county=keyword)
    if 'feeder' in request.GET:
        keyword = request.GET["feeder"]
        if keyword:
            lvinspections = lvinspections.filter(feeder__name__icontains=keyword)

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
    }
    return render(request, 'mediumv/mv_global.html', context)
    
@login_required(login_url="login")
def global_mv(request):
    today = date.today()

    no_fields = [
        "no_poleswithoutstays", "no_rottentxstructure", "no_leaningtxstructure",
        "no_sagstoretention", "no_sectionstodoublejumper", "no_replacefusemounts",
        "no_bypassedhtfuses", "no_spurtaplins", "no_faultyabswitces", "no_installabswitces",
        "no_overhangingtrees", "no_tracemaint", "no_upratingconductors", "no_autoclosures",
        "no_autoclosuresfaulty", "no_faultyhvcable", "no_structureswithouttx",
        "no_jumpercableswithoutlugs", "no_disconnsurged", "no_txmissingearthing",
        "no_ssnnumberless", "no_wayleaveinfrng", "no_leakingpininsul", "no_leakingsuspinsul",
    ]

    agg_kwargs = {
        "total_defective_poles": Count("poledefects_mvinspection", distinct=True),
        "inspections_count": Count("id", distinct=True),
        "latest_dtadd": Max("dtadd"),
    }
    for f in no_fields:
        agg_kwargs[f"sum__{f}"] = Sum(f)

    qs = (
        Mvinspection.objects
        .values("feeder_section_id", "feeder_section__name")  # <-- these are the raw keys
        .annotate(**agg_kwargs)
        .order_by("feeder_section__name")
    )

    # Flatten keys so the template is simple and never "empty"
    display_rows = []
    for r in qs:
        row = {
            "feeder_section_id": r["feeder_section_id"],
            "feeder_section_name": r["feeder_section__name"],  # <-- flattened
            "total_defective_poles": r["total_defective_poles"] or 0,
            "inspections_count": r["inspections_count"] or 0,
            "latest_dtadd": r["latest_dtadd"],
        }
        for f in no_fields:
            row[f] = r.get(f"sum__{f}") or 0
        display_rows.append(row)


    lvinspections = Mvinspection.objects.select_related('county','feeder','inspectedby','aprv_by').values(
        'id', 'feeder','feeder_section','dtupdate','feeder__region','county', 'save_status','aprv_status','feeder__region__name','county__name','inspectedby__user_id__stid','aprv_by__user_id__stid',
        'no_poleswithoutstays','no_rottentxstructure','no_leaningtxstructure','no_sagstoretention','no_sectionstodoublejumper','no_replacefusemounts','no_bypassedhtfuses','no_spurtaplins','no_faultyabswitces','no_installabswitces','no_overhangingtrees','no_tracemaint','no_upratingconductors','no_autoclosures',
        'no_autoclosuresfaulty','no_faultyhvcable','no_structureswithouttx','no_jumpercableswithoutlugs','no_disconnsurged','no_txmissingearthing','no_ssnnumberless','no_wayleaveinfrng','comments'
    ).filter(
        aprv_status=True,dtupdate__date=today).order_by('-dtupdate')




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
        'title' : today,
        "rows": display_rows,
        "no_fields": no_fields

    }
    return render(request, 'mediumv/mv_global.html', context)

@login_required(login_url="login")
def polemaintenance_delete(request, pk):
    lv = Poledefects_maintenance.objects.get(id=pk)
    if request.method == "POST":
        lv.delete()
        messages.success(request, "The Pole maintenance was deleted successfully")
        return redirect("mediumv:poledefects-maintenance-my")
    context = {"object": lv}
    return render(request, "mediumv/delete_pole_maintenance.html", context)
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
                return redirect('mediumv:poledefects-maintenance-my')

            elif request.POST.get("draft"):
                m_form.save_status = False
                m_form.save()
                messages.success(request, 'The Pole Makintenance Inspection was saved as a draft successfully.')
                return redirect('mediumv:poledefects-maintenance-my')

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
    return render(request, 'mediumv/maintain_pole_defect.html', context)
@login_required(login_url="login")
def poledefects_maintenance_my(request):
    mypolemaintenance = Poledefects_maintenance.objects.select_related('poledefect__feeder','inspectedby').filter(inspectedby=request.user.userprofile).order_by('-dtadd')

    context ={
        'title': 'My MV Pole Defects Maintenance',
        'data' : mypolemaintenance
    }
    return render(request,'lv/network_myinspections.html', context)
@login_required(login_url="login")
def poledefects_maintenance_new(request, pk=None):
    campaign = request.user.userprofile.campaign
    if campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')
    poledefect = get_object_or_404(Mv_poledefects, id=pk)
    any_pending = Poledefects_maintenance.objects.filter(save_status=False, inspectedby=request.user.userprofile)

    if any_pending:
        messages.error(request, 'You have an inspection that is saved as draft. Submit and click on new Inspection.')
        return redirect('mediumv:poledefects-maintenance-my')

    new_maintenance = Poledefects_maintenance.objects.create(poledefect=poledefect, inspectedby=request.user.userprofile)
    if new_maintenance:
        messages.success(request, 'A Draft of the New Pole Defect Maintebnance was saved successfully. Open to continue with the inspection')
        return redirect('mediumv:poledefects-maintenance-my')

    context = {
        'data': poledefect,
        'inspection_id' : new_maintenance.id,

    }
    return render(request,'lv/lvFailure_inspect.html', context)
@login_required(login_url="login")
def poledefects_list(request, pk=None):
    poledefects_list = Mv_poledefects.objects.filter(feeder=pk, status=False)
    paginator = Paginator(poledefects_list, 20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context={
        'poledefects_list' : paged_uploads,
        'ssn' : pk,

    }
    return render(request, 'mediumv/feeder_pole_defects.html', context)
@login_required(login_url="login")
def poledefects_maintain(request,pk=None):
    new_maintenance = get_object_or_404(Mv_poledefects, id=pk)

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
def county_mvinspections_dashboard(request):
    #county = UserProfile.objects.select_related('county').get(user=request.user).county
    county = request.user.userprofile.county
    mvfaults = Mv_defaults.objects.select_related('county').filter(county=county)
    pole_defects = Mv_poledefects.objects.select_related('county').filter(county=county, status=False).order_by('defect_type')
    mvinspections = Mvinspection.objects.select_related('county').filter(aprv_status=True,county=county)




    # def lvinspection_daily_trend():
    #     df = read_frame(mvinspections)
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
    #         title_text=f'', title_x=0.5, font={'size': 12},
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
        #'pole_defects' : data,
        #'lv_def': data1,
        'title':'List Of Total Defects on the Network',
        'title2': 'List Of Pole Defects on the Network',
        'title3': 'Daily Summarized MV Inspections',
        # 'lvinspection_daily_trend' : lvinspection_daily_trend
    }
    return render(request, 'mediumv/county_mv_dashboard.html', context)
    

@login_required(login_url="login")
def mvmaintenance_print(request, pk=None):
    lvinspection = get_object_or_404(Mvmaitenance, id=pk)

    context = {"lvinspection": lvinspection}

    return render(request, "mediumv/mvmaintenance_print.html", context)
@login_required(login_url="login")
def mvmaitenance_approve(request, pk=None):
    mv_maitenance = get_object_or_404(Mvmaitenance, id=pk)

    if request.method == "POST":
        form = MvmaintenanceApproveForm(request.POST, instance=mv_maitenance)

        if form.is_valid():
            regis = form.save(commit=False)
            regis.aprv_notes = form.cleaned_data["aprv_notes"]
            regis.aprv_key = form.cleaned_data["aprv_key"]
            regis.aprv_by = request.user.userprofile
            regis.aprv_status = True
            regis.aprv_dt = date.today()
            regis.save()
            messages.success(
                request, "The MV Maintenance was Approved/Declined successfully."
            )
            return redirect("mediumv:county-mvmaintenance")
        else:
            print("invalid form")
            print(form.errors)
    else:
        form = MvmaintenanceApproveForm(instance=mv_maitenance)

    context = {"lvinspection": mv_maitenance, "form": form,}
    return render(request, "mediumv/mvmaintenance_approve.html", context)


@login_required(login_url="login")
def county_mvmaintenancepending_list(request):
    county = request.user.userprofile.county
    lv = Mvmaitenance.objects.select_related(
        "county", "feeder", "feeder_section", "inspectedby"
    ).filter(county=county, save_status=True, aprv_status=False)
    context = {
        "county": county,
        "data": lv,
        "title": "List Of Pending Approval MV Maintenance",
    }
    return render(request, "mediumv/county_mvmaintenance.html", context)


@login_required(login_url="login")
def county_mvmaintenance_list(request):
    county = request.user.userprofile.county
    lv = (
        Mvmaitenance.objects.select_related(
            "feeder", "feeder_section", "inspectedby", "county"
        )
        # .values("id", "dtupdate", "feeder__name", "feeder_section__name", "inspectedby")
        .filter(county=county, save_status=True, aprv_status=True)
    )
    context = {
        "county": county,
        "data": lv,
        "title": "List Of Approved MV Maintenance",
    }
    return render(request, "mediumv/county_mvmaintenance.html", context)


@login_required(login_url="login")
def mvmaintenance_update(request, pk=None):
    mvmaintenance = get_object_or_404(Mvmaitenance, id=pk)
    mvinspection = get_object_or_404(Mvinspection, id=mvmaintenance.mvinspection.id)

    if request.method == "POST":
        lv_form = MvmaintenanceForm(request.POST, instance=mvmaintenance)

        if lv_form.is_valid():
            poled = lv_form.save(commit=False)
            poled.mvinspection = mvmaintenance.mvinspection
            poled.feeder = mvmaintenance.mvinspection.feeder
            poled.feeder_section = mvmaintenance.feeder_section
            poled.no_poleswithoutstays = lv_form.cleaned_data["no_poleswithoutstays"]
            poled.no_rottentxstructure = lv_form.cleaned_data["no_rottentxstructure"]
            poled.no_leaningtxstructure = lv_form.cleaned_data["no_leaningtxstructure"]
            poled.no_sagstoretention = lv_form.cleaned_data["no_sagstoretention"]
            poled.no_sectionstodoublejumper = lv_form.cleaned_data[
                "no_sectionstodoublejumper"
            ]
            poled.no_replacefusemounts = lv_form.cleaned_data["no_replacefusemounts"]
            poled.no_bypassedhtfuses = lv_form.cleaned_data["no_bypassedhtfuses"]
            poled.no_spurtaplins = lv_form.cleaned_data["no_spurtaplins"]
            poled.no_faultyabswitces = lv_form.cleaned_data["no_faultyabswitces"]
            poled.no_installabswitces = lv_form.cleaned_data["no_installabswitces"]
            poled.no_overhangingtrees = lv_form.cleaned_data["no_overhangingtrees"]
            poled.no_tracemaint = lv_form.cleaned_data["no_tracemaint"]
            poled.no_upratingconductors = lv_form.cleaned_data["no_upratingconductors"]
            poled.no_autoclosures = lv_form.cleaned_data["no_autoclosures"]
            poled.no_autoclosuresfaulty = lv_form.cleaned_data["no_autoclosuresfaulty"]
            poled.no_faultyhvcable = lv_form.cleaned_data["no_faultyhvcable"]
            poled.no_structureswithouttx = lv_form.cleaned_data[
                "no_structureswithouttx"
            ]
            poled.no_jumpercableswithoutlugs = lv_form.cleaned_data[
                "no_jumpercableswithoutlugs"
            ]
            poled.no_disconnsurged = lv_form.cleaned_data["no_disconnsurged"]
            poled.no_txmissingearthing = lv_form.cleaned_data["no_txmissingearthing"]
            poled.no_ssnnumberless = lv_form.cleaned_data["no_ssnnumberless"]
            poled.no_wayleaveinfrng = lv_form.cleaned_data["no_wayleaveinfrng"]
            poled.comments = lv_form.cleaned_data["comments"]
            poled.county = request.user.userprofile.county
            poled.inspectedby = request.user.userprofile

            if request.POST.get("finalsubmission"):
                with transaction.atomic():
                    poled.save_status = True
                    poled.save()
                    lv_d = Mv_defaults.objects.create(
                        mvinspection=mvmaintenance.mvinspection,
                        county=request.user.userprofile.county,
                        region=request.user.userprofile.region,
                        no_poleswithoutstays=-poled.no_poleswithoutstays,
                        no_rottentxstructure=-poled.no_rottentxstructure,
                        no_leaningtxstructure= -poled.no_leaningtxstructure,
                        no_sagstoretention= -poled.no_sagstoretention,
                        no_sectionstodoublejumper=-poled.no_sectionstodoublejumper,
                        no_replacefusemounts= -poled.no_replacefusemounts,
                        no_bypassedhtfuses= -poled.no_bypassedhtfuses,
                        no_spurtaplins= -poled.no_spurtaplins,
                        no_faultyabswitces= -poled.no_faultyabswitces,
                        no_installabswitces= -poled.no_installabswitces,
                        no_overhangingtrees= -poled.no_overhangingtrees,
                        no_tracemaint= -poled.no_tracemaint,
                        no_upratingconductors= -poled.no_upratingconductors,
                        no_autoclosures= -poled.no_autoclosures,
                        no_autoclosuresfaulty= -poled.no_autoclosuresfaulty,
                        no_faultyhvcable= -poled.no_faultyhvcable,
                        no_structureswithouttx= -poled.no_structureswithouttx,
                        no_jumpercableswithoutlugs= -poled.no_jumpercableswithoutlugs,
                        no_disconnsurged= -poled.no_disconnsurged,
                        no_txmissingearthing= -poled.no_txmissingearthing,
                        no_ssnnumberless= -poled.no_ssnnumberless,
                        no_wayleaveinfrng= -poled.no_wayleaveinfrng,
                        inspectedby=request.user.userprofile,
                        feeder=mvmaintenance.mvinspection.feeder
                    )
                    lv_d.save()
                messages.success(
                    request, "The MV Maintenance was submitted successfully."
                )
                return redirect("mediumv:mvmaintenance-my")

            if request.POST.get("draft"):
                poled.save_status = False
                poled.save()
                messages.success(
                    request, "The MV Makintenance was submitted successfully."
                )
                return redirect("mediumv:mvmaintenance-my")

        else:
            print("invalid form")
            print(lv_form.errors)
    else:
        lv_form = MvmaintenanceForm(instance=mvmaintenance)

    context = {
        "lv": mvmaintenance,
        "lv_form": lv_form,
        'mvinspection' : mvinspection
    }

    return render(request, "mediumv/mvmaintenance.html", context)


@login_required(login_url="login")
def mvmaintenance_delete(request, pk):
    lv = Mvmaitenance.objects.get(id=pk)
    if request.method == "POST":
        lv.delete()
        messages.success(request, "The MV  Maintenance was deleted successfully")
        return redirect("mediumv:mvmaintenance-my")
    context = {"object": lv}
    return render(request, "mediumv/delete_mvmaintenance_confirm.html", context)


@login_required(login_url="login")
def mvmaintenance_my(request):
    mvmaintenance = Mvmaitenance.objects.filter(
        inspectedby=request.user.userprofile
    ).order_by("-dtadd")

    paginator = Paginator(mvmaintenance, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {"data": paged_uploads, "title": "My MV Maintenance Inspections"}
    return render(request, "lv/network_myinspections.html", context)


@login_required(login_url="login")
def mvmaintenance_new(request, pk=None):
    inspection = get_object_or_404(Mvinspection, id=pk)
    any_pending = Mvmaitenance.objects.select_related("inspectedby").filter(
        save_status=False, inspectedby=request.user.userprofile
    )

    if any_pending:
        messages.error(
            request,
            "You have an inspection that is saved as draft. Submit and click on new Inspection.",
        )
        return redirect("mediumv:mvmaintenance-my")
    new_inspection = Mvmaitenance.objects.create(
        mvinspection=inspection,
        feeder_section=inspection.feeder_section,
        inspectedby=request.user.userprofile,
    )
    if new_inspection:
        messages.success(
            request,
            "A Draft of the New Inspection was saved successfully. Open to continue with the inspection",
        )
        return redirect("mediumv:mv-inspections-my")

    context = {
        "inspection_id": new_inspection.id,
    }
    return render(request, "lv/network_myinspections.html", context)


@login_required(login_url="login")
def inspected_sections(request, pk=None):
    sections = Mvinspection.objects.filter(feeder_section=pk)
    feeder_sections = Mvinspection.objects.filter(
        feeder=sections[0].feeder, aprv_status=True
    ).distinct("feeder_section")

    context = {
        "data": sections,
        "sections": feeder_sections,
    }
    return render(request, "mediumv/mvinspected_sections.html", context)


@login_required(login_url="login")
def county_analysis(request):
    county = UserProfile.objects.select_related("county").get(user=request.user).county
    DATE_RANGE = datetime.today() - timedelta(days=180)
    poledefects_list = Mv_poledefects.objects.filter(
        county=county, status=False, dtadd__gt=DATE_RANGE
    ).values("dtadd", "id", "defect_type")
    mvinspections = Mvinspection.objects.filter(
        county=county, aprv_status=True, dtadd__gt=DATE_RANGE
    ).values("id", "dtadd")
    mvmaintenance = Mvmaitenance.objects.filter(
        county=county, aprv_status=True, dtadd__gt=DATE_RANGE
    ).values("id", "dtadd")

    # def PoleDefects_analysis():
    #     df = read_frame(poledefects_list)
    #     df = df.groupby(by="defect_type", as_index=False, sort=False)["id"].count()
    #     names = df.defect_type
    #     values = df.id
    #     df = px.pie(
    #         df,
    #         values=values,
    #         names=names,
    #         title=f"Total Defects-{poledefects_list.count()}",
    #     )
    #     df.update_traces(textposition="inside", textinfo="percent+label")
    #     df.update_layout(
    #         margin=dict(l=20, r=20, b=20),
    #     ),
    #     df = json.dumps(df, cls=plotly.utils.PlotlyJSONEncoder)
    #     return df

    # def mvinspection_daily_trend():
    #     df = read_frame(mvinspections)
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
    #         title_text=f"MV Inspections- {mvinspections.count()}",
    #         title_x=0.5,
    #         font={"size": 12},
    #         # title=("Target vs Achievement"),
    #         xaxis_tickfont_size=14,
    #         yaxis_range=[0, 6],
    #         yaxis=dict(
    #             title="No Of Inspections",
    #             titlefont_size=16,
    #             tickfont_size=14,
    #             range=[0, 5],
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

    # def mvmaintenance_daily_trend():
    #     df = read_frame(mvmaintenance)
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
    #         title_text=f"Lv Maintenance Inspections- {mvmaintenance.count()}",
    #         title_x=0.5,
    #         font={"size": 12},
    #         # title=("Target vs Achievement"),
    #         xaxis_tickfont_size=14,
    #         yaxis_range=[0, 6],
    #         yaxis=dict(
    #             title="No Of Inspections",
    #             titlefont_size=16,
    #             tickfont_size=14,
    #             range=[0, 5],
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

    context = {
        # "poledefects": PoleDefects_analysis,
        "county": county,
        # "mvinspections": mvinspection_daily_trend,
        # 'mvmaintenance': mvmaintenance_daily_trend,
    }

    return render(request, "mediumv/county_analysis.html", context)


@login_required(login_url="login")
def mvinspection_delete(request, pk):
    lv = Mvinspection.objects.get(id=pk)
    if request.method == "POST":
        lv.delete()
        messages.success(request, "The MV  Inspection was deleted successfully")
        return redirect("mediumv:mv-inspections-my")
    context = {"object": lv}
    return render(request, "mediumv/delete_mvinspection_confirm.html", context)


@login_required(login_url="login")
def mvinspections_approved(request, pk=None):
    feeder_sections = Feeder_sections.objects.filter(feeder_id=pk)
    lvinspection = Mvinspection.objects.filter(feeder_id=pk, aprv_status=True)
    sections = Mvinspection.objects.filter(feeder_id=pk, aprv_status=True).distinct(
        "feeder_section"
    )

    context = {
        "lvinspection": lvinspection,
        "sections": sections,
    }

    return render(request, "mediumv/mvinspected_sections.html", context)


@login_required(login_url="login")
def mvinspection_print(request, pk=None):
    lvinspection = get_object_or_404(Mvinspection, id=pk)
    poledefects = Mv_poledefects.objects.filter(mvinspection=lvinspection)

    context = {"lvinspection": lvinspection, "poledefects": poledefects}

    return render(request, "mediumv/mvinspection_print.html", context)


@login_required(login_url="login")
def mvinspection_approve(request, pk=None):
    mv_inspection = get_object_or_404(Mvinspection, id=pk,save_status=True)
    poledefects = Mv_poledefects.objects.filter(mvinspection=mv_inspection)

    if request.method == "POST":
        form = MvinspectionApproveForm(request.POST, instance=mv_inspection)

        if form.is_valid():
            regis = form.save(commit=False)
            regis.aprv_notes = form.cleaned_data["aprv_notes"]
            regis.aprv_key = form.cleaned_data["aprv_key"]
            regis.aprv_by = request.user.userprofile
            regis.aprv_status = True
            regis.aprv_dt = date.today()
            regis.save()
            messages.success(
                request, "The MV Inspection was Approved/Declined successfully."
            )
            return redirect("mediumv:county-mvinspections")
        else:
            print("invalid form")
            print(form.errors)
    else:
        form = MvinspectionApproveForm(instance=mv_inspection)

    context = {"lvinspection": mv_inspection, "form": form,'poledefects' : poledefects,}
    return render(request, "mediumv/mvinspection_approve.html", context)


@login_required(login_url="login")
def county_mvpending_list(request):
    county = request.user.userprofile.county
    lv = Mvinspection.objects.select_related(
        "county", "feeder", "feeder_section", "inspectedby"
    ).filter(county=county, save_status=True, aprv_status=False)
    context = {
        "county": county,
        "data": lv,
        "title": "List Of Pending Approval MV Inspections",
    }
    return render(request, "mediumv/county_mvinspections.html", context)


@login_required(login_url="login")
def county_mvinspections_list(request):
    county = request.user.userprofile.county
    lv = (
        Mvinspection.objects.select_related("feeder", "feeder_section", "inspectedby")
        # .values("id", "dtupdate", "feeder__name", "feeder_section__name", "inspectedby__userprofile__user",'aprv_status')
        .filter(county=county, save_status=True, aprv_status=True)
    )

    context = {
        "county": county,
        "data": lv,
        "title": "List Of Approved MV Inspections",
    }
    return render(request, "mediumv/county_mvinspections.html", context)


@login_required(login_url="login")
def mvpoledefects_new(request):
    new_inspection = (
        Mvinspection.objects.filter(inspectedby=request.user.userprofile)
        .order_by("id")
        .last()
    )

    lv_form = MvinspectionForm()

    if request.method == "POST":
        pole_form = MvPoledefectsForm(request.POST)

        if pole_form.is_valid():
            poled = pole_form.save(commit=False)
            poled.defect_type = pole_form.cleaned_data["defect_type"]
            poled.polefitting_type = pole_form.cleaned_data["polefitting_type"]
            poled.x = pole_form.cleaned_data["x"]
            poled.y = pole_form.cleaned_data["y"]
            poled.location = pole_form.cleaned_data["location"]
            poled.county = request.user.userprofile.county
            poled.mvinspection = new_inspection
            poled.inspectedby = request.user.userprofile
            poled.feeder = new_inspection.feeder
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
            messages.success(request, "The Pole Defect was saved successfully.")
            return redirect("mediumv:mvinspection-update", new_inspection.id)
        else:
            print("invalid form")
            print(pole_form.errors)
            # print(Lvinsp_form.errors)
    else:
        pole_form = MvPoledefectsForm()
        # lv_form = LvinspectionForm(instance=new_inspection)

    context = {
        "lvinspections": new_inspection,
        "pole_form": pole_form,
        "lv_form": lv_form,
    }
    return render(request, "lv/poledefect_capture.html", context)


@login_required(login_url="login")
def feeder_dashboard(request, pk=None):
    feeder = (
        Feeder.objects.select_related("county")
        .values("id", "name", "county__name")
        .get(id=pk)
    )
    sections = Feeder_sections.objects.filter(feeder_id=pk)

    context = {
        "feeder": feeder,
        "feeder_sctn": sections,
    }

    return render(request, "mediumv/feeder_dashboard.html", context)


@login_required(login_url="login")
def mvinspection_update(request, pk=None):
    mvinspection = get_object_or_404(Mvinspection, id=pk)
    poledefects = Mv_poledefects.objects.filter(mvinspection=mvinspection)
    sections = Feeder_sections.objects.all()
    pole_form = MvPoledefectsForm()


    if request.method == "POST":
        lv_form = MvinspectionForm(
            request.POST, instance=mvinspection, request=mvinspection.feeder
        )

        if lv_form.is_valid():
            poled = lv_form.save(commit=False)
            poled.feeder = mvinspection.feeder
            poled.feeder_section = lv_form.cleaned_data["feeder_section"]
            poled.no_poleswithoutstays = lv_form.cleaned_data["no_poleswithoutstays"]
            poled.no_rottentxstructure = lv_form.cleaned_data["no_rottentxstructure"]
            poled.no_leaningtxstructure = lv_form.cleaned_data["no_leaningtxstructure"]
            poled.no_sagstoretention = lv_form.cleaned_data["no_sagstoretention"]
            poled.no_sectionstodoublejumper = lv_form.cleaned_data[
                "no_sectionstodoublejumper"
            ]
            poled.no_replacefusemounts = lv_form.cleaned_data["no_replacefusemounts"]
            poled.no_bypassedhtfuses = lv_form.cleaned_data["no_bypassedhtfuses"]
            poled.no_spurtaplins = lv_form.cleaned_data["no_spurtaplins"]
            poled.no_faultyabswitces = lv_form.cleaned_data["no_faultyabswitces"]
            poled.no_installabswitces = lv_form.cleaned_data["no_installabswitces"]
            poled.no_overhangingtrees = lv_form.cleaned_data["no_overhangingtrees"]
            poled.no_tracemaint = lv_form.cleaned_data["no_tracemaint"]
            poled.no_upratingconductors = lv_form.cleaned_data["no_upratingconductors"]
            poled.no_autoclosures = lv_form.cleaned_data["no_autoclosures"]
            poled.no_autoclosuresfaulty = lv_form.cleaned_data["no_autoclosuresfaulty"]
            poled.no_faultyhvcable = lv_form.cleaned_data["no_faultyhvcable"]
            poled.no_leakingpininsul = lv_form.cleaned_data["no_leakingpininsul"]
            poled.no_leakingsuspinsul = lv_form.cleaned_data["no_leakingsuspinsul"]
            poled.no_structureswithouttx = lv_form.cleaned_data[
                "no_structureswithouttx"
            ]
            poled.no_jumpercableswithoutlugs = lv_form.cleaned_data[
                "no_jumpercableswithoutlugs"
            ]
            poled.no_disconnsurged = lv_form.cleaned_data["no_disconnsurged"]
            poled.no_txmissingearthing = lv_form.cleaned_data["no_txmissingearthing"]
            poled.no_ssnnumberless = lv_form.cleaned_data["no_ssnnumberless"]
            poled.no_wayleaveinfrng = lv_form.cleaned_data["no_wayleaveinfrng"]
            poled.comments = lv_form.cleaned_data["comments"]
            poled.county = request.user.userprofile.county
            poled.inspectedby = request.user.userprofile

            if request.POST.get("finalsubmission"):
                with transaction.atomic():
                    lv_d = Mv_defaults.objects.create(
                        mvinspection=mvinspection,
                        county=request.user.userprofile.county,
                        region=request.user.userprofile.region,
                        no_poleswithoutstays=poled.no_poleswithoutstays,
                        no_rottentxstructure=poled.no_rottentxstructure,
                        no_leaningtxstructure=poled.no_leaningtxstructure,
                        no_sagstoretention=poled.no_sagstoretention,
                        no_sectionstodoublejumper=poled.no_sectionstodoublejumper,
                        no_replacefusemounts=poled.no_replacefusemounts,
                        no_bypassedhtfuses=poled.no_bypassedhtfuses,
                        no_spurtaplins=poled.no_spurtaplins,
                        no_faultyabswitces=poled.no_faultyabswitces,
                        no_installabswitces=poled.no_installabswitces,
                        no_overhangingtrees=poled.no_overhangingtrees,
                        no_tracemaint=poled.no_tracemaint,
                        no_upratingconductors=poled.no_upratingconductors,
                        no_autoclosures=poled.no_autoclosures,
                        no_autoclosuresfaulty=poled.no_autoclosuresfaulty,
                        no_faultyhvcable=poled.no_faultyhvcable,
                        no_structureswithouttx=poled.no_structureswithouttx,
                        no_jumpercableswithoutlugs=poled.no_jumpercableswithoutlugs,
                        no_disconnsurged=poled.no_disconnsurged,
                        no_txmissingearthing=poled.no_txmissingearthing,
                        no_ssnnumberless=poled.no_ssnnumberless,
                        no_wayleaveinfrng=poled.no_wayleaveinfrng,
                        inspectedby=request.user.userprofile,
                        feeder=mvinspection.feeder
                    )
                    lv_d.save()
                    poled.save_status = True
                    poled.save()
                messages.success(
                    request, "The MV Inspection was submitted successfully."
                )
                return redirect("mediumv:mv-inspections-my")

            if request.POST.get("draft"):
                poled.save_status = False
                poled.save()
                messages.success(
                    request, "The MV Inspection was submitted successfully."
                )
                return redirect("mediumv:mv-inspections-my")

        else:
            print("invalid form")
            print(lv_form.errors)
    else:
        lv_form = MvinspectionForm(instance=mvinspection, request=mvinspection.feeder)

    context = {
        "lv": mvinspection.id,
        "lv_form": lv_form,
        "poledefects": poledefects,
        "pole_form": pole_form,
        "sections": sections,
    }

    return render(request, "mediumv/mvinspection_new.html", context)


@login_required(login_url="login")
def mvinspection_new(request, pk=None):
    feeder = get_object_or_404(Feeder, id=pk)
    any_pending = Mvinspection.objects.select_related("inspectedby").filter(
        save_status=False, inspectedby=request.user.userprofile
    )

    if any_pending:
        messages.error(
            request,
            "You have an inspection that is saved as draft. Submit and click on new Inspection.",
        )
        return redirect("mediumv:mv-inspections-my")
    new_inspection = Mvinspection.objects.create(
        feeder=feeder, inspectedby=request.user.userprofile
    )
    if new_inspection:
        messages.success(
            request,
            "A Draft of the New Inspection was saved successfully. Open to continue with the inspection",
        )
        return redirect("mediumv:mv-inspections-my")

    context = {
        "inspection_id": new_inspection.id,
    }
    return render(request, "lv/ssn_dashboard.html", context)


@login_required(login_url="login")
def my_mvinspections(request):
    substations = (
        Mvinspection.objects.select_related("feeder_section", "inspectedby")
        .filter(inspectedby=request.user.userprofile)
        .order_by("-dtadd")
    )

    paginator = Paginator(substations, 20)
    page = request.GET.get("page")
    paged_uploads = paginator.get_page(page)

    context = {"title": "My MV Inspections", "data": paged_uploads}
    return render(request, "lv/network_myinspections.html", context)


@login_required(login_url="login")
def feeder_search(request):
    if request.user.is_authenticated:
        user = request.user

    return render(
        request,
        "mediumv/feeder_search.html",
    )


@login_required(login_url="login")
def feeder_search_results(request):
    # sb_list = Substation.objects.filter(county=request.user.userprofile.county)
    feeder_list = Feeder.objects.select_related("county").values(
        "id", "name", "county__name"
    )

    # feeder_list = Feeder_sections.objects.select_related('feeder').values('name','id','sec_from','sec_to','feeder__name')
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            feeder_list = feeder_list.filter(name__icontains=keyword)

    context = {
        "data": feeder_list,
    }
    return render(request, "mediumv/feeder_search.html", context)
