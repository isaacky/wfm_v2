from django.urls import path
from . import views

app_name = "mediumv"
urlpatterns = [
    path("feeder_search", views.feeder_search, name="feeder-search"),
    path(
        "feeder_search_results",
        views.feeder_search_results,
        name="feeder-search-results",
    ),
    path("my_mvinspections/", views.my_mvinspections, name="mv-inspections-my"),
    path("mvinspection_new/<str:pk>/", views.mvinspection_new, name="mvinspection-new"),
    path(
        "mvinspection_update/<str:pk>/",
        views.mvinspection_update,
        name="mvinspection-update",
    ),
    path(
        "mvinspection_delete/<str:pk>/",
        views.mvinspection_delete,
        name="mvinspection-delete",
    ),
    path(
        "mvmaintenance_update/<str:pk>/",
        views.mvmaintenance_update,
        name="mvmaintenance-update",
    ),
    path(
        "mvmaintenance_delete/<str:pk>/",
        views.mvmaintenance_delete,
        name="mvmaintenance-delete",
    ),
    path("feeder_dashboard/<str:pk>/", views.feeder_dashboard, name="feeder-dashboard"),
    path("mvpoledefects_new/", views.mvpoledefects_new, name="mvpoledefects-new"),
    path(
        "mediumv_delete_pole/<str:pk>/",
        views.mediumv_delete_pole,
        name="mediumv-delete-pole",
    ),
    path(
        "county_mvinspections_list/",
        views.county_mvinspections_list,
        name="county-mvinspections",
    ),
    path(
        "county_mvinspections_dashboard/",
        views.county_mvinspections_dashboard,
        name="county-mvinspections-dashbord",
    ),
    path(
        "county_mvmaintenance_list/",
        views.county_mvmaintenance_list,
        name="county-mvmaintenance",
    ),
    path(
        "county_mvpending_list/", views.county_mvpending_list, name="county-mv-pending"
    ),
    path(
        "county_mvmaintenancepending_list/",
        views.county_mvmaintenancepending_list,
        name="county-mvmaintenance-pending",
    ),
    path(
        "mvinspection_approve/<str:pk>/",
        views.mvinspection_approve,
        name="mvinspection-approve",
    ),
    path(
        "mvmaitenance_approve/<str:pk>/",
        views.mvmaitenance_approve,
        name="mvmaitenance-approve",
    ),
    path(
        "mvinspection_print/<str:pk>/",
        views.mvinspection_print,
        name="mvinspection-print",
    ),
    path(
        "mvmaintenance_print/<str:pk>/",
        views.mvmaintenance_print,
        name="mvmaintenance-print",
    ),
    path(
        "mvinspections_approved/<str:pk>/",
        views.mvinspections_approved,
        name="mvinspections-approved",
    ),
    path(
        "inspected_sections/<str:pk>/",
        views.inspected_sections,
        name="sections-inspected",
    ),
    path("county_analysis/", views.county_analysis, name="county-analysis"),
    path("mvmaintenance_my/", views.mvmaintenance_my, name="mvmaintenance-my"),
    path(
        "mvmaintenance_new/<str:pk>/", views.mvmaintenance_new, name="mvmaintenance-new"
    ),
    path('poledefects_list/<str:pk>/', views.poledefects_list, name="poledefects-list"),
    path('poledefects_maintenance_new/<str:pk>/', views.poledefects_maintenance_new, name="poledefects-maintain-new"),
    path('poledefects_maintenance_my/', views.poledefects_maintenance_my, name="poledefects-maintenance-my"),
    path('poledefects_maintain_update/<str:pk>/', views.poledefects_maintain_update, name="poledefect-maintainance-update"),
    path("polemaintenance_delete/<str:pk>/",views.polemaintenance_delete,name="polemaintenance-delete"),
    
    path('global_mv/', views.global_mv, name="global-mv"),
    path('global_mv_filter/', views.global_mv_filter, name="global_mv-search-rg"),
    path('global_mv_filter/', views.global_mv_filter, name="global_mv-search-county"),
    path('global_mv_filter/', views.global_mv_filter, name="global_mv-search-feeder"),
    path('global_mv_filter/', views.global_mv_filter, name="global_mv-search-staff"),
    path('global_mv_filter/', views.global_mv_filter, name="global_mv-search-date"),
    path('global_mv_filter/', views.global_mv_filter, name="global_mv-approver"),

    path('global_mv_maintenance/', views.global_mv_maintenance, name="global-mv-maintenance"),
    path('global_mv_maintenance_filter/', views.global_mv_maintenance_filter, name="global_mv-maintenance-search-rg"),
    path('global_mv_maintenance_filter/', views.global_mv_maintenance_filter, name="global_mv-maintenance-search-county"),
    path('global_mv_maintenance_filter/', views.global_mv_maintenance_filter, name="global_mv-maintenance-search-feeder"),
    path('global_mv_maintenance_filter/', views.global_mv_maintenance_filter, name="global_mv-maintenance-search-staff"),
    path('global_mv_maintenance_filter/', views.global_mv_maintenance_filter, name="global_mv-maintenance-search-date"),
    path('global_mv_maintenance_filter/', views.global_mv_maintenance_filter, name="global_mv-maintenance-approver"),
]
