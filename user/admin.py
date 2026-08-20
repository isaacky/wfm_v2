from django.contrib import admin
from .models import Account, UserProfile
# Register your models here.
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display =['stid','email','name','is_admin','is_active','is_staff','is_superuser','mobile']
    list_filter = ('is_active','is_staff')
    search_fields = ['stid']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display =['id','user','staffname','region','county','profiletype','campaign']
    list_filter = ('profiletype','campaign')
    search_fields = ['user']