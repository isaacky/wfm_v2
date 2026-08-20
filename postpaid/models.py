from django.db import models
from user.models import Account, UserProfile
from main.models import County, Region
from django.utils.translation import gettext_lazy as _

class Zerobills(models.Model):
    meterno = models.CharField(
        max_length=255, blank=True, verbose_name=_("Meter Number"), unique=True
    )
    accountno = models.CharField(max_length=255, blank=True, null=True)
    county = models.ForeignKey(
        County, on_delete=models.SET_NULL, null=True, related_name="county_zb_target"
    )
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True, related_name="region_zb_target"
    )
    user = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, related_name="zerobill_user"
    )
    itin = models.CharField(max_length=100, blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)
    zone = models.CharField(max_length=100, blank=True, null=True)
    incms_status = models.CharField(max_length=100, blank=True, null=True)
    phonenumber = models.CharField(max_length=100, blank=True, null=True)
    customername = models.CharField(max_length=200, blank=True, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    notimeszero = models.IntegerField(null=True, blank=True, default=0)
    reading = models.IntegerField(null=True, blank=True, default=0)
    tarrif = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=["dtadd"])]
        ordering = [
            "-dtadd",
        ]

    def __str__(self):
        return self.meterno
        
    
class Zerobillresolved(models.Model):
    STATUSCHOISES2 = (
        ("", "----CHOOSE A STATUS----"),
        ("billing", "BILLED"),
        ("irregularity", "REGULARISED"),
        ("genuine", "GENUINE ZEROBILL"),
        ("faulty", "REPLACED FAULTY"),
        ("pending", "PENDING BACKOFFICE"),
        ("meter_removed", "METERS REMOVED"),
        ("meters_normalised", "METERS NORMALISED"),
    )
    STATUSCHOISES = (
        ("", "----CHOOSE A STATUS----"),
        ("faulty", "FAULTY"),
        ("bypasses", "BY-PASSED"),
        ("tampered", "TAMPERED"),
        ("idle", "IDLE"),
        ("disconnected", "DISCONNECTED"),
        ("notonsite", "NOT-ON-SITE"),
        ("disconnected", "DISCONNECTED"),
        ("meterokay", "METER OKAY & READ"),
        ("vacantpremises", "VACANT PREMISES"),
    )
    zerobill = models.ForeignKey(Zerobills, on_delete=models.SET_NULL, null=True, related_name='zerobill_target')
    meterno = models.CharField(
        max_length=255, blank=True, verbose_name=_("Meter Number"), unique=True
    )
    accountno = models.IntegerField(blank=True, null=True)
    readings = models.IntegerField(
        blank=True,
        null=True,
        help_text="If the reading is blank input zero and give a narration in the comment field",
    )
    reading = models.IntegerField(default=0)
    comment = models.TextField(max_length=300, blank=True, null=True)
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="Zerobillresolved_user",
    )
    status = models.CharField(max_length=100, blank=True, null=True)
    county = models.ForeignKey(
        County, on_delete=models.SET_NULL, null=True, related_name="county_zb_resolved"
    )
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True, related_name="region_zb_resolved"
    )
    status2 = models.CharField(
        verbose_name=_("Change Status"),
        max_length=50,
        choices=STATUSCHOISES2,
        default="pending",
    )
    status3 = models.BooleanField(default=False)
    status4 = models.CharField(
        verbose_name=_("Choose Status"),
        max_length=50,
        choices=STATUSCHOISES,
    )
    user2 = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="Zerobillresolved_user2",
    )
    dtadd2 = models.DateTimeField(null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    meterimg = models.ImageField(
        default="default.jpg", upload_to="images/zerobills/%Y/%m/%d/"
    )
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    diffunits = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)

    class Meta:
        indexes = [models.Index(fields=["dtadd"])]
        ordering = [
            "-dtadd",
        ]

    def __str__(self):
        return self.meterno


class Feeder(models.Model):
    name =models.CharField(verbose_name=_("Feeder Name"), max_length=255)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class Kaguaconnection(models.Model):
    meterno = models.CharField(max_length=20,verbose_name=_("Meter Number"), unique=True)  
    accountno = models.CharField(max_length=20,verbose_name=_("Account Number"))     
    customer_name = models.CharField(verbose_name=_("Customer Name"), max_length=200, blank=True, null=True)   
    type = models.CharField(verbose_name=_("Service Type"), max_length=50, null=True, blank=True)
    telephone = models.CharField(verbose_name=_("Telephone Number"), max_length=100, null=True, blank=True)
    supply_phase = models.CharField(verbose_name=_("Supply Phase"), max_length=100, blank=True, null=True)
    substation = models.CharField(verbose_name=_("Substation"), max_length=100, blank=True, null=True)
    feeder = models.ForeignKey(Feeder, on_delete=models.SET_NULL, null=True)
    status = models.BooleanField(default=False)    
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.meterno} {self.accountno}'

class Inspect_connection(models.Model):
    METERINGSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('okay','OKAY'),
        ('faulty','FAULTY'),
        ('tampered','TAMPERED'),
        ('bypassed','BYPASSED'),           
        )
    INSTALLATIONSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('okay','OKAY'),
        ('notokay','NOT OKAY'),        
        )
    FAULTYSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('blankscreen','BLANK SCREEN'),
        ('noncommunicating','NON COMMUNICATING'), 
        ('obsolete','OBSOLETE'),
        ('fadeddigits','FADED DIGITS'),
        ('notpulsing','NOT PULSING'),
        ('burnt','BURNT'), 
        ('batterylow','BATTERY LOW'),
        ('cuifaulty','CIU FAULTY'),
        ('notabletoloadtoken','NOT ABLE TO LOAD TOKEN'),
        ('looseglass','LOOSE GLASS'),      
        )
    TAMPEREDSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('brokenseaals','BROKEN SEALS'),
        ('disabledvoltage','DISABLED VOLTAGE'), 
        ('disabledcurrent','DISABLED CURRENT'),
        ('brokenglass','BROKEN GLASS'),
        ('droppedlink','DROPPED LINK'),
        ('damagedmeter','DAMAGED METER'), 
        ('foreignobjects','FOREIGN OBJECTS INTRODUCED'),     
        )
    BYPASSSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('puncturedcable','PUNCTURED CABLE'),
        ('drilledcutout','DRILLED CUTOUT'),        
        )
    METERTYPE= (
        ('','----CHOOSE A METER TYPE----'),
        ('prepaid','PREPAID'),
        ('postpaid','POSTPAID'),        
        )
    NOTOKAYSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('loosejoints','LOOSE JOINTS'),
        ('noearth','NO EARTH'), 
        ('demolishedpremises','DEMOLISHED PREMISES'),
        ('vacant','VACANT'),
        ('nometertails','NO METER TAILS'),
        ('loosemeterbox','LOOSE METERBOX'),     
        )
    connection = models.ForeignKey(Kaguaconnection, on_delete=models.SET_NULL,null=True) 
    feeder_inspected = models.ForeignKey(Feeder, on_delete=models.SET_NULL, null=True)
    meterno = models.BigIntegerField(verbose_name=_("Meter Number"), unique=True)  
    accountno = models.BigIntegerField(verbose_name=_("Account Number")) 
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    meteringstatus = models.CharField(verbose_name=_("Metering Status"),max_length=50, choices=METERINGSTATUS)
    installationstatus = models.CharField(verbose_name=_("Installation Status"),max_length=50, choices=INSTALLATIONSTATUS)
    faultystatus = models.CharField(verbose_name=_("Faulty Status"),max_length=50, choices=FAULTYSTATUS, null=True, blank=True, default='NULL')
    tamperedstatus = models.CharField(verbose_name=_("Tampered Status"),max_length=50, choices=TAMPEREDSTATUS, null=True, blank=True)
    bypassstatus = models.CharField(verbose_name=_("Bypass Status"),max_length=50, choices=BYPASSSTATUS, null=True, blank=True)
    notokaystatus = models.CharField(verbose_name=_("Not Okay Status"),max_length=50, choices=NOTOKAYSTATUS, null=True, blank=True)
    reading = models.CharField(verbose_name=_("Meter Reading"),blank=True,null=True,max_length=100, help_text="Only required if 'shipping' is selected.")
    inspector = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    meterimg = models.ImageField(default='default.jpg', upload_to="images/kagua/%Y/%m/%d/")
    metertype = models.CharField(verbose_name=_("Type Of Meter"),max_length=50, choices=METERTYPE, null=True, blank=True)
    comment = models.TextField(verbose_name=_('Any Comment'), null=True, blank=True)
    county=models.ForeignKey(County,on_delete=models.SET_NULL, null=True)
    region= models.ForeignKey(Region,on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.meterno} {self.accountno}'
        

class Not_in_feeder(models.Model):
    METERINGSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('okay','OKAY'),
        ('faulty','FAULTY'),
        ('tampered','TAMPERED'),
        ('bypassed','BYPASSED'),           
        )
    INSTALLATIONSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('okay','OKAY'),
        ('notokay','NOT OKAY'),        
        )
    FAULTYSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('blankscreen','BLANK SCREEN'),
        ('noncommunicating','NON COMMUNICATING'), 
        ('obsolete','OBSOLETE'),
        ('fadeddigits','FADED DIGITS'),
        ('notpulsing','NOT PULSING'),
        ('burnt','BURNT'), 
        ('batterylow','BATTERY LOW'),
        ('cuifaulty','CIU FAULTY'),
        ('notabletoloadtoken','NOT ABLE TO LOAD TOKEN'),
        ('looseglass','LOOSE GLASS'),      
        )
    TAMPEREDSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('brokenseaals','BROKEN SEALS'),
        ('disabledvoltage','DISABLED VOLTAGE'), 
        ('disabledcurrent','DISABLED CURRENT'),
        ('brokenglass','BROKEN GLASS'),
        ('droppedlink','DROPPED LINK'),
        ('damagedmeter','DAMAGED METER'), 
        ('foreignobjects','FOREIGN OBJECTS INTRODUCED'),     
        )
    BYPASSSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('puncturedcable','PUNCTURED CABLE'),
        ('drilledcutout','DRILLED CUTOUT'),        
        )
    METERTYPE= (
        ('','----CHOOSE A METER TYPE----'),
        ('prepaid','PREPAID'),
        ('postpaid','POSTPAID'),        
        )
    NOTOKAYSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('loosejoints','LOOSE JOINTS'),
        ('noearth','NO EARTH'), 
        ('demolishedpremises','DEMOLISHED PREMISES'),
        ('vacant','VACANT'),
        ('nometertails','NO METER TAILS'),
        ('loosemeterbox','LOOSE METERBOX'),     
        )
    feeder= models.ForeignKey(Feeder, on_delete=models.SET_NULL, null=True)
    txnumber= models.CharField(verbose_name=_('TX Number'), max_length=100, null=True,blank=True)
    meterno = models.BigIntegerField(verbose_name=_("Meter Number"), unique=True)   
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    meteringstatus = models.CharField(verbose_name=_("Metering Status"),max_length=50, choices=METERINGSTATUS)
    installationstatus = models.CharField(verbose_name=_("Installation Status"),max_length=50, choices=INSTALLATIONSTATUS)
    faultystatus = models.CharField(verbose_name=_("Faulty Status"),max_length=50, choices=FAULTYSTATUS, null=True, blank=True, default='NULL')
    tamperedstatus = models.CharField(verbose_name=_("Tampered Status"),max_length=50, choices=TAMPEREDSTATUS, null=True, blank=True)
    bypassstatus = models.CharField(verbose_name=_("Bypass Status"),max_length=50, choices=BYPASSSTATUS, null=True, blank=True)
    notokaystatus = models.CharField(verbose_name=_("Not Okay Status"),max_length=50, choices=NOTOKAYSTATUS, null=True, blank=True)
    reading = models.CharField(verbose_name=_("Meter Reading"),blank=True,null=True,max_length=100, help_text="Only required if 'shipping' is selected.")
    inspector = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    meterimg = models.ImageField(default='default.jpg', upload_to="images/kagua/%Y/%m/%d/")
    metertype = models.CharField(verbose_name=_("Type Of Meter"),max_length=50, choices=METERTYPE, null=True, blank=True)
    comment = models.TextField(verbose_name=_('Any Comment'), null=True, blank=True)
    Neighbour_Meter = models.CharField(verbose_name=_('Neighbour Meter'), null=True, blank=True, max_length=100)
    county=models.ForeignKey(County,on_delete=models.SET_NULL, null=True)
    region= models.ForeignKey(Region,on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.meterno}'


class Kagua_county(models.Model):
    county = models.CharField(max_length=50) 
    no_of_feeders = models.IntegerField()
    target = models.BigIntegerField()  
    achieved = models.BigIntegerField() 
    

    class Meta:
        managed = False
        db_table = "kagua_county"

class Threephase_target(models.Model):
    meterno = models.CharField(max_length=30,verbose_name=_('Meter Number'), blank=True, null=True)
    accountno = models.CharField(max_length=30,verbose_name=_('Account Number'), blank=True,null=True)
    county=models.ForeignKey(County,on_delete=models.SET_NULL, null=True, related_name='highend_county_target')
    region= models.ForeignKey(Region,on_delete=models.SET_NULL, null=True,related_name='highend_region_target')
    customer_name = models.CharField(verbose_name=_("Customer Name"), max_length=200, blank=True, null=True)
    supplylocation = models.CharField(_('Supply Location'), max_length=255,blank=True, null=True)
    lon = models.CharField(_('Longitude'), max_length=255, blank=True, null=True)
    lat = models.CharField(_('Latitude'), max_length=255, blank=True, null=True)
    itin = models.CharField(_('Itinerary'), max_length=255, blank=True,null=True)
    sector = models.CharField(_('Sector'), max_length=100, blank=True, null=True)
    zone = models.CharField(_('Zone'), max_length=100, blank=True,null=True)
    units = models.CharField(max_length=100, null=True, blank=True)
    avg_units = models.DecimalField(_("Average Units"), max_digits=12, decimal_places=2)
    tarrif = models.CharField(max_length=100, null=True, blank=True)
    phase = models.CharField(max_length=100, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.meterno

class Threephase_inspection(models.Model):
    METERINGSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('okay','OKAY'),
        ('faulty','FAULTY'),
        ('tampered','TAMPERED'),
        ('bypassed','BYPASSED'),           
        )
    INSTALLATIONSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('okay','OKAY'),
        ('notokay','NOT OKAY'),        
        )
    FAULTYSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('blankscreen','BLANK SCREEN'),
        ('noncommunicating','NON COMMUNICATING'), 
        ('obsolete','OBSOLETE'),
        ('fadeddigits','FADED DIGITS'),
        ('notpulsing','NOT PULSING'),
        ('burnt','BURNT'), 
        ('batterylow','BATTERY LOW'),
        ('cuifaulty','CIU FAULTY'),
        ('notabletoloadtoken','NOT ABLE TO LOAD TOKEN'),
        ('looseglass','LOOSE GLASS'),      
        )
    TAMPEREDSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('brokenseaals','BROKEN SEALS'),
        ('disabledvoltage','DISABLED VOLTAGE'), 
        ('disabledcurrent','DISABLED CURRENT'),
        ('brokenglass','BROKEN GLASS'),
        ('droppedlink','DROPPED LINK'),
        ('damagedmeter','DAMAGED METER'), 
        ('foreignobjects','FOREIGN OBJECTS INTRODUCED'),     
        )
    BYPASSSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('puncturedcable','PUNCTURED CABLE'),
        ('drilledcutout','DRILLED CUTOUT'),        
        )
    METERTYPE= (
        ('','----CHOOSE A PHASE TYPE----'),
        ('singlephase','SINGLE PHASE'),
        ('threephase','THREE PHASE'),
        )
    NOTOKAYSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('loosejoints','LOOSE JOINTS'),
        ('noearth','NO EARTH'), 
        ('demolishedpremises','DEMOLISHED PREMISES'),
        ('vacant','VACANT'),
        ('nometertails','NO METER TAILS'),
        ('loosemeterbox','LOOSE METERBOX'),     
        )
    threepase = models.ForeignKey(Threephase_target, on_delete=models.SET_NULL,null=True, related_name='three_target')
    meterno = models.CharField(max_length=20,verbose_name=_("Meter Number"), unique=True)
    accountno = models.CharField(max_length=20,verbose_name=_("Account Number"))
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    meteringstatus = models.CharField(verbose_name=_("Metering Status"),max_length=50, choices=METERINGSTATUS)
    installationstatus = models.CharField(verbose_name=_("Installation Status"),max_length=50, choices=INSTALLATIONSTATUS)
    faultystatus = models.CharField(verbose_name=_("Faulty Status"),max_length=50, choices=FAULTYSTATUS, null=True, blank=True, default='NULL')
    tamperedstatus = models.CharField(verbose_name=_("Tampered Status"),max_length=50, choices=TAMPEREDSTATUS, null=True, blank=True)
    bypassstatus = models.CharField(verbose_name=_("Bypass Status"),max_length=50, choices=BYPASSSTATUS, null=True, blank=True)
    notokaystatus = models.CharField(verbose_name=_("Not Okay Status"),max_length=50, choices=NOTOKAYSTATUS, null=True, blank=True)
    reading = models.CharField(verbose_name=_("Meter Reading"),blank=True,null=True,max_length=100, help_text="Only required if 'shipping' is selected.")
    inspector = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='threephase_inspector')
    meterimg = models.ImageField(upload_to="images/threepase/%Y/%m/%d/", null=True, blank=True, default='images/default.jpg')
    metertype = models.CharField(verbose_name=_("Type Of Meter"),max_length=50, choices=METERTYPE, null=True, blank=True)
    comment = models.TextField(verbose_name=_('Any Comment'), null=True, blank=True)
    county=models.ForeignKey(County,on_delete=models.SET_NULL, null=True,related_name='highend_county')
    region= models.ForeignKey(Region,on_delete=models.SET_NULL, null=True,related_name='highend_region')
    sealno = models.CharField(max_length=50, verbose_name=_('Seal Number'), blank=True, null=True)
    incms_status = models.BooleanField(default=False)
    incms_nextlevel = models.BooleanField(default=False)
    r_units = models.DecimalField(
        _("Billed Units"), max_digits=12, decimal_places=2, default=0
    )
    system_reading = models.DecimalField(
        _("System reading"), max_digits=12, decimal_places=2, default=0
    )
    anomaly_status = models.BooleanField(default=False)

    def __str__(self):
        return self.meterno

class Telcos_target(models.Model):
    siteid = models.CharField(verbose_name=_('Site ID'), max_length=50, blank=True,null=True)
    sitename = models.CharField(verbose_name=_('Site ID'), max_length=255, blank=True, null=True)
    meterno = models.CharField(verbose_name=_('Meter Number'), blank=True, null=True, max_length=100)
    accountno = models.CharField(verbose_name=_('Account Number'), blank=True,null=True, max_length=100)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='telcos_county')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='telcoe_region')
    lon = models.CharField(_('Longitude'), max_length=255, blank=True, null=True)
    lat = models.CharField(_('Latitude'), max_length=255, blank=True, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    system_reading = models.IntegerField(verbose_name=_('System Reading'),blank=True, null=True)
    consumption = models.IntegerField(verbose_name=_('Usage'), blank=True, null=True)
    avgconsumption = models.IntegerField(verbose_name=_('avg'), blank=True, null=True)
    timesonefive = models.IntegerField(verbose_name=_('times 1.5'), blank=True, null=True)
    telcos_type = models.CharField(max_length=20, blank=True,null=True)

    def __str__(self):
        return f'{self.meterno}'

class Telcos_inspection(models.Model):
    METERINGSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('okay','OKAY'),
        ('faulty','FAULTY'),
        ('tampered','TAMPERED'),
        ('bypassed','BYPASSED'),
        )
    INSTALLATIONSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('okay','OKAY'),
        ('notokay','NOT OKAY'),
        )
    PHASESTATUS = (
        ('', '----CHOOSE A STATUS----'),
        ('single', 'SINGLE PHASE'),
        ('threephase', 'THREE PHASE'),
    )
    FAULTYSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('blankscreen','BLANK SCREEN'),
        ('noncommunicating','NON COMMUNICATING'),
        ('obsolete','OBSOLETE'),
        ('fadeddigits','FADED DIGITS'),
        ('notpulsing','NOT PULSING'),
        ('burnt','BURNT'),
        ('batterylow','BATTERY LOW'),
        ('cuifaulty','CIU FAULTY'),
        ('notabletoloadtoken','NOT ABLE TO LOAD TOKEN'),
        ('looseglass','LOOSE GLASS'),
        )
    TAMPEREDSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('brokenseaals','BROKEN SEALS'),
        ('disabledvoltage','DISABLED VOLTAGE'),
        ('disabledcurrent','DISABLED CURRENT'),
        ('brokenglass','BROKEN GLASS'),
        ('droppedlink','DROPPED LINK'),
        ('damagedmeter','DAMAGED METER'),
        ('foreignobjects','FOREIGN OBJECTS INTRODUCED'),
        )
    BYPASSSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('puncturedcable','PUNCTURED CABLE'),
        ('drilledcutout','DRILLED CUTOUT'),
        )
    METERTYPE= (
        ('','----CHOOSE A METER TYPE----'),
        ('prepaid','PREPAID'),
        ('postpaid','POSTPAID'),
        )
    NOTOKAYSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('loosejoints','LOOSE JOINTS'),
        ('noearth','NO EARTH'),
        ('demolishedpremises','DEMOLISHED PREMISES'),
        ('vacant','VACANT'),
        ('nometertails','NO METER TAILS'),
        ('loosemeterbox','LOOSE METERBOX'),
        )
    siteid = models.CharField(verbose_name=_('Site ID'), max_length=50, unique=True)
    sitename = models.CharField(verbose_name=_('Site Name'), max_length=255, blank=True, null=True)
    telcos = models.ForeignKey(Telcos_target, on_delete=models.SET_NULL, null=True, related_name='telcos_target')
    meterno = models.CharField(verbose_name=_("Meter Number"), unique=True, max_length=100)
    accountno = models.CharField(verbose_name=_("Account Number"), max_length=100)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    phase = models.CharField(verbose_name=_("Phase Status"), max_length=50, choices=PHASESTATUS, null=True,blank=True)
    meteringstatus = models.CharField(verbose_name=_("Metering Status"),max_length=50, choices=METERINGSTATUS)
    installationstatus = models.CharField(verbose_name=_("Installation Status"),max_length=50, choices=INSTALLATIONSTATUS)
    faultystatus = models.CharField(verbose_name=_("Faulty Status"),max_length=50, choices=FAULTYSTATUS, null=True, blank=True, default='NULL')
    tamperedstatus = models.CharField(verbose_name=_("Tampered Status"),max_length=50, choices=TAMPEREDSTATUS, null=True, blank=True)
    bypassstatus = models.CharField(verbose_name=_("Bypass Status"),max_length=50, choices=BYPASSSTATUS, null=True, blank=True)
    notokaystatus = models.CharField(verbose_name=_("Not Okay Status"),max_length=50, choices=NOTOKAYSTATUS, null=True, blank=True)
    reading = models.IntegerField(verbose_name=_("Meter Reading(This is a required Field)"), help_text="Required")
    inspector = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='telcos')
    telcosimg = models.ImageField(upload_to="images/telcos/%Y/%m/%d/",verbose_name=_('CLEAR IMAGE UPLOAD(This is Required)'))
    diimg = models.ImageField(upload_to="di/telcos/%Y/%m/%d/", default='default.jpg', verbose_name=_('DI UPLOAD(Take a clear Picture of the DI Filled Form)'))
    metertype = models.CharField(verbose_name=_("Type Of Meter"),max_length=50, choices=METERTYPE, null=True, blank=True)
    comment = models.TextField(verbose_name=_('Any Comment'), null=True, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    y = models.CharField(_('Y'), max_length=255)
    x = models.CharField(_('X'), max_length=255)
    incms = models.BooleanField(verbose_name=_('Back Office Resolve'),default=False)
    nextlevel = models.BooleanField(verbose_name=_('Back Office Level'), default=False)
    billed = models.BigIntegerField(verbose_name=_('Rebilled Amount'),  default=0)
    system_reading = models.IntegerField(verbose_name=_('System Reading'), blank=True, null=True)
    consumption = models.IntegerField(verbose_name=_('Usage'), blank=True, null=True)
    units = models.IntegerField(verbose_name=_("Units"),null=True, blank=True)

    def __str__(self):
        return f'{self.meterno} {self.siteid}'

    @property
    def usage(self):
        return (int(self.reading)) - (int(self.system_reading))

class Public_lighting_target(models.Model):
    meterno = models.CharField(verbose_name=_("Meter Number"), unique=True, max_length=100)
    accountno = models.CharField(verbose_name=_("Account Number"), max_length=100,blank=True, null=True)
    customer = models.CharField(verbose_name=_('Customer Name'), max_length=255, null=True, blank=True)
    supplylocation = models.CharField(verbose_name=_('Supply Location'), max_length=255, null=True, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey(Region,on_delete=models.SET_NULL, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    system_reading = models.IntegerField(verbose_name=_('System Reading'), blank=True, null=True)
    consumption = models.IntegerField(verbose_name=_('Usage'), blank=True, null=True)
    tarrif = models.CharField(max_length=255, null=True, blank=True)
    contract_status = models.CharField(max_length=255, null=True, blank=True)
    y = models.CharField(_('Y'), max_length=255, blank=True, null=True)
    x = models.CharField(_('X'), max_length=255,blank=True, null=True)


    def __str__(self):
        return self.meterno

class Public_lighting_inspection(models.Model):
    METERINGSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('okay','OKAY'),
        ('faulty','FAULTY'),
        ('tampered','TAMPERED'),
        ('bypassed','BYPASSED'),
        )
    INSTALLATIONSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('okay','OKAY'),
        ('notokay','NOT OKAY'),
        )
    PHASESTATUS = (
        ('', '----CHOOSE A STATUS----'),
        ('single', 'SINGLE PHASE'),
        ('threephase', 'THREE PHASE'),
    )
    FAULTYSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('blankscreen','BLANK SCREEN'),
        ('noncommunicating','NON COMMUNICATING'),
        ('obsolete','OBSOLETE'),
        ('fadeddigits','FADED DIGITS'),
        ('notpulsing','NOT PULSING'),
        ('burnt','BURNT'),
        ('batterylow','BATTERY LOW'),
        ('cuifaulty','CIU FAULTY'),
        ('notabletoloadtoken','NOT ABLE TO LOAD TOKEN'),
        ('looseglass','LOOSE GLASS'),
        )
    TAMPEREDSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('brokenseaals','BROKEN SEALS'),
        ('disabledvoltage','DISABLED VOLTAGE'),
        ('disabledcurrent','DISABLED CURRENT'),
        ('brokenglass','BROKEN GLASS'),
        ('droppedlink','DROPPED LINK'),
        ('damagedmeter','DAMAGED METER'),
        ('foreignobjects','FOREIGN OBJECTS INTRODUCED'),
        )
    BYPASSSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('puncturedcable','PUNCTURED CABLE'),
        ('drilledcutout','DRILLED CUTOUT'),
        )
    METERTYPE= (
        ('','----CHOOSE A METER TYPE----'),
        ('prepaid','PREPAID'),
        ('postpaid','POSTPAID'),
        )
    METERINSTALLTYPE = (
        ('', '----CHOOSE A METER TYPE----'),
        ('nonsmart', 'NON SMART'),
        ('smart', 'SMART'),
    )
    METERREADABLE = (
        ('', '----CHOOSE A STATUS----'),
        ('yes', 'YES'),
        ('no', 'NO'),
    )
    NOTOKAYSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('loosejoints','LOOSE JOINTS'),
        ('noearth','NO EARTH'),
        ('demolishedpremises','DEMOLISHED PREMISES'),
        ('vacant','VACANT'),
        ('nometertails','NO METER TAILS'),
        ('loosemeterbox','LOOSE METERBOX'),
        )
    target = models.ForeignKey(Public_lighting_target, on_delete=models.SET_NULL, null=True,related_name='publiclighting_target_24')
    meterno = models.CharField(verbose_name=_("Meter Number"),max_length=100,null=True,blank=True)
    accountno = models.CharField(verbose_name=_("Account Number"), max_length=100, null=True,blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    meter_type = models.CharField(verbose_name=_("Meter Installation Type"), max_length=50, choices=METERINSTALLTYPE, null=True, blank=True)
    phase = models.CharField(verbose_name=_("Phase Status"), max_length=50, choices=PHASESTATUS, null=True,blank=True)
    meteringstatus = models.CharField(verbose_name=_("Metering Status"),max_length=50, choices=METERINGSTATUS)
    installationstatus = models.CharField(verbose_name=_("Installation Status"),max_length=50, choices=INSTALLATIONSTATUS)
    faultystatus = models.CharField(verbose_name=_("Faulty Status"),max_length=50, choices=FAULTYSTATUS, null=True, blank=True, default='NULL')
    tamperedstatus = models.CharField(verbose_name=_("Tampered Status"),max_length=50, choices=TAMPEREDSTATUS, null=True, blank=True)
    bypassstatus = models.CharField(verbose_name=_("Bypass Status"),max_length=50, choices=BYPASSSTATUS, null=True, blank=True)
    notokaystatus = models.CharField(verbose_name=_("Not Okay Status"),max_length=50, choices=NOTOKAYSTATUS, null=True, blank=True)
    meter_readable = models.CharField(verbose_name=_("Meter Readable"), max_length=50, choices=METERREADABLE, null=True,blank=True)
    reading = models.IntegerField(verbose_name=_("Meter Reading(This is a required Field)"), help_text="Required", null=True,blank=True)
    inspector = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='public_lighting_24')
    public_l_img = models.ImageField(upload_to="images/publicl/%Y/%m/%d/",verbose_name=_('CLEAR IMAGE UPLOAD(This is Required)'))
    diimg = models.ImageField(upload_to="di/publicl/%Y/%m/%d/", default='default.jpg', verbose_name=_('DI UPLOAD(Take a clear Picture of the DI Filled Form)'))
    metertype = models.CharField(verbose_name=_("Type Of Meter"),max_length=50, choices=METERTYPE, null=True, blank=True)
    comment = models.TextField(verbose_name=_('Any Comment'), null=True, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='county_public_lighting_24')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='region_public_lighting_24')
    y = models.CharField(_('Y'), max_length=255)
    x = models.CharField(_('X'), max_length=255)
    incms = models.BooleanField(verbose_name=_('Back Office Resolve'),default=False)
    nextlevel = models.BooleanField(verbose_name=_('Back Office Level'), default=False)
    billed = models.BigIntegerField(verbose_name=_('Rebilled Amount'),  default=0)
    system_reading = models.IntegerField(verbose_name=_('System Reading'), blank=True, null=True)
    consumption = models.IntegerField(verbose_name=_('Usage'), blank=True, null=True)
    units = models.IntegerField(verbose_name=_("Units"),null=True, blank=True)


    def __str__(self):
        return  self.meterno

    @property
    def usage(self):
        return (int(self.reading)) - (int(self.system_reading))


class Public_lighting_inspection_25(models.Model):
    METERINGSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('okay','OKAY'),
        ('faulty','FAULTY'),
        ('tampered','TAMPERED'),
        ('bypassed','BYPASSED'),
        )
    INSTALLATIONSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('okay','OKAY'),
        ('notokay','NOT OKAY'),
        )
    PHASESTATUS = (
        ('', '----CHOOSE A STATUS----'),
        ('single', 'SINGLE PHASE'),
        ('threephase', 'THREE PHASE'),
    )
    FAULTYSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('blankscreen','BLANK SCREEN'),
        ('noncommunicating','NON COMMUNICATING'),
        ('obsolete','OBSOLETE'),
        ('fadeddigits','FADED DIGITS'),
        ('notpulsing','NOT PULSING'),
        ('burnt','BURNT'),
        ('batterylow','BATTERY LOW'),
        ('cuifaulty','CIU FAULTY'),
        ('notabletoloadtoken','NOT ABLE TO LOAD TOKEN'),
        ('looseglass','LOOSE GLASS'),
        )
    TAMPEREDSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('brokenseaals','BROKEN SEALS'),
        ('disabledvoltage','DISABLED VOLTAGE'),
        ('disabledcurrent','DISABLED CURRENT'),
        ('brokenglass','BROKEN GLASS'),
        ('droppedlink','DROPPED LINK'),
        ('damagedmeter','DAMAGED METER'),
        ('foreignobjects','FOREIGN OBJECTS INTRODUCED'),
        )
    BYPASSSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('puncturedcable','PUNCTURED CABLE'),
        ('drilledcutout','DRILLED CUTOUT'),
        )
    METERTYPE= (
        ('','----CHOOSE A METER TYPE----'),
        ('prepaid','PREPAID'),
        ('postpaid','POSTPAID'),
        )
    METERINSTALLTYPE = (
        ('', '----CHOOSE A METER TYPE----'),
        ('nonsmart', 'NON SMART'),
        ('smart', 'SMART'),
    )
    METERREADABLE = (
        ('', '----CHOOSE A STATUS----'),
        ('yes', 'YES'),
        ('no', 'NO'),
    )
    NOTOKAYSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('loosejoints','LOOSE JOINTS'),
        ('noearth','NO EARTH'),
        ('demolishedpremises','DEMOLISHED PREMISES'),
        ('vacant','VACANT'),
        ('nometertails','NO METER TAILS'),
        ('loosemeterbox','LOOSE METERBOX'),
        )
    target = models.ForeignKey(Public_lighting_target, on_delete=models.SET_NULL, null=True,related_name='publiclighting_target')
    meterno = models.CharField(verbose_name=_("Meter Number"),max_length=100,null=True,blank=True)
    accountno = models.CharField(verbose_name=_("Account Number"), max_length=100, null=True,blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    meter_type = models.CharField(verbose_name=_("Meter Installation Type"), max_length=50, choices=METERINSTALLTYPE, null=True, blank=True)
    phase = models.CharField(verbose_name=_("Phase Status"), max_length=50, choices=PHASESTATUS, null=True,blank=True)
    meteringstatus = models.CharField(verbose_name=_("Metering Status"),max_length=50, choices=METERINGSTATUS)
    installationstatus = models.CharField(verbose_name=_("Installation Status"),max_length=50, choices=INSTALLATIONSTATUS)
    faultystatus = models.CharField(verbose_name=_("Faulty Status"),max_length=50, choices=FAULTYSTATUS, null=True, blank=True, default='NULL')
    tamperedstatus = models.CharField(verbose_name=_("Tampered Status"),max_length=50, choices=TAMPEREDSTATUS, null=True, blank=True)
    bypassstatus = models.CharField(verbose_name=_("Bypass Status"),max_length=50, choices=BYPASSSTATUS, null=True, blank=True)
    notokaystatus = models.CharField(verbose_name=_("Not Okay Status"),max_length=50, choices=NOTOKAYSTATUS, null=True, blank=True)
    meter_readable = models.CharField(verbose_name=_("Meter Readable"), max_length=50, choices=METERREADABLE, null=True,blank=True)
    reading = models.IntegerField(verbose_name=_("Meter Reading(This is a required Field)"), help_text="Required", null=True,blank=True)
    inspector = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='public_lighting')
    public_l_img = models.ImageField(upload_to="images/publicl/%Y/%m/%d/",verbose_name=_('CLEAR IMAGE UPLOAD(This is Required)'))
    diimg = models.ImageField(upload_to="di/publicl/%Y/%m/%d/", default='default.jpg', verbose_name=_('DI UPLOAD(Take a clear Picture of the DI Filled Form)'))
    metertype = models.CharField(verbose_name=_("Type Of Meter"),max_length=50, choices=METERTYPE, null=True, blank=True)
    comment = models.TextField(verbose_name=_('Any Comment'), null=True, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='county_public_lighting')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='region_public_lighting')
    y = models.CharField(_('Y'), max_length=255)
    x = models.CharField(_('X'), max_length=255)
    incms = models.BooleanField(verbose_name=_('Back Office Resolve'),default=False)
    nextlevel = models.BooleanField(verbose_name=_('Back Office Level'), default=False)
    billed = models.BigIntegerField(verbose_name=_('Rebilled Amount'),  default=0)
    system_reading = models.IntegerField(verbose_name=_('System Reading'), blank=True, null=True)
    consumption = models.IntegerField(verbose_name=_('Usage'), blank=True, null=True)
    units = models.IntegerField(verbose_name=_("Units"),null=True, blank=True)


    def __str__(self):
        return  self.meterno

    @property
    def usage(self):
        return (int(self.reading)) - (int(self.system_reading))


class Public_lightint_direct_supply(models.Model):
    INSTALLATIONSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('okay','OKAY'),
        ('notokay','NOT OKAY'),
        )
    NOTOKAYSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('loosejoints','LOOSE JOINTS'),
        ('noearth','NO EARTH'),
        ('demolishedpremises','DEMOLISHED PREMISES'),
        ('vacant','VACANT'),
        ('nometertails','NO METER TAILS'),
        ('loosemeterbox','LOOSE METERBOX'),
        )

    accountno = models.BigIntegerField(verbose_name=_("Account Number"), null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    installationstatus = models.CharField(verbose_name=_("Installation Status"),max_length=50, choices=INSTALLATIONSTATUS)
    notokaystatus = models.CharField(verbose_name=_("Not Okay Status"),max_length=50, choices=NOTOKAYSTATUS, null=True, blank=True)
    inspector = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(verbose_name=_('Any Comment'), null=True, blank=True)
    location = models.CharField(verbose_name=_('A Brief Description of the Physical location'), null=True, blank=True, max_length=255)
    county=models.ForeignKey(County,on_delete=models.SET_NULL, null=True)
    region= models.ForeignKey(Region,on_delete=models.SET_NULL, null=True)
    y = models.CharField(_('Y'), max_length=255)
    x = models.CharField(_('X'), max_length=255)

    def __str__(self):
        return  self.meterno

class Public_lighting_not_in_target(models.Model):
    METERINGSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('okay','OKAY'),
        ('faulty','FAULTY'),
        ('tampered','TAMPERED'),
        ('bypassed','BYPASSED'),
        ('nometer', 'NO METER'),
        )
    INSTALLATIONSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('okay','OKAY'),
        ('notokay','NOT OKAY'),
        )
    PHASESTATUS = (
        ('', '----CHOOSE A STATUS----'),
        ('single', 'SINGLE PHASE'),
        ('threephase', 'THREE PHASE'),
    )
    FAULTYSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('blankscreen','BLANK SCREEN'),
        ('noncommunicating','NON COMMUNICATING'),
        ('obsolete','OBSOLETE'),
        ('fadeddigits','FADED DIGITS'),
        ('notpulsing','NOT PULSING'),
        ('burnt','BURNT'),
        ('batterylow','BATTERY LOW'),
        ('cuifaulty','CIU FAULTY'),
        ('notabletoloadtoken','NOT ABLE TO LOAD TOKEN'),
        ('looseglass','LOOSE GLASS'),
        )
    TAMPEREDSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('brokenseaals','BROKEN SEALS'),
        ('disabledvoltage','DISABLED VOLTAGE'),
        ('disabledcurrent','DISABLED CURRENT'),
        ('brokenglass','BROKEN GLASS'),
        ('droppedlink','DROPPED LINK'),
        ('damagedmeter','DAMAGED METER'),
        ('foreignobjects','FOREIGN OBJECTS INTRODUCED'),
        )
    BYPASSSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('puncturedcable','PUNCTURED CABLE'),
        ('drilledcutout','DRILLED CUTOUT'),
        )
    METERTYPE= (
        ('','----CHOOSE A METER TYPE----'),
        ('prepaid','PREPAID'),
        ('postpaid','POSTPAID'),
        )
    METERINSTALLTYPE = (
        ('', '----CHOOSE A METER TYPE----'),
        ('nonsmart', 'NON SMART'),
        ('smart', 'SMART'),
    )
    METERREADABLE = (
        ('', '----CHOOSE A STATUS----'),
        ('yes', 'YES'),
        ('no', 'NO'),
    )
    NOTOKAYSTATUS= (
        ('','----CHOOSE A STATUS----'),
        ('loosejoints','LOOSE JOINTS'),
        ('noearth','NO EARTH'),
        ('demolishedpremises','DEMOLISHED PREMISES'),
        ('vacant','VACANT'),
        ('nometertails','NO METER TAILS'),
        ('loosemeterbox','LOOSE METERBOX'),
        )

    meterno = models.CharField(verbose_name=_("Meter Number"), unique=True, max_length=100)
    accountno = models.CharField(verbose_name=_("Account Number"), max_length=100, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    phase = models.CharField(verbose_name=_("Phase Status"), max_length=50, choices=PHASESTATUS, null=True,blank=True)
    meter_type = models.CharField(verbose_name=_("Meter Installation Type"), max_length=50, choices=METERINSTALLTYPE,
                                  null=True, blank=True)
    meteringstatus = models.CharField(verbose_name=_("Metering Status"),max_length=50, choices=METERINGSTATUS)
    installationstatus = models.CharField(verbose_name=_("Installation Status"),max_length=50, choices=INSTALLATIONSTATUS)
    faultystatus = models.CharField(verbose_name=_("Faulty Status"),max_length=50, choices=FAULTYSTATUS, null=True, blank=True, default='NULL')
    tamperedstatus = models.CharField(verbose_name=_("Tampered Status"),max_length=50, choices=TAMPEREDSTATUS, null=True, blank=True)
    bypassstatus = models.CharField(verbose_name=_("Bypass Status"),max_length=50, choices=BYPASSSTATUS, null=True, blank=True)
    notokaystatus = models.CharField(verbose_name=_("Not Okay Status"),max_length=50, choices=NOTOKAYSTATUS, null=True, blank=True)
    meter_readable = models.CharField(verbose_name=_("Meter Readable"), max_length=50, choices=METERREADABLE, null=True,
                                      blank=True)
    reading = models.IntegerField(verbose_name=_("Meter Reading(This is a required Field)"), help_text="Required")
    inspector = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='insp_public_lighting_notintarget')
    public_l_img = models.ImageField(upload_to="images/publicl/%Y/%m/%d/",verbose_name=_('CLEAR IMAGE UPLOAD(This is Required)'))
    metertype = models.CharField(verbose_name=_("Type Of Meter"),max_length=50, choices=METERTYPE, null=True, blank=True)
    comment = models.TextField(verbose_name=_('Any Comment'), null=True, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='county_public_lighting_notintarget')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='region_public_lighting_notinTarget')
    y = models.CharField(_('Y'), max_length=255)
    x = models.CharField(_('X'), max_length=255)
    incms = models.BooleanField(verbose_name=_('Back Office Resolve'),default=False)
    nextlevel = models.BooleanField(verbose_name=_('Back Office Level'), default=False)
    billed = models.BigIntegerField(verbose_name=_('Rebilled Amount'),default=0)
    system_reading = models.IntegerField(verbose_name=_('System Reading'), blank=True, null=True)
    consumption = models.IntegerField(verbose_name=_('Usage'), blank=True, null=True)
    units = models.IntegerField(verbose_name=_("Units"),null=True, blank=True)


    def __str__(self):
        return  self.meterno

class Largepower_accounts(models.Model):
    accountno = models.CharField(verbose_name=_("Account Number"), null=True, blank=True,max_length=100)
    srn = models.CharField(verbose_name=_("SRN"), null=True, blank=True, max_length=100)
    meterno = models.CharField(verbose_name=_("MEter Number"), null=True, blank=True,max_length=100)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    asigned = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return  self.meterno

class Lp_typeofindustry(models.Model):
    name = models.CharField(verbose_name=_("Name"), null=True, blank=True, max_length=100)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    asigned = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return  self.name

class Largepower_accounts_2024(models.Model):
    accountno = models.CharField(verbose_name=_("Account Number"), null=True, blank=True,max_length=100)
    srn = models.CharField(verbose_name=_("SRN"), null=True, blank=True, max_length=100)
    meterno = models.CharField(verbose_name=_("MEter Number"), null=True, blank=True,max_length=100)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    asigned = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    status = models.BooleanField(default=False)
    inspection_status = models.IntegerField(default=0)
    customer_data = models.IntegerField(default=0)
    sealing_data = models.IntegerField(default=0)
    ctvt_data = models.IntegerField(default=0)
    zera_test = models.IntegerField(default=0)
    meter_rading = models.IntegerField(default=0)
    otherinfo = models.IntegerField(default=0)
    final_sub = models.IntegerField(default=0)
    current = models.IntegerField(default=0)
    ctvt_mismatch = models.CharField(max_length=3, blank=True, null=True)
    zera_failed = models.CharField(max_length=3, blank=True, null=True)
    currents_mismatch = models.CharField(max_length=3, blank=True, null=True)
    over_per = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return  self.meterno

class Lp_new_inspection(models.Model):
    lp = models.ForeignKey(Largepower_accounts_2024, on_delete=models.DO_NOTHING, null=True, related_name='lp_new_inspection')
    meterno = models.CharField(verbose_name=_("Meter Number"), null=True, blank=True,max_length=100, unique=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, related_name='lp_new_inspected_by')
    save_status = models.BooleanField(default=False)
    over_rem = models.TextField(null=True, blank=True)
    declaration = models.BooleanField(default=False)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='lp_new_inspection_county')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='lp_new_inspection_region')

    def __str__(self):
        return self.lp.meterno

INST = (
        ("", "----CHOOSE A STATUS----"),
        ("POLEMOUNTEDACCESSIBLE", "POLE MOUNTED ACCESSIBLE"),
        ("POLEMOUNTEDELEVATED", "POLE MOUNTED ELEVATED"),
        ("GROUNDMOUNTEDACCESSIBLE", " GROUND MOUNTED ACCESSIBLE"),
        ("GROUNDMOUNTEDELEVATED", " GROUND MOUNTED ELEVATED"),
        ("AMRMETERING", "AMR METERING"),
    )
class Lp_inspect_customerData(models.Model):
    lp = models.OneToOneField(Lp_new_inspection, on_delete=models.CASCADE, null=True, related_name='lp_customerdata')
    meterno = models.CharField(max_length=100, null=True, blank=True)
    srn = models.CharField(max_length=100, null=True, blank=True)
    accountno = models.CharField(max_length=100, null=True, blank=True)
    type_of_industry = models.ForeignKey(Lp_typeofindustry, on_delete=models.DO_NOTHING, null=True,related_name='industry_type')
    smart_meter_i = models.CharField(max_length=100, choices=INST, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.lp.lp.meterno

class LP_inspection_sealing(models.Model):
    lp = models.OneToOneField(Lp_new_inspection, on_delete=models.CASCADE, null=True, related_name='lp_sealing')
    prg_seal_init = models.CharField(max_length=100, null=True, blank=True)
    prg_seal_fin = models.CharField(max_length=100, null=True, blank=True)
    term_sl_init = models.CharField(max_length=100, null=True, blank=True, help_text="Initail and Final cannot be the same")
    term_sl_fin = models.CharField(max_length=100, null=True, blank=True)
    testb_sl_init = models.CharField(max_length=100, null=True, blank=True)
    testb_sl_fin = models.CharField(max_length=100, null=True, blank=True)
    body_sl_init = models.CharField(max_length=100, null=True, blank=True)
    body_sl_fin = models.CharField(max_length=100, null=True, blank=True)
    smart_meter_sl_init = models.CharField(max_length=100, null=True, blank=True,help_text="Initail and Final cannot be the same")
    smart_meter_sl_fin = models.CharField(max_length=100, null=True, blank=True)
    amr_sl_init = models.CharField(max_length=100, null=True, blank=True,help_text="Initail and Final cannot be the same")
    amr_sl_fin = models.CharField(max_length=100, null=True, blank=True)
    is_amr = models.CharField(max_length=5, null=True, blank=True)
    other_sl_init = models.CharField(max_length=100, null=True, blank=True)
    other_sl_fin = models.CharField(max_length=100, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.lp.lp.meterno

INST = (
        ('', '----CHOOSE A STATUS----'),
        ('3P3W', '3P3W'),
        ('3P4W', '3P4W'),
    )
MVOLT = (
        ('', '----CHOOSE A STATUS----'),
        ('1/1', '1/1'),
        ('11000/110', '11000/110'),
        ('132000/100', '132000/100'),
        ('132000/110', '132000/110'),
        ('220000/110', '220000/110'),
        ('33000/110', '33000/110'),
        ('66000/110', '66000/110'),
    )
CTRATIO = (
        ('', '----CHOOSE A STATUS----'),
        ('1/1', '1/1'),
        ('100/1', '100/1'),
        ('100/5', '100/5'),
        ('1000/5', '1000/5'),
        ('1200/5', '1200/5'),
        ('150/1', '150/1'),
        ('150/5', '150/5'),
        ('1500/5', '1500/5'),
        ('200/1', '200/1'),
        ('200/5', '200/5'),
        ('2000/5', '2000/5'),
        ('25/1', '25/1'),
        ('250/5', '250/5'),
        ('30/1', '30/1'),
        ('300/1', '300/1'),
        ('300/5', '300/5'),
        ('360/1', '360/1'),
        ('40/5', '40/5'),
        ('400/1', '400/1'),
        ('400/5', '400/5'),
        ('50/1', '50/1'),
        ('50/5', '50/5'),
        ('500/5', '500/5'),
        ('800/1', '800/1'),
        ('800/5', '800/5'),

    )
YESNO = (
        ('', '----CHOOSE A STATUS----'),
        ('YES', 'YES'),
        ('NO', 'NO'),
    )
class Lp_inspect_ctvt(models.Model):
    lp = models.OneToOneField(Lp_new_inspection, on_delete=models.CASCADE, null=True, related_name='lp_ctvt')
    meter_config = models.CharField(max_length=20, choices=INST, null=True)
    meter_voltage = models.CharField(max_length=20, choices=MVOLT, null=True)
    ct_ratio_prmed = models.CharField(max_length=20, choices=CTRATIO, null=True)
    ctratio_img = models.ImageField(upload_to="images/lp2024/ctratio/%Y/%m/%d/", default='images/default.jpg')
    ct_ratio_inst = models.CharField(max_length=20, choices=CTRATIO, null=True)
    vt_ratio_prmed = models.CharField(max_length=20, choices=MVOLT, null=True)
    amr_recovered = models.CharField(max_length=20, choices=YESNO, null=True)
    ctvt_match = models.CharField(max_length=20, choices=YESNO, null=True)
    ctvt_mismatch_text = models.TextField(null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.lp.lp.meterno

class Lp_inspect_zeratest(models.Model):
    lp = models.OneToOneField(Lp_new_inspection, on_delete=models.CASCADE, null=True, related_name='lp_zeratest')
    zeratest = models.CharField(max_length=20, choices=YESNO, null=True)
    error_trial = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    error_test_rem = models.TextField(null=True, blank=True)
    register_error = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    register_error_rem = models.TextField(null=True, blank=True)
    meter_passed = models.CharField(max_length=20, choices=YESNO, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.lp.lp.meterno

class Lp_inspect_current(models.Model):
    lp = models.OneToOneField(Lp_new_inspection, on_delete=models.CASCADE, null=True, related_name='lp_current')
    rphase_amcoder = models.CharField(max_length=255, null=True, blank=True)
    rphase_meter = models.CharField(max_length=255, null=True, blank=True)
    yphase_amcoder = models.CharField(max_length=255, null=True, blank=True)
    yphase_meter = models.CharField(max_length=255, null=True, blank=True)
    bphase_amcoder = models.CharField(max_length=255, null=True, blank=True)
    bphase_meter = models.CharField(max_length=255, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    load_balancing = models.TextField(null=True, blank=True)
    currents_range = models.CharField(max_length=20, choices=YESNO, null=True)


    def __str__(self):
        return self.lp.lp.meterno

class LP_meter_readings(models.Model):
    lp = models.OneToOneField(Lp_new_inspection, on_delete=models.CASCADE, null=True, related_name='lp_mreadings')
    meter_time_actual = models.TimeField(null=True, blank=True)
    meter_time_meter = models.TimeField(null=True, blank=True)
    meter_date_actual = models.DateField(null=True, blank=True)
    meter_date_meter = models.DateField(null=True, blank=True)
    kwh_180_cur = models.CharField(max_length=255, null=True, blank=True)
    kwh_180_mem = models.CharField(max_length=255, null=True, blank=True)
    reading_180_img = models.ImageField(
        upload_to="images/lp2024/reading180/%Y/%m/%d/",
        default="images/default.jpg"
    )
    reading_280_img = models.ImageField(
        upload_to="images/lp2024/reading280/%Y/%m/%d/",
        default="images/default.jpg"
    )
    kwh_280_cur = models.CharField(max_length=255, null=True, blank=True)
    kwh_280_mem = models.CharField(max_length=255, null=True, blank=True)
    kva_960_cur = models.CharField(max_length=255, null=True, blank=True)
    kva_960_mem = models.CharField(max_length=255, null=True, blank=True)
    kwh_181_cur = models.CharField(max_length=255, null=True, blank=True)
    kwh_181_mem = models.CharField(max_length=255, null=True, blank=True)
    kwh_182_cur = models.CharField(max_length=255, null=True, blank=True)
    kwh_182_mem = models.CharField(max_length=255, null=True, blank=True)
    kwh_150_cur = models.CharField(max_length=255, null=True, blank=True)
    kwh_150_mem = models.CharField(max_length=255, null=True, blank=True)
    kva_970_cur = models.CharField(max_length=255, null=True, blank=True)
    kva_970_mem = models.CharField(max_length=255, null=True, blank=True)
    kwh_170_cur = models.CharField(max_length=255, null=True, blank=True)
    kwh_170_mem = models.CharField(max_length=255, null=True, blank=True)
    r_phase_v = models.CharField(max_length=255, null=True, blank=True)
    y_phase_v = models.CharField(max_length=255, null=True, blank=True)
    b_phase_v = models.CharField(max_length=255, null=True, blank=True)
    r_phase_c = models.CharField(max_length=255, null=True, blank=True)
    y_phase_c = models.CharField(max_length=255, null=True, blank=True)
    b_phase_c = models.CharField(max_length=255, null=True, blank=True)
    pw_f = models.CharField(max_length=255, null=True, blank=True)
    m_remarks = models.TextField(null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return self.lp.lp.meterno

class Lp_inspect_info(models.Model):
    lp = models.OneToOneField(Lp_new_inspection, on_delete=models.CASCADE, null=True, related_name='lp_solar')
    solar_installed = models.CharField(max_length=20, choices=YESNO, null=True)
    solar_size = models.CharField(max_length=255, null=True, blank=True)
    dt_installation = models.DateField(null=True, blank=True)
    overal_rem = models.TextField(null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return self.lp.lp.meterno
class Largepower_inspection(models.Model):
    SMARTMETER = (
        ('', '----CHOOSE A STATUS----'),
        ('yes', 'YES'),
        ('no', 'NO'),
    )
    SMARTMETER1 = (
        ('', '----CHOOSE A STATUS----'),
        ('yes', 'YES'),
        ('no', 'NO'),
        ('none', 'N/A'),
    )
    INDUSTRYTYPE = (
        ('', '----CHOOSE A STATUS----'),
        ('ACADEMIC_INSTITUTIONS', 'ACADEMIC INSTITUTIONS'),
        ('AGRIBUSINESS', 'AGRIBUSINESS'),
        ('CONSTRUCTION', 'CONSTRUCTION'),
        ('COUNTY_GOV_OFFICES', 'COUNTY GOV OFFICES'),
        ('ACADEMIC_INSTITUTIONS', 'ACADEMIC INSTITUTIONS'),
        ('ENTERTAINMENT_JOINT', 'ENTERTAINMENT JOINT'),
        ('FOOD_PROCESSING', 'FOOD PROCESSING'),
        ('FOREIGN_EMBASSY_MISSION', 'FOREIGN EMBASSY/MISSION'),
        ('GOVT_PARASTATAL', 'GOVERNMENT PARASTATAL'),
        ('HOSPITAL', 'HOSPITAL'),
        ('HOSPITALITY', 'HOSPITALITY'),
        ('HOUSING', 'HOUSING'),
        ('IRRIGATION_SCHEME', 'IRRIGATION SCHEME'),
        ('AGRIBUSINESS', 'AGRIBUSINESS'),
        ('MINING', 'MINING'),
        ('MULTI_USE_OFFICE_COMPLEX', 'MULTI-USE OFFICE COMPLEX'),
        ('POWER_GENERATION', 'POWER GENERATION'),
        ('RESIDENTIAL_PREMISES', 'RESIDENTIAL PREMISES'),
        ('SERVICE', 'SERVICE'),
        ('SHOPPING_MALL', 'SHOPPING MALL'),
        ('STONE_QUARRY', 'STONE QUARRY'),
        ('SUPERMARKET', 'SUPERMARKET'),
        ('TEXTILE_INDUSTRY', 'TEXTILE INDUSTRY'),
        ('WATER_COMPANY', 'WATER COMPANY'),
        ('MANUFACTURING', 'MANUFACTURING'),
    )
    MPCC = (
        ('', '----CHOOSE A STATUS----'),
        ('3P3W', '3P3W'),
        ('3P4W', '3P4W'),
    )
    METERVOLTAGE = (
        ('', '----CHOOSE A STATUS----'),
        ('0.415kV', '0.415kV'),
        ('11kV', '11kV'),
        ('33kV', '33kV'),
        ('66kV', '66kV'),
        ('132kV', '132kV'),
        ('220kV', '220kV'),
    )
    VTRATION = (
        ('', '----CHOOSE A STATUS----'),
        ('1:1V', '1:1V'),
        ('11,000/110V', '11,000/110V'),
        ('33,000/110V', '33,000/110V'),
        ('66,000/110V', '66,000/110V'),
        ('132,000/110V', '132,000/110V'),
        ('220,000/110V', '220,000/110V'),
    )
    CTRATION = (
        ('', '----CHOOSE CT----'),
        ('1:1A', '1:1A'),
        ('200/5A', '200/5A'),
        ('300/5A', '300/5A'),
        ('500/5A', '500/5A'),
        ('1000/5A', '1000/5A'),
        ('1500/5A', '1500/5A'),
        ('2000/5A', '2000/5A'),
        ('100/1A', '100/1A'),
        ('100/5A', '100/5A'),
        ('200/1A', '200/1A'),
        ('300/1A', '300/1A'),
        ('400/1A', '400/1A'),
        ('600/1A', '600/1A'),
        ('120/5A', '120/5A'),
        ('1200/5A', '1200/5A'),
        ('150/1A', '150/1A'),
        ('150/5A', '150/5A'),
        ('25/1A', '25/1A'),
        ('250/5A', '250/5A'),
        ('30/1A', '30/1A'),
        ('360/1A', '360/1A'),
        ('40/5A', '40/5A'),
        ('400/5A', '400/5A'),
        ('50/1A', '50/1A'),
        ('50/5A', '50/5A'),
        ('800/1A', '800/1A'),
        ('800/5A', '800/5A'),
        ('none', 'N/A'),
    )
    AMRRECOVERED = (
        ('', '----CHOOSE A STATUS----'),
        ('yes', 'YES'),
        ('no', 'NO'),
        ('na', 'NOT AVAILABLE'),
    )
    LOADBALANCING = (
        ('', '----CHOOSE A STATUS----'),
        ('okay', 'OKAY'),
        ('poor', 'POOR'),
        ('na', 'N/A'),
    )
    target = models.ForeignKey(Largepower_accounts, on_delete=models.SET_NULL, null=True, related_name='lp_insp_target')
    meterno = models.CharField(verbose_name=_("Meter Number"), unique=True, max_length=100)
    accountno = models.CharField(verbose_name=_("Account Number"), max_length=100, null=True, blank=True)
    y = models.CharField(_('Y'), max_length=255)
    x = models.CharField(_('X'), max_length=255)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspector = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='lp_inspected_by')
    smartmeter = models.CharField(verbose_name=_("Smart Meter"), max_length=10, choices=SMARTMETER,help_text='This is required')
    type_of_industry = models.CharField(verbose_name=_("Industry Type"), max_length=50, choices=INDUSTRYTYPE, help_text='This is required')
    meterbox_enclosure_seal_b4 =  models.CharField(null=True, blank=True, max_length=100)
    meterbox_enclosure_seal_after = models.CharField(null=True, blank=True,  max_length=100)
    meterbox_terminal_seal_b4 = models.CharField(null=True, blank=True,  max_length=100)
    meterbox_terminal_seal_after = models.CharField(null=True, max_length=100, help_text='Required Field')
    testblock_seal_b4 = models.CharField(null=True, max_length=100)
    testblock_seal_after = models.CharField(null=True,  max_length=100)
    meterbody_seal_b4 = models.CharField(null=True, max_length=100)
    meterbody_seal_after = models.CharField(null=True,  max_length=100)
    ctchamber_seal_b4 = models.CharField(null=True,  max_length=100,blank=True)
    ctchamber_seal_after = models.CharField(null=True,  max_length=100,blank=True)
    mpcc = models.CharField(max_length=50, choices=MPCC)
    metervoltage = models.CharField(max_length=50, choices=METERVOLTAGE)
    ctratio_ci = models.CharField(max_length=50, choices=CTRATION,default='none')
    ctratio_programed = models.CharField(max_length=50, choices=CTRATION)
    ctratio_installedsite = models.CharField(max_length=50, choices=CTRATION)
    ctratio_img = models.ImageField(upload_to="images/lp/ctratio/%Y/%m/%d/",default='images/default.jpg')
    ctratio_ci_match = models.CharField(verbose_name=_("CT Ration Mismatch"), max_length=10, choices=SMARTMETER1,default='none')
    ctratio_ci_match_rsn = models.CharField(null=True, blank=True, max_length=255, help_text='rqquired Field')
    vtratio = models.CharField(verbose_name=_("VT Ratio"), max_length=20, choices=VTRATION)
    amrrecovered = models.CharField(verbose_name=_("AMR RECOVERED"), max_length=10, choices=AMRRECOVERED)
    total_180 =  models.CharField(null=True,  max_length=100)
    total_180_img = models.ImageField(upload_to="images/lp/reading180/%Y/%m/%d/", verbose_name=_('Reading 1.8.0 IMAGE UPLOAD(This is Required)'))
    max_kva_960 =  models.CharField(null=True,  max_length=100)
    max_kw_150 =  models.CharField(null=True,  max_length=100)
    t1_181 =  models.CharField(null=True,  max_length=100)
    t2_182 =  models.CharField(null=True,  max_length=100)
    r_energy = models.CharField(null=True, blank=True, max_length=100)
    reverse_consumption = models.CharField(verbose_name=_("Reverse Consumption"), max_length=10, choices=SMARTMETER)
    reverse_consumption_rsn = models.CharField(null=True, blank=True, max_length=255)
    current_red=models.CharField(null=True, blank=True, max_length=255)
    current_yellow = models.CharField(null=True, blank=True, max_length=255)
    current_blue = models.CharField(null=True, blank=True, max_length=255)
    voltage_red = models.CharField(null=True, blank=True, max_length=255)
    voltage_yellow = models.CharField(null=True, blank=True, max_length=255)
    voltage_blue = models.CharField(null=True, blank=True, max_length=255)
    moduleinstalled = models.CharField(verbose_name=_("Module Installed"), max_length=10, choices=SMARTMETER1,default='none')
    modulecomm_ci = models.CharField(verbose_name=_("Module Communicate to C&I"), max_length=10, choices=SMARTMETER1,default='none')
    modulecom_not_rsn = models.CharField(null=True, blank=True, max_length=255, help_text='Requird Field')
    civector_img = models.ImageField(upload_to="images/lp/civector/%Y/%m/%d/", default='images/default.jpg')
    sim_serial = models.CharField(null=True, blank=True, max_length=100, help_text='optional')
    sim_provider = models.CharField(null=True, blank=True, max_length=100)
    zera_test = models.CharField(verbose_name=_("Zera Test Done"), max_length=10, choices=SMARTMETER)
    error_register =  models.CharField(null=True, blank=True, max_length=100)
    loadbalance = models.CharField(verbose_name=_("LOAD BALACING"), max_length=10, choices=LOADBALANCING, default='na')
    redphase_zera = models.CharField(null=True, blank=True, max_length=100)
    redphase_meter =  models.CharField(null=True, blank=True, max_length=100)
    redphase_clamp = models.CharField(null=True, blank=True, max_length=100)
    yellowphase_zera =  models.CharField(null=True, blank=True, max_length=100)
    yellowphase_meter =  models.CharField(null=True, blank=True, max_length=100)
    yellowphase_clamp =  models.CharField(null=True, blank=True, max_length=100)
    bluephase_zera =  models.CharField(null=True, blank=True, max_length=100)
    bluephase_meter =  models.CharField(null=True, blank=True, max_length=100)
    bluephase_clamp = models.CharField(null=True, blank=True, max_length=100)
    powerfactor_value =  models.CharField(null=True, blank=True, max_length=100)
    remarks = models.TextField(verbose_name=_('Any Comment'), null=True, blank=True)
    collaborate = models.CharField(null=True, blank=True, max_length=100)
    total_180_incms =  models.CharField(null=True, blank=True, max_length=100)
    commit_inspection = models.BooleanField(default=False)
    arethereanomalies = models.CharField(max_length=10, choices=SMARTMETER)
    anomalies_list = models.CharField(null=True, blank=True, max_length=255)
    anomalies_addressed_insp = models.CharField(max_length=10, choices=SMARTMETER)
    anomalies_addressed_insp_list = models.CharField(null=True, blank=True, max_length=255)
    fallback_req  = models.CharField(max_length=10, choices=SMARTMETER)
    fallback_activities = models.CharField(null=True, blank=True, max_length=255)
    metered_correctly = models.CharField(max_length=10, choices=SMARTMETER)
    commit_annomalies = models.BooleanField(default=False)
    oktoworkwith =  models.CharField(max_length=10, choices=SMARTMETER)

    def __str__(self):
        return  self.target.meterno

# DOMESTIC CUSTOMERS TARGET
class Domestic_customers(models.Model):
    dc_meterno = models.CharField(
        max_length=20, verbose_name=_("Meter Number"), unique=True
    )
    dc_accountno = models.CharField(max_length=20, verbose_name=_("Account Number"))
    itin = models.CharField(
        verbose_name=_("Itinerary"), max_length=200, blank=True, null=True
    )
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    sector = models.CharField(
        max_length=100, verbose_name=_("Sector"), null=True, blank=True
    )
    zone = models.CharField(
        max_length=100, verbose_name=_("Zone"), null=True, blank=True
    )
    customer_name = models.CharField(
        verbose_name=_("Customer Name"), max_length=200, blank=True, null=True
    )
    contract_type = models.CharField(
        verbose_name=_("Contract Type"), max_length=50, null=True, blank=True
    )
    cod_tarrif = models.CharField(
        verbose_name=_("Tarrif"), max_length=50, null=True, blank=True
    )
    supply_phase = models.CharField(
        verbose_name=_("Supply Phase"), max_length=100, blank=True, null=True
    )
    supply_address = models.CharField(
        verbose_name=_("Supply Address"), max_length=255, blank=True, null=True
    )
    longitute = models.CharField(_("Longitude"), max_length=255, null=True, blank=True)
    latitude = models.CharField(_("Latitude"), max_length=255, null=True, blank=True)
    avg_units = models.DecimalField(_("Average Units"), max_digits=12, decimal_places=2)
    status = models.BooleanField(default=False)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.dc_meterno

# DC Inspection
class Dc_inspection(models.Model):
    METERINGSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("okay", "OKAY"),
        ("faulty", "FAULTY"),
        ("tampered", "TAMPERED"),
        ("bypassed", "BYPASSED"),
        ("nometer", "NO METER"),
    )
    INSTALLATIONSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("okay", "OKAY"),
        ("notokay", "NOT OKAY"),
    )
    FAULTYSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("blankscreen", "BLANK SCREEN"),
        ("noncommunicating", "NON COMMUNICATING"),
        ("obsolete", "OBSOLETE"),
        ("fadeddigits", "FADED DIGITS"),
        ("notpulsing", "NOT PULSING"),
        ("burnt", "BURNT"),
        ("batterylow", "BATTERY LOW"),
        ("cuifaulty", "CIU FAULTY"),
        ("notabletoloadtoken", "NOT ABLE TO LOAD TOKEN"),
        ("looseglass", "LOOSE GLASS"),
    )
    TAMPEREDSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("brokenseaals", "BROKEN SEALS"),
        ("disabledvoltage", "DISABLED VOLTAGE"),
        ("disabledcurrent", "DISABLED CURRENT"),
        ("brokenglass", "BROKEN GLASS"),
        ("droppedlink", "DROPPED LINK"),
        ("damagedmeter", "DAMAGED METER"),
        ("foreignobjects", "FOREIGN OBJECTS INTRODUCED"),
    )
    BYPASSSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("puncturedcable", "PUNCTURED CABLE"),
        ("drilledcutout", "DRILLED CUTOUT"),
    )
    METERTYPE = (
        ("", "----CHOOSE A PHASE TYPE----"),
        ("singlephase", "SINGLE PHASE"),
        ("threephase", "THREE PHASE"),
    )
    CONFTYPE = (
        ("", "----CHOOSE A METER TYPE----"),
        ("postpaid", "POSTPAID"),
        ("prepaid", "PREPAID"),
    )
    NOTOKAYSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("loosejoints", "LOOSE JOINTS"),
        ("noearth", "NO EARTH"),
        ("demolishedpremises", "DEMOLISHED PREMISES"),
        ("vacant", "VACANT"),
        ("nometertails", "NO METER TAILS"),
        ("loosemeterbox", "LOOSE METERBOX"),
    )
    dc = models.ForeignKey(
        Domestic_customers,
        on_delete=models.SET_NULL,
        null=True,
        related_name="dc_target",
    )
    dc_meterno = models.CharField(
        max_length=20, verbose_name=_("Meter Number"), unique=True
    )
    dc_accountno = models.CharField(max_length=20, verbose_name=_("Account Number"))
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    dc_meteringstatus = models.CharField(
        verbose_name=_("Metering Status"), max_length=50, choices=METERINGSTATUS
    )
    dc_installationstatus = models.CharField(
        verbose_name=_("Installation Status"), max_length=50, choices=INSTALLATIONSTATUS
    )
    dc_faultystatus = models.CharField(
        verbose_name=_("Faulty Status"),
        max_length=50,
        choices=FAULTYSTATUS,
        null=True,
        blank=True,
        default="NULL",
    )
    dc_tamperedstatus = models.CharField(
        verbose_name=_("Tampered Status"),
        max_length=50,
        choices=TAMPEREDSTATUS,
        null=True,
        blank=True,
    )
    dc_bypassstatus = models.CharField(
        verbose_name=_("Bypass Status"),
        max_length=50,
        choices=BYPASSSTATUS,
        null=True,
        blank=True,
    )
    dc_notokaystatus = models.CharField(
        verbose_name=_("Not Okay Status"),
        max_length=50,
        choices=NOTOKAYSTATUS,
        null=True,
        blank=True,
    )
    dc_reading = models.CharField(
        verbose_name=_("Meter Reading"),
        blank=True,
        null=True,
        max_length=100,
        help_text="Only required if 'Meter' is Postpaid.",
    )
    dc_inspector = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, related_name="dc_inspector"
    )
    dc_meterimg = models.ImageField(
        upload_to="images/dc/%Y/%m/%d/",
        null=True,
        blank=True,
        default="images/default.jpg",
    )
    dc_metertype = models.CharField(
        verbose_name=_("Type Of Meter"),
        max_length=50,
        choices=METERTYPE,
        null=True,
        blank=True,
    )
    dc_conf_type = models.CharField(
        verbose_name=_("Type Of Meter"),
        max_length=50,
        choices=CONFTYPE,
        null=True,
        blank=True,
    )
    dc_comment = models.TextField(verbose_name=_("Any Comment"), null=True, blank=True)
    dc_county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='dc_county_rtn')
    dc_region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='dc_region_rtn')
    dc_sealno = models.CharField(
        max_length=50, verbose_name=_("Seal Number"), blank=True, null=True
    )
    incms_status = models.BooleanField(default=False)
    incms_nextlevel = models.BooleanField(default=False)
    r_units = models.DecimalField(_("Billed Units"), max_digits=12, decimal_places=2, default=0)
    system_reading = models.DecimalField(
        _("System reading"), max_digits=12, decimal_places=2, default=0
    )
    anomaly_status = models.BooleanField(default=False)
    y = models.CharField(_("Y"), max_length=255)
    x = models.CharField(_("X"), max_length=255)

    def __str__(self):
        return self.meterno
        
class Generation_stations(models.Model):
    srn = models.CharField(verbose_name=_("SRN"), null=True, blank=True, max_length=100)
    meterno = models.CharField(
        verbose_name=_("Meter Number"), null=True, blank=True, max_length=100
    )
    plant_name = models.CharField(max_length=255, blank=True, null=True)
    make = models.CharField(max_length=255, blank=True, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    vtr =  models.CharField(max_length=255, blank=True, null=True)
    ctr = models.CharField(max_length=255, blank=True, null=True)
    wiring = models.CharField(max_length=255, blank=True, null=True)
    circuit_metered = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.meterno

class Generation_stations_inspection(models.Model):
    GENERATIONTYPE = (
        ("", "----CHOOSE A TYPE----"),
        ("thermal", "THERMAL"),
        ("hydro", "HYDRO"),
        ("geothermal", "GEOTHERMAL"),
        ("wind", "WIND"),
        ("solar", "SOLAR"),
        ("biogas", "BIOGAS"),
    )
    NOTESTEQUIPMENT = (
        ("", "----CHOOSE NUMBER----"),
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
    )
    TESTEQUIPMENT = (
        ("", "----CHOOSE TYPE----"),
        ("omicroncpc100", "OMICRON CPC 100"),
        ("omicroncta", "OMICRON CTA"),
        ("isasts5000", "ISA STS 5000"),
        ("redphaseinstrument590", "RED PHASE INSTRUMENT 590"),
        ("zeramt320", "ZERA MT 320"),
    )
    genstn = models.ForeignKey(
        Generation_stations,
        on_delete=models.SET_NULL,
        null=True,
        related_name="genstn_target",
    )
    meterno = models.CharField(
        verbose_name=_("Meter Number"), unique=True, max_length=100
    )
    generation_type = models.CharField(
        verbose_name=_("Generation Type"),
        max_length=50,
        choices=GENERATIONTYPE,
        help_text="This is required",
    )
    y = models.CharField(_("Y"), max_length=255)
    x = models.CharField(_("X"), max_length=255)
    md_reset_b4 = models.CharField(null=True, blank=True, max_length=100)
    md_reset_after = models.CharField(null=True, blank=True, max_length=100)
    meterbox_terminal_seal_b4 = models.CharField(null=True, blank=True, max_length=100)
    meterbox_terminal_seal_after = models.CharField(
        null=True, max_length=100, help_text="Required Field"
    )
    testblock_seal_b4 = models.CharField(null=True, max_length=100)
    testblock_seal_after = models.CharField(null=True, max_length=100)
    meterbody_seal_b4 = models.CharField(null=True, max_length=100)
    meterbody_seal_after = models.CharField(null=True, max_length=100)
    noofequipments = models.CharField(
        verbose_name=_("Number Of Equipments"),
        max_length=5,
        choices=NOTESTEQUIPMENT,
        help_text="This is required",
    )
    testequipment = models.CharField(
        verbose_name=_("Generation Type"),
        max_length=50,
        choices=TESTEQUIPMENT,
        help_text="This is required",
        null=True,
        blank=True,
    )
    testequipment1 = models.CharField(
        verbose_name=_("Generation Type"),
        max_length=50,
        choices=TESTEQUIPMENT,
        help_text="This is required",
        null=True,
        blank=True,
    )
    testequipment2 = models.CharField(
        verbose_name=_("Generation Type"),
        max_length=50,
        choices=TESTEQUIPMENT,
        help_text="This is required",
        null=True,
        blank=True,
    )
    testequipment3 = models.CharField(
        verbose_name=_("Generation Type"),
        max_length=50,
        choices=TESTEQUIPMENT,
        help_text="This is required",
        null=True,
        blank=True,
    )
    equipment_srn = models.CharField(null=True, max_length=255, blank=True)
    equipment_srn1 = models.CharField(null=True, max_length=255, blank=True)
    equipment_srn2 = models.CharField(null=True, max_length=255, blank=True)
    equipment_srn3 = models.CharField(null=True, max_length=255, blank=True)
    portable_energy_std = models.CharField(null=True, max_length=255, blank=True)
    portable_srn = models.CharField(null=True, max_length=255, blank=True)
    accuracy_class = models.CharField(null=True, max_length=255, blank=True)
    relative_humid_start = models.CharField(null=True, max_length=255, blank=True)
    relative_humid_end = models.CharField(null=True, max_length=255, blank=True)
    relative_humid_avg = models.CharField(null=True, max_length=255, blank=True)
    temp_start = models.CharField(null=True, max_length=255, blank=True)
    temp_end = models.CharField(null=True, max_length=255, blank=True)
    temp_avg = models.CharField(null=True, max_length=255, blank=True)
    per_error_trial1 = models.CharField(null=True, max_length=255, blank=True)
    per_error_trial2 = models.CharField(null=True, max_length=255, blank=True)
    per_error_trial3 = models.CharField(null=True, max_length=255, blank=True)
    avg_per_error = models.CharField(null=True, max_length=255, blank=True)
    results_remarks = models.TextField(null=True, blank=True)
    register_trail1 = models.CharField(null=True, max_length=255, blank=True)
    register_trail2 = models.CharField(null=True, max_length=255, blank=True)
    register_avg_per_error = models.CharField(null=True, max_length=255, blank=True)
    register_remarks = models.TextField(null=True, blank=True)
    ct_y_serialno = models.CharField(null=True, max_length=255, blank=True)
    ct_y_manufacturer = models.CharField(null=True, max_length=255, blank=True)
    ct_y_ratedvoltage = models.CharField(null=True, max_length=255, blank=True)
    ct_y_testobject = models.CharField(null=True, max_length=255, blank=True)
    ct_y_nameplate_ratio = models.CharField(null=True, max_length=255, blank=True)
    ct_y_testvoltage = models.CharField(null=True, max_length=255, blank=True)
    ct_y_turnsratio = models.CharField(null=True, max_length=255, blank=True)
    ct_y_per_ratiodeviation = models.CharField(null=True, max_length=255, blank=True)
    ct_y_remarks = models.TextField(null=True, blank=True)
    ct_b_serialno = models.CharField(null=True, max_length=255, blank=True)
    ct_b_manufacturer = models.CharField(null=True, max_length=255, blank=True)
    ct_b_ratedvoltage = models.CharField(null=True, max_length=255, blank=True)
    ct_b_testobject = models.CharField(null=True, max_length=255, blank=True)
    ct_b_nameplate_ratio = models.CharField(null=True, max_length=255, blank=True)
    ct_b_testvoltage = models.CharField(null=True, max_length=255, blank=True)
    ct_b_turnsratio = models.CharField(null=True, max_length=255, blank=True)
    ct_b_per_ratiodeviation = models.CharField(null=True, max_length=255, blank=True)
    ct_b_remarks = models.TextField(null=True, blank=True)
    ct_r_serialno = models.CharField(null=True, max_length=255, blank=True)
    ct_r_manufacturer = models.CharField(null=True, max_length=255, blank=True)
    ct_r_ratedvoltage = models.CharField(null=True, max_length=255, blank=True)
    ct_r_testobject = models.CharField(null=True, max_length=255, blank=True)
    ct_r_nameplate_ratio = models.CharField(null=True, max_length=255, blank=True)
    ct_r_testvoltage = models.CharField(null=True, max_length=255, blank=True)
    ct_r_turnsratio = models.CharField(null=True, max_length=255, blank=True)
    ct_r_per_ratiodeviation = models.CharField(null=True, max_length=255, blank=True)
    ct_r_remarks = models.TextField(null=True, blank=True)
    vt_y_serialno = models.CharField(null=True, max_length=255, blank=True)
    vt_y_manufacturer = models.CharField(null=True, max_length=255, blank=True)
    vt_y_ratedvoltage = models.CharField(null=True, max_length=255, blank=True)
    vt_y_testobject = models.CharField(null=True, max_length=255, blank=True)
    vt_y_nameplate_ratio = models.CharField(null=True, max_length=255, blank=True)
    vt_y_testvoltage = models.CharField(null=True, max_length=255, blank=True)
    vt_y_turnsratio = models.CharField(null=True, max_length=255, blank=True)
    vt_y_per_ratiodeviation = models.CharField(null=True, max_length=255, blank=True)
    vt_y_remarks = models.TextField(null=True, blank=True)
    vt_b_serialno = models.CharField(null=True, max_length=255, blank=True)
    vt_b_manufacturer = models.CharField(null=True, max_length=255, blank=True)
    vt_b_ratedvoltage = models.CharField(null=True, max_length=255, blank=True)
    vt_b_testobject = models.CharField(null=True, max_length=255, blank=True)
    vt_b_nameplate_ratio = models.CharField(null=True, max_length=255, blank=True)
    vt_b_testvoltage = models.CharField(null=True, max_length=255, blank=True)
    vt_b_turnsratio = models.CharField(null=True, max_length=255, blank=True)
    vt_b_per_ratiodeviation = models.CharField(null=True, max_length=255, blank=True)
    vt_b_remarks = models.TextField(null=True, blank=True)
    vt_r_serialno = models.CharField(null=True, max_length=255, blank=True)
    vt_r_manufacturer = models.CharField(null=True, max_length=255, blank=True)
    vt_r_ratedvoltage = models.CharField(null=True, max_length=255, blank=True)
    vt_r_testobject = models.CharField(null=True, max_length=255, blank=True)
    vt_r_nameplate_ratio = models.CharField(null=True, max_length=255, blank=True)
    vt_r_testvoltage = models.CharField(null=True, max_length=255, blank=True)
    vt_r_turnsratio = models.CharField(null=True, max_length=255, blank=True)
    vt_r_per_ratiodeviation = models.CharField(null=True, max_length=255, blank=True)
    vt_r_remarks = models.TextField(null=True, blank=True)
    reading_180 = models.CharField(max_length=255)
    reading_280 = models.CharField(max_length=255)
    img_180 = models.ImageField(upload_to="images/genstn/img180/%Y/%m/%d/")
    img_280 = models.ImageField(upload_to="images/genstn/img280/%Y/%m/%d/")
    cert = models.ImageField(upload_to="images/genstn/cert/%Y/%m/%d/")
    inspector = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="genstn_inspected_by",
    )
    team = models.CharField(null=True, max_length=255, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    overall_remarks = models.TextField(null=True, blank=True)
    confirmation = models.BooleanField()
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    yr_manufacturer = models.CharField(max_length=255, null=True, blank=True)
    meter_accuracy_class = models.CharField(max_length=255, null=True, blank=True)
    vt_chamber_r_initail = models.CharField(max_length=255, null=True, blank=True)
    vt_chamber_r_final = models.CharField(max_length=255, null=True, blank=True)
    vt_chamber_y_initail = models.CharField(max_length=255, null=True, blank=True)
    vt_chamber_y_final = models.CharField(max_length=255, null=True, blank=True)
    vt_chamber_b_initail = models.CharField(max_length=255, null=True, blank=True)
    vt_chamber_b_final = models.CharField(max_length=255, null=True, blank=True)
    ct_chamber_r_initail = models.CharField(max_length=255, null=True, blank=True)
    ct_chamber_r_final = models.CharField(max_length=255, null=True, blank=True)
    ct_chamber_y_initail = models.CharField(max_length=255, null=True, blank=True)
    ct_chamber_y_final = models.CharField(max_length=255, null=True, blank=True)
    ct_chamber_b_initail = models.CharField(max_length=255, null=True, blank=True)
    ct_chamber_b_final = models.CharField(max_length=255, null=True, blank=True)
    ct_yom_red = models.CharField(max_length=255, null=True, blank=True)
    vt_yom_red = models.CharField(max_length=255, null=True, blank=True)
    ct_yom_yellow = models.CharField(max_length=255, null=True, blank=True)
    vt_yom_yellow = models.CharField(max_length=255, null=True, blank=True)
    ct_yom_blue = models.CharField(max_length=255, null=True, blank=True)
    vt_yom_blue = models.CharField(max_length=255, null=True, blank=True)
    ct_noofcores_red = models.CharField(max_length=255, null=True, blank=True)
    vt_noofcores_red = models.CharField(max_length=255, null=True, blank=True)
    ct_noofcores_yellow = models.CharField(max_length=255, null=True, blank=True)
    vt_noofcores_yellow = models.CharField(max_length=255, null=True, blank=True)
    ct_noofcores_blue = models.CharField(max_length=255, null=True, blank=True)
    vt_noofcores_blue = models.CharField(max_length=255, null=True, blank=True)
    ct_connected_red = models.CharField(max_length=255, null=True, blank=True)
    vt_connected_red = models.CharField(max_length=255, null=True, blank=True)
    ct_connected_yellow = models.CharField(max_length=255, null=True, blank=True)
    vt_connected_yellow = models.CharField(max_length=255, null=True, blank=True)
    ct_connected_blue = models.CharField(max_length=255, null=True, blank=True)
    vt_connected_blue = models.CharField(max_length=255, null=True, blank=True)
    ct_accuracyclass_red = models.CharField(max_length=255, null=True, blank=True)
    vt_accuracyclass_red = models.CharField(max_length=255, null=True, blank=True)
    ct_accuracyclass_yellow = models.CharField(max_length=255, null=True, blank=True)
    vt_accuracyclass_yellow = models.CharField(max_length=255, null=True, blank=True)
    ct_accuracyclass_blue = models.CharField(max_length=255, null=True, blank=True)
    vt_accuracyclass_blue = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.meterno
        
class Telcos_rpl_target(models.Model):
    siteid = models.CharField(
        verbose_name=_("Site ID"), max_length=50, blank=True, null=True
    )
    sitename = models.CharField(
        verbose_name=_("Site ID"), max_length=255, blank=True, null=True
    )
    meterno = models.CharField(
        verbose_name=_("Meter Number"), blank=True, null=True, max_length=100
    )
    accountno = models.CharField(
        verbose_name=_("Account Number"), blank=True, null=True, max_length=100
    )
    county = models.ForeignKey(
        County, on_delete=models.SET_NULL, null=True, related_name="telcos_county_replace"
    )
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True, related_name="telcos_region_replace"
    )
    lon = models.CharField(_("Longitude"), max_length=255, blank=True, null=True)
    lat = models.CharField(_("Latitude"), max_length=255, blank=True, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    system_reading = models.IntegerField(
        verbose_name=_("System Reading"), blank=True, null=True
    )
    avgconsumption = models.IntegerField(verbose_name=_("avg"), blank=True, null=True)
    telcos_type = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.meterno

class Telcos_replacement(models.Model):
    METERINGSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("okay", "OKAY"),
        ("faulty", "FAULTY"),
        ("tampered", "TAMPERED"),
        ("bypassed", "BYPASSED"),
    )
    PHASESTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("single", "SINGLE PHASE"),
        ("threephase", "THREE PHASE"),
    )
    FAULTYSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("blankscreen", "BLANK SCREEN"),
        ("noncommunicating", "NON COMMUNICATING"),
        ("obsolete", "OBSOLETE"),
        ("fadeddigits", "FADED DIGITS"),
        ("notpulsing", "NOT PULSING"),
        ("burnt", "BURNT"),
        ("batterylow", "BATTERY LOW"),
        ("cuifaulty", "CIU FAULTY"),
        ("notabletoloadtoken", "NOT ABLE TO LOAD TOKEN"),
        ("looseglass", "LOOSE GLASS"),
    )
    TAMPEREDSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("brokenseaals", "BROKEN SEALS"),
        ("disabledvoltage", "DISABLED VOLTAGE"),
        ("disabledcurrent", "DISABLED CURRENT"),
        ("brokenglass", "BROKEN GLASS"),
        ("droppedlink", "DROPPED LINK"),
        ("damagedmeter", "DAMAGED METER"),
        ("foreignobjects", "FOREIGN OBJECTS INTRODUCED"),
    )
    BYPASSSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("puncturedcable", "PUNCTURED CABLE"),
        ("drilledcutout", "DRILLED CUTOUT"),
    )
    VALIDATESTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("yes", "YES"),
        ("no", "NO"),
    )
    siteid = models.CharField(verbose_name=_("Site ID"), max_length=50, unique=True)
    sitename = models.CharField(
        verbose_name=_("Site Name"), max_length=255, blank=True, null=True
    )
    txnumber = models.CharField(
        verbose_name=_("Transformer Number"), max_length=255, blank=True, null=True
    )
    feeder_name = models.CharField(
        verbose_name=_("Feeder Name"), max_length=255, blank=True, null=True
    )
    dedicated_lv = models.CharField(
        verbose_name=_("Is The LV Dedicated To Site?"), max_length=50, choices=VALIDATESTATUS
    )
    telcos = models.ForeignKey(
        Telcos_rpl_target,
        on_delete=models.SET_NULL,
        null=True,
        related_name="telcos_rplc_target",
    )
    oldmeter= models.CharField(
        verbose_name=_("Meter Number Removed"), unique=True, max_length=100
    )
    newmeter = models.CharField(
        verbose_name=_("Meter Number Installed"), unique=True, max_length=100
    )
    accountno = models.CharField(verbose_name=_("Account Number"), max_length=100, null=True,blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    phase = models.CharField(
        verbose_name=_("Phase Status"),
        max_length=50,
        choices=PHASESTATUS,
        null=True,
        blank=True,
    )
    meteringstatus = models.CharField(
        verbose_name=_("Metering Status"), max_length=50, choices=METERINGSTATUS
    )
    faultystatus = models.CharField(
        verbose_name=_("Faulty Status"),
        max_length=50,
        choices=FAULTYSTATUS,
        null=True,
        blank=True,
        default="NULL",
    )
    tamperedstatus = models.CharField(
        verbose_name=_("Tampered Status"),
        max_length=50,
        choices=TAMPEREDSTATUS,
        null=True,
        blank=True,
    )
    bypassstatus = models.CharField(
        verbose_name=_("Bypass Status"),
        max_length=50,
        choices=BYPASSSTATUS,
        null=True,
        blank=True,
    )
    removal_reading = models.IntegerField(
        verbose_name=_("Meter Removal Reading(This is a required Field)"), help_text="Required"
    )
    install_reading = models.IntegerField(
        verbose_name=_("Meter Install Reading(This is a required Field)"), help_text="Required"
    )
    inspector = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, related_name="telcos_rplc_inspector"
    )
    removal_img = models.ImageField(
        upload_to="images/telcos/removal/%Y/%m/%d/",
        verbose_name=_("CLEAR IMAGE OF REMOVED METER(This is Required)"),
    )
    install_img = models.ImageField(
        upload_to="images/telcos/install/%Y/%m/%d/",
        verbose_name=_("CLEAR IMAGE OF INSTALLED METER(This is Required)"),
    )
    comment = models.TextField(verbose_name=_("Any Comment"), null=True, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='county_repalcement')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='region_repalcement')
    y = models.CharField(_("Y"), max_length=255)
    x = models.CharField(_("X"), max_length=255)
    validated = models.CharField(
        verbose_name=_("Validated Status"), max_length=50, choices=VALIDATESTATUS
    )
    validate_status = models.BooleanField(default=False)
    nextlevel = models.BooleanField(verbose_name=_("Back Office Level"), default=False)
    billed = models.BigIntegerField(verbose_name=_("Rebilled Amount"), default=0)
    consumption = models.IntegerField(verbose_name=_("Usage"), default=0)
    units = models.IntegerField(verbose_name=_("Units"), null=True, blank=True)
    concurrence_status = models.BooleanField(default=False)
    concurrence = models.CharField(
        verbose_name=_("Do You Consent With The Information"), max_length=50, choices=VALIDATESTATUS, default='Pending'
    )
    concurrence_notes = models.TextField(verbose_name=_("Concurrence Notes"), null=True, blank=True)
    concurrence_staff = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, related_name="concurrence_saf"
    )
    seal_terminalcover = models.CharField(
        verbose_name=_("Terminal Cover Seal"), max_length=100, null=True, blank=True
    )
    seal_gprs = models.CharField(
        verbose_name=_("GPRS Module Cover Seal"), max_length=100, null=True, blank=True
    )
    gprs_ariel = models.CharField(
        verbose_name=_("Is The GPRS Ariel Installed?"), max_length=50, choices=VALIDATESTATUS, default='Pending'
    )

    def __str__(self):
        return self.newmeter

    @property
    def unbilled_units(self):
        return (int(self.telcos.system_reading)) - (int(self.removal_reading))
        
class Anomlalous_accounts(models.Model):
    meterno = models.CharField(
        max_length=255, blank=True, verbose_name=_("Meter Number"), unique=True
    )
    accountno = models.CharField(max_length=255, blank=True, null=True)
    county = models.ForeignKey(
        County,
        on_delete=models.SET_NULL,
        null=True,
        related_name="county_anomalous_target",
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        related_name="region_anomalous_target",
    )
    user = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, related_name="anomalous_user"
    )
    anomaly_type = models.CharField(max_length=100, blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    source_dt = models.DateTimeField(null=True)
    make = models.CharField(max_length=100, blank=True, null=True)
    incms_status = models.CharField(max_length=100, blank=True, null=True)
    itin = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    type = models.CharField(max_length=20, blank=True, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    sector = models.CharField(max_length=100, blank=True, null=True)
    zone = models.CharField(max_length=100, blank=True, null=True)
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    supply_address = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=["dtadd"])]
        ordering = [
            "-dtadd",
        ]

    def __str__(self):
        return self.meterno

class Anomalous_resolved(models.Model):
    FAULTYSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("replaced_faulty", "REPLACEMENT"),
        ("normalised_bypass", "NORMALISED METER"),
        ("found_meter_okay", "FOUND METER OKAY"),
    )
    TAMPEREDSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("replaced_tampered", "REPLACED TAMPERED"),
        ("found_okay", "FOUND METER OKAY"),
    )
    anomaly = models.ForeignKey(
        Anomlalous_accounts,
        on_delete=models.SET_NULL,
        null=True,
        related_name="anomalous_resolved",
    )
    meterno = models.CharField(
        max_length=255, blank=True, verbose_name=_("Meter Number")
    )
    new_meterno = models.CharField(max_length=255, blank=True, null=True)
    accountno = models.IntegerField(blank=True, null=True)
    comment = models.TextField(max_length=300, blank=True, null=True)
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="anomalous_resolved_user",
    )
    status = models.CharField(max_length=100, blank=True, null=True)
    county = models.ForeignKey(
        County,
        on_delete=models.SET_NULL,
        null=True,
        related_name="county_anomalous_resolved",
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        related_name="region_anomalous_resolved",
    )
    faultystatus = models.CharField(
        verbose_name=_("Change Status"),
        max_length=50,
        choices=FAULTYSTATUS,
    )
    tamperedstatus = models.CharField(
        verbose_name=_("Choose Status"),
        max_length=50,
        choices=TAMPEREDSTATUS,
    )
    user2 = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="anomalous_resolved_user2",
    )
    dtadd2 = models.DateTimeField(null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    meterimg = models.ImageField(
        default="default.jpg", upload_to="images/anomalous/%Y/%m/%d/"
    )
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    diffunits = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    recoveries = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    incms_status = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["dtadd"])]
        ordering = [
            "-dtadd",
        ]

    def __str__(self):
        return self.meterno

class ElsewedyAccounts(models.Model):
    meterno = models.CharField(
        max_length=20, verbose_name=_("Meter Number"), unique=True
    )
    accountno = models.CharField(max_length=20, verbose_name=_("Account Number"))
    itin = models.CharField(
        verbose_name=_("Itinerary"), max_length=200, blank=True, null=True
    )
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    sector = models.CharField(
        max_length=100, verbose_name=_("Sector"), null=True, blank=True
    )
    zone = models.CharField(
        max_length=100, verbose_name=_("Zone"), null=True, blank=True
    )
    customer_name = models.CharField(
        verbose_name=_("Customer Name"), max_length=200, blank=True, null=True
    )
    cod_tarrif = models.CharField(
        verbose_name=_("Tarrif"), max_length=50, null=True, blank=True
    )
    supply_address = models.CharField(
        verbose_name=_("Supply Address"), max_length=255, blank=True, null=True
    )
    y = models.CharField(_("Longitude"), max_length=255, null=True, blank=True)
    x = models.CharField(_("Latitude"), max_length=255, null=True, blank=True)
    status = models.BooleanField(default=False)
    billed_reading = models.IntegerField(default=0)
    incms_status = models.BooleanField(default=False)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    diffunits = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)

    def __str__(self):
        return self.meterno

class ElsewedyReplacement(models.Model):
    METERINGSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("okay", "OKAY"),
        ("faulty", "FAULTY"),
        ("tampered", "TAMPERED"),
        ("bypassed", "BYPASSED"),
    )
    FAULTYSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("blankscreen", "BLANK SCREEN"),
        ("noncommunicating", "NON COMMUNICATING"),
        ("obsolete", "OBSOLETE"),
        ("fadeddigits", "FADED DIGITS"),
        ("notpulsing", "NOT PULSING"),
        ("burnt", "BURNT"),
        ("batterylow", "BATTERY LOW"),
        ("cuifaulty", "CIU FAULTY"),
        ("notabletoloadtoken", "NOT ABLE TO LOAD TOKEN"),
        ("looseglass", "LOOSE GLASS"),
    )
    TAMPEREDSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("brokenseaals", "BROKEN SEALS"),
        ("disabledvoltage", "DISABLED VOLTAGE"),
        ("disabledcurrent", "DISABLED CURRENT"),
        ("brokenglass", "BROKEN GLASS"),
        ("droppedlink", "DROPPED LINK"),
        ("damagedmeter", "DAMAGED METER"),
        ("foreignobjects", "FOREIGN OBJECTS INTRODUCED"),
    )
    BYPASSSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("puncturedcable", "PUNCTURED CABLE"),
        ("drilledcutout", "DRILLED CUTOUT"),
    )
    VALIDATESTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("yes", "YES"),
        ("no", "NO"),
    )
    elsewedy = models.ForeignKey(
        ElsewedyAccounts,
        on_delete=models.SET_NULL,
        null=True,
        related_name="elsewedy_replaced_meter",
    )
    accountno = models.CharField(
        verbose_name=_("Account Number"), max_length=255, blank=True, null=True
    )
    oldmeter= models.CharField(
        verbose_name=_("Meter Number Removed"), unique=True, max_length=100
    )
    newmeter = models.CharField(
        verbose_name=_("Meter Number Installed"), unique=True, max_length=100
    )
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    meteringstatus = models.CharField(
        verbose_name=_("Metering Status"), max_length=50, choices=METERINGSTATUS
    )
    faultystatus = models.CharField(
        verbose_name=_("Faulty Status"),
        max_length=50,
        choices=FAULTYSTATUS,
        null=True,
        blank=True,
        default="NULL",
    )
    tamperedstatus = models.CharField(
        verbose_name=_("Tampered Status"),
        max_length=50,
        choices=TAMPEREDSTATUS,
        null=True,
        blank=True,
    )
    bypassstatus = models.CharField(
        verbose_name=_("Bypass Status"),
        max_length=50,
        choices=BYPASSSTATUS,
        null=True,
        blank=True,
    )
    removal_reading = models.IntegerField(
        verbose_name=_("Meter Removal Reading(This is a required Field)"), help_text="Required"
    )
    inspector = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, related_name="elsewedy_inspector"
    )
    removal_img = models.ImageField(
        upload_to="images/elsewedy/removal/%Y/%m/%d/",
        verbose_name=_("CLEAR IMAGE OF REMOVED METER(This is Required)"),
    )
    comment = models.TextField(verbose_name=_("Any Comment"), null=True, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='county_elsewedy_repalcement')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='region_elsewedy_repalcement')
    validated = models.CharField(
        verbose_name=_("Validated Status"), max_length=50, choices=VALIDATESTATUS
    )
    validate_status = models.BooleanField(default=False)
    billed = models.BigIntegerField(verbose_name=_("Rebilled Amount"), default=0)
    consumption = models.IntegerField(verbose_name=_("Usage"), default=0)
    units = models.IntegerField(verbose_name=_("Units"), null=True, blank=True)
    seal_cover = models.CharField(
        verbose_name=_("Seal"), max_length=100, null=True, blank=True
    )


    def __str__(self):
        return self.newmeter

    # @property
    # def unbilled_units(self):
    #     return (int(self.telcos.system_reading)) - (int(self.removal_reading))

class Domestic_customers_rri(models.Model):
    dc_meterno = models.CharField(
        max_length=20, verbose_name=_("Meter Number"), unique=True
    )
    dc_accountno = models.CharField(max_length=20, verbose_name=_("Account Number"))
    itin = models.CharField(
        verbose_name=_("Itinerary"), max_length=200, blank=True, null=True
    )
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    sector = models.CharField(
        max_length=100, verbose_name=_("Sector"), null=True, blank=True
    )
    zone = models.CharField(
        max_length=100, verbose_name=_("Zone"), null=True, blank=True
    )
    customer_name = models.CharField(
        verbose_name=_("Customer Name"), max_length=200, blank=True, null=True
    )
    contract_type = models.CharField(
        verbose_name=_("Contract Type"), max_length=50, null=True, blank=True
    )
    cod_tarrif = models.CharField(
        verbose_name=_("Tarrif"), max_length=50, null=True, blank=True
    )
    supply_phase = models.CharField(
        verbose_name=_("Supply Phase"), max_length=100, blank=True, null=True
    )
    supply_address = models.CharField(
        verbose_name=_("Supply Address"), max_length=255, blank=True, null=True
    )
    longitute = models.CharField(_("Longitude"), max_length=255, null=True, blank=True)
    latitude = models.CharField(_("Latitude"), max_length=255, null=True, blank=True)
    avg_units = models.DecimalField(_("Average Units"), max_digits=12, decimal_places=2)
    status = models.BooleanField(default=False)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.dc_meterno

class RetrofitAccounts(models.Model):
    meterno = models.CharField(
        max_length=20, verbose_name=_("Meter Number"), unique=True
    )
    accountno = models.CharField(max_length=20, verbose_name=_("Account Number"))
    itin = models.CharField(
        verbose_name=_("Itinerary"), max_length=200, blank=True, null=True
    )
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='retrofits_county')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True,related_name='retrofits_region')
    sector = models.CharField(
        max_length=100, verbose_name=_("Sector"), null=True, blank=True
    )
    zone = models.CharField(
        max_length=100, verbose_name=_("Zone"), null=True, blank=True
    )
    customer_name = models.CharField(
        verbose_name=_("Customer Name"), max_length=200, blank=True, null=True
    )
    cod_tarrif = models.CharField(
        verbose_name=_("Tarrif"), max_length=50, null=True, blank=True
    )
    supply_address = models.CharField(
        verbose_name=_("Supply Address"), max_length=255, blank=True, null=True
    )
    y = models.CharField(_("Longitude"), max_length=255, null=True, blank=True)
    x = models.CharField(_("Latitude"), max_length=255, null=True, blank=True)
    status = models.BooleanField(default=False)
    contract_type = models.CharField(max_length=20, blank=True, null=True)
    tech_center = models.CharField(max_length=255, blank=True, null=True)
    billed_reading = models.IntegerField(default=0)
    incms_status = models.BooleanField(default=False)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    diffunits = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)

    def __str__(self):
        return self.meterno

class LPODK(models.Model):
    SubmissionDate = models.DateField(verbose_name=_("Submission Date"))
    Latitude = models.FloatField(verbose_name=_("Latitude"), null=True, blank=True)
    Longitude = models.FloatField(verbose_name=_("Longitude"), null=True, blank=True)
    meter_number = models.CharField(blank=True, null=True, max_length=50)
    customer_name = models.CharField(blank=True, null=True, max_length=250)
    srn_number = models.CharField(blank=True, null=True, max_length=50)
    county_id = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name="odk_county")
    region_id = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name="odk_region")
    type_of_industry = models.CharField(blank=True, null=True, max_length=50)
    metering_installation =models.CharField(blank=True, null=True, max_length=50)
    account_number =models.CharField(blank=True, null=True, max_length=50)
    progaming_initial =models.CharField(blank=True, null=True, max_length=50)
    progaming_final =models.CharField(blank=True, null=True, max_length=50)
    meter_terminal_initial =models.CharField(blank=True, null=True, max_length=50)
    meter_terminal_final =models.CharField(blank=True, null=True, max_length=50)
    test_block_initial =models.CharField(blank=True, null=True, max_length=50)
    test_block_final =models.CharField(blank=True, null=True, max_length=50)
    meter_body_seal_initial =models.CharField(blank=True, null=True, max_length=50)
    meter_body_seal_final =models.CharField(blank=True, null=True, max_length=50)
    smart_meter_enclosure_initial =models.CharField(blank=True, null=True, max_length=50)
    smart_meter_enclosure_final =models.CharField(blank=True, null=True, max_length=50)
    amr_initial =models.CharField(blank=True, null=True, max_length=50)
    amr_final =models.CharField(blank=True, null=True, max_length=50)
    other_seals =models.CharField(blank=True, null=True, max_length=50)
    connection_configs =models.CharField(blank=True, null=True, max_length=50)
    meter_voltage_atsite =models.CharField(blank=True, null=True, max_length=50)
    ct_ratio_progammed =models.CharField(blank=True, null=True, max_length=50)
    ct_ratio_prog_at_meter =models.CharField(blank=True, null=True, max_length=50)
    ct_ratio_installed =models.CharField(blank=True, null=True, max_length=50)
    vt_ratio =models.CharField(blank=True, null=True, max_length=50)
    y_n =models.CharField(blank=True, null=True, max_length=50)
    ct_vt_match =models.CharField(blank=True, null=True, max_length=50)
    mismatch_description =models.CharField(blank=True, null=True, max_length=50)
    zera_test_done =models.CharField(blank=True, null=True, max_length=50)
    error_trial_per =models.CharField(blank=True, null=True, max_length=50)
    error_test_remarks =models.CharField(blank=True, null=True, max_length=50)
    error_per =models.CharField(blank=True, null=True, max_length=50)
    test_results_remarks =models.CharField(blank=True, null=True, max_length=50)
    meter_pass_test =models.CharField(blank=True, null=True, max_length=50)
    red_phase_amcorder =models.CharField(blank=True, null=True, max_length=50)
    red_phase_meter =models.CharField(blank=True, null=True, max_length=50)
    yellow_phase_amcorder =models.CharField(blank=True, null=True, max_length=50)
    yellow_phase_meter =models.CharField(blank=True, null=True, max_length=50)
    blue_phase_amcorder =models.CharField(blank=True, null=True, max_length=50)
    blue_phase_meter =models.CharField(blank=True, null=True, max_length=50)
    load_balancing =models.CharField(blank=True, null=True, max_length=50)
    m_n_clamp_currents =models.CharField(blank=True, null=True, max_length=50)
    time_actual =models.CharField(blank=True, null=True, max_length=50)
    time_meter =models.CharField(blank=True, null=True, max_length=50)
    date_actual =models.CharField(blank=True, null=True, max_length=50)
    date_meter =models.CharField(blank=True, null=True, max_length=50)
    current_180_kwh =models.CharField(blank=True, null=True, max_length=50)
    memory_180_kwh =models.CharField(blank=True, null=True, max_length=50)
    image_180_kwh =models.CharField(blank=True, null=True, max_length=50)
    current_280_kwh =models.CharField(blank=True, null=True, max_length=50)
    memory_280_kwh =models.CharField(blank=True, null=True, max_length=50)
    image_280_kwh =models.CharField(blank=True, null=True, max_length=50)
    current_960_kva =models.CharField(blank=True, null=True, max_length=50)
    memory_960_kva =models.CharField(blank=True, null=True, max_length=50)
    current_150_kwh =models.CharField(blank=True, null=True, max_length=50)
    memory_150_kwh =models.CharField(blank=True, null=True, max_length=50)
    current_181_kwh =models.CharField(blank=True, null=True, max_length=50)
    memory_181_kwh =models.CharField(blank=True, null=True, max_length=50)
    current_182_kwh =models.CharField(blank=True, null=True, max_length=50)
    memory_182_kwh =models.CharField(blank=True, null=True, max_length=50)
    instatenious_970_kva =models.CharField(blank=True, null=True, max_length=50)
    instatenious_170_kva =models.CharField(blank=True, null=True, max_length=50)
    red_phase_voltage =models.CharField(blank=True, null=True, max_length=50)
    yellow_phase_voltage =models.CharField(blank=True, null=True, max_length=50)
    blue_phase_voltage =models.CharField(blank=True, null=True, max_length=50)
    red_phase_current =models.CharField(blank=True, null=True, max_length=50)
    yellow_phase_current =models.CharField(blank=True, null=True, max_length=50)
    blue_phase_current =models.CharField(blank=True, null=True, max_length=50)
    power_factor  =models.CharField(blank=True, null=True, max_length=50)
    reading_remarks =models.CharField(blank=True, null=True, max_length=50)
    solar_installation =models.CharField(blank=True, null=True, max_length=50)
    solar_size =models.CharField(blank=True, null=True, max_length=50)
    solar_installation_date =models.CharField(blank=True, null=True, max_length=50)
    overall_remarks=models.TextField(blank=True, null=True)
    declaration =models.CharField(blank=True, null=True, max_length=50)
    instanceID =models.CharField(blank=True, null=True, max_length=50)
    SubmitterID =models.CharField(blank=True, null=True, max_length=50)
    SubmitterName =models.CharField(blank=True, null=True, max_length=50)
    mitterName =models.CharField(blank=True, null=True, max_length=50)
    user_id = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name="odk_staff")
    def __str__(self):
        return self.meter_number


class LP_inspection_2025_2026(models.Model):
    start = models.DateField(verbose_name=_("Start Date"))
    end = models.DateField(verbose_name=_("End Date"))
    device_id = models.CharField(max_length=100)
    xy = models.FloatField(verbose_name=_("XY"), null=True, blank=True)
    meter_number = models.CharField(blank=True, null=True, max_length=50)
    meter_installation = models.CharField(blank=True, null=True, max_length=200)
    srn_number = models.CharField(blank=True, null=True, max_length=50)
    account_number = models.CharField(blank=True, null=True, max_length=50)
    county_id = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    region_id = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    type_of_industry = models.CharField(blank=True, null=True, max_length=50)
    metering_installation =models.CharField(blank=True, null=True, max_length=50)
    progamming_initial =models.CharField(blank=True, null=True, max_length=50)
    progamming_final =models.CharField(blank=True, null=True, max_length=50)
    meter_terminal_initial =models.CharField(blank=True, null=True, max_length=50)
    meter_terminal_final =models.CharField(blank=True, null=True, max_length=50)
    test_block_initial =models.CharField(blank=True, null=True, max_length=50)
    test_block_final =models.CharField(blank=True, null=True, max_length=50)
    meter_body_seal_initial =models.CharField(blank=True, null=True, max_length=50)
    meter_body_seal_final =models.CharField(blank=True, null=True, max_length=50)
    smart_meter_enclosure_initial =models.CharField(blank=True, null=True, max_length=50)
    smart_meter_enclosure_final =models.CharField(blank=True, null=True, max_length=50)
    amr_initial =models.CharField(blank=True, null=True, max_length=50)
    amr_final =models.CharField(blank=True, null=True, max_length=50)
    other_seals =models.CharField(blank=True, null=True, max_length=50)
    connection_configs =models.CharField(blank=True, null=True, max_length=50)
    meter_voltage_at_site =models.CharField(blank=True, null=True, max_length=50)
    ct_ratio_programmed =models.CharField(blank=True, null=True, max_length=50)
    ct_ratio_at_meter =models.CharField(blank=True, null=True, max_length=50)
    ct_ratio_installed =models.CharField(blank=True, null=True, max_length=50)
    vt_ratio =models.CharField(blank=True, null=True, max_length=50)
    ct_vt_done =models.CharField(blank=True, null=True, max_length=50)
    ct_vt_match =models.CharField(blank=True, null=True, max_length=50)
    mismatch_description =models.CharField(blank=True, null=True, max_length=50)
    zera_test_done =models.CharField(blank=True, null=True, max_length=50)
    error_trial_per =models.CharField(blank=True, null=True, max_length=50)
    error_test_remarks =models.CharField(blank=True, null=True, max_length=50)
    error_per =models.CharField(blank=True, null=True, max_length=50)
    test_results_remarks =models.CharField(blank=True, null=True, max_length=50)
    meter_pass_test =models.CharField(blank=True, null=True, max_length=50)
    red_phase_amcorder =models.CharField(blank=True, null=True, max_length=50)
    red_phase_meter =models.CharField(blank=True, null=True, max_length=50)
    yellow_phase_amcorder =models.CharField(blank=True, null=True, max_length=50)
    yellow_phase_meter =models.CharField(blank=True, null=True, max_length=50)
    blue_phase_amcorder =models.CharField(blank=True, null=True, max_length=50)
    blue_phase_meter =models.CharField(blank=True, null=True, max_length=50)
    load_balancing =models.CharField(blank=True, null=True, max_length=50)
    m_n_clamp_currents =models.CharField(blank=True, null=True, max_length=50)
    time_actual =models.CharField(blank=True, null=True, max_length=50)
    time_meter =models.CharField(blank=True, null=True, max_length=50)
    date_actual =models.CharField(blank=True, null=True, max_length=50)
    date_meter =models.CharField(blank=True, null=True, max_length=50)
    current_180_kwh =models.CharField(blank=True, null=True, max_length=50)
    memory_180_kwh =models.CharField(blank=True, null=True, max_length=50)
    image_180_kwh =models.CharField(blank=True, null=True, max_length=50)
    current_280_kwh =models.CharField(blank=True, null=True, max_length=50)
    memory_280_kwh =models.CharField(blank=True, null=True, max_length=50)
    image_280_kwh =models.CharField(blank=True, null=True, max_length=50)
    current_960_kva =models.CharField(blank=True, null=True, max_length=50)
    memory_960_kva =models.CharField(blank=True, null=True, max_length=50)
    current_150_kwh =models.CharField(blank=True, null=True, max_length=50)
    memory_150_kwh =models.CharField(blank=True, null=True, max_length=50)
    current_181_kwh =models.CharField(blank=True, null=True, max_length=50)
    memory_181_kwh =models.CharField(blank=True, null=True, max_length=50)
    current_182_kwh =models.CharField(blank=True, null=True, max_length=50)
    memory_182_kwh =models.CharField(blank=True, null=True, max_length=50)
    instatenious_970_kva =models.CharField(blank=True, null=True, max_length=50)
    instatenious_170_kva =models.CharField(blank=True, null=True, max_length=50)
    red_phase_voltage =models.CharField(blank=True, null=True, max_length=50)
    yellow_phase_voltage =models.CharField(blank=True, null=True, max_length=50)
    blue_phase_voltage =models.CharField(blank=True, null=True, max_length=50)
    red_phase_current =models.CharField(blank=True, null=True, max_length=50)
    yellow_phase_current =models.CharField(blank=True, null=True, max_length=50)
    blue_phase_current =models.CharField(blank=True, null=True, max_length=50)
    power_factor  =models.CharField(blank=True, null=True, max_length=50)
    reading_remarks =models.CharField(blank=True, null=True, max_length=50)
    solar_installation =models.CharField(blank=True, null=True, max_length=50)
    solar_size =models.CharField(blank=True, null=True, max_length=50)
    solar_installation_date =models.CharField(blank=True, null=True, max_length=50)
    overall_remarks=models.TextField(blank=True, null=True)
    declaration =models.CharField(blank=True, null=True, max_length=50)
    instance_id =models.CharField(blank=True, null=True, max_length=50)
    submission_date = models.DateField(verbose_name=_("Submission Date"))
    submitter_id =models.CharField(blank=True, null=True, max_length=50)
    submitter_name =models.CharField(blank=True, null=True, max_length=50)
    user_id = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.meter_number

class Amcorder(models.Model):
    CONCONFIG = (
        ("", "----CHOOSE A TYPE----"),
        ("3P3W", "3P3W"),
        ("3P4W", "3P4W"),
    )
    INSTALLATIONPOINT = (
        ("", "----CHOOSE A TYPE----"),
        ("FEEDER", "FEEDER"),
        ("TX", "TX"),
        ("CUSTOMER_POINT", "CUSTOMER POINT"),
        ("TERMINAL_POLE", "TERMINAL POLE"),
        ("OTHER", "OTHER"),
    )
    FVOLTAGE = (
        ("", "----CHOOSE A TYPE----"),
        ("11KV", "11KV"),
        ("33KV", "33KV"),
        ("66KV", "66KV"),
    )
    VTRATION = (
        ('', '----CHOOSE A STATUS----'),
        ('1:1V', '1:1V'),
        ('11,000/110V', '11,000/110V'),
        ('33,000/110V', '33,000/110V'),
        ('66,000/110V', '66,000/110V'),
        ('132,000/110V', '132,000/110V'),
        ('220,000/110V', '220,000/110V'),
    )
    CTRATION = (
        ('', '----CHOOSE CT----'),
        ('1:1A', '1:1A'),
        ('200/5A', '200/5A'),
        ('300/5A', '300/5A'),
        ('500/5A', '500/5A'),
        ('1000/5A', '1000/5A'),
        ('1500/5A', '1500/5A'),
        ('2000/5A', '2000/5A'),
        ('100/1A', '100/1A'),
        ('100/5A', '100/5A'),
        ('200/1A', '200/1A'),
        ('300/1A', '300/1A'),
        ('400/1A', '400/1A'),
        ('600/1A', '600/1A'),
        ('120/5A', '120/5A'),
        ('1200/5A', '1200/5A'),
        ('150/1A', '150/1A'),
        ('150/5A', '150/5A'),
        ('25/1A', '25/1A'),
        ('250/5A', '250/5A'),
        ('30/1A', '30/1A'),
        ('360/1A', '360/1A'),
        ('40/5A', '40/5A'),
        ('400/5A', '400/5A'),
        ('50/1A', '50/1A'),
        ('50/5A', '50/5A'),
        ('800/1A', '800/1A'),
        ('800/5A', '800/5A'),
        ('none', 'N/A'),
    )
    meter = models.ForeignKey(Largepower_accounts_2024, on_delete=models.SET_NULL, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='amcorder_county')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='amcorder_region')
    user_id = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='amcoder_user')
    conn_config = models.CharField(verbose_name=_("Meter Configuration"),max_length=10,choices=CONCONFIG)
    ct_ratio = models.CharField(verbose_name=_("CT Ratio"), max_length=50, choices=CTRATION)
    vt_ratio = models.CharField(verbose_name=_("VT Ratio"), max_length=50, choices=VTRATION)
    ct_programing = models.CharField(verbose_name=_("CT Programming"), max_length=50, choices=CTRATION)
    vt_programing = models.CharField(verbose_name=_("VT Programming"), max_length=50, choices=VTRATION)
    logger_red_serial = models.CharField(blank=True, null=True, max_length=100)
    logger_yellow_serial = models.CharField(blank=True, null=True, max_length=100)
    logger_blue_serial = models.CharField(blank=True, null=True, max_length=100)
    time_installed = models.TimeField(null=True, blank=True)
    date_installed = models.DateField(null=True, blank=True)
    instal_point = models.CharField(verbose_name=_("Installation Point"), max_length=50, choices=INSTALLATIONPOINT)
    log_interval = models.IntegerField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True,verbose_name=_("Amcorder Start time: (Synchronize with meter time)"))
    read_180 = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_("Meter Reading: 1.8.0"))
    read_181 = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_("Meter Reading 1.8.1"))
    read_182 = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_("Meter Reading 1.8.2"))
    feeder_name = models.CharField(blank=True, null=True, max_length=100,verbose_name=_(" (Feeder name (From InCMS))"))
    feeder_meter_number = models.CharField(blank=True, null=True, max_length=100, verbose_name=_("Feeder meter number: (If Known)"))
    feeder_voltage = models.CharField(verbose_name=_("Feeder Voltage"), max_length=50, choices=FVOLTAGE)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Amcorder Inspection"
        verbose_name_plural = "Amcorder Inspections"
        indexes = [
            models.Index(fields=['meter']),
        ]

    def __str__(self):
        return f"{self.meter} - {self.logger_red_serial}"

class AmcorderRetrieval(models.Model):
    CONSISTENCY = (
        ("", "----CHOOSE A TYPE----"),
        ("CONSISTENT", "CONSISTENT"),
        ("MINOR_VARIANCE", "MINOR VARIANCE"),
        ("MAJOR VARIANCE", "MAJOR VARIANCE"),
    )
    meter= models.OneToOneField(Amcorder, on_delete=models.CASCADE, null=True, related_name='meter_retrieval')
    date_retrieved = models.DateField(null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    read_180 = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_("Meter Reading: 1.8.0"))
    read_181 = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_("Meter Reading 1.8.1"))
    read_182 = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_("Meter Reading 1.8.2"))
    feeder_read_180 = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_("Feeder Reading: 1.8.0"))
    feeder_read_181 = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_("Feeder Reading 1.8.1"))
    feeder_read_182 = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_("Feeder Reading 1.8.2"))
    logger_phase_a = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_("Logger Phase A Current"))
    logger_phase_b = models.DecimalField(max_digits=6, decimal_places=2, default=0,verbose_name=_("Logger Phase B Current"))
    logger_phase_c = models.DecimalField(max_digits=6, decimal_places=2, default=0,verbose_name=_("Logger Phase C Current"))
    peak_load = models.DecimalField(max_digits=6, decimal_places=2, default=0,verbose_name=_("Peak Load"))
    computed_kwh_logged =  models.DecimalField(max_digits=6, decimal_places=2, default=0,verbose_name=_("Computed kWh from Logged Data:"))
    meter_consumption = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                                              verbose_name=_("Meter kWh consumption for logging period:"))
    logger_consumption = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                                              verbose_name=_("Logger kWh consumption for logging period:"))
    variance_consumption = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                                              verbose_name=_("Variance (kWh):"))
    consistence = models.CharField(verbose_name=_("Consistency between Logger Current & Meter Load Profile:"), max_length=50, choices=CONSISTENCY)
    comments = models.TextField(verbose_name=_('Comment'), null=True, blank=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.meter} - {self.meter.logger_red_serial}-{self.meter.logger_yellow_serial}-{self.meter.logger_blue_serial}"

class AnomalyType(models.Model):
    code = models.CharField(max_length=50)
    label = models.CharField(max_length=100)

    def __str__(self):
        return self.label

class AmcorderAnalysis(models.Model):
    CONSISTENCY = (
        ("", "----CHOOSE A TYPE----"),
        ("CONSISTENT", "CONSISTENT"),
        ("MINOR_VARIANCE", "MINOR VARIANCE"),
        ("MAJOR VARIANCE", "MAJOR VARIANCE"),
    )
    VISSUES = (
        ("", "----CHOOSE A TYPE----"),
        ("Electricity_theft", " Suspected Electricity Theft"),
        ("bypassed_ct", "Bypassed CT / Wrong CT ratio"),
        ("Wrong_meter_prgrm", "Wrong meter programming (CT/VT)"),
        ("Phase loss / imbalance", "Phase loss / imbalance"),
        ("Intermittent_load", "Intermittent load"),
        ("No_anomalies", "No anomalies detected"),
    )
    meter= models.OneToOneField(Amcorder, on_delete=models.CASCADE, null=True, related_name='meter_analysis')
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    user_id = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    consistence = models.CharField(verbose_name=_("Consistency between Logger Current & Meter Load Profile:"),
                                   max_length=50, choices=CONSISTENCY)
    anomalies = models.ManyToManyField(AnomalyType, blank=True)
    raw_logger = models.FileField(
        upload_to="images/amcorder/rawlogger/%Y/%m/%d/",
        verbose_name=_("Upload Raw Logger Download Data (CSV / XLSX)"), default="default.csv"
    )
    logger_analysed = models.FileField(
        upload_to="images/amcorder/analysed/%Y/%m/%d/",
        verbose_name=_("Upload Logger Data Analysis Report (Excel / PDF):"),
    )
    site_images = models.ImageField(
        upload_to="images/amcorder/siteimages/%Y/%m/%d/",
        verbose_name=_("Upload Site Images (CTs, Meter, Logger Placement):"),
    )
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.meter} - {self.meter.logger_red_serial}-{self.meter.logger_yellow_serial}-{self.meter.logger_blue_serial}"








