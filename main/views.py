from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import csv
from datetime import datetime
from .models import  Meters,Analytics,Feeder_sections, Feeder
from user.models import Account,UserProfile
from .forms import MeterForm, ResolveForm, CountyForm, AsignForm,Feeder_sectionsForm
from main.models import County
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import F, Q
from django.db.models import Count


# Create your views here.

@login_required(login_url="login")
def feeder_section_edit(request, pk=None):
    ssn = get_object_or_404(Feeder_sections, id=pk)

    campaign = request.user.userprofile.campaign

    if campaign == "network_supervisors":
        if request.method == "POST":
            m_form = Feeder_sectionsForm(request.POST, request.FILES,instance=ssn,request=request)

            if m_form.is_valid():
                section = m_form.save(commit=False)
                section.logged_by = request.user.userprofile
                section.feeder = m_form.cleaned_data["feeder"]
                section.name = m_form.cleaned_data["name"]
                section.save()
                messages.success(
                    request, "The Feeder Section Has been successfully saved."
                )
                return redirect("main:feeder-sections-list")
            else:
                print("invalid form")
                print(m_form.errors)

        else:
            # user_form = UserForm(instance=request.user)

            m_form = Feeder_sectionsForm(request=request,instance=ssn)
        context = {
            "form": m_form,
            'feeders' : Feeder.objects.select_related('county').filter(county=request.user.userprofile.county)
        }
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

    return render(request, "main/feeder_section_new.html", context)
    

@login_required(login_url="login")
def mydashboard(request):
    meters = Meters.objects.filter(user=request.user)


    sectorname = request.user.userprofile.county
    context = {
        'meters' : meters,
        'sectorname' : sectorname,
        'nbar' : 'home',
    }
    return  render(request, 'main/mydashboard.html', context)
    
@login_required(login_url="login")
def feeder_sections_list(request):
    county = request.user.userprofile.county
    feeder_sections = Feeder_sections.objects.select_related('feeder').filter(feeder__county=county)#.values('id','dtadd','substation')
    #paginator = Paginator(feeder_sections, 20)
    #page = request.GET.get('page')
    #paged_uploads = paginator.get_page(page)


    context ={
        'data' : feeder_sections,
        'county': county,


    }
    return render(request, 'main/feeder_sections_list.html', context)
    
@login_required(login_url="login")
def feeder_section(request):
    # region_users = UserProfile.objects.filter(region=userprofile.region,campaign='lp').exclude(user=request.user)
    campaign = request.user.userprofile.campaign

    if campaign == "network_supervisors":  # or campaign == "threephase":
        if request.method == "POST":
            # user_form = UserForm(request.POST, instance=request.user)
            m_form = Feeder_sectionsForm(request.POST, request.FILES,request=request)

            if m_form.is_valid():
                section = m_form.save(commit=False)
                section.logged_by = request.user.userprofile
                section.feeder =  m_form.cleaned_data["feeder"]
                section.name = m_form.cleaned_data["name"]
                section.aprx_length = m_form.cleaned_data["aprx_length"]
                section.save()
                messages.success(
                    request, "Feeder Section Has been successfully saved."
                )
                return redirect("main:feeder-sections-list")
            else:
                messages.error(
                    request, "There was an error in submitting your Feeder SEction."
                )
                print("invalid form")
                print(m_form.errors)
                # m_form = LpForm(instance=img)
        else:
            m_form = Feeder_sectionsForm(request=request)
        context = {
            "form": m_form,
        }
    else:
        messages.error(request, "You are not configured to run on this campaign.")
        return redirect("main:my-dashboard")

    return render(request, "main/feeder_section_new.html", context)
        

@login_required(login_url="login")
def newupload(request):
    sectorname = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = MeterForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            meter = form.save(commit=False)
            meter.user = request.user
            countyy = request.user.userprofile.county
            meter.county = request.user.userprofile.county
            meter.resposnsible = UserProfile.objects.get(profiletype='cse', county=request.user.userprofile.county)
            uploaded  =Meters.objects.filter(meternumber=meter.meternumber, status='pending')
            if uploaded.count() > 0: 
              messages.error(request,'That Meter Information is already uploaded and Pending Resolution.')
              return redirect('main:upload-new')
            else:
                meter.save()                
            messages.success(request,'Your record has been uploaded successfully')
            return redirect('main:my-dashboard')
        else:
            messages.error(request,'Error Uploading the record. Please Try Again')
    else:
        form = MeterForm(request=request)
    return render(request,'main/newupload.html', {'form': form,'sectorname':sectorname})

@login_required(login_url="login")
def myuploads(request):
    if request.user.is_authenticated:
        user = request.user
    meters = Meters.objects.filter(user=user)
    paginator = Paginator(meters,30)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()
    meters_pending = meters.filter(status = 'pending').count()
    meters_resolved = meters.filter(status = 'solved').count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : meters_count,
        'meters_pending' : meters_pending,
        'meters_resolved' : meters_resolved,
        'nbar' : 'myuploads'}
    return render(request, 'main/myuploads.html', context)

@login_required(login_url="login")
def viewuploaded(request, pk):
    meter = Meters.objects.get(id=pk)
    username = meter.resposnsible.user
    if meter.asigned:
        asigned = meter.asigned.user
    else:
        asigned = 'None'
    context = {'meter' : meter,
               'username' : username,
               'asigned' : asigned}
    return render(request, 'main/viewimageuploaded.html', context)

@login_required(login_url="login")
def updateupload(request,pk):
    img  = Meters.objects.get(id=pk)
    form = MeterForm(instance=img, request=request)

    if request.method == 'POST':
        form = MeterForm(request.POST,request.FILES, instance=img, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Updated successfully')
            return redirect('main:my-uploaded-list')

    context ={'form': form}
    return render(request, 'main/newupload.html', context)

@login_required(login_url="login")
def uploadasign(request,pk):
    img  = Meters.objects.get(id=pk)
    form = AsignForm(instance=img, county=img.county)

    if request.method == 'POST':
        form = AsignForm(request.POST,request.FILES, instance=img, county=img.county)
        if form.is_valid():
            form.save()
            
            context ={'meters' : img}
            messages.success(request, 'Asigned successfully')
            
            return redirect('main:my-asignment-list')

    context ={'form': form}
    return render(request, 'main/newupload.html', context)

@login_required(login_url="login")
def resolveupload(request,pk):
    img  = Meters.objects.get(id=pk)
    form = ResolveForm(instance=img)

    if request.method == 'POST':
        form = ResolveForm(request.POST,request.FILES, instance=img)
        if form.is_valid():
            meter = form.save(commit=False)
            meter.status = 'initiated'
            form.save()
            messages.success(request, 'Resolution Record saved successfully')
            return redirect('main:my-asignment-list')

    context ={'form': form}
    return render(request, 'main/asignresolve.html', context)    

@login_required(login_url="login")
def deleteupload(request, pk):
    img  = Meters.objects.get(id=pk)
    if request.method =='POST':
        img.delete()
        return redirect('main:my-uploaded-list')
    context = {'object' : img}
    return render(request, 'main/delete_confirmation.html', context)

@login_required(login_url="login")
def myasignments(request):
    if request.user.is_authenticated:
        user = request.user.userprofile
    meters = Meters.objects.filter(resposnsible=user, status = 'pending')
    paginator = Paginator(meters,30)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()
    meters_pending = meters.filter(status = 'pending').count()
    meters_resolved = meters.filter(status = 'solved').count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : meters_count,
        'meters_pending' : meters_pending,
        'meters_resolved' : meters_resolved,
        'nbar' : 'myasignments'}
    return render(request, 'main/myasignments.html', context)

@login_required(login_url="login")
def myasignments(request):
    if request.user.is_authenticated:
        user = request.user.userprofile
    meters = Meters.objects.filter(resposnsible=user, status = 'pending')
    paginator = Paginator(meters,30)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()
    meters_pending = meters.filter(status = 'pending').count()
    meters_resolved = meters.filter(status = 'solved').count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : meters_count,
        'meters_pending' : meters_pending,
        'meters_resolved' : meters_resolved,
        'nbar' : 'myasignments'}
    return render(request, 'main/myasignments.html', context)

@login_required(login_url="login")
def viewuploadedasigned(request, pk):
    meter = Meters.objects.get(id=pk)
    username = meter.resposnsible.user
    u = UserProfile.objects.get(user=username)
    form_asigned = AsignForm(instance=meter, county=meter.county )
    
    if meter.asigned:
        asigned = meter.asigned.user
    else:
        asigned = 'None'
    context = {
        'meter' : meter,
        'form_asign' : form_asigned,
        'username' : username,
        'asigned' : asigned
        }
    return render(request, 'main/viewimageuploadedasigned.html', context)

@login_required(login_url="login")
def alluploads(request):
    if request.user.is_authenticated:
        user = request.user
    meters = Meters.objects.all()
    paginator = Paginator(meters,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()
    meters_pending = meters.filter(status = 'pending').count()
    meters_resolved = meters.filter(status = 'solved').count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : meters_count,
        'meters_pending' : meters_pending,
        'meters_resolved' : meters_resolved,
        'nbar' : 'alluploads'}
    return render(request, 'main/alluploads.html', context)

@login_required(login_url="login")
def analytics(request, pk=None):
    if request.user.is_authenticated:
        user = request.user
    meters = Meters.objects.all()
    paginator = Paginator(meters,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_count = meters.count()
    analytics = County.objects.values('name').annotate(
        faulty=(Count('id', filter=Q(meters__anomalytype='faultymeter'))),
        meternotinincms=(Count('id', filter=Q(meters__anomalytype='meternotinincms'))),
        retrofits=(Count('id', filter=Q(meters__anomalytype='retrofit'))),
        billing=(Count('id', filter=Q(meters__anomalytype='rebilling'))),
        irregularity=(Count('id', filter=Q(meters__anomalytype='irregularity'))),
        idle=(Count('id', filter=Q(meters__anomalytype='idle'))),
        directconnection=(Count('id', filter=Q(meters__anomalytype='directconnecction'))),
        faulty_pending=(Count('id', filter=Q(meters__anomalytype='faultymeter')&Q(meters__status='pending'))),
        notinincms_pending=(Count('id', filter=Q(meters__anomalytype='meternotinincms')&Q(meters__status='pending'))),
        retrofits_pending=(Count('id', filter=Q(meters__anomalytype='retrofit')&Q(meters__status='pending'))),
        billing_pending=(Count('id', filter=Q(meters__anomalytype='rebilling')&Q(meters__status='pending'))),
        irregularity_pending=(Count('id', filter=Q(meters__anomalytype='irregularity')&Q(meters__status='pending'))),
        idle_pending=(Count('id', filter=Q(meters__anomalytype='idle')&Q(meters__status='pending'))),
        directconnection_pending=(Count('id', filter=Q(meters__anomalytype='directconnecction')&Q(meters__status='pending'))),
        faulty_resolved=(Count('id', filter=Q(meters__anomalytype='faultymeter')&Q(meters__status='solved'))),
        notinincms_resolved=(Count('id', filter=Q(meters__anomalytype='meternotinincms')&Q(meters__status='solved'))),
        retrofits_resolved=(Count('id', filter=Q(meters__anomalytype='retrofit')&Q(meters__status='solved'))),
        billing_resolved=(Count('id', filter=Q(meters__anomalytype='rebilling')&Q(meters__status='solved'))),
        irregularity_resolved=(Count('id', filter=Q(meters__anomalytype='irregularity')&Q(meters__status='solved'))),
        idle_resolved=(Count('id', filter=Q(meters__anomalytype='idle')&Q(meters__status='solved'))),
        directconnection_resolved=(Count('id', filter=Q(meters__anomalytype='directconnecction')&Q(meters__status='solved'))),
        ).order_by('name')
    meters_pending = meters.filter(status = 'pending').count()
    meters_resolved = meters.filter(status = 'solved').count()
    faultymeters = meters.filter(anomalytype='faultymeter').count()
    faultymeters_pending = Meters.objects.filter(anomalytype='faultymeter', status='pending').count()
    faultymeters_resolved= Meters.objects.filter(anomalytype='faultymeter', status='solved').count()
    metersnotincms = Meters.objects.filter(anomalytype='meternotinincms').count()
    metersnotincms_pending = Meters.objects.filter(anomalytype='meternotinincms', status='pending').count()
    metersnotincms_resolved = Meters.objects.filter(anomalytype='meternotinincms', status='solved').count()
    rebilling_issues = Meters.objects.filter(anomalytype='rebilling').count()
    rebilling_issues_pending = Meters.objects.filter(anomalytype='rebilling', status='pending').count()
    rebilling_issues_resolved = Meters.objects.filter(anomalytype='rebilling', status='solved').count()
    
    irregularity_issues = Meters.objects.filter(anomalytype='irregularity').count()
    irregularity_issues_pending = Meters.objects.filter(anomalytype='irregularity', status='pending').count()
    irregularity_issues_resolved = Meters.objects.filter(anomalytype='irregularity', status='solved').count()
    
    directconnections = Meters.objects.filter(anomalytype='directconnecction').count()
    directconnections_pending = Meters.objects.filter(anomalytype='directconnecction', status='pending').count()
    directconnections_resolved = Meters.objects.filter(anomalytype='directconnecction', status='solved').count()
    context = {
        'meters' : paged_uploads,
        'analytics' : analytics,
        'meters_count' : meters_count,
        'meters_pending' : meters_pending,
        'meters_resolved' : meters_resolved,
        'faultymeters' : faultymeters,
        'faultymeters_pending' : faultymeters_pending,
        'faultymeters_resolved' : faultymeters_resolved,
        'metersnotincms' : metersnotincms,
        'metersnotincms_pending' : metersnotincms_pending,
        'metersnotincms_resolved' : metersnotincms_resolved,
        'rebilling_issues': rebilling_issues,
        'rebilling_issues_pending' : rebilling_issues_pending,
        'rebilling_issues_resolved' : rebilling_issues_resolved,
        'irregularity_issues': irregularity_issues,
        'irregularity_issues_pending' : irregularity_issues_pending,
        'irregularity_issues_resolved' : irregularity_issues_resolved,
        'directconnections' :directconnections,
        'directconnections_pending' : directconnections_pending,
        'directconnections_resolved': directconnections_resolved,
        'nbar' : 'analytics'
        
        }
    return render(request, 'main/analytics.html', context)

@login_required(login_url="login")
def exportupload(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    meters = Meters.objects.all()

    writer.writerow(['COUNTY','SECTROR','ANOMALY TYPE','USER-NARRATION','METER NUMBER','CUSTOMER NAME','CUSTOMER CONTACT','METER READINGS','UPLOADED-BY','UPLOADED-BY-NAME','UPLOADED-BY-MOBILE','RESPONSIBLE','DATE UPLOADED','STATUS'])
    for meter in meters:        
        writer.writerow([meter.county.name,meter.sector.name, meter.anomalytype,meter.naration,meter.meternumber,meter.customername, meter.customercontact, meter.readings,meter.user,meter.user.name,meter.user.mobile,meter.resposnsible,meter.dtadd,meter.status])

    response['Content-Disposition'] = 'attachment; filename="UPLOADED METERS.csv" '
    return response

@login_required(login_url="login")
def faultymeters(request):
    if request.user.is_authenticated:
        user = request.user
    faultymeters = Meters.objects.filter(anomalytype='faultymeter')
    paginator = Paginator(faultymeters,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    faultymeters_count = faultymeters.count()
    faultymeters_pending = Meters.objects.filter(anomalytype='faultymeter', status='pending').count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : faultymeters_count,
         'nbar' : 'faultymeters',
         'faultymeters_pending' : faultymeters_pending
        }
    return render(request, 'main/faultymeters.html', context)

@login_required(login_url="login")
def exportupload_faultymeters(request):
    response = HttpResponse(content_type='text/csv')
    current_date = datetime.date.today()
    writer = csv.writer(response)
    meters = Meters.objects.filter(anomalytype='faultymeter')

    writer.writerow(['TICKETID','COUNTY','SECTOR','CATEGORY','METER NUMBER','CUSTOMER NAME','CUSTOMER CONTACT','METER READINGS','RESPONSIBLE','ASIGNED TO','UPLOADED BY(KPL)','NARRATION','DATE UPLOADED','STATUS','ASIGNED TO','CSE NARRATION','RCCS'])
    for meter in meters:        
        writer.writerow([meter.id,meter.county,meter.sector, meter.anomalytype,meter.meternumber,meter.customername, meter.customercontact, meter.readings,meter.resposnsible.user,meter.asigned.user,meter.user,meter.naration,meter.dtadd,meter.status,meter.asigned,meter.asigned_narration,meter.rccsNumber])

    response['Content-Disposition'] = 'attachment; filename="UPLOADED FAULTY METERS.csv" '
    return response

@login_required(login_url="login")
def faultymeters_pending(request):
    if request.user.is_authenticated:
        user = request.user
    faultymeters = Meters.objects.filter(anomalytype='faultymeter', status='pending')
    paginator = Paginator(faultymeters,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    faultymeters_count = faultymeters.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : faultymeters_count,
        'nbar' : 'faultymeterspending'
        }
    return render(request, 'main/faultymeters_pending.html', context)

@login_required(login_url="login")
def exportupload_faultymeters_pending(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    meters = Meters.objects.filter(anomalytype='faultymeter', status='pending')

    writer.writerow(['TICKETID','COUNTY','SECTOR','CATEGORY','METER NUMBER','CUSTOMER NAME','CUSTOMER CONTACT','METER READINGS','RESPONSIBLE','ASIGNED TO','UPLOADED BY(KPL)','NARRATION','DATE UPLOADED','STATUS','ASIGNED TO','CSE NARRATION','RCCS'])
    for meter in meters:        
        writer.writerow([meter.id,meter.county,meter.sector, meter.anomalytype,meter.meternumber,meter.customername, meter.customercontact, meter.readings,meter.resposnsible.user,meter.asigned.user,meter.user,meter.naration,meter.dtadd,meter.status,meter.asigned,meter.asigned_narration,meter.rccsNumber])

    response['Content-Disposition'] = 'attachment; filename="UPLOADED FAULTY METERS PENDING.csv" '
    return response

@login_required(login_url="login")
def faultymeters_resolved(request):
    if request.user.is_authenticated:
        user = request.user
    faultymeters = Meters.objects.filter(anomalytype='faultymeter', status='solved')
    paginator = Paginator(faultymeters,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    faultymeters_count = faultymeters.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : faultymeters_count,
        'nbar' : 'faultymetersresolved'
        }
    return render(request, 'main/faultymeters_resolved.html', context)

@login_required(login_url="login")
def exportupload_faultymeters_resolved(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    meters = Meters.objects.filter(anomalytype='faultymeter', status='solved')

    writer.writerow(['COUNTY','ANOMALY TYPE','METER NUMBER','CUSTOMER NAME','CUSTOMER CONTACT','METER READINGS','STAFf(KPL)','NARRATION','DATE UPLOADED','STATUS','ASIGNED TO','CSE NARRATION'])
    for meter in meters:        
         writer.writerow([meter.id,meter.county,meter.sector, meter.anomalytype,meter.meternumber,meter.customername, meter.customercontact, meter.readings,meter.resposnsible.user,meter.asigned.user,meter.user,meter.naration,meter.dtadd,meter.status,meter.asigned,meter.asigned_narration,meter.rccsNumber])

    response['Content-Disposition'] = 'attachment; filename="UPLOADED FAULTY METERS RESOLVED.csv" '
    return response

@login_required(login_url="login")
def metersnotin_incms(request):
    if request.user.is_authenticated:
        user = request.user
    metersnotincms = Meters.objects.filter(anomalytype='meternotinincms')
    paginator = Paginator(metersnotincms,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    metersnotincms_count = metersnotincms.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : metersnotincms_count,
        'nbar' : 'metersnotinincms'
        }
    return render(request, 'main/metersnotin_incms.html', context)

@login_required(login_url="login")
def exportupload_metersnotinincms(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    meters = Meters.objects.filter(anomalytype='meternotinincms')

    writer.writerow(['TICKETID','COUNTY','SECTOR','CATEGORY','METER NUMBER','CUSTOMER NAME','CUSTOMER CONTACT','METER READINGS','RESPONSIBLE','ASIGNEDTO','UPLOADEDBY(KPL)','NARRATION','DATE UPLOADED','STATUS','CSE NARRATION'])
    for meter in meters:        
        writer.writerow([meter.id, meter.county,meter.sector, meter.anomalytype,meter.meternumber,meter.customername, meter.customercontact, meter.readings,meter.resposnsible,meter.asigned, meter.user,meter.naration,meter.dtadd,meter.status,meter.asigned_narration])

    response['Content-Disposition'] = 'attachment; filename="UPLOADED METERS NOT IN INCMS.csv" '
    return response

@login_required(login_url="login")
def metersnotin_incms_pending(request):
    if request.user.is_authenticated:
        user = request.user
    metersnotinincms = Meters.objects.filter(anomalytype='meternotinincms', status='pending')
    paginator = Paginator(metersnotinincms,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    metersnotinincms_count = metersnotinincms.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : metersnotinincms_count,
        'nbar' : 'notinincmspending'
        }
    return render(request, 'main/metersnotincms_pending.html', context)

@login_required(login_url="login")
def exportupload_metersnotinincms_pending(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    meters = Meters.objects.filter(anomalytype='meternotinincms', status='pending')

    writer.writerow(['TICKETID','COUNTY','SECTOR','CATEGORY','METER NUMBER','CUSTOMER NAME','CUSTOMER CONTACT','METER READINGS','RESPONSIBLE','ASIGNEDTO','UPLOADEDBY(KPL)','NARRATION','DATE UPLOADED','STATUS','CSE NARRATION'])
    for meter in meters:        
        writer.writerow([meter.id, meter.county,meter.sector, meter.anomalytype,meter.meternumber,meter.customername, meter.customercontact, meter.readings,meter.resposnsible,meter.asigned, meter.user,meter.naration,meter.dtadd,meter.status,meter.asigned_narration])

    response['Content-Disposition'] = 'attachment; filename="UPLOADED METERS NOT IN INCMS PENDING.csv" '
    return response

@login_required(login_url="login")
def metersnotin_incms_resolved(request):
    if request.user.is_authenticated:
        user = request.user
    metersnotinincms_resolved = Meters.objects.filter(anomalytype='meternotinincms', status='solved')
    paginator = Paginator(metersnotinincms_resolved,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    metersnotinincms_count = metersnotinincms_resolved.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : metersnotinincms_count,
        'nbar' : 'admin'
        }
    return render(request, 'main/metersnotincms_resolved.html', context)

@login_required(login_url="login")
def exportupload_metersnotinincms_resolved(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    meters = Meters.objects.filter(anomalytype='meternotinincms', status='solved')

    writer.writerow(['COUNTY','ANOMALY TYPE','METER NUMBER','CUSTOMER NAME','CUSTOMER CONTACT','METER READINGS','STAFf(KPL)','NARRATION','DATE UPLOADED','STATUS','ASIGNED TO','CSE NARRATION'])
    for meter in meters:        
        writer.writerow([meter.county.name, meter.anomalytype,meter.meternumber,meter.customername, meter.customercontact, meter.readings,meter.user,meter.naration,meter.dtadd,meter.status,meter.asigned,meter.asigned_narration])

    response['Content-Disposition'] = 'attachment; filename="UPLOADED METERS NOT IN INCMS RESOLVED.csv" '
    return response

@login_required(login_url="login")
def billing_issues(request):
    if request.user.is_authenticated:
        user = request.user
    billing = Meters.objects.filter(anomalytype='rebilling')
    paginator = Paginator(billing,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    billing_count = billing.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : billing_count,
        'nbar' : 'billingqueries'
        }
    return render(request, 'main/billing_issues.html', context)

@login_required(login_url="login")
def exportupload_billingissues(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    meters = Meters.objects.filter(anomalytype='rebilling')

    writer.writerow(['COUNTY','ANOMALY TYPE','METER NUMBER','CUSTOMER NAME','CUSTOMER CONTACT','METER READINGS','STAFf(KPL)','NARRATION','DATE UPLOADED','STATUS','ASIGNED TO','CSE NARRATION'])
    for meter in meters:        
        writer.writerow([meter.county.name, meter.anomalytype,meter.meternumber,meter.customername, meter.customercontact, meter.readings,meter.user,meter.naration,meter.dtadd,meter.status,meter.asigned,meter.asigned_narration])

    response['Content-Disposition'] = 'attachment; filename="UPLOADED METERS WITH BILLING QUERIES.csv" '
    return response

@login_required(login_url="login")
def billing_issues_pending(request):
    if request.user.is_authenticated:
        user = request.user
    billing_issues = Meters.objects.filter(anomalytype='rebilling', status='pending')
    paginator = Paginator(billing_issues,10)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    billing_issues_count = billing_issues.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : billing_issues_count,
        'nbar' : 'admin'
        }
    return render(request, 'main/billing_issues_pending.html', context)

@login_required(login_url="login")
def exportupload_billingissues_pending(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    meters = Meters.objects.filter(anomalytype='rebilling', status='pending')

    writer.writerow(['COUNTY','ANOMALY TYPE','METER NUMBER','CUSTOMER NAME','CUSTOMER CONTACT','METER READINGS','STAFf(KPL)','NARRATION','DATE UPLOADED','STATUS','ASIGNED TO','CSE NARRATION'])
    for meter in meters:        
        writer.writerow([meter.county.name, meter.anomalytype,meter.meternumber,meter.customername, meter.customercontact, meter.readings,meter.user,meter.naration,meter.dtadd,meter.status,meter.asigned,meter.asigned_narration])

    response['Content-Disposition'] = 'attachment; filename="UPLOADED METERS WITH BILLING QUERIES PENDING.csv" '
    return response

@login_required(login_url="login")
def billing_issues_resolved(request):
    if request.user.is_authenticated:
        user = request.user
    billing_resolved = Meters.objects.filter(anomalytype='rebilling', status='solved')
    paginator = Paginator(billing_resolved,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    billing_resolved_count = billing_resolved.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : billing_resolved_count,
        'nbar' : 'admin'
        }
    return render(request, 'main/billing_resolved.html', context)

@login_required(login_url="login")
def exportupload_billingissues_resolved(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    meters = Meters.objects.filter(anomalytype='rebilling', status='solved')

    writer.writerow(['COUNTY','ANOMALY TYPE','METER NUMBER','CUSTOMER NAME','CUSTOMER CONTACT','METER READINGS','STAFf(KPL)','NARRATION','DATE UPLOADED','STATUS','ASIGNED TO','CSE NARRATION'])
    for meter in meters:        
        writer.writerow([meter.county.name, meter.anomalytype,meter.meternumber,meter.customername, meter.customercontact, meter.readings,meter.user,meter.naration,meter.dtadd,meter.status,meter.asigned,meter.asigned_narration])

    response['Content-Disposition'] = 'attachment; filename="UPLOADED METERS WITH BILLING QUERIES SOLVED.csv" '
    return response

@login_required(login_url="login")
def irregularity_issues(request):
    if request.user.is_authenticated:
        user = request.user
    billing = Meters.objects.filter(anomalytype='irregularity')
    paginator = Paginator(billing,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    billing_count = billing.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : billing_count,
        'nbar' : 'billingqueries'
        }
    return render(request, 'main/irregularity_billing.html', context)

@login_required(login_url="login")
def exportupload_irregularities(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    meters = Meters.objects.filter(anomalytype='irregularity')

    writer.writerow(['COUNTY','ANOMALY TYPE','METER NUMBER','CUSTOMER NAME','CUSTOMER CONTACT','METER READINGS','STAFf(KPL)','NARRATION','DATE UPLOADED','STATUS','ASIGNED TO','CSE NARRATION'])
    for meter in meters:        
        writer.writerow([meter.county.name, meter.anomalytype,meter.meternumber,meter.customername, meter.customercontact, meter.readings,meter.user,meter.naration,meter.dtadd,meter.status,meter.asigned,meter.asigned_narration])

    response['Content-Disposition'] = 'attachment; filename="UPLOADED METERS WITH IRREGULARITIES.csv" '
    return response

@login_required(login_url="login")
def irregularity_issues_pending(request):
    if request.user.is_authenticated:
        user = request.user
    billing_issues = Meters.objects.filter(anomalytype='irregularity', status='pending')
    paginator = Paginator(billing_issues,10)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    billing_issues_count = billing_issues.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : billing_issues_count,
        'nbar' : 'admin'
        }
    return render(request, 'main/irregularity_issues_pending.html', context)

@login_required(login_url="login")
def exportupload_irregularity_pending(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    meters =Meters.objects.filter(anomalytype='irregularity', status='pending')

    writer.writerow(['COUNTY','ANOMALY TYPE','METER NUMBER','CUSTOMER NAME','CUSTOMER CONTACT','METER READINGS','STAFf(KPL)','NARRATION','DATE UPLOADED','STATUS','ASIGNED TO','CSE NARRATION'])
    for meter in meters:        
        writer.writerow([meter.county.name, meter.anomalytype,meter.meternumber,meter.customername, meter.customercontact, meter.readings,meter.user,meter.naration,meter.dtadd,meter.status,meter.asigned,meter.asigned_narration])

    response['Content-Disposition'] = 'attachment; filename="UPLOADED METERS WITH IRREGULARITIES PENDING.csv" '
    return response

@login_required(login_url="login")
def irregularity_resolved(request):
    if request.user.is_authenticated:
        user = request.user
    billing_resolved = Meters.objects.filter(anomalytype='irregularity', status='solved')
    paginator = Paginator(billing_resolved,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    billing_resolved_count = billing_resolved.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : billing_resolved_count,
        'nbar' : 'admin'
        }
    return render(request, 'main/irregularity_resolved.html', context)

@login_required(login_url="login")
def exportupload_irregularity_resolved(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    meters =Meters.objects.filter(anomalytype='irregularity', status='solved')

    writer.writerow(['COUNTY','ANOMALY TYPE','METER NUMBER','CUSTOMER NAME','CUSTOMER CONTACT','METER READINGS','STAFf(KPL)','NARRATION','DATE UPLOADED','STATUS','ASIGNED TO','CSE NARRATION'])
    for meter in meters:        
        writer.writerow([meter.county.name, meter.anomalytype,meter.meternumber,meter.customername, meter.customercontact, meter.readings,meter.user,meter.naration,meter.dtadd,meter.status,meter.asigned,meter.asigned_narration])

    response['Content-Disposition'] = 'attachment; filename="UPLOADED METERS WITH IRREGULARITIES SOLVED.csv" '
    return response

@login_required(login_url="login")
def directconnections(request):
    if request.user.is_authenticated:
        user = request.user
    directconnections = Meters.objects.filter(anomalytype='directconnecction')
    paginator = Paginator(directconnections,10)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    directconnections_count = directconnections.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : directconnections_count,
        'nbar' : 'admin'
        }
    return render(request, 'main/directconnections.html', context)

@login_required(login_url="login")
def directconnections_pending(request):
    if request.user.is_authenticated:
        user = request.user
    directconnections = Meters.objects.filter(anomalytype='directconnecction', status='pending')
    paginator = Paginator(directconnections,10)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    directconnections_count = directconnections.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : directconnections_count,
        'nbar' : 'admin'
        }
    return render(request, 'main/directconnections_pending.html', context)

@login_required(login_url="login")
def directconnections_resolved(request):
    if request.user.is_authenticated:
        user = request.user
    directconnections_resolved = Meters.objects.filter(anomalytype='directconnecction', status='solved')
    paginator = Paginator(directconnections_resolved,10)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    directconnections_resolved_count = directconnections_resolved.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : directconnections_resolved_count,
        'nbar' : 'admin'
        }
    return render(request, 'main/directconnections_resolved.html', context)

@login_required(login_url="login")
def county_configuration(request):
    if request.user.is_authenticated:
        user = request.user
    counties = County.objects.all()
    paginator = Paginator(counties,20)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    meters_count = counties.count()
   
    context = {
        'meters' : paged_uploads,
        'meters_count' : meters_count,
        'nbar' : 'countyconfigs'}
    return render(request, 'main/countyconfiguration.html', context)

@login_required(login_url="login")
def update_county_configuration(request,pk):
    img  = County.objects.get(id=pk)
    form = CountyForm(instance=img)

    if request.method == 'POST':
        form = CountyForm(request.POST, instance=img)
        if form.is_valid():
            county = form.save(commit=False)
            county.staff = request.user
            form.save()
            messages.success(request, 'County Configuration Updated successfully')
            return redirect('main:county-configuration')

    context ={'form': form,
              'nbar' : 'updatecounty'}
    return render(request, 'main/newcountyconfiguration.html', context)

@login_required(login_url="login")
def search_meter(request):
	if 'keyword' in request.GET:
		keyword = request.GET["keyword"]
		if keyword:
			paged_uploads = Meters.objects.filter(meternumber__icontains=keyword)
    			
	context = {
		'meters' : paged_uploads,	
        'meters_count' : paged_uploads.count(),
        'nbar': 'searchmeter',	
	}
	
	return render(request, 'main/alluploads.html', context)

@login_required(login_url="login")
def illegalretrofits(request):
    if request.user.is_authenticated:
        user = request.user
    illegalretrofits = Meters.objects.filter(anomalytype='retrofit')
    paginator = Paginator(illegalretrofits,10)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    illegalretrofits_count = illegalretrofits.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : illegalretrofits_count,
        'nbar' : 'admin'
        }
    return render(request, 'main/illegalretrofits.html', context)


@login_required(login_url="login")
def exportupload_illegalretrofits(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    meters =Meters.objects.filter(anomalytype='retrofit')

    writer.writerow(['COUNTY','ANOMALY TYPE','METER NUMBER','CUSTOMER NAME','CUSTOMER CONTACT','METER READINGS','STAFf(KPL)','NARRATION','DATE UPLOADED','STATUS','ASIGNED TO','CSE NARRATION'])
    for meter in meters:        
        writer.writerow([meter.county.name, meter.anomalytype,meter.meternumber,meter.customername, meter.customercontact, meter.readings,meter.user,meter.naration,meter.dtadd,meter.status,meter.asigned,meter.asigned_narration])

    response['Content-Disposition'] = 'attachment; filename="UPLOADED METERS WITH ILLEGAL RETROFITS.csv" '
    return response

@login_required(login_url="login")
def illegalretrofits_pending(request):
    if request.user.is_authenticated:
        user = request.user
    illegalretrofits_pending = Meters.objects.filter(anomalytype='retrofit', status='pending')
    paginator = Paginator(illegalretrofits_pending,10)
    page = request.GET.get('page')
    paged_uploads = paginator.get_page(page)
    illegalretrofits_pending_count = illegalretrofits_pending.count()
    context = {
        'meters' : paged_uploads,
        'meters_count' : illegalretrofits_pending_count,
        'nbar' : 'admin'
        }
    return render(request, 'main/illegalretrofits_pending.html', context)

@login_required(login_url="login")
def exportupload_illegalretrofits_pending(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    meters =Meters.objects.filter(anomalytype='retrofit', status='pending')

    writer.writerow(['COUNTY','ANOMALY TYPE','METER NUMBER','CUSTOMER NAME','CUSTOMER CONTACT','METER READINGS','STAFf(KPL)','NARRATION','DATE UPLOADED','STATUS','ASIGNED TO','CSE NARRATION'])
    for meter in meters:        
        writer.writerow([meter.county.name, meter.anomalytype,meter.meternumber,meter.customername, meter.customercontact, meter.readings,meter.user,meter.naration,meter.dtadd,meter.status,meter.asigned,meter.asigned_narration])

    response['Content-Disposition'] = 'attachment; filename="UPLOADED METERS WITH ILLEGAL RETROFITS.csv" '
    return response