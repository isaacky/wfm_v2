from django.urls import path
from . import views

app_name = "hradmin"
urlpatterns = [
  path("inventory_groups_list", views.inventory_groups_list, name="inventory-groups-list"),
  path("invntory_group_new", views.inventory_group_new, name="inventory-group-new"),
  path('inventory_group_edit/<str:pk>/', views.inventory_group_edit, name='inventory-group-edit'),
  path("inventory_list", views.inventory_list, name="inventory-list"),
  path("invntory_new", views.inventory_new, name="inventory-new"),
]