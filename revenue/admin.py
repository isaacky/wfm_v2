from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Debtlist)
class DebtListAdmin(admin.ModelAdmin):
    list_display =['id','meterno','accountno','county','region','status','dtupdate']
    list_filter = ('status',)
    search_fields = ['meterno','county']
    
@admin.register(Revenuerecollection)
class RevenueCollectionAdmin(admin.ModelAdmin):
    list_display =['id','meterno','accountno','region','county','incms_status','collector','dtupdate']
    list_filter = ('incms_status',)
    search_fields = ['meterno','collector']