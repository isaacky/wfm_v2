from unicodedata import name
from django.urls import path
from . import views


urlpatterns = [
    # path('', views.loginPage, name='login'),
    path('changesector/', views.changesector, name='change-sector'),
    path('logout/', views.logoutUser, name='signout'),
    path('login/', views.loginuser, name='login'),
    path('changepassword/', views.change_password, name='change_password'),
    path('deactivateuser/<str:stid>/', views.deactivateuser, name='deactivate'),
    path('activateuser/<str:stid>/', views.activateuser, name='activate'),
    path('reset_password/<str:stid>/', views.reset_password, name='reset-password'),
    path('set_admin/<str:stid>/', views.set_admin, name='set-admin'),
    path('set_user/<str:stid>/', views.set_user, name='set-user'),
    path('update_user/<str:pk>/', views.update_user, name='update-user'),
    path('delete_user/<str:pk>/', views.delete_user, name='delete-user'),
    
    path('search_user/', views.search_user, name="search-by-stid"),

    path('register/', views.registerUser, name='register-user'),
    path('registeredusers/', views.registeredusers, name='registered-user'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    # path('change_password/', views.change_password, name='change_password'),

]
