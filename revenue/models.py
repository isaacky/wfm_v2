from django.db import models
from user.models import Account, UserProfile
from main.models import County, Region
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Debtlist(models.Model):
    meterno = models.CharField(max_length=255, blank=True,verbose_name=_("Meter Number"))
    accountno = models.CharField(max_length=255,blank=True, null=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='county_debt_list')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='region_debt_list')
    sector = models.CharField(max_length=100, null=True,blank=True)
    zone = models.CharField(max_length=100, null=True,blank=True)
    totalbalance = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    overdue_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    last_bill = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    systemreading = models.IntegerField(null=True, blank=True)
    phonenumber = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=300, blank=True, null=True)
    name = models.TextField(max_length=300, blank=True, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    itin = models.CharField(max_length=300, blank=True, null=True)
    xcood = models.CharField(max_length=300, blank=True, null=True)
    ycood = models.CharField(max_length=300, blank=True, null=True)
    asigned_to = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='debt_asigned_to')
    dt_asigned = models.DateField()
    asigned_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='debt_asigned_by')
    totalbalance_new = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    target_acc = models.BooleanField(default=True)
    classification = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=["meterno"])]
        ordering = ['-dtadd',]

    def __str__(self):
        return self.accountno
      
class Revenuerecollection(models.Model):
    STATUSCHOISES= (
        ('','----CHOOSE A STATUS----'),
        ('paid','PAID'),
        ('fdc','FDC'),
        ('disconnected', 'DISCONNECTED'),
        ('poledisconnection', 'POLE DISCONNECTION'),
        ('cablerecovery', 'CABLE RECOVERY'),
        ('notonsite','NOT-ON-SITE'),
        ('faulty', 'FAULTY'),
        ('wrongreading', 'WRONG READING'),
        )
    target = models.ForeignKey(Debtlist,on_delete=models.SET_NULL, null=True,related_name='debt_list')
    meterno = models.CharField(max_length=255, blank=True,verbose_name=_("Meter Number"))
    accountno = models.IntegerField(blank=True, null=True)
    collector = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    collection_status = models.CharField(max_length=50, choices=STATUSCHOISES, default='pending')
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='county_revenue_resolved')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='region_rev_action')
    reading = models.IntegerField(blank=True, null=True)
    amountpaid = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    totalbalance = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    overdue_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    verified_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    incms_status = models.BooleanField(default=False)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    xcood = models.CharField(max_length=300, blank=True, null=True)
    ycood = models.CharField(max_length=300, blank=True, null=True)
    sector = models.CharField(max_length=100, null=True,blank=True)
    zone = models.CharField(max_length=100, null=True,blank=True)
    comment = models.TextField(null=True, blank=True)

    
    class Meta:
        indexes = [models.Index(fields=["meterno"])]
        ordering = ['-dtadd',]

    def __str__(self):
        return self.meterno