from django.db import models
from user.models import Account, UserProfile
from django.utils.translation import gettext_lazy as _


class TransmissionDepot(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True,)

    def __str__(self):
        return self.name
class TransmissionLines(models.Model):
    name = models.CharField(blank=True, null=True, max_length=255,verbose_name=_("Line Name"))
    depot = models.ForeignKey(TransmissionDepot, blank=True, null=True, on_delete=models.CASCADE, related_name="line_deport")
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True,related_name='txlines_by')

    class Meta:
        verbose_name = "Transmission Lines"
        verbose_name_plural = "Transmission Lines"
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.name}"

# Create your models here.
class TrnsGroundInspection(models.Model):
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True,related_name='trns_ground_insp_by')
    line_name=  models.ForeignKey(TransmissionLines, on_delete=models.SET_NULL, null=True, related_name='tx_lines')
    towerno = models.CharField(blank=True, null=True, max_length=100, verbose_name=_("Tower Number From"))
    towerno_to = models.CharField(blank=True, null=True, max_length=100, verbose_name=_("Tower Number To"))
    span_lng = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("span Length"))
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    voltage = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("Voltage Level"))
    save_status = models.BooleanField(default=False, db_index=True)
    final_status = models.BooleanField(default=False, db_index=True)
    aprv_status = models.BooleanField(default=False, db_index=True)
    aprv_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='trns_ground_aprv_by')
    aprv_notes = models.TextField(blank=True, null=True)
    aprv_dt = models.DateField(null=True, blank=True)


    class Meta:
        verbose_name = "Trans Ground Inspection"
        verbose_name_plural = "Trans Ground Inspection"
        indexes = [
            models.Index(fields=['towerno']),
            models.Index(fields=['inspectedby']),
            models.Index(fields=['save_status']),
            models.Index(fields=['aprv_status']),
        ]

    def __str__(self):
        return f"{self.towerno} - {self.line_name}"


class InsulatorInspection(models.Model):
    YN = (
        ("", "----CHOOSE A TYPE----"),
        ("YES", "YES"),
        ("NO", "NO"),
    )
    line = models.OneToOneField(TrnsGroundInspection, on_delete=models.CASCADE, null=True, related_name='grnd_lin_insul')
    insul_bkn_dsk = models.IntegerField(null=True, blank=True, verbose_name=_("Number of brocken disks"))
    flashed_insul = models.CharField(verbose_name=_("Flushed/Polluted Insulators"), max_length=10, choices=YN)
    rusted_pins = models.CharField(verbose_name=_("rusted lock pins "), max_length=10, choices=YN)
    comments = models.TextField(verbose_name=_('Comment'), null=True, blank=True)
    save_status = models.BooleanField(default=False, db_index=True)


    def __str__(self):
        return f"{self.line.towerno} - {self.line.line_name}"


class ConductorInspection(models.Model):
    YN = (
        ("", "----CHOOSE A TYPE----"),
        ("YES", "YES"),
        ("NO", "NO"),
    )
    line = models.OneToOneField(TrnsGroundInspection, on_delete=models.CASCADE, null=True,related_name='grnd_line_cond')
    cond_bkn = models.CharField(verbose_name=_("Broken/loose strands/Corrosion?"), max_length=10, choices=YN)
    dampers_missn = models.CharField(verbose_name=_("Missing dampers & armor rods "), max_length=10, choices=YN)
    sag_increase = models.CharField(verbose_name=_("Increase in sag or reduction in ground clearance"), max_length=10,choices=YN)
    loose_clamp = models.CharField(verbose_name=_("Clamps and jumpers loose? "), max_length=10, choices=YN)
    cond_joins = models.CharField(verbose_name=_("Conductor joints ok?"), max_length=10, choices=YN)
    comments = models.TextField(verbose_name=_('Comment'), null=True, blank=True)
    save_status = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.line.towerno} - {self.line.line_name}"


class EarthOPGW(models.Model):
    YN = (
        ("", "----CHOOSE A TYPE----"),
        ("YES", "YES"),
        ("NO", "NO"),
    )
    line = models.OneToOneField(TrnsGroundInspection, on_delete=models.CASCADE, null=True,related_name='grnd_line_opgw')
    bonding = models.CharField(verbose_name=_("Bonding to tower body ok? "), max_length=10, choices=YN)
    spicebox = models.CharField(verbose_name=_("Splice box ok? "), max_length=10, choices=YN)
    sag_increase = models.CharField(verbose_name=_("Increase in sag?"), max_length=10, choices=YN)
    dumper_vibtation = models.CharField(verbose_name=_("Vibration dumper?"), max_length=10, choices=YN)
    comments = models.TextField(verbose_name=_('Comment'), null=True, blank=True)
    save_status = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.line.towerno} - {self.line.line_name}"


class TowerFoundations(models.Model):
    YN = (
        ("", "----CHOOSE A TYPE----"),
        ("YES", "YES"),
        ("NO", "NO"),
    )
    line = models.OneToOneField(TrnsGroundInspection, on_delete=models.CASCADE, null=True,related_name='grnd_line_found')
    cracks_damages = models.CharField(verbose_name=_("Visible damages/cracks & exposure ? "), max_length=10, choices=YN)
    errosion = models.CharField(verbose_name=_("Soil erosion/water accumulation/ Soil & litter damping near foundation?"), max_length=10, choices=YN)
    wildlife = models.CharField(verbose_name=_("Wildlife/bird nests affecting equipment? "), max_length=10, choices=YN)
    poles = models.CharField(verbose_name=_("damaged cross arms/poles? "), max_length=10, choices=YN)
    verticality = models.CharField(verbose_name=_("Tower verticality (no tilting) ok? "), max_length=10, choices=YN)
    ro_way = models.CharField(verbose_name=_("Trees/bushes and other structures(settlement) within the ROW"), max_length=10, choices=YN)
    trees_row = models.CharField(verbose_name=_("Trees outside the ROW that are likely to endanger the line? "), max_length=10, choices=YN)
    encrouch = models.CharField(verbose_name=_("unauthorized activities near line/tower ( e.g. roads)? "), max_length=10, choices=YN)
    clamps_corrosion = models.CharField(verbose_name=_("Rusting/Corrosion on clamps?"),max_length=10, choices=YN)
    vandalism = models.CharField(verbose_name=_("Signs of Vandalism (Loose/missing hardware bolts & pins)?"),max_length=10, choices=YN)
    arcing_horns = models.CharField(verbose_name=_("misaligned arcing horns/corona rings? "),max_length=10, choices=YN)
    number_plate = models.CharField(verbose_name=_("Number plate/Step bolts/Anti-climbing devices secure "),max_length=10, choices=YN)
    comments = models.TextField(verbose_name=_('Comment'), null=True, blank=True)
    save_status = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.line.towerno} - {self.line.line_name}"