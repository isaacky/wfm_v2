from django.urls import path
from . import views

app_name = "postpaid"
urlpatterns = [
    # Elsewedy Meter Replacement
    path("elsewedy_accounts", views.elsewedy_accounts, name="elsewedy-customers"),
    path("replace_elsewedy/<str:pk>/", views.replace_elsewedy, name="replace-elsewedy"),
    path("elsewedy_target_search_account/",views.elsewedy_target_search_account,name="elsewedy-target-search-account"),
    path("myelsewedy_list/", views.myelsewedy_list, name="myelsewedy-list"),
    path("elsewedy_replaced_list/", views.elsewedy_replaced_list, name="elsewedy-replaced-list"),
    path("view_replaced_elsewedy/<str:pk>/", views.view_replaced_elsewedy, name="view-replcd_elsewedy"),
    path("elsewedy_replaced_search_account/",views.elsewedy_replaced_search_account,name="elsewedy-replaced-search-account"),
    path("region_elsewedy_useranalytics/", views.region_elsewedy_useranalytics, name="region-elsewedy-useranalytics"),
    path("elsewedy_replacememt_dashboard/",views.elsewedy_replacememt_dashboard,name="elsewedy-replacememt-dashboard",),
    path('elsewedy_export_inspected_county/', views.elsewedy_export_inspected_county, name='elsewedy-export-inspected-county'),

    # RRI-

    path("retrofitting_target/", views.retrofitting_target, name="retrofitting-target"),
    path("retrofit_target_export/",views.retrofit_target_export,name="retrofit-target-export"),
    path("retrofit_dashboard/", views.retrofit_dashboard, name="retrofit-dashboard"),



    path("zerobills", views.zerobills, name="zerobills-list"),
    path("viewzerobill/<str:pk>/", views.viewzerobill, name="view-zerobill"),
    path("search_meter/", views.search_meter, name="search-by-meter"),
    path("viewresults", views.viewresults, name="results-list"),
    path("viewupload/<str:pk>/", views.viewuploaded, name="view-uploaded"),
    path("zerobillanalytics/", views.zerobillanalytics, name="analytics-report"),
    path("staffresolutions/", views.staffresolutions, name="staff-report"),
    path("globalreport/", views.globalreport, name="analytics-global"),
    path("regionalreport/", views.regionalreport, name="analytics-regional"),
    path("viewcounty/<str:pk>/", views.viewcounty, name="view-county"),
    path("viewuser/<str:pk>/", views.viewuser, name="view-user"),
    path("exportupload/", views.exportupload, name="export-uploads"),
    path(
        "search_meter_resolved/",
        views.search_meter_resolved,
        name="search-by-meter-resolved",
    ),
    path("kagua_connection", views.kagua_connection, name="kagua-connection"),
    path("search_connection/", views.search_connection, name="search-connection"),
    path("viewkagua/<str:pk>/", views.viewkagua, name="view-kagua"),
    path("myconnection/", views.myconnection, name="myconnection-list"),
    path("kaguaresultslist/", views.kaguaresultslist, name="kagua-results-list"),
    path(
        "kagua_analytics_global/",
        views.kagua_analytics_global,
        name="kagua-analytics-global",
    ),
    path(
        "kagua_inspector_analytics/",
        views.kagua_inspector_analytics,
        name="kagua-inspector-analytics",
    ),
    path("not_in_feeder/", views.not_in_feeder, name="not-in-feeder"),
    path(
        "kagua_regional_analytics/",
        views.kagua_regional_analytics,
        name="kagua-regional-analytics",
    ),
    path(
        "kagua_county_analysis/<str:pk>/",
        views.kagua_county_analysis,
        name="kagua-county-analysis",
    ),
    path(
        "export_kagua_connection/<str:pk>/",
        views.export_kagua_connection,
        name="export_kagua_connection",
    ),
    path(
        "export_kagua_connection_notinfeeder/<str:pk>/",
        views.export_kagua_connection_notinfeeder,
        name="export_kagua_connection_notinfeeder",
    ),
    path("kagua_dashboard", views.kagua_dashboard, name="kagua-dashboard"),
    path("threephase_target", views.threephase_target, name="threephase-target"),
    path("mythreepase_list/", views.mythreephase_list, name="mythreephase-list"),
    path(
        "inspect_threephase/<str:pk>/",
        views.inspect_threephase,
        name="inspect-threephase",
    ),
    path(
        "threephase_search_meter/",
        views.threephase_search_meter,
        name="threephase-search-by-meter",
    ),
    path(
        "threephase_search_itin/",
        views.threephase_search_itin,
        name="threephase-search-by-itin",
    ),
    path("search_by_sector/", views.search_by_sector, name="search-by-sector"),
    path(
        "threephase_target_export/",
        views.threephase_target_export,
        name="threephase-target-export",
    ),
    path("threephase_itins/<str:pk>/", views.threephase_itins, name="threephase-itins"),
    path(
        "threephase_results_list",
        views.threephase_results_list,
        name="threephase-results-list",
    ),
    path(
        "threephase_dashboard/", views.threephase_dashboard, name="threephase-dashboard"
    ),
    path(
        "threephase_inspector_analytics/",
        views.threephase_inspector_analytics,
        name="threephase-inspector-analytics",
    ),
    path(
        "threephase_regional_analytics/",
        views.threephase_regional_analytics,
        name="threephase-regional-analytics",
    ),
    path(
        "threephase_county_analysis/<str:pk>/",
        views.threephase_county_analysis,
        name="threephase-county-analysis",
    ),
    path(
        "export_threephase_connection/<str:pk>/",
        views.export_threephase_connection,
        name="export_threephase_connection",
    ),
    path(
        "threephase_export_uploads/",
        views.threephase_export_uploads,
        name="threephase_export-uploads",
    ),
    path(
        "view_uploaded_highend/<str:pk>/",
        views.view_uploaded_highend,
        name="view-uploaded-highend",
    ),
    path(
        "highend_anomolous_dashboard/",
        views.highend_anomolous_dashboard,
        name="highend-anomalous-dashboard",
    ),
    path(
        "highend_anomolous_unbilled/",
        views.highend_anomolous_unbilled,
        name="highend-anomalous-unbilled",
    ),
    path(
        "highend_anomolous_unbilled_export/",
        views.highend_anomolous_unbilled_export,
        name="unbilled-anomalous-export-highend",
    ),
    path(
        "highend_anomolous_faulty_export/",
        views.highend_anomolous_faulty_export,
        name="faulty-anomalous-export-highend",
    ),
    # telcos routes
    path("telcos_replc_target", views.telcos_replc_target, name="telcos-rplc_target"),
    path("telcos_replc_search_meter/", views.telcos_replc_search_meter, name="telcos-rplc_search-by-meter"),
    path("telcos_replc_search_siteid/",views.telcos_replc_search_siteid,name="telcos-rplc_search-by-siteid"),
    path("replace_telcos/<str:pk>/", views.replace_telcos, name="replace-telcos"),
    path("mytelcos_replc_list/", views.mytelcos_replc_list, name="mytelcos-replc_list"),
    path("view_replaced_telcos/", views.view_replaced_telcos, name="view-replc_telcos"),
    path("view_replaced_telcos_sf/", views.view_replaced_telcos_sf, name="view-replc_telcos_sf"),
    path("view_replaced_telcos_ad/", views.view_replaced_telcos_ad, name="view-replc_telcos_ad"),
    path("view_replaced_site/<str:pk>/", views.view_replaced_site, name="view-replaced_site"),
    path("collaborate/<str:pk>/", views.collaborate, name="collaborate"),
    path("replacement_print/<str:pk>/", views.replacement_print, name="replacement_print"),
    path("search_by_newmeter_replaced/",views.search_by_newmeter_replaced,name="search-by-newmeter-replaced",),
    path("search_by_siteid_replaced/",views.search_by_siteid_replaced,name="search-by-siteid-replaced",),
    path("telcos_repalcement_dashboard/", views.telcos_repalcement_dashboard, name="telcos-replacement-dahboard"),
    path("export_replacements_telcos/", views.export_replacements_telcos, name="export-replacements-telcos"),
    path("replacement_edit/<str:pk>/", views.replacement_edit, name="replacement_edit"),
    path("county_telcosrep_useranalytics/", views.county_telcosrep_useranalytics, name="county-replacement-analytics"),
    path(
        "telcos_repl_pending_export/",
        views.telcos_repl_pending_export,
        name="telcos-repl-pending-export",
    ),



    path("telcos_target", views.telcos_target, name="telcos-target"),
    path("inspect_telcos/<str:pk>/", views.inspect_telcos, name="inspect-telcos"),
    path(
        "telcos_search_meter/", views.telcos_search_meter, name="telcos-search-by-meter"
    ),
    path(
        "telcos_search_siteid/",
        views.telcos_search_siteid,
        name="telcos-search-by-siteid",
    ),
    path("mytelcos_list/", views.mytelcos_list, name="mytelcos-list"),
    path("viewtelcos/", views.viewtelcos, name="view-telcos"),
    path("viewsite/<str:pk>/", views.viewsite, name="view-site"),
    path(
        "telcos_export_uploads/",
        views.telcos_export_uploads,
        name="telcos_export-uploads",
    ),
    # path('telcos_dashboard/', views.telcos_dashboard, name='telcos-dashboard-atc'),
    path(
        "telcos_dashboard_atc/", views.telcos_dashboard_atc, name="telcos-dashboard-atc"
    ),
    path("tcos_dashboard/", views.tcos_dashboard, name="tcos-dahboard"),
    path(
        "telcos_inspector_analytics/",
        views.telcos_inspector_analytics,
        name="telcos-inspector-analytics",
    ),
    path(
        "search_meter_telcos_resolved/",
        views.search_meter_telcos_resolved,
        name="search-by-meter-telcos_resolved",
    ),
    path("telcos_tobe_billed/", views.telcos_tobe_billed, name="telcos-tobe-billed"),
    path(
        "telcos_export_uploads_tobebilled/",
        views.telcos_export_uploads_tobebilled,
        name="telcos_export-uploads-tobebilled",
    ),
    path("telcos_anomolous/", views.telcos_anomolous, name="telcos-anomolous"),
    path(
        "telcos_anomalous_export_uploads/",
        views.telcos_anomalous_export_uploads,
        name="telcos-anomalous-export",
    ),
    path(
        "publiclighting_target",
        views.publiclighting_target,
        name="publiclighting-target",
    ),
    path(
        "inspect_publiclighting/<str:pk>/",
        views.inspect_publiclighting,
        name="inspect-publiclighting",
    ),
    path(
        "mypubliclighting_list/",
        views.mypubliclighting_list,
        name="mypubliclighting-list",
    ),
    path("viewpubliclighting/", views.viewpubliclighting, name="view-publiclighting"),
    path(
        "publiclighting_search_meter/",
        views.publiclighting_search_meter,
        name="publiclighting-search-by-meter",
    ),
    path(
        "search_meter_publiclighting_resolved/",
        views.search_meter_publiclighting_resolved,
        name="search-by-meter-publiclighting_resolved",
    ),
    path("viewinspected/<str:pk>/", views.viewinspected, name="view-inspected"),
    path(
        "publiclighting_dashboard/",
        views.publiclighting_dashboard,
        name="publiclighting-dashboard",
    ),
    path(
        "publiclighting_inspector_analytics/",
        views.publiclighting_inspector_analytics,
        name="publiclighting-inspector-analytics",
    ),
    path(
        "publiclighting_direct/",
        views.publiclighting_direct,
        name="publiclighting-direct",
    ),
    path(
        "publiclighting_target_export/",
        views.public_lighting_target_export,
        name="publiclighting-target-export",
    ),
    path(
        "exportupload_publiclighting/",
        views.exportupload_publiclighting,
        name="export-uploads-publiclighting",
    ),
    path(
        "exportupload_publiclighting_wothoutmeter/",
        views.exportupload_publiclighting_wothoutmeter,
        name="export-uploads-publiclighting-notin-system",
    ),
    path(
        "publiclighting_not_in_target/",
        views.publiclighting_not_in_target,
        name="publiclighting-noton-target",
    ),
    path(
        "publiclighting_anomolous_dashboard/",
        views.publiclighting_anomolous_dashboard,
        name="publiclighting-anomalous-dashboard",
    ),
    path(
        "publiclighting_anomolous_unbilled/",
        views.publiclighting_anomolous_unbilled,
        name="publiclighting-anomalous-unbilled",
    ),
    # LP
    path("lp_target", views.lp_target, name="lp-target"),
    path("lp_search_srn/", views.lp_search_srn, name="lp-search-by-srn"),
    path("lp_search_meterno/", views.lp_search_meterno, name="lp-search-by-meterno"),
    path("inspect_lp/<str:pk>/", views.inspect_lp, name="inspect-lp"),
    path("my_lp/", views.my_lp, name="my-lp"),
    path("lp_viewinspected/", views.lp_viewinspected, name="lp-view-inspeted"),
    path(
        "search_meter_lp_inspected/",
        views.search_meter_lp_inspected,
        name="search-by-meter-lp-inspected",
    ),
    path(
        "view_lp_inspeted/<str:pk>/", views.view_lp_inspeted, name="view-lp-inspected"
    ),
    path("lp_dashboard/", views.lp_dashboard, name="lp-dashboard"),
    path("exportupload_lp/", views.exportupload_lp, name="export-uploads-lp"),
    path("lp_not_in_target/", views.lp_not_in_target, name="lp-noton-target"),
    path(
        "lp_inspector_analytics/",
        views.lp_inspector_analytics,
        name="lp-inspector-analytics",
    ),
    # LP NEW
    path("lp_new_target", views.lp_new_target, name="lp-new-target"),
    path("lp_new_inspected", views.lp_new_inspected, name="lp-new-inspected"),
    path("lp_new_inspected_my", views.lp_new_inspected_my, name="lp-new-inspected-my"),
    path("lp_new_search_srn/", views.lp_new_search_srn, name="lp-new-search-by-srn"),
    path("lp_new_search_meterno/", views.lp_new_search_meterno, name="lp-new-search-by-meterno"),
    path("lp_new_search_srn_inspected/", views.lp_new_search_srn_inspected, name="lp-new-search-by-srn-inspected"),
    path("lp_new_search_srn_inspected_my/", views.lp_new_search_srn_inspected_my, name="lp-new-search-by-srn-inspected-my"),
    path("lp_new_search_meterno_inspected/", views.lp_new_search_meterno_inspected, name="lp-new-search-by-meterno-inspected"),
    path("lp_new_search_meterno_inspected_my/", views.lp_new_search_meterno_inspected_my,
         name="lp-new-search-by-meterno-inspected-my"),

    path("lp_new_inspections/<str:pk>/", views.lp_new_inspections, name="lp-new-inspection"),
    path("lp_update_inspection/<str:pk>/", views.lp_update_inspection, name="lp-update-inspection"),
    path("lp_customer_data/<str:pk>/", views.lp_customer_data, name="lp-customerdata-inspection"),
    path("lp_sealing_data/<str:pk>/", views.lp_sealing_data, name="lp-sealing-inspection"),
    path("lp_ctvt_data/<str:pk>/", views.lp_ctvt_data, name="lp-ctvt-inspection"),
    path("lp_zeratest_data/<str:pk>/", views.lp_zeratest_data, name="lp-zeratest-inspection"),
    path("lp_currents_data/<str:pk>/", views.lp_currents_data, name="lp-current-inspection"),
    path("lp_mreadings_data/<str:pk>/", views.lp_mreadings_data, name="lp-mreadings-inspection"),
    path("lp_otherinfo_data/<str:pk>/", views.lp_otherinfo_data, name="lp-otherinfo-inspection"),
    path("finalsubmission/<str:pk>/", views.finalsubmission, name="lp-finalsubmission"),
    path("inspection_delete/<str:pk>/", views.inspection_delete, name="inspection-delete"),
    path("inspection_print/<str:pk>/", views.inspection_print, name="inspection-print"),
    path("lp_new_inspector_analytics/",views.lp_new_inspector_analytics,name="lp-new-inspector-analytics"),
    path("lp_new_not_in_target/",views.lp_new_not_in_target,name="lp-not-in-target"),
    path("lp_2024_analytics/",views.lp_2024_analytics,name="lp-analytics"),


    # Domestic Customers inspections
    path("domestic_customers", views.domestic_customers, name="domestic-customers"),
    path("dc_search_meter/", views.dc_search_meter, name="dc-search-by-meter"),
    path("inspect_dc/<str:pk>/", views.inspect_dc, name="inspect-dc"),
    path("my_dc/", views.my_dc, name="my-dc"),
    path("dc_viewinspected/", views.dc_viewinspected, name="dc-viewinspected"),
    path(
        "search_meter_dc_inspected/",
        views.search_meter_dc_inspected,
        name="search-by-meter-dc-inspected",
    ),
    path(
        "view_dc_inspeted/<str:pk>/", views.view_dc_inspeted, name="view-dc-inspected"
    ),
    path("dc_dashboard/", views.dc_dashboard, name="dc-dashboard"),
    path("dc_useranalytics/", views.dc_useranalytics, name="dc-useranalytics"),
    path(
        "dc_export_uploads/",
        views.dc_export_uploads,
        name="dc-export-uploads",
    ),
    path(
        "dc_anomolous_dashboard/",
        views.dc_anomolous_dashboard,
        name="dc-anomalous-dashboard",
    ),
    path(
        "dc_anomolous_unbilled/",
        views.dc_anomolous_unbilled,
        name="dc-anomalous-unbilled",
    ),
    path(
        "dc_anomolous_unbilled_export/",
        views.dc_anomolous_unbilled_export,
        name="unbilled-anomalous-export",
    ),
    path(
        "dc_anomolous_faulty_export/",
        views.dc_anomolous_faulty_export,
        name="faulty-anomalous-export",
    ),
    path(
        "dc_not_in_target/",
        views.dc_not_in_target,
        name="dc-not-in-target",
    ),
    # GENERATING STATIONS
    path("generation_stations/", views.generation_stations, name="generation-stations"),
    path(
        "dc_search_plantname/", views.dc_search_plantname, name="dc-search-by-plantname"
    ),
    path("inspect_genstn/<str:pk>/", views.inspect_genstn, name="inspect-genstn"),
    path("my_genstns/", views.my_genstns, name="my-genstns"),
    path(
        "genstn_viewinspected/", views.genstn_viewinspected, name="genstn-viewinspected"
    ),
    path(
        "view_genstn_inspeted/<str:pk>/",
        views.view_genstn_inspeted,
        name="view-genstn-inspected",
    ),
    path(
        "generation_stns_dashboard/",
        views.generation_stns_dashboard,
        name="generation-dashboard",
    ),
    
    # zerobills routes
    path("zerobills_target", views.zerobills_target, name="zerobills_target"),
    path("zerobills_search_meter/", views.zerobills_search_meter, name="zerobills-search-by-meter"),
    path("zerobill_confirm/<str:pk>/", views.zerobill_confirm, name="confirm-zerobill"),
    path("myzerobills_list/", views.myzerobills_list, name="myzerobills-list"),
    path("zerobills_confirmed_list/", views.zerobills_confirmed_list, name="view-confirmed-zerobill"),
    path("view_confirmed_meter/<str:pk>/", views.view_confirmed_meter, name="view-confirmed-meter"),
    path("zerobills_targets_export_uploads/",views.zerobills_targets_export_uploads,name="zerobills_export-uploads",
    ),
    path("zerobills_export_uploads/",views.zerobills_export_uploads,name="zerobills_confirmed_export-uploads",
    ),
    path("zerobills__all_export_uploads/",views.zerobills__all_export_uploads,name="zerobills_all_confirmed_export-uploads",
    ),
    path("zerobill_inspector_analytics/",views.zerobill_inspector_analytics,name="zerobills_useranalytics",
    ),
    path(
        "zerobill_confirmation_dashboard/",
        views.zerobill_confirmation_dashboard,
        name="zerobills-confirmation-dashboard",
    ),
    path(
        "zerobills_search_account/",
        views.zerobills_search_account,
        name="zerobills-search-by-account",
    ),
    path(
        "view-zerobill-county/<str:pk>/",
        views.view_zerobill_county,
        name="view-zerobill-county",
    ),
     # Anomalous Routes
    path("anomalous_target", views.anomalous_target, name="anomalous-target"),
    path(
        "anomalous_search_meter/",
        views.anomalous_search_meter,
        name="anomalous-search-by-meter",
    ),
    path(
        "anomalous_replace_faulty/<str:pk>/",
        views.anomalous_replace_faulty,
        name="anomalous-replace-faulty",
    ),
    path("myanomalous_list/", views.myanomalous_list, name="myanomalous-list"),
    path(
        "anomaly_resolved_list/",
        views.anomaly_resolved_list,
        name="view-resolved-anomaly",
    ),
    path(
        "anomalous_inspector_analytics/",
        views.anomalous_inspector_analytics,
        name="anomalous-useranalytics",
    ),
    path(
        "anomalous_dashboard/",
        views.anomalous_dashboard,
        name="anomalous-dashboard",
    ),
    path(
        "anomalous_export_uploads/",
        views.anomalous_export_uploads,
        name="anomalous_target_export-uploads",
    ),
    path(
        "anomalous_export_resolved_county/",
        views.anomalous_export_resolved_county,
        name="anomalous_resolved_export-uploads-county",
    ),
    path(
        "anomalous_export_resolved_all/",
        views.anomalous_export_resolved_all,
        name="anomalous_resolved_export-uploads-all",
    ),
    path(
        "hexing_pending_county/",
        views.hexing_pending_county,
        name="hexing_pending_replacement_county",
    ),

    path('amcorder_search', views.amcorder_search, name='amcorder-search'),
    path('search_by_lp/', views.search_by_lp, name="search-by-lp"),
    path("amcorder_inspect/<str:pk>/", views.amcorder_inspect, name="amcorder-inspect"),
    path("amcorder_install/<str:pk>/", views.amcorder_install, name="amcorder-install"),
    path("amcorder_retrieve/<str:pk>/", views.amcorder_retrieve, name="amcorder-retrieve"),

    path("amcorder_analysis/<str:pk>/", views.amcorder_analysis, name="amcorder-analysis"),
    path("amcorder/<int:pk>/pdf/", views.amcorder_pdf, name="amcorder-pdf"),
    path("amcorder_installed/", views.amcorder_installed, name="amcorder-installed"),
    path("amcorder_myinstalled/", views.amcorder_myinstalled, name="amcorder-my-installed"),
]
