from django.urls import path
from . import views

app_name = 'lv'
urlpatterns = [
    path('substation_search', views.substation_search, name='substation-search'),
    path('search_by_ssn/', views.search_by_ssn, name="search-by-ssn"),
    path('ssn_detail/<str:pk>/', views.ssn_detail, name="ssn-detail"),
    path('lvinspection_new/<str:pk>/', views.lvinspection_new, name="lvinspection-new"),
    path('lvinspection_my/', views.lvinspection_my, name="lvinspection-my"),
    path('lvinspection_update/<str:pk>/', views.lvinspection_update, name="lvinspection-update"),
    path('lvinspection_print/<str:pk>/', views.lvinspection_print, name="lvinspection-print"),
    path('county_analysis/', views.county_analysis, name="county-analysis"),

    path('global_lv/', views.global_lv, name="global-lv"),
    path('global_mv/', views.global_mv, name="global-mv"),
    path('lvinspection_range_export/', views.lvinspection_range_export, name="lvinspection-range-export"),

    path('lv_inspections_pending_app/', views.lv_inspections_pending_app, name="lvinspections-pending-apprv"),
    path('lvinspection_approve/<str:pk>/', views.lvinspection_approve, name="lvinspection-approve"),
    path('lv_inspections_county/', views.lv_inspections_county, name="lvinspections-county"),
    path('ssn_lvinspections/<str:pk>/', views.ssn_lvinspections, name="ssn-lvinspections"),
    path('lvinspection_delete/<str:pk>/', views.lvinspection_delete, name="lvisnpection-delete"),
    path(
        "lv_delete_pole/<str:pk>/",
        views.lv_delete_pole,
        name="lv-delete-pole",
    ),

    path('lvmaintenance_new/<str:pk>/', views.lvmaintenance_new, name="lvmaintenance-new"),
    path('lvmaintenance_my/', views.lvmaintenance_my, name="lvmaintenance-my"),
    path('lvmaitenance_approve/<str:pk>/', views.lvmaintenance_approve, name="lvmaintenance-approve"),
    path('lvinspection_maintain_update/<str:pk>/', views.lvinspection_maintain_update, name="lvmaintenance-update"),
    path('ssn_lvmaintenance/<str:pk>/', views.ssn_lvmaintenance, name="ssn-lvmakintenance"),
    path('lvmaintenance_update/<str:pk>/', views.lvmaintenance_update, name="lvmaintenance-update"),
    path('lvmaintenance_delete/<str:pk>/', views.lvmaintenance_delete, name="lvmaintenance-delete"),
    path('lvmaintenance_print/<str:pk>/', views.lvmaintenance_print, name="lvmaintenance-print"),

    path('poledefects_new/', views.poledefects_new, name="poledefects-new"),
    path('poledefects_list/<str:pk>/', views.poledefects_list, name="poledefects-list"),
    path('poledefects_maintenance_new/<str:pk>/', views.poledefects_maintenance_new, name="poledefects-maintain-new"),
    path('poledefects_maintenance_my/', views.poledefects_maintenance_my, name="poledefects-maintenance-my"),
    path('poledefects_maintain_update/<str:pk>/', views.poledefects_maintain_update, name="poledefect-maintainance-update"),
    path('polemaintenance_approve/<str:pk>/', views.polemaintenance_approve, name="polemaintenance-approve"),
    path('polemaintenance_pending_app/', views.polemaintenance_pending_app, name="poledefects-m-pending-apprv"),
    path('polemaintenance_delete/<str:pk>/', views.polemaintenance_delete, name="polemaintenance-delete"),

#poledefects_maintain

    path('lvfailure_new/<str:pk>/', views.lvfailure_new, name="lvfailure-new"),
    path('lvfailure_my/', views.lvfailure_my, name="lvfailure-my"),
    path('lvfailure_approve/<str:pk>/', views.lvfailure_approve, name="lvfailure-approve"),
    path('lvfailure_update/<str:pk>/', views.lvfailure_update, name="lvfailure-update"),
    path('lvfailure_delete/<str:pk>/', views.lvfailure_delete, name="lvfailure-delete"),
    path('ssn_txfailure/<str:pk>/', views.ssn_txfailure, name="ssn-txfailure"),
    path('txfailure_pending_app/', views.txfailure_pending_app, name="txfailure-pending-apprv"),
    path('txfailure_print/<str:pk>/', views.txfailure_print, name="txfailure-print"),


    # county urls
    path('county_lvinspections_dashboard/', views.county_lvinspections_dashboard, name="county-lvinspections-dashboard"),
    path('county_lvinspections_list/', views.county_lvinspections_list, name="county-lvinspections"),
    path('county_lvmaintenance_list/', views.county_lvmaintenance_list, name="county-lvmaintenance"),
    path('county_lvmaintenance_pending/', views.county_lvmaintenance_pending, name="county-lvmaintenance-pending"),
    path('county_txfailure_list/', views.county_txfailure_list, name="county-txfailure"),
    path('county_substation_list/', views.county_substation_list, name="county-substation"),
    path('county_substation_maintenance_list/', views.county_substation_maintenance_list, name="county-substation-maintenance"),
    path('county_commission_list/', views.county_commission_list, name="county-commission"),
    path('county_poledefects_list/', views.county_poledefects_list, name="county-poledefects"),
    path('county_lv_useranalytics/', views.county_lv_useranalytics, name="county-lv-staff-analytics"),
    path('county_lv_today/', views.county_lv_today, name="county-lv-map-today"),
    path('county_tx_today_failure/', views.county_tx_today_failure, name="county-failure-map-today"),
    path('county_lvinspection_useranalytics/', views.county_lvinspection_useranalytics, name="county-lvinspections-staff-analytics"),
    
    path('county_lv_pages/', views.county_lv_pages, name="county-lv-pages"),
    path('county_lv_pages_filter/', views.county_lv_pages_filter, name="county-lv-pages-datarange"),
    path('county_lv_pages_filter/', views.county_lv_pages_filter, name="county-lv-pages-ssn"),
    path('county_lv_pages_filter/', views.county_lv_pages_filter, name="county-lv-pages-aprvstatus"),
    path('county_lv_pages_filter/', views.county_lv_pages_filter, name="county-lv-pages-staff"),
    path('county_lv_pages_filter/', views.county_lv_pages_filter, name="county-lv-pages-approver"),
    
    path('county_lvmaintenance_pages/', views.county_lvmaintenance_pages, name="county-lvmaintenance-pages"),
    path('county_lvmaintenance_pages_filter/', views.county_lvmaintenance_pages_filter, name="county-lvmaintenance-pages-datarange"),
    path('county_lvmaintenance_pages_filter/', views.county_lvmaintenance_pages_filter, name="county-lvmaintenance-pages-ssn"),
    path('county_lvmaintenance_pages_filter/', views.county_lvmaintenance_pages_filter, name="county-lvmaintenance-pages-aprvstatus"),
    path('county_lvmaintenance_pages_filter/', views.county_lvmaintenance_pages_filter, name="county-lvmaintenance-pages-staff"),
    path('county_lvmaintenance_pages_filter/', views.county_lvmaintenance_pages_filter, name="county-lvmaintenance-pages-approver"),
    
    path('county_failure_pages/', views.county_failure_pages, name="county-failure-pages"),
    path('county_failure_pages_filter/', views.county_failure_pages_filter, name="county-failure-pages-datarange"),
    path('county_failure_pages_filter/', views.county_failure_pages_filter, name="county-failure-pages-ssn"),
    path('county_failure_pages_filter/', views.county_failure_pages_filter, name="county-failure-pages-aprvstatus"),
    path('county_failure_pages_filter/', views.county_failure_pages_filter, name="county-failure-pages-staff"),
    path('county_failure_pages_filter/', views.county_failure_pages_filter, name="county-failure-pages-approver"),
    
    path('county_commission_pages/', views.county_commission_pages, name="county-commission-pages"),
    path('county_commission_pages_filter/', views.county_commission_pages_filter, name="county-commission-pages-datarange"),
    path('county_commission_pages_filter/', views.county_commission_pages_filter, name="county-commission-pages-ssn"),
    path('county_commission_pages_filter/', views.county_commission_pages_filter, name="county-commission-pages-aprvstatus"),
    path('county_commission_pages_filter/', views.county_commission_pages_filter, name="county-commission-pages-staff"),
    path('county_commission_pages_filter/', views.county_commission_pages_filter, name="county-commission-pages-approver"),
    
    path('county_substation_inspection_pages/', views.county_substation_inspection_pages, name="county-substation-inspection-pages"),
    path('county_substation_inspection_pages_filter/', views.county_substation_inspection_pages_filter, name="county-substation-inspection-pages-datarange"),
    path('county_substation_inspection_pages_filter/', views.county_substation_inspection_pages_filter, name="county-substation-inspection-pages-ssn"),
    path('county_substation_inspection_pages_filter/', views.county_substation_inspection_pages_filter, name="county-substation-inspection-pages-aprvstatus"),
    path('county_substation_inspection_pages_filter/', views.county_substation_inspection_pages_filter, name="county-substation-inspection-pages-staff"),
    path('county_substation_inspection_pages_filter/', views.county_substation_inspection_pages_filter, name="county-substation-inspection-pages-approver"),
    
    path('county_substation_maintenance_pages/', views.county_substation_maintenance_pages, name="county-substation-maintenance-pages"),
    path('county_substation_maintenance_pages_filter/', views.county_substation_maintenance_pages_filter, name="county-substation-maintenance-pages-datarange"),
    path('county_substation_maintenance_pages_filter/', views.county_substation_maintenance_pages_filter, name="county-substation-maintenance-pages-ssn"),
    path('county_substation_maintenance_pages_filter/', views.county_substation_maintenance_pages_filter, name="county-substation-maintenance-pages-aprvstatus"),
    path('county_substation_maintenance_pages_filter/', views.county_substation_maintenance_pages_filter, name="county-substation-maintenance-pages-staff"),
    path('county_substation_maintenance_pages_filter/', views.county_substation_maintenance_pages_filter, name="county-substation-maintenance-pages-approver"),
    
    path('county_pole_defects_pages/', views.county_pole_defects_pages, name="county-pole-defects-pages"),
    path('county_pole_defects_pages_filter/', views.county_pole_defects_pages_filter, name="county-pole-defects-pages-datarange"),
    path('county_pole_defects_pages_filter/', views.county_pole_defects_pages_filter, name="county-pole-defects-pages-ssn"),
    path('county_pole_defects_pages_filter/', views.county_pole_defects_pages_filter, name="county-pole-defects-pages-aprvstatus"),
    path('county_pole_defects_pages_filter/', views.county_pole_defects_pages_filter, name="county-pole-defects-pages-staff"),
    path('county_pole_defects_pages_filter/', views.county_pole_defects_pages_filter, name="county-pole-defects-pages-approver"),
    path('county_pole_defects_pages_filter/', views.county_pole_defects_pages_filter, name="county-pole-defects-pages-maintained"),


    path('substation_approve/<str:pk>/', views.substation_approve, name="substation-approve"),
    path('substation_print/<str:pk>/', views.substation_print, name="substation-print"),
    path('county_ssn/', views.county_ssn, name="county_ssn"),
    path('ssn_new/', views.ssn_new, name="ssn-new"),
    path('substation_edit/<str:pk>/', views.substation_edit, name="substation-edit"),
    path('substation_inspection_print/<str:pk>/', views.substation_inspection_print, name="substation-inspection-print"),

    # substation Inspections routes
    path('substation_new/<str:pk>/', views.substation_new, name="substation-new"),
    path('substation_my/', views.substation_my, name="substation-my"),
    path('substation_update/<str:pk>/', views.substation_update, name="substation-update"),
    path('global_substation_edit/<str:pk>/', views.global_substation_edit, name="global-substation-update"),
    path('substation_delete/<str:pk>/', views.substation_delete, name="substation-delete"),
    path('substations_pending_app/', views.substations_pending_app, name="substation-pending-apprv"),

    path('network_myinspections/', views.network_myinspections, name="network-myinspections"),

    path('commission_new/<str:pk>/', views.commission_new, name="commission-new"),
    path('commission_my/', views.commission_my, name="commission-my"),
    path('commission_update/<str:pk>/', views.commission_update, name="commission-update"),
    path('commission_delete/<str:pk>/', views.commission_delete, name="commission-delete"),
    path('commission_pending_app/', views.commission_pending_app, name="commission-pending-apprv"),
    path('commission_approve/<str:pk>/', views.commission_approve, name="commission-approve"),
    path('commission_print/<str:pk>/', views.commission_print, name="commission-print"),

    path('substation_maintenance_new/<str:pk>/', views.substation_maintenance_new, name="substation-maintenance-new"),
    path('substation_maintenance_my/', views.substation_maintenance_my, name="substation-maintenance-my"),
    path('substation_maintenance_delete/<str:pk>/', views.substation_maintenance_delete, name="substation-maintenance-delete"),
    path('substation_maintenance_update/<str:pk>/', views.substation_maintenance_update, name="substation-maintenance-update"),
    path('substation_maintenance_pending_app/', views.substation_maintenance_pending_app, name="substation-maintenance-pending-apprv"),
    path('substation_maintenance_approve/<str:pk>/', views.substation_maintenance_approve, name="substation-maintenance-approve"),
    path('substation_maintenance_print/<str:pk>/', views.substation_maintenance_print, name="substation-maintenance-print"),

    path('global_lvinspections/', views.global_lvinspections, name="global-lv"),
    path('search_by_ssn_global/', views.search_by_ssn_global, name="search-by-ssn-global"),
    path('global_substation_inspections/', views.global_substation_inspections, name="global-substation"),
    path('global_lv/', views.global_lv, name="global-lv-inspections"),
    path('global_lv_filter/', views.global_lv_filter, name="global-lv-search-rg"),
    path('global_lv_filter/', views.global_lv_filter, name="global-lv-search-cnty"),
    path('global_lv_filter/', views.global_lv_filter, name="global-lv-search-ssn"),
    path('global_lv_filter/', views.global_lv_filter, name="global-lv-search-date"),
    path('global_lv_filter/', views.global_lv_filter, name="global-lv-search-staff"),
    path('global_lv_filter/', views.global_lv_filter, name="global-lv-search-approver"),
    path('global_lv_today/', views.global_lv_today, name="global-lv-map-today"),

    #INSPECTOR
    path('inspector_analytics_dashbord/<str:pk>/', views.inspector_analytics_dashbord, name="inspector-analytics-dashboard"),
    path('todays_visibility/', views.todays_visibility, name="todays-visibility"),
    path('global_lv_useranalytics/', views.global_lv_useranalytics, name="global-lv-useranalytics"),


    path('global_lvmaintenance/', views.global_lvmaintenance, name="global-lvmaintenance"),
    path('global_lvmaintenance_filter/', views.global_lvmaintenance_filter, name="global-lvmaintenance-search-rg"),
    path('global_lvmaintenance_filter/', views.global_lvmaintenance_filter, name="global-lvmaintenance-search-county"),
    path('global_lvmaintenance_filter/', views.global_lvmaintenance_filter, name="global-lvmaintenance-search-ssn"),
    path('global_lvmaintenance_filter/', views.global_lvmaintenance_filter, name="global-lvmaintenance-search-staff"),
    path('global_lvmaintenance_filter/', views.global_lvmaintenance_filter, name="global-lvmaintenance-search-approver"),
    path('global_lvmaintenance_filter/', views.global_lvmaintenance_filter, name="global-lvmaintenance-search-date"),


    path('global_substation/', views.global_substation, name="global-substation"),
    path('global_substation_filter/', views.global_substation_filter, name="global-substation-search-rg"),
    path('global_substation_filter/', views.global_substation_filter, name="global-substation-search-county"),
    path('global_substation_filter/', views.global_substation_filter, name="global-substation-search-ssn"),
    path('global_substation_filter/', views.global_substation_filter, name="global-substation-search-staff"),
    path('global_substation_filter/', views.global_substation_filter, name="global-substation-search-approver"),
    path('global_substation_filter/', views.global_substation_filter, name="global-substation-search-date"),
    
    path('global_substation_maintenance/', views.global_substation_maintenance, name="global-substation-maintenance"),
    path('global_substation_maintenance_filter/', views.global_substation_maintenance_filter, name="global-substation-maintenance-search-rg"),
    path('global_substation_maintenance_filter/', views.global_substation_maintenance_filter, name="global-substation-maintenance-search-county"),
    path('global_substation_maintenance_filter/', views.global_substation_maintenance_filter, name="global-substation-maintenance-search-ssn"),
    path('global_substation_maintenance_filter/', views.global_substation_maintenance_filter, name="global-substation-maintenance-search-staff"),
    path('global_substation_maintenance_filter/', views.global_substation_maintenance_filter, name="global-substation-maintenance-search-approver"),
    path('global_substation_maintenance_filter/', views.global_substation_maintenance_filter, name="global-substation-maintenance-search-date"),
    
    path('global_ssnfailures/', views.global_ssnfailures, name="global-txfailure"),
    path('global_ssnfailures_filter/', views.global_ssnfailures_filter, name="global-ssnfailure-search-rg"),
    path('global_ssnfailures_filter/', views.global_ssnfailures_filter, name="global-ssnfailure-search-county"),
    path('global_ssnfailures_filter/', views.global_ssnfailures_filter, name="global-ssnfailure-search-ssn"),
    path('global_ssnfailures_filter/', views.global_ssnfailures_filter, name="global-ssnfailure-search-staff"),
    path('global_ssnfailures_filter/', views.global_ssnfailures_filter, name="global-ssnfailure-search-date"),
    path('global_ssnfailures_filter/', views.global_ssnfailures_filter, name="global-ssnfailure-search-approver"),
    
    path('global_commissions/', views.global_commissions, name="global-commissions"),
    path('global_commissions_filter/', views.global_commissions_filter, name="global-commissions-search-rg"),
    path('global_commissions_filter/', views.global_commissions_filter, name="global-commissions-search-county"),
    path('global_commissions_filter/', views.global_commissions_filter, name="global-commissions-search-ssn"),
    path('global_commissions_filter/', views.global_commissions_filter, name="global-commissions-search-staff"),
    path('global_commissions_filter/', views.global_commissions_filter, name="global-commissions-search-date"),
    path('global_commissions_filter/', views.global_commissions_filter, name="global-commissions-search-approver"),
    
    path('global_pole_defects/', views.global_pole_defects, name="global-pole-defects"),
    path('global_poledefects_filter/', views.global_poledefects_filter, name="global-pole-defects-search-rg"),
    path('global_poledefects_filter/', views.global_poledefects_filter, name="global-pole-defects-search-county"),
    path('global_poledefects_filter/', views.global_poledefects_filter, name="global-pole-defects-search-ssn"),
    path('global_poledefects_filter/', views.global_poledefects_filter, name="global-pole-defects-search-staff"),
    path('global_poledefects_filter/', views.global_poledefects_filter, name="global-pole-defects-search-date"),
    path('global_poledefects_filter/', views.global_poledefects_filter, name="global-pole-defects-search-approver"),
    path('global_poledefects_filter/', views.global_poledefects_filter, name="global-pole-defects-search-maintained"),
    
    path('global_ssn/', views.global_ssn, name="global_ssn"),
    path('global_sssn_search/', views.global_sssn_search, name="global-ssn-search"),
    
    path('region_lvinspections/', views.region_lvinspections, name="region-analysis"),

    path('ssn_print/', views.ssn_print, name='ssn-print'),

    path('load_checks_new/<str:pk>/', views.load_checks_new, name="load-checks-new"),
    path('loadchecks_my/', views.loadchecks_my, name="loadchecks-my"),
    path('loadchecks_update/<str:pk>/', views.loadchecks_update, name="loadchecks-update"),
    path('county_loadchecks_pages/', views.county_loadchecks_pages, name="county-loadchecks-pages"),
    path('county_loadchecks_pages_filter/', views.county_loadchecks_pages_filter, name="county-loadchecks-pages-datarange"),
    path('county_loadchecks_pages_filter/', views.county_loadchecks_pages_filter, name="county-loadchecks-pages-ssn"),
    path('county_loadchecks_pages_filter/', views.county_loadchecks_pages_filter, name="county-loadchecks-pages-aprvstatus"),
    path('county_loadchecks_pages_filter/', views.county_loadchecks_pages_filter, name="county-loadchecks-pages-staff"),
    path('county_loadchecks_pages_filter/', views.county_loadchecks_pages_filter, name="county-loadchecks-pages-approver"),

    path('global_loadchecks/', views.global_loadchecks, name="global-load-checks"),
    path('global_loadchecks_filter/', views.global_loadchecks_filter, name="global-loadchecks-search-rg"),
    path('global_loadchecks_filter/', views.global_loadchecks_filter, name="global-loadchecks-search-cnty"),
    path('global_loadchecks_filter/', views.global_loadchecks_filter, name="global-loadchecks-search-ssn"),
    path('global_loadchecks_filter/', views.global_loadchecks_filter, name="global-loadchecks-search-date"),
    path('global_loadchecks_filter/', views.global_loadchecks_filter, name="global-loadchecks-search-staff"),
    path('global_loadchecks_filter/', views.global_loadchecks_filter, name="global-loadchecks-search-approver"),
    path('global_loadchecks_filter/', views.global_loadchecks_filter, name="global-loadchecks-map-today"),




]