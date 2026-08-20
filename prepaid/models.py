from django.db import models
from user.models import Account, UserProfile
from main.models import County, Region
from django.utils.translation import gettext_lazy as _



class Tid_meters(models.Model):
    meterno = models.CharField(
        max_length=20, verbose_name=_("Meter Number"), unique=True, db_index=True
    )
    accountno = models.CharField(max_length=20, verbose_name=_("Account Number"))
    itin = models.CharField(
        verbose_name=_("Itinerary"), max_length=200, blank=True, null=True
    )
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True,related_name='tid_county_target')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True,related_name='tid_region_target')
    sector = models.CharField(
        max_length=100, verbose_name=_("Sector"), null=True, blank=True
    )
    zone = models.CharField(
        max_length=100, verbose_name=_("Zone"), null=True, blank=True
    )
    customer_name = models.CharField(
        verbose_name=_("Customer Name"), max_length=200, blank=True, null=True
    )
    mobile_vend = models.CharField(
        verbose_name=_("Mobile Number"), max_length=50, null=True, blank=True
    )
    mobile_incms = models.CharField(
        verbose_name=_("Mobile Number"), max_length=50, null=True, blank=True
    )
    tech_center = models.CharField(
        verbose_name=_("Tech Center"), max_length=50, null=True, blank=True
    )
    office_name = models.CharField(
        verbose_name=_("Office Name"), max_length=100, blank=True, null=True
    )
    supply_address = models.CharField(
        verbose_name=_("Supply Address"), max_length=255, blank=True, null=True
    )
    longitute = models.CharField(_("Longitude"), max_length=255, null=True, blank=True)
    latitude = models.CharField(_("Latitude"), max_length=255, null=True, blank=True)
    status = models.BooleanField(default=False)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.meterno

class Tid_inspection(models.Model):
    METERINGSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("okay", "OKAY"),
        ("faulty", "FAULTY"),
        ("tampered", "TAMPERED"),
        ("bypassed", "BYPASSED"),
        ("nometer", "NO METER"),
    )
    TIDSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("upgraded", "UPGRADED"),
        ("failed", "FAILED"),
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

    NOTOKAYSTATUS = (
        ("", "----CHOOSE A STATUS----"),
        ("loosejoints", "LOOSE JOINTS"),
        ("noearth", "NO EARTH"),
        ("demolishedpremises", "DEMOLISHED PREMISES"),
        ("vacant", "VACANT"),
        ("nometertails", "NO METER TAILS"),
        ("loosemeterbox", "LOOSE METERBOX"),
    )
    tid = models.ForeignKey(
        Tid_meters,
        on_delete=models.SET_NULL,
        null=True,
        related_name="dc_target",
    )
    meterno = models.CharField(
        max_length=20, verbose_name=_("Meter Number"), unique=True, db_index=True
    )
    accountno = models.CharField(max_length=20, verbose_name=_("Account Number"))
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
    notokaystatus = models.CharField(
        verbose_name=_("Not Okay Status"),
        max_length=50,
        choices=NOTOKAYSTATUS,
        null=True,
        blank=True,
    )
    inspector = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, related_name="tid_inspector"
    )
    meterimg = models.ImageField(
        upload_to="images/tid/%Y/%m/%d/",
        null=True,
        blank=True,
        default="images/default.jpg",
    )

    comment = models.TextField(verbose_name=_("Any Comment"), null=True, blank=True)
    county = models.ForeignKey(
        County, on_delete=models.SET_NULL, null=True, related_name="tid_county"
    )
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True, related_name="tid_region"
    )
    sealno = models.CharField(
        max_length=50, verbose_name=_("Seal Number"), blank=True, null=True
    )
    incms_status = models.BooleanField(default=False)
    incms_nextlevel = models.BooleanField(default=False)
    r_units = models.DecimalField(
        _("Billed Units"), max_digits=12, decimal_places=2, default=0
    )
    anomaly_status = models.BooleanField(default=False)
    y = models.CharField(_("Y"), max_length=255)
    x = models.CharField(_("X"), max_length=255)
    tidstatus = models.CharField(
        verbose_name=_("TID Status"),
        max_length=50,
        choices=TIDSTATUS,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.meterno

class LP_inspection_2025_2026(models.Model):
    start = models.DateField(verbose_name=_("Start Date"))
    end = models.DateField(verbose_name=_("End Date"))
    device_id = models.CharField(max_length=100)
    xy = models.FloatField(verbose_name=_("XY"), null=True, blank=True)
    meter_number = models.CharField(blank=True, null=True, max_length=50)
    meter_installation = models.CharField(blank=True, null=True, max_length=200)
    srn_number = models.CharField(blank=True, null=True, max_length=50)
    account_number = models.CharField(blank=True, null=True, max_length=50)
    county_id = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name="lp202526_county")
    region_id = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name="lp202526_region")
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
    user_id = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name="lp202526_staff")
    def __str__(self):
        return self.meter_number
        