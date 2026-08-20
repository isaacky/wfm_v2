from django.db import models
from main.models import County,Region, Da,Feeder, Feeder_sections
from user.models import Account, UserProfile
from datetime import datetime

class Mvinspection(models.Model):
    APRVKEY = (
        ('', '----CHOOSE THE STATUS----'),
        ('approved', 'APPROVED'),
        ('declined', 'DECLINED'),
    )
    feeder_section = models.ForeignKey(Feeder_sections, on_delete=models.SET_NULL, null=True, related_name='mv_feeder_section')
    feeder = models.ForeignKey(Feeder,on_delete=models.SET_NULL, null=True, related_name='mv_feeder')
    no_poleswithoutstays = models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_rottentxstructure =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_leaningtxstructure =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_sagstoretention =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_sectionstodoublejumper = models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_replacefusemounts =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_bypassedhtfuses =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_spurtaplins = models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_faultyabswitces =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_installabswitces = models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_overhangingtrees =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_tracemaint = models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_upratingconductors =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_autoclosures = models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_autoclosuresfaulty =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_faultyhvcable = models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_structureswithouttx = models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_jumpercableswithoutlugs =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_disconnsurged = models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_txmissingearthing =   models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_ssnnumberless =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_wayleaveinfrng = models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_leakingpininsul = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_leakingsuspinsul = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    save_status = models.BooleanField(default=False, db_index=True)
    aprv_status = models.BooleanField(default=False, db_index=True)
    aprv_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='mv_approved_by')
    aprv_notes = models.TextField(blank=True, null=True)
    aprv_dt = models.DateField(blank=True, null=True)
    aprv_key = models.CharField(max_length=10, choices=APRVKEY, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='mv_inspected_by')
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='mvinspection_county')

    def __str__(self):
        return self.feeder_section.name

class Mv_poledefects(models.Model):
    DEFECTTYPE = (
        ('', '----CHOOSE THE STATUS----'),
        ('rotten', 'ROTTEN'),
        ('leaning', 'LEANING'),
        ('midspanpole', 'MIDSPAN POLE'),
        ('brockenpole', 'BROKEN POLE'),
    )
    POLEFITTING = (
        ('', '----CHOOSE THE STATUS----'),
        ('linepole', 'LINE POLE'),
        ('sectionpole', 'SECTION POLE'),
    )
    TYPEPOLE = (
        ('', '----CHOOSE THE STATUS----'),
        ('10mwooden', '10m WOODEN'),
        ('11mwooden', '11m WOODEN'),
        ('12mwooden', '12m WOODEN'),
        ('10mconcrete', '10m CONCRETE'),
        ('11mconcrete', '11m CONCRETE'),
        ('12mconcrete', '12m CONCRETE'),
        ('14mconcrete', '14m CONCRETE'),
    )
    mvinspection = models.ForeignKey(Mvinspection, on_delete=models.SET_NULL, null=True, related_name='poledefects_mvinspection')
    feeder = models.ForeignKey(Feeder, on_delete=models.SET_NULL, null=True, related_name='poledefects_feeder')
    defect_type = models.CharField(max_length=50, choices=DEFECTTYPE, null=True, blank=True)
    polefitting_type = models.CharField(max_length=50, choices=POLEFITTING, null=True, blank=True)
    pole_type = models.CharField(max_length=50, choices=TYPEPOLE, null=True, blank=True)
    y = models.CharField(max_length=100, blank=True, null=True)
    x = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='mvpoledefects_county')
    status = models.BooleanField(default=False)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='mv_inspected_poles_d_by')

    def __str__(self):
        return self.feeder.name

class Mvmaitenance(models.Model):
    APRVKEY = (
        ('', '----CHOOSE THE STATUS----'),
        ('approved', 'APPROVED'),
        ('declined', 'DECLINED'),
    )
    mvinspection = models.ForeignKey(Mvinspection, on_delete=models.SET_NULL, null=True,related_name='mv_inspection')
    feeder_section = models.ForeignKey(Feeder_sections, on_delete=models.SET_NULL, null=True, related_name='mv_maintenace_feeder_section')
    feeder = models.ForeignKey(Feeder,on_delete=models.SET_NULL, null=True, related_name='mv_maitenance_feeder')
    no_poleswithoutstays =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_rottentxstructure =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_leaningtxstructure =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_sagstoretention =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_sectionstodoublejumper =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_replacefusemounts =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_bypassedhtfuses =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_spurtaplins = models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_faultyabswitces =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_installabswitces = models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_overhangingtrees =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_tracemaint =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_upratingconductors =  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_autoclosures=  models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_autoclosuresfaulty = models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_faultyhvcable =models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_structureswithouttx =models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_jumpercableswithoutlugs =models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_disconnsurged =models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_txmissingearthing = models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_ssnnumberless = models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    no_wayleaveinfrng =models.IntegerField(help_text='If none insert 0',blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    save_status = models.BooleanField(default=False, db_index=True)
    aprv_status = models.BooleanField(default=False, db_index=True)
    aprv_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='mv_maintenance_approved_by')
    aprv_notes = models.TextField(blank=True, null=True)
    aprv_dt = models.DateField(blank=True, null=True)
    aprv_key = models.CharField(max_length=10, choices=APRVKEY, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='mv_maintenance_inspected_by')
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='mvmaintenance_county')

    def __str__(self):
        return self.feeder_section.name

class Mv_defaults(models.Model):
    mvinspection = models.ForeignKey(Mvinspection, on_delete=models.SET_NULL, null=True,related_name='mv_inspection_default', db_index=True)
    feeder = models.ForeignKey(Feeder, on_delete=models.SET_NULL, null=True,related_name='mvdefects_feeder', db_index=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='mv_default_inspected_by')
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='mvdefaults_county')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='mvdefaults_region')
    no_poleswithoutstays = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_rottentxstructure = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_leaningtxstructure = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_sagstoretention = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_sectionstodoublejumper = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_replacefusemounts = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_bypassedhtfuses = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_spurtaplins = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_faultyabswitces = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_installabswitces = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_overhangingtrees = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_tracemaint = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_upratingconductors = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_autoclosures = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_autoclosuresfaulty = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_faultyhvcable = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_structureswithouttx = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_jumpercableswithoutlugs = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_disconnsurged = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_txmissingearthing = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_ssnnumberless = models.IntegerField(help_text='If none insert 0', blank=True, null=True)
    no_wayleaveinfrng = models.IntegerField(help_text='If none insert 0', blank=True, null=True)

    def __str__(self):
        return self.mvinspection.feeder.name

class Poledefects_maintenance(models.Model):
    DEFECTTYPE = (
        ('', '----CHOOSE THE STATUS----'),
        ('new', 'NEW'),
        ('repair', 'REPAIR'),
        ('midspanpole', 'MIDSPAN POLE'),
    )
    TYPEPOLE = (
        ('', '----CHOOSE THE STATUS----'),
        ('10mwooden', '10m WOODEN'),
        ('11mwooden', '11m WOODEN'),
        ('12mwooden', '12m WOODEN'),
        ('10mconcrete', '10m CONCRETE'),
        ('11mconcrete', '11m CONCRETE'),
        ('12mconcrete', '12m CONCRETE'),
        ('14mconcrete', '14m CONCRETE'),
    )
    APRVKEY = (
        ('', '----CHOOSE THE STATUS----'),
        ('approved', 'APPROVED'),
        ('declined', 'DECLINED'),
    )
    poledefect = models.ForeignKey(Mv_poledefects, on_delete=models.SET_NULL, null=True, related_name='poledefects_mv_makintenance')
    pole_type = models.CharField(max_length=50, choices=TYPEPOLE, null=True, blank=True)
    defect_type = models.CharField(max_length=100, choices=DEFECTTYPE, null=True, blank=True)
    y = models.CharField(max_length=100, blank=True, null=True)
    x = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='mv_poledefects_maintained_county')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True,related_name='mv_poledefects_maintained_region')
    status = models.BooleanField(default=False)
    maintain_notes = models.TextField(blank=True, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='mv_mainteained_poles_d_by')
    save_status = models.BooleanField(default=False)
    aprv_status = models.BooleanField(default=False)
    aprv_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='mv_poledefects_m_approved_by')
    aprv_notes = models.TextField(blank=True, null=True)
    aprv_key = models.CharField(max_length=10, choices=APRVKEY, null=True, blank=True)
    aprv_dt = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.poledefect.feeder.name