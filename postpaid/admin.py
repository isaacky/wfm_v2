from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Zerobillresolved)
class ZerobillResolvedAdmin(admin.ModelAdmin):
    list_display =['id','meterno','accountno','region','county','status','dtupdate']
    list_filter = ('status',)
    search_fields = ['meterno']
    
@admin.register(Zerobills)
class ZerobillsAdmin(admin.ModelAdmin):
    list_display =['id','meterno','accountno','region','county','status','dtadd','dtupdate']
    list_filter = ('status',)
    search_fields = ['meterno']

@admin.register(Feeder)
class FeederAdmin(admin.ModelAdmin):
    list_display =['id','name']
    search_fields = ['name']

@admin.register(Kaguaconnection)
class KaguaconnectionAdmin(admin.ModelAdmin):
    list_display =['id','meterno','accountno','customer_name','type','status','substation','feeder']
    list_filter = ('status',)
    search_fields = ['meterno','feeder']

@admin.register(Threephase_target)
class Threephase_inspectionAdmin(admin.ModelAdmin):
    list_display =['id','meterno','accountno','customer_name','county','region','status']
    list_filter = ('status',)
    search_fields = ['meterno','accountno']

@admin.register(Threephase_inspection)
class Threephase_inspectionAdmin(admin.ModelAdmin):
    list_display =['id','meterno','accountno','meteringstatus','installationstatus','county','region']
    list_filter = ('meteringstatus','installationstatus')
    search_fields = ['meterno','accountno']

@admin.register(Telcos_target)
class Telcos_targetAdmin(admin.ModelAdmin):
    list_display =['id','meterno','accountno','county','region','status']
    list_filter = ('status',)
    search_fields = ['meterno','accountno']

@admin.register(Largepower_accounts_2024)
class LP_AccountsAdmin(admin.ModelAdmin):
    list_display =['id','meterno','accountno','customer_name','county','region','status']
    list_filter = ('status',)
    search_fields = ['meterno','accountno']

# @admin.register(Lp_new_inspection)
# class LP_AccountsNewInspectionAdmin(admin.ModelAdmin):
#     list_display =['id','lp','meterno','inspectedby']
#     # list_filter = ('status',)
#     search_fields = ['lp']

@admin.register(Lp_inspect_customerData)
class LP_CustomerDataInspectionAdmin(admin.ModelAdmin):
    list_display =['id','lp','type_of_industry','smart_meter_i','inspectedby']
    # list_filter = ('status',)
    search_fields = ['lp']

@admin.register(LP_inspection_sealing)
class LP_SealingInspectionAdmin(admin.ModelAdmin):
    list_display =['id','lp','inspectedby']
    # list_filter = ('status',)
    search_fields = ['lp']

@admin.register(Lp_inspect_ctvt)
class LP_CTVTInspectionAdmin(admin.ModelAdmin):
    list_display =['id','lp','inspectedby']
    # list_filter = ('status',)
    search_fields = ['lp__lp__meterno']

@admin.register(Lp_inspect_zeratest)
class LP_ZeraTestInspectionAdmin(admin.ModelAdmin):
    list_display =['id','lp','inspectedby']
    # list_filter = ('status',)
    search_fields = ['lp__lp__meterno']

@admin.register(LP_meter_readings)
class LP_ReadingsInspectionAdmin(admin.ModelAdmin):
    list_display =['id','lp','inspectedby']
    # list_filter = ('status',)
    search_fields = ['lp__lp__meterno']

@admin.register(Lp_inspect_info)
class LP_InfoInspectionAdmin(admin.ModelAdmin):
    list_display =['id','lp','inspectedby']
    # list_filter = ('status',)
    search_fields = ['lp__lp__meterno']


@admin.register(Lp_typeofindustry)
class TypeOfIndustryAdmin(admin.ModelAdmin):
    list_display =['id','name']
    search_fields = ['name']

@admin.register(RetrofitAccounts)
class RetrofitsAdmin(admin.ModelAdmin):
    list_display =['id','meterno','accountno','itin','county','region']
    search_fields = ['meterno']

# admin.site.register(Lp_inspect_ctvt, LP_CTVTInspectionAdmin)