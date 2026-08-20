from django.urls import path
from . import views

app_name = 'revenue'
urlpatterns = [
  path('debtlist', views.debtlist, name='debt-list'),
  path('debtlist_by_itin', views.debtlist_by_itin, name='debt-list-itin'),
  path('debtlist_by_zone', views.debtlist_by_zone, name='debt-list-zone'),
  path('viewdebtaccount/<str:pk>/', views.viewdebtaccount, name='view-debtaccount'),
  path('viewdebtlistitins/<str:pk>/', views.viewdebtlistitins, name='debtlist-itins'),
  path('viewresults', views.viewresults, name='results-list'),
  path('collections_dashboard/', views.collections_dashboard, name="analytics-global"),
  path('regionalreport/', views.regionalreport, name="analytics-regional"),
  path('viewcounty/<str:pk>/', views.viewcounty, name='view-county'),
  path('viewuser/<str:pk>/', views.viewuser, name='view-user'),
  path('search_itin/', views.search_itin, name="search-by-itin"),
  path('search_asigned_itin/', views.search_asigned_itin, name="search-asigned_by-itin"),
  path('search_meter/', views.search_meter, name="search-by-meter"),
  path('search_asigned_meter/', views.search_asigned_meter, name="search-asigned_by-meter"),
  path('search_collected_meter/', views.search_collected_meter, name="search-collected-meter"),
  path('export_county_debtlist/', views.export_county_debtlist, name='export-county-debtlist'),
  path('my_actioned/', views.my_actioned, name='achievement-list'),
  path("county_collector_useranalytics/", views.county_collector_useranalytics, name="county-collector-useranalytics"),
  path('collections_dashboard_region/<str:pk>/', views.collections_dashboard_region, name='collections-dashboard-region'),
  path('asign_accounts/', views.asign_accounts, name='asign-accounts'),
  path('asigned_accounts/', views.asigned_accounts, name='county-asignments'),
  path('debt_list_mytarget/', views.debt_list_mytarget, name='debt-list-mytarget'),
  path('export_my_debtlist/', views.export_my_debtlist, name='export-my-debtlist'),
  path('search_by_staff_number/', views.search_by_staff_number, name="search-by-staff-number"),
  path('exportupload_all_collections/', views.exportupload_all_collections, name='export-uploads-all'),
  path('exportupload/', views.exportupload, name='export-uploads-seven'),
  path('search_itin_itn/', views.search_itin_itn, name="search-by-itin-itin"),
  path('search_zone_zone/', views.search_zone_zone, name="search-by-zone-zone"),
  path('asign_accounts_itin/', views.asign_accounts_itin, name='asign-accounts-itin'),
  path('asign_accounts_zone/', views.asign_accounts_zone, name='asign-accounts-zone'),


]