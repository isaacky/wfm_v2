from django.db import models
from main.models import County, Region,Department,Divisions
from user.models import Account, UserProfile
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Inventory_group(models.Model):
    name = models.CharField(max_length=255,null=True, blank=True)
    description = models.CharField(max_length=255, null=True,blank=True)

    def __str__(self):
        return self.name

class Inventory_list(models.Model):
    INVCOND = (
        ("", "----CHOOSE A STATUS----"),
        ("good", "GOOD"),
        ("faulty", "FAULTY"),
    )
    tagid = models.CharField(max_length=100, unique=True,verbose_name=_("Tag Number"))
    inv_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Inventory Name"))
    inv_group = models.ForeignKey(Inventory_group, on_delete=models.SET_NULL, null=True,verbose_name=_("Inventory Group"))
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True,verbose_name=_("County"))
    office_station = models.CharField(max_length=255, null=True,blank=True)
    condition = models.CharField(max_length=100,choices=INVCOND,null=True,blank=True,verbose_name=_("Condition"))
    dt_purchase = models.DateField()
    purchase_price_vat_incl = models.FloatField()
    purchase_price_vat_excl = models.FloatField()
    reciepient_stid = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Receipeint Staff Number"))
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Inventory Description"))
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True,verbose_name=_("Inventory department"))
    quantity = models.IntegerField(default=0)
    supplier = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Supplier Name"))
    lpo_number = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("LPO Number"))
    ac_number = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Account Number"))
    internal_order = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Internal Order"))
    minute_no = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Minute Number"))
    lon = models.CharField(_("Longitude"), max_length=255, blank=True, null=True)
    lat = models.CharField(_("Latitude"), max_length=255, blank=True, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    inspector = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inspector_staff",
    )

    def __str__(self):
        return self.inv_name
