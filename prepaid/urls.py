from django.urls import path
from . import views

app_name = 'prepaid'
urlpatterns = [


  # tid
  path("star_tid_customers", views.star_tid_customers, name="star-tid-customers"),
  path("tid_search_meter/",views.tid_search_meter,name="tid-search-by-meter"),
  path("upgrade_tidmeter/<str:pk>/",views.upgrade_tidmeter,name="upgrade-tid"),
  path("mytidupgrade_list/", views.mytidupgrade_list, name="mytidupgrade-list"),
  path("upgraded_list/", views.upgraded_list, name="tidupgraded-list"),
  path("tid_upgrade_dashboard/", views.tid_upgrade_dashboard, name="tid-dashboard"),
  path("county_tid_useranalytics/", views.county_tid_useranalytics, name="tid-inspector-analytics"),
  path('tid_pending_upgrade/', views.tid_pending_upgrade, name='tid-export-pending'),
  path('tid_pending_upgrade_all/', views.tid_pending_upgrade_all, name='tid-export-pending-overall'),
  path('tid_export_inspected_region/', views.tid_export_inspected_region, name='tid-export-inspected-region'),


      
]