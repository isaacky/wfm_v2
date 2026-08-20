from turtledemo.minimal_hanoi import Tower

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from user.models import UserProfile
from main.models import Region,County
from .models import *
from .forms import *
import logging

from datetime import timedelta, time, date,datetime

logger = logging.getLogger(__name__)

@login_required(login_url="login")
def tower_approve(request, pk=None):
    inspection = (
        TrnsGroundInspection.objects
        .select_related(
            "grnd_lin_insul",
            "grnd_line_cond",
            "grnd_line_opgw",
            "grnd_line_found",
            "inspectedby"
        )
        .get(pk=pk)
    )



    context ={
        'lvinspection' : inspection,

    }

    return render(request, 'transmission/tower/tower_approve_inspection.html', context)

@login_required(login_url="login")
def tower_dashboard(request):
    today = date.today()
    # towers = TrnsGroundInspection.objects.all()
    towers = (
        TrnsGroundInspection.objects
        .select_related(
            "grnd_lin_insul",
            "grnd_line_cond",
            "grnd_line_opgw",
            "grnd_line_found",
            "inspectedby",
        ).values('id','line_name__depot__name','line_name__name','towerno','span_lng','voltage','dtupdate','aprv_status')
    )
    context = {'data':towers}

    return render(request,'transmission/tower/tower_dashboard.html',context)

@login_required(login_url="login")
def transmission_dashboard(request):

    return render(request,'transmission/trans_dashboard.html')

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
def towerinspection_update_finalize(request, pk):
    user_profile = request.user.userprofile

    # Access control
    if user_profile.campaign != "network_technician":
        messages.error(request, "Access Denied.")
        return redirect("main:my-dashboard")

    # Fetch inspection with related objects
    inspection = (
        TrnsGroundInspection.objects
        .select_related(
            "grnd_lin_insul",
            "grnd_line_cond",
            "grnd_line_opgw",
            "grnd_line_found",
            "inspectedby"
        )
        .get(pk=pk)
    )

    # Phase validation rules
    phase_checks = [
        (inspection.save_status, "The 1st phase of the inspection is not yet completed."),
        (inspection.grnd_lin_insul.save_status, "The 2nd phase of the inspection is not yet completed."),
        (inspection.grnd_line_cond.save_status, "The 3rd phase of the inspection is not yet completed."),
        (inspection.grnd_line_opgw.save_status, "The 4th phase of the inspection is not yet completed."),
        (inspection.grnd_line_found.save_status, "The 5th phase of the inspection is not yet completed."),
    ]

    # Loop through phases and stop at first failure
    for status, error_msg in phase_checks:
        if not status:
            messages.error(request, error_msg)
            return redirect("transmission:trans-dashboard-my")

    try:
        inspection.final_status = True
        inspection.save()
        messages.success(request, "Tower Inspection sent for approval.")
        return redirect("transmission:trans-dashboard-my")

    except Exception as e:
        print("Save error:", e)
        messages.error(request, "Failed to finalize the inspection. Please try again.")
        return redirect("transmission:trans-dashboard-my")


@login_required(login_url="login")
def towerinspection_update_foundation(request, pk):
    user_profile = request.user.userprofile

    if user_profile.campaign != "network_technician":
        messages.error(request, "Access Denied.")
        return redirect("main:my-dashboard")

    # Load inspection
    inspection = get_object_or_404(TowerFoundations, line_id=pk)

    if request.method == "POST":
        m_form1 = TowerFoundationsForm(request.POST, instance=inspection)

        if m_form1.is_valid():
            obj = m_form1.save(commit=False)
            obj.line = inspection.line
            obj.save_status = True
            obj.save()

            messages.success(request, "Tower Foundation Inspection updated successfully.")
            return redirect("transmission:trans-dashboard-my")

        else:
            messages.error(request, "Invalid form submission. Please correct the errors.")
            print(m_form1.errors)

    else:
        m_form1 = TowerFoundationsForm(instance=inspection)

    context = {
        "insp_form": m_form1,
        "inspection": inspection.id,
    }

    return render(request, "transmission/transmission_dashboard.html", context)

@login_required(login_url="login")
def towerinspection_update_earth(request, pk):
    user_profile = request.user.userprofile

    if user_profile.campaign != "network_technician":
        messages.error(request, "Access Denied.")
        return redirect("main:my-dashboard")

    # Load inspection
    inspection = get_object_or_404(EarthOPGW, line_id=pk)

    if request.method == "POST":
        m_form1 = EarthOPGWForm(request.POST, instance=inspection)

        if m_form1.is_valid():
            obj = m_form1.save(commit=False)
            obj.line = inspection.line
            obj.save_status = True
            obj.save()

            messages.success(request, "Insulation Inspection updated successfully.")
            return redirect("transmission:trans-dashboard-my")

        else:
            messages.error(request, "Invalid form submission. Please correct the errors.")
            print(m_form1.errors)

    else:
        m_form1 = EarthOPGWForm(instance=inspection)

    context = {
        "insp_form": m_form1,
        "inspection": inspection.id,
    }

    return render(request, "transmission/transmission_dashboard.html", context)
@login_required(login_url="login")
def towerinspection_update_conductors(request, pk):
    user_profile = request.user.userprofile

    if user_profile.campaign != "network_technician":
        messages.error(request, "Access Denied.")
        return redirect("main:my-dashboard")

    # Load inspection
    inspection = get_object_or_404(ConductorInspection, line_id=pk)

    if request.method == "POST":
        m_form1 = ConductorInspectionForm(request.POST, instance=inspection)

        if m_form1.is_valid():
            obj = m_form1.save(commit=False)
            obj.line = inspection.line
            obj.save_status = True
            obj.save()

            messages.success(request, "Insulation Inspection updated successfully.")
            return redirect("transmission:trans-dashboard-my")

        else:
            messages.error(request, "Invalid form submission. Please correct the errors.")
            print(m_form1.errors)

    else:
        m_form1 = ConductorInspectionForm(instance=inspection)

    context = {
        "insp_form": m_form1,
        "inspection": inspection.id,
    }

    return render(request, "transmission/transmission_dashboard.html", context)

@login_required(login_url="login")
def towerinspection_update_insulators(request, pk):
    user_profile = request.user.userprofile

    if user_profile.campaign != "network_technician":
        messages.error(request, "Access Denied.")
        return redirect("main:my-dashboard")

    # Load inspection
    inspection = get_object_or_404(InsulatorInspection, line_id=pk)

    if request.method == "POST":
        m_form1 = InsulatorInspectionForm(request.POST, instance=inspection)

        if m_form1.is_valid():
            obj = m_form1.save(commit=False)
            obj.line = inspection.line
            obj.save_status = True
            obj.save()

            messages.success(request, "Insulation Inspection updated successfully.")
            return redirect("transmission:trans-dashboard-my")

        else:
            messages.error(request, "Invalid form submission. Please correct the errors.")
            print(m_form1.errors)

    else:
        m_form1 = InsulatorInspectionForm(instance=inspection)

    context = {
        "insp_form": m_form1,
        "inspection": inspection.id,
    }

    return render(request, "transmission/transmission_dashboard.html", context)

@login_required(login_url="login")
def towerinspection_update_location(request, pk):
    user_profile = request.user.userprofile

    if user_profile.campaign != "network_technician":
        messages.error(request, "Access Denied.")
        return redirect("main:my-dashboard")

    # Load inspection
    inspection = get_object_or_404(TrnsGroundInspection, pk=pk)

    if request.method == "POST":
        m_form1 = TrnsGroundInspectionForm(request.POST, instance=inspection)

        if m_form1.is_valid():
            obj = m_form1.save(commit=False)
            obj.save_status = True
            obj.save()

            messages.success(request, "Inspection updated successfully.")
            return redirect("transmission:trans-dashboard-my")

        else:
            messages.error(request, "Invalid form submission. Please correct the errors.")
            print(m_form1.errors)

    else:
        m_form1 = TrnsGroundInspectionForm(instance=inspection)

    context = {
        "insp_form": m_form1,
        "inspection": inspection.id,
    }

    return render(request, "transmission/transmission_dashboard.html", context)


@login_required(login_url="login")
def txline_inspect(request, pk):
    img = get_object_or_404(TransmissionLines, id=pk)
    profile = request.user.userprofile
    if profile.campaign != "network_technician":
        messages.error(request, "Access Denied.")
        return redirect("main:my-dashboard")
    any_pending = TrnsGroundInspection.objects.filter(final_status=False, inspectedby=profile)

    if any_pending:
        messages.error(request, 'You have an inspection that is saved as draft. Submit and click on new Inspection.')
        return redirect('transmission:trans-dashboard-my')
    try:
        with transaction.atomic():
            new_inspection = TrnsGroundInspection.objects.create(
                line_name=img,
                inspectedby=profile,
            )
            InsulatorInspection.objects.create(line=new_inspection)
            ConductorInspection.objects.create(line=new_inspection)
            EarthOPGW.objects.create(line=new_inspection)
            TowerFoundations.objects.create(line=new_inspection)
        messages.success(request, "Draft inspection created successfully.")
        return redirect("transmission:trans-dashboard-my")

    except Exception as e:
        messages.error(request, f"Error creating inspection: {str(e)}")
        return redirect("transmission:txlines-search")

@login_required(login_url="login")
def search_by_txline(request):
    keyword = request.GET.get("keyword", "")

    sb_list = TransmissionLines.objects.values(
        "name", "id","depot__name"
    )

    if keyword:
        sb_list = sb_list.filter(name__icontains=keyword)[:10]  # limit suggestions

    context = {"data": sb_list}

    # If HTMX request → return only the suggestion list
    if request.headers.get("HX-Request"):
        return render(request, "transmission/tx_autocomplete.html", context)

    # Normal page load
    return render(request, "transmission/tx_lines_search.html", context)

@login_required(login_url="login")
def txlines_search(request):
    if request.user.is_authenticated:
        user = request.user


    return render(request, 'transmission/tx_lines_search.html',)
@login_required(login_url="login")
def tower_location_update(request, pk):
    img = get_object_or_404(TrnsGroundInspection, id=pk)


    if request.method == "POST":
        m_form = TrnsGroundInspectionForm(request.POST, request.FILES, instance=img)
        if m_form.is_valid():
            zerov = m_form.save(commit=False)

            profile = request.user.userprofile
            zerov.inspectedby = profile
            zerov.status = True

            zerov.save()
            messages.success(
                request, "Your Analysis Has been successfully saved."
            )
            return redirect("transmission:tower-update",pk=pk)
        else:
            print('invalid form')
            print(m_form.errors)
        messages.error(request, "Invalid form submission. Please correct the errors.")

    else:
        m_form = TrnsGroundInspectionForm(instance=img)

    return render(request, "transmission/transmission_dashboard.html", {"form": m_form})

@login_required(login_url="login")
def towerinspection_update(request, pk):
    user_profile = request.user.userprofile

    if user_profile.campaign != "network_technician":
        messages.error(request, "Access Denied.")
        return redirect("main:my-dashboard")

    # Load only required fields + all OneToOne in ONE query
    inspection = get_object_or_404(
        TrnsGroundInspection.objects.select_related(
            "grnd_lin_insul",
            "grnd_line_cond",
            "grnd_line_opgw",
            "grnd_line_found",
            "inspectedby"
        ),
        pk=pk
    )


    if not inspection:
        messages.error(request, "Inspection not found.")
        return redirect("transmission:trans-dashboard-my")

    # Related objects (already fetched, no extra queries)
    insulator = inspection.grnd_lin_insul
    conductor = inspection.grnd_line_cond
    earth = inspection.grnd_line_opgw
    foundation = inspection.grnd_line_found

    # Build forms once
    if request.method == "POST":
        forms = [
            TrnsGroundInspectionForm(request.POST, instance=inspection),
            InsulatorInspectionForm(request.POST, instance=insulator),
            ConductorInspectionForm(request.POST, instance=conductor),
            EarthOPGWForm(request.POST, instance=earth),
            TowerFoundationsForm(request.POST, instance=foundation),
        ]

        if all(form.is_valid() for form in forms):
            try:
                with transaction.atomic():
                    for form in forms:
                        form.save()

                messages.success(request, "Inspection updated successfully.")
                return redirect("transmission:trans-dashboard-my")

            except Exception as e:
                messages.error(request, f"Error updating inspection: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        forms = [
            TrnsGroundInspectionForm(instance=inspection),
            InsulatorInspectionForm(instance=insulator),
            ConductorInspectionForm(instance=conductor),
            EarthOPGWForm(instance=earth),
            TowerFoundationsForm(instance=foundation),
        ]

    context = {
        "insp_form": forms[0],
        "ins_form": forms[1],
        "cond_form": forms[2],
        "earth_form": forms[3],
        "found_form": forms[4],
        "inspection": inspection.id,
    }

    return render(request, "transmission/tower/tower_inspection_update.html", context)

# @login_required(login_url="login")
# def towerinspection_update(request, pk):
#     campaign = request.user.userprofile
#
#     if campaign.campaign != "network_technician":
#         messages.error(request, "Access Denied.")
#         return redirect("main:my-dashboard")
#
#     inspection = (
#         TrnsGroundInspection.objects
#         .select_related(
#             "grnd_lin_insul",
#             "grnd_line_cond",
#             "grnd_line_opgw",
#             "grnd_line_found",
#         )
#         .filter(id=pk, inspectedby=campaign)
#         .first()
#     )
#     if not inspection:
#         messages.error(request, "Inspection not found.")
#         return redirect("transmission:trans-dashboard-my")
#
#     insulator = inspection.grnd_lin_insul
#     conductor = inspection.grnd_line_cond
#     earth = inspection.grnd_line_opgw
#     foundation = inspection.grnd_line_found
#
#     def build_forms(post=None):
#         return (
#             TrnsGroundInspectionForm(post, instance=inspection),
#             InsulatorInspectionForm(post, instance=insulator),
#             ConductorInspectionForm(post, instance=conductor),
#             EarthOPGWForm(post, instance=earth),
#             TowerFoundationsForm(post, instance=foundation),
#         )
#
#     if request.method == "POST":
#         insp_form, ins_form, cond_form, earth_form, found_form = build_forms(request.POST)
#
#         all_valid = (
#                 insp_form.is_valid()
#                 and ins_form.is_valid()
#                 and cond_form.is_valid()
#                 and earth_form.is_valid()
#                 and found_form.is_valid()
#         )
#         if all_valid:
#             try:
#                 with transaction.atomic():
#                     insp_form.save()
#                     ins_form.save()
#                     cond_form.save()
#                     earth_form.save()
#                     found_form.save()
#                 messages.success(request, "Inspection updated successfully.")
#                 return redirect("transmission:trans-dashboard-my")
#             except Exception as e:
#                 messages.error(request, f"Error updating inspection: {str(e)}")
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         insp_form, ins_form, cond_form, earth_form, found_form = build_forms()
#     context = {
#         "insp_form": insp_form,
#         "ins_form": ins_form,
#         "cond_form": cond_form,
#         "earth_form": earth_form,
#         "found_form": found_form,
#         "inspection": inspection,
#     }
#
#
#     return render(request, "transmission/tower/tower_inspection_update.html", context)


@login_required(login_url="login")
def tower_delete(request, pk):
    tower = get_object_or_404(TrnsGroundInspection, id=pk)
    try:
        tower.delete()  # Profile deleted automatically via CASCADE
        messages.success(request, "Tower and related records deleted successfully.")
        return redirect('transmission:trans-dashboard-my')
    except Exception as e:
        logger.error(f"Failed to delete tower inspection {id}: {e}")
        messages.error(request, "An error occurred while deleting the inspection.")
        return redirect('transmission:trans-dashboard-my')


@login_required(login_url="login")
def trans_dashboard_my(request):
    mytrans = TrnsGroundInspection.objects.select_related('inspectedby').order_by('-dtupdate').values(
        'id', 'dtupdate', 'save_status','final_status', 'aprv_status','towerno').filter(
        inspectedby=request.user.userprofile)
    paginator = Paginator(mytrans, 100)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)

    context = {
        'title': 'My Tower Inspections',
        'data': paged_uploads
    }
    return render(request,'transmission/transmission_dashboard.html', context)


@login_required(login_url="login")
def towerinspection_new(request):
    campaign = request.user.userprofile
    any_pending = TrnsGroundInspection.objects.filter(save_status=False, inspectedby=campaign)

    if campaign.campaign != 'network_technician':
        messages.error(request, 'Access Denied.')
        return redirect('main:my-dashboard')

    if any_pending:
        messages.error(request, 'You have an inspection that is saved as draft. Submit and click on new Inspection.')
        return redirect('transmission:towerinspection-new')

    try:
        with transaction.atomic():
            new_inspection = TrnsGroundInspection.objects.create(
                inspectedby=campaign,

            )
            InsulatorInspection.objects.create(line=new_inspection)
            ConductorInspection.objects.create(line=new_inspection)
            EarthOPGW.objects.create(line=new_inspection)
            TowerFoundations.objects.create(line=new_inspection)
        messages.success(request, "Draft inspection created successfully.")
        return redirect("transmission:trans-dashboard-my")

    except Exception as e:
        messages.error(request, f"Error creating inspection: {str(e)}")
        return redirect("transmission:trans-dashboard-my")
