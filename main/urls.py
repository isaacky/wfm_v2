from django.urls import path
from . import views

app_name = 'main'
urlpatterns = [
    path('viewuploadasigned/<str:pk>/', views.viewuploadedasigned, name='view-uploaded-asigned'),
    path('viewupload/<str:pk>/', views.viewuploaded, name='view-uploaded'),
    path('uploadupdate/<str:pk>/', views.updateupload, name='update-upload'),
    path('uploadasign/<str:pk>/', views.uploadasign, name='asign'),
    path('update_county_configaration/<str:pk>/', views.update_county_configuration, name='update-county-configuration'),
    path('resolveupload/<str:pk>/', views.resolveupload, name='resolve-upload'),
    path('uploaddelete/<str:pk>/', views.deleteupload, name='delete-upload'),
    path('', views.mydashboard, name='my-dashboard'),
    path('newupload', views.newupload, name='upload-new'),
    path('myuploads/', views.myuploads, name='my-uploaded-list'),
    path('myasignments/', views.myasignments, name='my-asignment-list'),
    path('alluploads/', views.alluploads, name='all-uploads'),
    path('county_configuration/', views.county_configuration, name='county-configuration'),

    path('analytics/', views.analytics, name='analytics-dashboard'),
    
    path('search_meter/', views.search_meter, name="search-by-meter"),

    path('faultymeters/', views.faultymeters, name='faulty-meter-list'),
    path('faultymeters_pending/', views.faultymeters_pending, name='faulty-meter-pending'),
    path('faultymeters_resolved/', views.faultymeters_resolved, name='faulty-meter-resolved'),
    
    path('metersnotin_incms/', views.metersnotin_incms, name='meters-notincms-list'),
    path('metersnotin_incms_pending/', views.metersnotin_incms_pending, name='meters-notincms-pending'),
    path('metersnotin_incms_resolved/', views.metersnotin_incms_resolved, name='meters-notincms-resolved'),

    path('billing_issues/', views.billing_issues, name='billing-issues-list'),
    path('billing_issues_pending/', views.billing_issues_pending, name='billing-issues-pending'),
    path('billing_issues_resolved/', views.billing_issues_resolved, name='billing-issues-resolved'),
    
    path('irregularitybilling_issues/', views.irregularity_issues, name='irregularity-issues-list'),
    path('irregularity_issues_pending/', views.irregularity_issues_pending, name='irregularity-issues-pending'),
    path('irregularity_resolved/', views.irregularity_resolved, name='irregularity-issues-resolved'),

    path('directconnections/', views.directconnections, name='direct-connections-list'),
    path('directconnections_pending/', views.directconnections_pending, name='direct-connections-pending'),
    path('directconnections_resolved/', views.directconnections_resolved, name='direct-connections-resolved'),
    
    path('illegalretrofits/', views.illegalretrofits, name='illegalretrofits-list'),
    path('directconnections_pending/', views.directconnections_pending, name='direct-connections-pending'),
    path('directconnections_resolved/', views.directconnections_resolved, name='direct-connections-resolved'),

    path('exportuploads/', views.exportupload, name='export-uploads'),
    path('exportupload_faultymeters/', views.exportupload_faultymeters, name='export-uploads-faultymeters'),
    path('exportupload_faultymeters_pending/', views.exportupload_faultymeters_pending, name='export-uploads-faulty-pending'),
    path('exportupload_faultymeters_resolved/', views.exportupload_faultymeters_resolved, name='export-uploads-faultymeters-resolved'),

    path('exportupload_metersnotinincms/', views.exportupload_metersnotinincms, name='export-uploads-metersnotinincms'),
    path('exportupload_metersnotinincms_pending/', views.exportupload_metersnotinincms_pending, name='export-uploads-metersnotinincms-pending'),
    path('exportupload_metersnotinincms_resolved/', views.exportupload_metersnotinincms_resolved, name='export-uploads-metersnotinincms-resolved'),

    path('exportupload_billingissues/', views.exportupload_billingissues, name='export-uploads-billingissues'),
    path('exportupload_billingissues_pending/', views.exportupload_billingissues_pending, name='export-uploads-billingissues-pending'),
    path('exportupload_billingissues_resolved/', views.exportupload_billingissues_resolved, name='export-uploads-billingissues-resolved'),
    
    path('exportupload_irregularities/', views.exportupload_irregularities, name='export-uploads-irregularities'),
    path('exportupload_irregularity_pending/', views.exportupload_irregularity_pending, name='export-uploads-irregularity-pending'),
    path('exportupload_irregularity_resolved/', views.exportupload_irregularity_resolved, name='export-uploads-billingissues-resolved'),
    
    path('exportupload_illegalretrofits/', views.exportupload_illegalretrofits, name='export-uploads-illegalretrofits'),
    path('exportupload_illegalretrofits_pending/', views.exportupload_illegalretrofits_pending, name='export-uploads-illegalretrofits-pending'),
    path('exportupload_irregularity_resolved/', views.exportupload_irregularity_resolved, name='export-uploads-billingissues-resolved'),
    
    path('feeder_section/', views.feeder_section, name='feeder-sections'),
    path('feeder_sections_list/', views.feeder_sections_list, name='feeder-sections-list'),
    path('feeder_section_edit/<str:pk>/', views.feeder_section_edit, name="feeder-section-edit"),
    
   
    
]
