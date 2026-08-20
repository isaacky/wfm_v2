from django.db import models
from user.models import UserProfile
from main.models import County, Region
from django.utils.translation import gettext_lazy as _

class Sixtysix_kv_customer(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    feeder = models.CharField(max_length=255, null=True, blank=True)
    meter_number = models.CharField(max_length=255, unique=True)
    account_number = models.CharField(max_length=255, null=True, blank=True)
    new_account_number = models.CharField(max_length=255, null=True, blank=True)
    type = models.IntegerField(default=0)
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sixtysix_region",
    )
    county = models.ForeignKey(
        County,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sixtysix_county",
    )
    status = models.BooleanField(default=False)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sixtysix_user",
    )

    def __str__(self):
        return self.name

TR_V = (
        ("", "----CHOOSE A STATUS----"),
        ("220/66", "220/66"),
        ("132/66", "132/66"),
        ("66/33", "66/33"),
        ("66/11", "66/11"),
    )
class Sixtysix_kv_substation(models.Model):
    customer = models.ForeignKey(Sixtysix_kv_customer, on_delete=models.DO_NOTHING, null=True, related_name='sixtysix_substation')
    substation_name = models.CharField(max_length=255, null=True, blank=True)
    transform_voltage = models.CharField(max_length=20, choices=TR_V, null=True)
    no_tx_ss = models.IntegerField(null=True, blank=True)
    tx_rating = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    no_hv_lines = models.IntegerField(null=True, blank=True)
    no_mv_lines = models.IntegerField(null=True, blank=True)
    save_status = models.BooleanField(default=False)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='county_sixty_substation')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True,related_name='region_sixty_substation')

    def __str__(self):
        return self.customer.name
CONCONFIG = (
        ("", "----CHOOSE A STATUS----"),
        ("YES", "YES"),
        ("NO", "NO"),
    )

class Sixtysix_kv_otherinfo(models.Model):
    customer = models.OneToOneField(Sixtysix_kv_substation, on_delete=models.CASCADE, null=True, related_name='sixtysix_otherinfo')
    aux_supp_meter = models.CharField(max_length=20, choices=CONCONFIG, null=True)
    aux_supp_meterno =models.CharField(max_length=255, null=True, blank=True)
    certificates = models.ImageField(
        upload_to="images/transdist/sistysix/certificates/%Y/%m/%d/",
        default="images/default.jpg"
    )
    team_members = models.CharField(max_length=255, null=True, blank=True)
    overall_rem = models.TextField(null=True, blank=True)
    declaration = models.BooleanField(default=False)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.customer.name


class Sixtysix_kv_meter_readings(models.Model):
    customer = models.OneToOneField(Sixtysix_kv_substation, on_delete=models.CASCADE, null=True, related_name='sixtysix_readings')
    meter_time_curr = models.TimeField(null=True, blank=True)
    meter_time_mem = models.TimeField(null=True, blank=True)
    meter_date_cur = models.DateField(null=True, blank=True)
    meter_date_mem = models.DateField(null=True, blank=True)
    imp_180_cur = models.CharField(max_length=255, null=True, blank=True)
    reading_180_img = models.ImageField(
        upload_to="images/transdist/sistysix/reading180/%Y/%m/%d/",
        default="images/default.jpg"
    )
    reading_280_img = models.ImageField(
        upload_to="images/transdist/sistysix/reading280/%Y/%m/%d/",
        default="images/default.jpg"
    )
    imp_180_mem = models.CharField(max_length=255, null=True, blank=True)
    exp_280_cur = models.CharField(max_length=255, null=True, blank=True)
    exp_280_mem = models.CharField(max_length=255, null=True, blank=True)
    rated_v_ct = models.CharField(max_length=255, null=True, blank=True)
    rated_v_vt = models.CharField(max_length=255, null=True, blank=True)
    kva_960_cur = models.CharField(max_length=255, null=True, blank=True)
    kva_960_mem = models.CharField(max_length=255, null=True, blank=True)
    kw_150_cur = models.CharField(max_length=255, null=True, blank=True)
    kw_150_mem = models.CharField(max_length=255, null=True, blank=True)
    r_phase_v = models.CharField(max_length=255, null=True, blank=True)
    y_phase_v = models.CharField(max_length=255, null=True, blank=True)
    b_phase_v = models.CharField(max_length=255, null=True, blank=True)
    r_phase_c = models.CharField(max_length=255, null=True, blank=True)
    y_phase_c = models.CharField(max_length=255, null=True, blank=True)
    b_phase_c = models.CharField(max_length=255, null=True, blank=True)
    pw_f = models.CharField(max_length=255, null=True, blank=True)
    ct_vt_match = models.CharField(max_length=20, choices=CONCONFIG, null=True)
    m_remarks = models.TextField(null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.customer.name

CONCONFIG1 = (
        ("", "----CHOOSE A STATUS----"),
        ("LILO", "LILO"),
        ("T-OFF", "T-OFF"),
    )


class Sixtysix_kv_ctvt_bluephase(models.Model):
    customer = models.OneToOneField(Sixtysix_kv_substation, on_delete=models.CASCADE, null=True, related_name='sixtysix_ctvt_blue')
    sn_ct = models.CharField(max_length=255, null=True, blank=True)
    sn_vt = models.CharField(max_length=255, null=True, blank=True)
    man_ct = models.CharField(max_length=255, null=True, blank=True)
    man_vt = models.CharField(max_length=255, null=True, blank=True)
    yom_ct = models.CharField(max_length=255, null=True, blank=True)
    yom_vt = models.CharField(max_length=255, null=True, blank=True)
    rated_v_ct = models.CharField(max_length=255, null=True, blank=True)
    rated_v_vt = models.CharField(max_length=255, null=True, blank=True)
    cores_ct = models.CharField(max_length=255, null=True, blank=True)
    cores_vt = models.CharField(max_length=255, null=True, blank=True)
    con_core_ct = models.CharField(max_length=255, null=True, blank=True)
    con_core_vt = models.CharField(max_length=255, null=True, blank=True)
    meter_core_ct = models.CharField(max_length=255, null=True, blank=True)
    meter_core_vt = models.CharField(max_length=255, null=True, blank=True)
    nameplate_ratio_ct = models.CharField(max_length=255, null=True, blank=True)
    nameplate_ratio_vt = models.CharField(max_length=255, null=True, blank=True)
    acc_meter_core_ct = models.CharField(max_length=255, null=True, blank=True)
    acc_meter_core_vt = models.CharField(max_length=255, null=True, blank=True)
    test_eqp_ct = models.CharField(max_length=255, null=True, blank=True)
    test_eqp_vt = models.CharField(max_length=255, null=True, blank=True)
    meas_trn_rt_ct = models.CharField(max_length=255, null=True, blank=True)
    meas_trn_rt_vt = models.CharField(max_length=255, null=True, blank=True)
    ration_dev_ct = models.CharField(max_length=255, null=True, blank=True)
    ration_dev_vt = models.CharField(max_length=255, null=True, blank=True)
    rem_ct = models.CharField(max_length=255, null=True, blank=True)
    rem_vt = models.CharField(max_length=255, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.customer.name

class Sixtysix_kv_ctvt_yellowphase(models.Model):
    customer = models.OneToOneField(Sixtysix_kv_substation, on_delete=models.CASCADE, null=True, related_name='sixtysix_ctvt_yellow')
    sn_ct = models.CharField(max_length=255, null=True, blank=True)
    sn_vt = models.CharField(max_length=255, null=True, blank=True)
    man_ct = models.CharField(max_length=255, null=True, blank=True)
    man_vt = models.CharField(max_length=255, null=True, blank=True)
    yom_ct = models.CharField(max_length=255, null=True, blank=True)
    yom_vt = models.CharField(max_length=255, null=True, blank=True)
    rated_v_ct = models.CharField(max_length=255, null=True, blank=True)
    rated_v_vt = models.CharField(max_length=255, null=True, blank=True)
    cores_ct = models.CharField(max_length=255, null=True, blank=True)
    cores_vt = models.CharField(max_length=255, null=True, blank=True)
    con_core_ct = models.CharField(max_length=255, null=True, blank=True)
    con_core_vt = models.CharField(max_length=255, null=True, blank=True)
    meter_core_ct = models.CharField(max_length=255, null=True, blank=True)
    meter_core_vt = models.CharField(max_length=255, null=True, blank=True)
    nameplate_ratio_ct = models.CharField(max_length=255, null=True, blank=True)
    nameplate_ratio_vt = models.CharField(max_length=255, null=True, blank=True)
    acc_meter_core_ct = models.CharField(max_length=255, null=True, blank=True)
    acc_meter_core_vt = models.CharField(max_length=255, null=True, blank=True)
    test_eqp_ct = models.CharField(max_length=255, null=True, blank=True)
    test_eqp_vt = models.CharField(max_length=255, null=True, blank=True)
    meas_trn_rt_ct = models.CharField(max_length=255, null=True, blank=True)
    meas_trn_rt_vt = models.CharField(max_length=255, null=True, blank=True)
    ration_dev_ct = models.CharField(max_length=255, null=True, blank=True)
    ration_dev_vt = models.CharField(max_length=255, null=True, blank=True)
    rem_ct = models.CharField(max_length=255, null=True, blank=True)
    rem_vt = models.CharField(max_length=255, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.customer.name

class Sixtysix_kv_ctvt_redphase(models.Model):
    customer = models.OneToOneField(Sixtysix_kv_substation, on_delete=models.CASCADE, null=True, related_name='sixtysix_ctvt_red')
    sn_ct = models.CharField(max_length=255, null=True, blank=True)
    sn_vt = models.CharField(max_length=255, null=True, blank=True)
    man_ct = models.CharField(max_length=255, null=True, blank=True)
    man_vt = models.CharField(max_length=255, null=True, blank=True)
    yom_ct = models.CharField(max_length=255, null=True, blank=True)
    yom_vt = models.CharField(max_length=255, null=True, blank=True)
    rated_v_ct = models.CharField(max_length=255, null=True, blank=True)
    rated_v_vt = models.CharField(max_length=255, null=True, blank=True)
    cores_ct = models.CharField(max_length=255, null=True, blank=True)
    cores_vt = models.CharField(max_length=255, null=True, blank=True)
    con_core_ct = models.CharField(max_length=255, null=True, blank=True)
    con_core_vt = models.CharField(max_length=255, null=True, blank=True)
    meter_core_ct = models.CharField(max_length=255, null=True, blank=True)
    meter_core_vt = models.CharField(max_length=255, null=True, blank=True)
    nameplate_ratio_ct = models.CharField(max_length=255, null=True, blank=True)
    nameplate_ratio_vt = models.CharField(max_length=255, null=True, blank=True)
    acc_meter_core_ct = models.CharField(max_length=255, null=True, blank=True)
    acc_meter_core_vt = models.CharField(max_length=255, null=True, blank=True)
    test_eqp_ct = models.CharField(max_length=255, null=True, blank=True)
    test_eqp_vt = models.CharField(max_length=255, null=True, blank=True)
    meas_trn_rt_ct = models.CharField(max_length=255, null=True, blank=True)
    meas_trn_rt_vt = models.CharField(max_length=255, null=True, blank=True)
    ration_dev_ct = models.CharField(max_length=255, null=True, blank=True)
    ration_dev_vt = models.CharField(max_length=255, null=True, blank=True)
    rem_ct = models.CharField(max_length=255, null=True, blank=True)
    rem_vt = models.CharField(max_length=255, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.customer.name
class Sixtysix_kv_current(models.Model):
    customer = models.OneToOneField(Sixtysix_kv_substation, on_delete=models.CASCADE, null=True, related_name='sixtysix_current')
    rphase_amcoder = models.CharField(max_length=255, null=True, blank=True)
    rphase_meter = models.CharField(max_length=255, null=True, blank=True)
    rphase_zera = models.CharField(max_length=255, null=True, blank=True)
    yphase_amcoder = models.CharField(max_length=255, null=True, blank=True)
    yphase_meter = models.CharField(max_length=255, null=True, blank=True)
    yphase_zera = models.CharField(max_length=255, null=True, blank=True)
    bphase_amcoder = models.CharField(max_length=255, null=True, blank=True)
    bphase_meter = models.CharField(max_length=255, null=True, blank=True)
    bphase_zera = models.CharField(max_length=255, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.customer.name

class Sixtysix_kv_testeqipment(models.Model):
    customer = models.OneToOneField(Sixtysix_kv_substation, on_delete=models.CASCADE, null=True, related_name='sixtysix_testeqp')
    zera_sn = models.CharField(max_length=255, null=True, blank=True)
    ct_analyz_sn = models.CharField(max_length=255, null=True, blank=True)
    vt_isa_sn = models.CharField(max_length=255, null=True, blank=True)
    amcoder_sn = models.CharField(max_length=255, null=True, blank=True)
    error_t1 = models.CharField(max_length=255, null=True, blank=True)
    error_t2 = models.CharField(max_length=255, null=True, blank=True)
    error_t3 = models.CharField(max_length=255, null=True, blank=True)
    error_avg = models.CharField(max_length=255, null=True, blank=True)
    rem_error_test = models.TextField(null=True, blank=True)
    avg_per_err = models.CharField(max_length=255, null=True, blank=True)
    rem_reg_test = models.TextField(null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.customer.name

class Sixtysix_kv_sealing(models.Model):
    customer = models.OneToOneField(Sixtysix_kv_substation, on_delete=models.CASCADE, null=True, related_name='sixtysix_sealing')
    prg_seal_init = models.CharField(max_length=255, null=True, blank=True)
    prg_seal_fin = models.CharField(max_length=255, null=True, blank=True)
    term_sl_init = models.CharField(max_length=255, null=True, blank=True)
    term_sl_fin = models.CharField(max_length=255, null=True, blank=True)
    testb_sl_init = models.CharField(max_length=255, null=True, blank=True)
    testb_sl_fin = models.CharField(max_length=255, null=True, blank=True)
    body_sl_init = models.CharField(max_length=255, null=True, blank=True)
    body_sl_fin = models.CharField(max_length=255, null=True, blank=True)
    vten_r_sl_init = models.CharField(max_length=255, null=True, blank=True)
    vten_r_sl_fin = models.CharField(max_length=255, null=True, blank=True)
    vten_y_sl_init = models.CharField(max_length=255, null=True, blank=True)
    vten_y_sl_fin = models.CharField(max_length=255, null=True, blank=True)
    vten_b_sl_init = models.CharField(max_length=255, null=True, blank=True)
    vten_b_sl_fin = models.CharField(max_length=255, null=True, blank=True)
    cten_r_sl_init = models.CharField(max_length=255, null=True, blank=True)
    cten_r_sl_fin = models.CharField(max_length=255, null=True, blank=True)
    cten_y_sl_init = models.CharField(max_length=255, null=True, blank=True)
    cten_y_sl_fin = models.CharField(max_length=255, null=True, blank=True)
    cten_b_sl_init = models.CharField(max_length=255, null=True, blank=True)
    cten_b_sl_fin = models.CharField(max_length=255, null=True, blank=True)
    marsha_kiosk_init = models.CharField(max_length=255, null=True, blank=True)
    marsha_kiosk_fin = models.CharField(max_length=255, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.customer.name

MCONFIGS = (
        ("", "----CHOOSE A STATUS----"),
        ("3P3W", "3P3W"),
        ("3P4W", "3P4W"),
    )
class Sixtysix_kv_meter(models.Model):
    customer = models.OneToOneField(Sixtysix_kv_substation, on_delete=models.CASCADE, null=True, related_name='sixtysix_meter')
    meter_number = models.CharField(max_length=255, null=True, blank=True)
    feeder_name = models.CharField(max_length=255, null=True, blank=True)
    manufacturer = models.CharField(max_length=255, null=True, blank=True)
    meter_model = models.CharField(max_length=255, null=True, blank=True)
    conn_config = models.CharField(max_length=20, choices=CONCONFIG, null=True)
    yom = models.IntegerField(null=True, blank=True)
    meter_accuracy_class = models.CharField(max_length=255, null=True, blank=True)
    progrm_ctr = models.CharField(max_length=255, null=True, blank=True)
    progrm_vtr = models.CharField(max_length=255, null=True, blank=True)
    meter_config = models.CharField(max_length=20, choices=MCONFIGS, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.customer.name
class Transdist_subsations(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    internalcode = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transdist_sbstn_region",
    )
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Transdist_insp(models.Model):
    transdist = models.ForeignKey(
        Transdist_subsations,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transdist_target",
    )
    county = models.ForeignKey(
        County,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transdist_county",
    )
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    inspector = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transdist_inspected_by",
    )
    save_status = models.BooleanField(default=False)

    def __str__(self):
        return self.transdist


class Feeder_inspection(models.Model):
    YESNO = (
        ("", "----CHOOSE A STATUS----"),
        ("yes", "YES"),
        ("no", "NO"),
    )
    MTYPE = (
        ("", "----CHOOSE A STATUS----"),
        ("smart", "SMART"),
        ("amr", "AMR"),
        ("other", "OTHER"),
    )
    transdist = models.ForeignKey(
        Transdist_insp,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transdist_inspection",
    )
    feeder_source = models.CharField(max_length=255, blank=True, null=True)
    feeder_metered = models.CharField(
        max_length=10, choices=YESNO, null=True, blank=True
    )
    meternumber = models.CharField(max_length=255, null=True, blank=True)
    meterbrand = models.CharField(max_length=255, null=True, blank=True)
    metermodel = models.CharField(max_length=255, null=True, blank=True)
    metertype = models.CharField(max_length=50, choices=MTYPE, null=True, blank=True)
    classofmeter = models.CharField(max_length=255, null=True, blank=True)
    ct_ratio = models.CharField(max_length=255, null=True, blank=True)
    vt_ratio = models.CharField(max_length=255, null=True, blank=True)
    metering_core_ctratio = models.CharField(max_length=255, null=True, blank=True)
    metering_core_class_ct = models.CharField(max_length=255, null=True, blank=True)
    metering_core_burden_va = models.CharField(max_length=255, null=True, blank=True)
    vt_ration_linked_yard = models.CharField(max_length=255, null=True, blank=True)
    ct_ration_linked_yard = models.CharField(max_length=255, null=True, blank=True)
    class_vt = models.CharField(max_length=255, null=True, blank=True)
    vt_burden_va = models.CharField(max_length=255, null=True, blank=True)
    dt_visit = models.DateField(null=True,blank=True)
    tm_visit = models.TimeField(null=True,blank=True)
    dt_on_meter_during_visit = models.DateField(null=True,blank=True)
    tm_on_meter_during_visit = models.TimeField(null=True,blank=True)
    reading_180 = models.CharField(max_length=255, null=True, blank=True)
    reading_1801 = models.CharField(max_length=255, null=True, blank=True)
    reading_280 = models.CharField(max_length=255, null=True, blank=True)
    reading_2801 = models.CharField(max_length=255, null=True, blank=True)
    powerfactor = models.CharField(max_length=255, null=True, blank=True)
    vlt_redphase = models.CharField(max_length=255, null=True, blank=True)
    vlt_yellowphase = models.CharField(max_length=255, null=True, blank=True)
    vlt_bluephase = models.CharField(max_length=255, null=True, blank=True)
    crnt_redphase = models.CharField(max_length=255, null=True, blank=True)
    crnt_yellowphase = models.CharField(max_length=255, null=True, blank=True)
    crnt_bluephase = models.CharField(max_length=255, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    recommendation = models.TextField(null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspector = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="feeder_inspected_by",
    )
    reading_180_img = models.ImageField(
        upload_to="images/transdist/feeder/reading180/%Y/%m/%d/",
        default="images/default.jpg"
    )
    metering_vt_ratio = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.transdist.transdist.name


class Feeder_inspection_outgoing(models.Model):
    YESNO = (
        ("", "----CHOOSE A STATUS----"),
        ("yes", "YES"),
        ("no", "NO"),
    )
    MTYPE = (
        ("", "----CHOOSE A STATUS----"),
        ("smart", "SMART"),
        ("amr", "AMR"),
        ("other", "OTHER"),
    )
    transdist = models.ForeignKey(
        Transdist_insp,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transdist_inspection_outgoing",
    )
    feeder_source = models.CharField(max_length=255, blank=True, null=True)
    feeder_metered = models.CharField(
        max_length=10, choices=YESNO, null=True, blank=True
    )
    meternumber = models.CharField(max_length=255, null=True, blank=True)
    meterbrand = models.CharField(max_length=255, null=True, blank=True)
    metermodel = models.CharField(max_length=255, null=True, blank=True)
    metertype = models.CharField(max_length=50, choices=MTYPE, null=True, blank=True)
    classofmeter = models.CharField(max_length=255, null=True, blank=True)
    ct_ratio = models.CharField(max_length=255, null=True, blank=True)
    vt_ratio = models.CharField(max_length=255, null=True, blank=True)
    metering_core_ctratio = models.CharField(max_length=255, null=True, blank=True)
    metering_core_class_ct = models.CharField(max_length=255, null=True, blank=True)
    metering_core_burden_va = models.CharField(max_length=255, null=True, blank=True)
    vt_ration_linked_yard = models.CharField(max_length=255, null=True, blank=True)
    ct_ration_linked_yard = models.CharField(max_length=255, null=True, blank=True)
    class_vt = models.CharField(max_length=255, null=True, blank=True)
    vt_burden_va = models.CharField(max_length=255, null=True, blank=True)
    dt_visit = models.DateField(null=True,blank=True)
    tm_visit = models.TimeField(null=True,blank=True)
    dt_on_meter_during_visit = models.DateField(null=True,blank=True)
    tm_on_meter_during_visit = models.TimeField(null=True,blank=True)
    reading_180 = models.CharField(max_length=255, null=True, blank=True)
    reading_1801 = models.CharField(max_length=255, null=True, blank=True)
    reading_280 = models.CharField(max_length=255, null=True, blank=True)
    reading_2801 = models.CharField(max_length=255, null=True, blank=True)
    powerfactor = models.CharField(max_length=255, null=True, blank=True)
    vlt_redphase = models.CharField(max_length=255, null=True, blank=True)
    vlt_yellowphase = models.CharField(max_length=255, null=True, blank=True)
    vlt_bluephase = models.CharField(max_length=255, null=True, blank=True)
    crnt_redphase = models.CharField(max_length=255, null=True, blank=True)
    crnt_yellowphase = models.CharField(max_length=255, null=True, blank=True)
    crnt_bluephase = models.CharField(max_length=255, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    recommendation = models.TextField(null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspector = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="feeder_inspected_by_outgoing",
    )
    reading_180_img = models.ImageField(
        upload_to="images/transdist/feeder/reading180/%Y/%m/%d/",
        default="images/default.jpg"
    )
    metering_vt_ratio = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.transdist.transdist.name


class Power_tx_inspection(models.Model):
    YESNO = (
        ("", "----CHOOSE A STATUS----"),
        ("yes", "YES"),
        ("no", "NO"),
    )
    MTYPE = (
        ("", "----CHOOSE A STATUS----"),
        ("smart", "SMART"),
        ("amr", "AMR"),
        ("other", "OTHER"),
    )
    powername = models.CharField(max_length=255, null=True, blank=True)
    transdist = models.ForeignKey(
        Transdist_insp,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transdist_inspection_powertx",
    )
    istherenameplate = models.CharField(
        max_length=10, choices=YESNO, null=True, blank=True
    )
    nameplateimg = models.ImageField(
        upload_to="images/transdist/powertx/nameplate/%Y/%m/%d/",
        default="images/default.jpg",
    )
    rated_mva = models.CharField(max_length=255, null=True, blank=True)
    noloadloss = models.CharField(max_length=255, null=True, blank=True)
    loadloss = models.CharField(max_length=255, null=True, blank=True)
    metering_vt_ratio=models.CharField(max_length=255, null=True, blank=True)
    metering_vt_class = models.CharField(max_length=255, null=True, blank=True)
    metering_core_burden_vt = models.CharField(max_length=255, null=True, blank=True)
    metering_core_ctratio = models.CharField(max_length=255, null=True, blank=True)
    metering_core_class_ct = models.CharField(max_length=255, null=True, blank=True)
    metering_core_burden_ct = models.CharField(max_length=255, null=True, blank=True)
    ismetered = models.CharField(
        max_length=10, choices=YESNO, null=True, blank=True
    )
    meternumber = models.CharField(max_length=255, null=True, blank=True)
    meterbrand = models.CharField(max_length=255, null=True, blank=True)
    metermodel = models.CharField(max_length=255, null=True, blank=True)
    metertype = models.CharField(max_length=50, choices=MTYPE, null=True, blank=True)
    classofmeter = models.CharField(max_length=255, null=True, blank=True)
    ct_ratio = models.CharField(max_length=255, null=True, blank=True)
    vt_ratio = models.CharField(max_length=255, null=True, blank=True)
    vt_ration_linked_meter = models.CharField(max_length=255, null=True, blank=True)
    ct_ration_linked_meter = models.CharField(max_length=255, null=True, blank=True)
    dt_visit = models.DateField(null=True,blank=True)
    tm_visit = models.TimeField(null=True,blank=True)
    dt_on_meter_during_visit = models.DateField(null=True,blank=True)
    tm_on_meter_during_visit = models.TimeField(null=True, blank=True)
    reading_180 = models.CharField(max_length=255, null=True, blank=True)
    reading_1801 = models.CharField(max_length=255, null=True, blank=True)
    reading_280 = models.CharField(max_length=255, null=True, blank=True)
    reading_2801 = models.CharField(max_length=255, null=True, blank=True)
    powerfactor = models.CharField(max_length=255, null=True, blank=True)
    vlt_redphase = models.CharField(max_length=255, null=True, blank=True)
    vlt_yellowphase = models.CharField(max_length=255, null=True, blank=True)
    vlt_bluephase = models.CharField(max_length=255, null=True, blank=True)
    crnt_redphase = models.CharField(max_length=255, null=True, blank=True)
    crnt_yellowphase = models.CharField(max_length=255, null=True, blank=True)
    crnt_bluephase = models.CharField(max_length=255, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    recommendation = models.TextField(null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspector = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="powertx_inspected_by",
    )
    reading_180_img = models.ImageField(
        upload_to="images/transdist/powertx/reading180/%Y/%m/%d/",
        default="images/default.jpg"
    )

    def __str__(self):
        return self.transdist.transdist.name

class Aux_tx_inspection(models.Model):
    MTYPE = (
        ("", "----CHOOSE A STATUS----"),
        ("ct", "CT"),
        ("directmetering", "DIRECT METERING"),
    )
    YESNO = (
        ("", "----CHOOSE A STATUS----"),
        ("yes", "YES"),
        ("no", "NO"),
    )
    transdist = models.ForeignKey(
        Transdist_insp,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transdist_inspection_auxtx",
    )
    ssn = models.CharField(max_length=255, null=True, blank=True)
    metered = models.CharField(max_length=10, choices=YESNO, null=True, blank=True)
    mounting_strx = models.CharField(max_length=255, null=True, blank=True)
    meternumber = models.CharField(max_length=255, null=True, blank=True)
    meterbrand = models.CharField(max_length=255, null=True, blank=True)
    metermodel = models.CharField(max_length=255, null=True, blank=True)
    metertype = models.CharField(max_length=50, choices=MTYPE, null=True, blank=True)
    reading_180 = models.CharField(max_length=255, null=True, blank=True)
    reading_280 = models.CharField(max_length=255, null=True, blank=True)
    reading_180_img = models.ImageField(
        upload_to="images/transdist/powertx/reading180/%Y/%m/%d/",
        default="images/default.jpg"
    )
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspector = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        related_name="auxtx_inspected_by",
    )
    remarks = models.TextField(null=True, blank=True)
    recommendation = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.transdist.transdist.name
