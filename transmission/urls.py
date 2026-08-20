from django.urls import path
from . import views

app_name = "transmission"
urlpatterns = [
    path('txlines_search', views.txlines_search, name='txlines-search'),
    path('search_by_txline/', views.search_by_txline, name="search-by-txline"),
    path("txline_inspect/<str:pk>/", views.txline_inspect, name="towerinspection-new"),

    path('towerinspection_update_location/<str:pk>/', views.towerinspection_update_location,
         name="tower-update-location"),
    path('towerinspection_update_insulators/<str:pk>/', views.towerinspection_update_insulators,
         name="tower-update-insulators"),

    path('towerinspection_update_conductors/<str:pk>/', views.towerinspection_update_conductors,
         name="tower-update-conductors"),

    path('towerinspection_update_foundation/<str:pk>/', views.towerinspection_update_foundation,
         name="tower-update-foundation"),

    path('towerinspection_update_earth/<str:pk>/', views.towerinspection_update_earth, name="tower-update-earth"),

    path('towerinspection_update_finalize/<str:pk>/', views.towerinspection_update_finalize,
         name="tower-update-finalize"),
    # path('txline_inspect', views.txline_inspect, name="towerinspection-new"),
    path('trans_dashboard_my', views.trans_dashboard_my, name="trans-dashboard-my"),
    path('tower_delete/<str:pk>/', views.tower_delete, name="tower-delete"),
    path('towerinspection_update/<str:pk>/', views.towerinspection_update, name="tower-update"),
    path('tower_location_update/<str:pk>/', views.tower_location_update, name="tower-location-update"),

    path('global_lv/', views.global_lv, name="global-transmission"),
    path('transmission_dashboard/', views.transmission_dashboard, name="transmission-dashboard"),
    path('tower_dashboard/', views.tower_dashboard, name="tower-dashboard"),

    path('tower_approve/<str:pk>/', views.tower_approve, name="tower-approve"),
]
