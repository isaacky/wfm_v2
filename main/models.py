
from django.db import models
from user.models import Account, UserProfile

# Create your models here.
class County(models.Model):
  
    name = models.CharField(max_length=100)
    cse_name = models.CharField(max_length=255, blank=True,null=True)
    cse_stid = models.CharField(max_length=10, blank=True,null=True)
    cse_mobile = models.CharField(max_length=20, blank=True,null=True)
    region = models.ForeignKey('Region', on_delete=models.CASCADE)
    cse_email = models.EmailField()
    dc_target = models.IntegerField()
    dc_daily_target = models.IntegerField()
    highend_target = models.IntegerField()
    highend_daily_target = models.IntegerField()
    telcos_replace_target_daily = models.IntegerField(null=True, blank=True)
    telcos_replace_target = models.IntegerField(null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    staff = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    telcos_target = models.IntegerField(null=True, blank=True)
    telcos_target_overall = models.IntegerField(null=True, blank=True)
    publiclighting_target = models.IntegerField(null=True, blank=True)
    publiclighting_target_overall = models.IntegerField(null=True, blank=True)
    atc = models.IntegerField(null=True, blank=True)
    tid_overall_target = models.IntegerField(null=True, blank=True)
    tid_daily_target = models.IntegerField(null=True, blank=True)
    zerobill_march = models.IntegerField(null=True, blank=True)
    zerobill_april = models.IntegerField(null=True, blank=True)
    zerobill_may = models.IntegerField(null=True, blank=True)
    zerobill_june = models.IntegerField(null=True, blank=True)
    zerobill_recoveries = models.DecimalField(
        max_digits=16, decimal_places=2, default=0.00
    )
    anomalous_target = models.IntegerField(null=True, blank=True)
    anomalous_recoveries = models.DecimalField(
        max_digits=16, decimal_places=2, default=0.00
    )
    fallbackrri_target = models.IntegerField(null=True, blank=True)
    fallbackrri_faulty = models.IntegerField(null=True, blank=True)
    fallbackrri_tampered = models.IntegerField(null=True, blank=True)
    fallbackrri_bypassed = models.IntegerField(null=True, blank=True)
    fallbackrri_dc = models.IntegerField(null=True, blank=True)
    fallbackrri_replace = models.IntegerField(null=True, blank=True)
    fallbackrri_tid = models.IntegerField(null=True, blank=True)
    collection_target = models.DecimalField(
        max_digits=16, decimal_places=2, default=0.00
    )
    collection_target_count = models.IntegerField(null=True, blank=True)
    collection_amount_paid = models.DecimalField(
        max_digits=16, decimal_places=2, default=0.00
    )
    collection_paid_count = models.IntegerField(null=True, blank=True)
    totalbalance_new = models.DecimalField(
        max_digits=16, decimal_places=2, default=0.00
    )
    retrofit_target = models.IntegerField()
    retrofit_daily_target = models.IntegerField()

    class Meta:
        verbose_name = 'county'
        verbose_name_plural  = 'counties'
        ordering = ['name', ]
	
    def __str__(self):
        return self.name

# Create your models here.
class Region(models.Model):
  
    name = models.CharField(max_length=100)
    rm = models.CharField(max_length=255, blank=True,null=True)
    rm_stid = models.CharField(max_length=10, blank=True,null=True)
    rm_mobile = models.CharField(max_length=20, blank=True,null=True)
    rm_email = models.EmailField()
    dc_target = models.IntegerField()
    highend_target = models.IntegerField()
    highend_daily_target = models.IntegerField()
    telcos_replace_target_daily = models.IntegerField(null=True, blank=True)
    telcos_replace_target = models.IntegerField(null=True, blank=True)
    dc_daily_target = models.IntegerField()
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    staff = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    telcos_target = models.IntegerField(null=True, blank=True)
    telcos_target_overall = models.IntegerField(null=True, blank=True)
    tid_overall_target = models.IntegerField(null=True, blank=True)
    tid_daily_target = models.IntegerField(null=True, blank=True)
    zerobill_march = models.IntegerField(null=True, blank=True)
    zerobill_april = models.IntegerField(null=True, blank=True)
    zerobill_may = models.IntegerField(null=True, blank=True)
    zerobill_june = models.IntegerField(null=True, blank=True)
    zerobill_recoveries = models.DecimalField(
        max_digits=16, decimal_places=2, default=0.00
    )
    anomalous_target = models.IntegerField(null=True, blank=True)
    anomalous_recoveries = models.DecimalField(
        max_digits=16, decimal_places=2, default=0.00
    )
    fallbackrri_target = models.IntegerField(null=True, blank=True)
    fallbackrri_faulty = models.IntegerField(null=True, blank=True)
    fallbackrri_tampered = models.IntegerField(null=True, blank=True)
    fallbackrri_bypassed = models.IntegerField(null=True, blank=True)
    fallbackrri_dc = models.IntegerField(null=True, blank=True)
    fallbackrri_replace = models.IntegerField(null=True, blank=True)
    fallbackrri_tid = models.IntegerField(null=True, blank=True)
    publiclighting_target = models.IntegerField(null=True, blank=True)
    publiclighting_daily_target = models.IntegerField(null=True, blank=True)
    collection_target = models.DecimalField(
        max_digits=16, decimal_places=2, default=0.00
    )
    collection_target_count = models.IntegerField(null=True, blank=True)
    collection_amount_paid = models.DecimalField(
        max_digits=16, decimal_places=2, default=0.00
    )
    collection_paid_count = models.IntegerField(null=True, blank=True)
    totalbalance_new = models.DecimalField(
        max_digits=16, decimal_places=2, default=0.00
    )
    retrofit_target = models.IntegerField()
    retrofit_daily_target = models.IntegerField()

    class Meta:
        verbose_name = 'region'
        verbose_name_plural  = 'regions'

    def __str__(self):
        return self.name


class Sector(models.Model):
    name = models.CharField(max_length=100)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='county_sectors')
    incharge_name = models.CharField(max_length=255, blank=True,null=True)
    incharge_stid = models.CharField(max_length=10, blank=True,null=True)
    incharge_mobile = models.CharField(max_length=20, blank=True,null=True)
    incharge_email = models.EmailField()
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    staff = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'sector'
        verbose_name_plural  = 'sectors'

    def __str__(self):
        return self.name


class Meters(models.Model):
    STATUSCHOISES= (
        ('pending','PENDING'),
        ('solved','SOLVED'),
        ('initiated','INITIATED')
       
        )
    ANOMALYTYPE =(
        ('faultymeter','FAULTY METER'),
        ('meternotinincms','METER NOT IN INCMS'),
        ('rebilling','REBILLING'),
        ('irregularity','IRREGULARITY'),
        ('retrofit','ILLEGAL RETROFIT'),
        ('directconnecction','DIRECT CONNECTION'),
        ('idle','IDLE METER'),
	('terminatedonmvt','TERMINATED ON MVT'),

    )
    anomalytype = models.CharField(max_length=20, choices=ANOMALYTYPE, null=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='Meters_user')
    meternumber = models.PositiveBigIntegerField(null=True,blank=True)
    accountnumber = models.PositiveBigIntegerField(null=True,blank=True)
    customername =models.CharField(max_length=255, blank=True)
    customercontact = models.CharField(max_length=100, blank=True)
    readings = models.IntegerField(null=True, blank=True,help_text="If the reading is blank input zero and give a narration in the narration field")
    resposnsible =  models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='Meters_responsible')
    asigned =  models.ForeignKey(UserProfile, on_delete=models.SET_NULL,blank=True, null=True, related_name='Meters_asigned')
    reasigndt = models.DateField(null=True, blank=True)
    resolvedt = models.DateField(null=True, blank=True)
    requestremove =models.BooleanField(default=False)
    removereason = models.TextField(null=True, blank=True,help_text='Give reason for deletion/Removal   ')
    rccsNumber = models.CharField(max_length=100, blank=True, null=True)
    woNumber = models.CharField(max_length=100, blank=True, null=True)
    naration = models.TextField()
    status = models.CharField(max_length=10, choices=STATUSCHOISES, default='pending')
    rebilledunits =models.IntegerField(default=0)
    physicallocation=models.CharField(max_length=255, null=True, blank=True)
    meterimg = models.ImageField(default='default.jpg', upload_to="images/")
    longitude = models.CharField(max_length=30, null=True, blank=True)
    latitide = models.CharField(max_length=30, null=True, blank=True)
    asigned_narration = models.TextField(blank=True, default='')
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["dtadd"])]
        ordering = ['-dtadd',]

    def save(self, force_insert=False, force_update=False):
        self.naration = self.naration.upper()
        self.asigned_narration = self.asigned_narration.upper()
        super(Meters, self).save(force_insert, force_update)

    def __str__(self):
        return f'{self.meternumber} {self.customername}'

class Analytics(models.Model):
    county_id = models.CharField(max_length=100)
    faulty = models.PositiveBigIntegerField()
    faultypending = models.PositiveBigIntegerField()
    faultysolved = models.PositiveBigIntegerField()
    notincms = models.PositiveBigIntegerField()

    class Meta:
        managed = False
        db_table = "analytics"
        

class Da(models.Model):
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='county_da')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='region_da')
    name = models.CharField(max_length=255, null=True, blank=True)
    dae = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='dae_user')
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    logged_by = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='logged_user_da')

    def __str__(self):
        return self.name

class Feeder(models.Model):
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='feeder_county')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='feeder_region')
    da = models.ForeignKey(Da, on_delete=models.CASCADE, related_name='feeder_da')
    name = models.CharField(max_length=255, null=True, blank=True)
    length = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    logged_by = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name='feeder_user_county')

    def __str__(self):
        return self.name

class Feeder_sections(models.Model):
    feeder = models.ForeignKey(Feeder, on_delete=models.CASCADE, related_name='section_feeder')
    name = models.CharField(max_length=255, null=True, blank=True)
    detail = models.CharField(max_length=255, null=True, blank=True)
    sec_from = models.CharField(max_length=255, null=True, blank=True)
    sec_to = models.CharField(max_length=255, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    aprx_length = models.DecimalField(help_text='Aproximate length in km"s',max_digits=4, decimal_places=2, default=0.00)
    logged_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='section_feeder_logged')

    def __str__(self):
        return self.name    
        
class Divisions(models.Model):
    name= models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Division'
        verbose_name_plural = 'Divisions'
        ordering = ['name', ]

    def __str__(self):
        return self.name
        
class Department(models.Model):
    name = models.CharField(max_length=100)
    div = models.ForeignKey(Divisions, on_delete=models.SET_NULL, null=True)
    class Meta:
        verbose_name = 'department'
        verbose_name_plural = 'departments'
        ordering = ['name', ]

    def __str__(self):
        return self.name   