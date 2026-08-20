from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display =['name','cse_name','cse_stid','cse_mobile','cse_email','dtadd']
    
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display =['name','rm','rm_stid','rm_mobile','rm_email','dtadd']

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display =['name','county','incharge_name','incharge_stid','incharge_mobile','incharge_email','dtadd']

@admin.register(Meters)
class MetersAdmin(admin.ModelAdmin):
    list_display =['id','anomalytype','meternumber','county','sector','user','readings','asigned','dtadd']
    list_filter = ('anomalytype','status')
    search_fields = ['meternumber']