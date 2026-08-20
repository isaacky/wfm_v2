from django.urls import path
from . import views

app_name = "transdist"
urlpatterns = [
    path("transdist_stations", views.transdist_stations, name="transdist-stations"),
    path("transdist_new/<str:pk>/", views.transdist_new, name="new-inspection"),
    path("inspections_my/", views.inspections_my, name="inspections-my"),
    path("transdist_update/<str:pk>/", views.transdist_update, name="transdist-update"),
    path("search_by_ssn/", views.search_by_ssn, name="search-by-ssn"),
    path("search_by_ssn_inspected/", views.search_by_ssn_inspected, name="search-by-ssn-inspected"),
    path(
        "feederinspection_new/<str:pk>/",
        views.feederinspection_new,
        name="feederinspection-new",
    ),
    path(
        "feeder_outgoing_inspection_new/<str:pk>/",
        views.feeder_outgoing_inspection_new,
        name="feederinspection-outgoing-new",
    ),
    path(
        "powertxinspection_new/<str:pk>/",
        views.powertxinspection_new,
        name="powertxinspection-new",
    ),
    path(
        "auxtxinspection_new/<str:pk>/",
        views.auxtxinspection_new,
        name="auxtxinspection-new",
    ),
    path(
        "transdist_inspections/",
        views.transdist_inspections,
        name="transdist-inspections",
    ),
    path(
        "inspection_detail/<str:pk>/",
        views.inspection_detail,
        name="inspection-detail",
    ),
    path(
        "transdist_dashboard/",
        views.transdist_dashboard,
        name="transdist-dashboard",
    ),
    path(
        "transdist-delete/<str:pk>/",
        views.transdist_delete,
        name="transdist-delete",
    ),
    path(
        "incomer_delete/<str:pk>/",
        views.incomer_delete,
        name="incomer-delete",
    ),
    path(
        "powertx_delete/<str:pk>/",
        views.powertx_delete,
        name="powertx-delete",
    ),
    path(
        "outgoing_delete/<str:pk>/",
        views.outgoing_delete,
        name="outgoing-delete",
    ),
    path(
        "auxtx_delete/<str:pk>/",
        views.auxtx_delete,
        name="auxtx-delete",
    ),

    # 66 KV INSPECTIONS
    path("sixtysix_customers", views.sixtysix_customers, name="sixtysix-customers"),
    path("sistysix_search_by_meter/", views.sistysix_search_by_meter, name="sistysix-search-by-meter"),
    path("sixty_six_not_in_target/", views.sixty_six_not_in_target, name="sixty-six-not-in-target"),
    path("sixty_six_inspection/<str:pk>/", views.sixty_six_inspection, name="new-sixtysix-inspection"),
    path("sixtysix_update/<str:pk>/", views.sixtysix_update, name="sixtysix-update"),
    path("sixtysix_update_substation/<str:pk>/", views.sixtysix_update_substation, name="sixtysix-update-substation"),
    path("sixtysix_update_meter/<str:pk>/", views.sixtysix_update_meter, name="sixtysix-update-meter"),
    path("sixtysix_update_sealing/<str:pk>/", views.sixtysix_update_sealing, name="sixtysix-update-sealing"),
    path("sixtysix_update_testequipment/<str:pk>/", views.sixtysix_update_testequipment, name="sixtysix-update-equpment"),
    path("sixtysix_update_current/<str:pk>/", views.sixtysix_update_current, name="sixtysix-update-current"),
    path("sixtysix_update_ctvt_redphase/<str:pk>/", views.sixtysix_update_ctvt_redphase, name="sixtysix-update-ctvt_redphase"),
    path("sixtysix_update_ctvt_yellowphase/<str:pk>/", views.sixtysix_update_ctvt_yellowphase, name="sixtysix-update-ctvt_yellowphase"),
    path("sixtysix_update_ctvt_bluephase/<str:pk>/", views.sixtysix_update_ctvt_bluephase, name="sixtysix-update-ctvt_bluephase"),
    path("sixtysix_update_meter_readings/<str:pk>/", views.sixtysix_update_meter_readings, name="sixtysix-update-meter-readings"),
    path("sixtysix_update_otherinfo/<str:pk>/", views.sixtysix_update_otherinfo, name="sixtysix-update-otherinfo"),
    path("sixtysix_update_finalsubmission/<str:pk>/", views.sixtysix_update_finalsubmission, name="sixtysix-update-otherfinalsubmission"),
    path("sixtysix_print/<str:pk>/", views.sixtysix_print, name="sixtysix-print"),
    path("sixtysix_delete/<str:pk>/", views.sixtysix_delete, name="sixtysix-delete"),

]
