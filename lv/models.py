from django.db import models
from main.models import County,Region
from user.models import Account, UserProfile
from datetime import datetime


# Create your models here.
class Txmakes(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    createdby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class Substation(models.Model):
    ssn = models.CharField(max_length=255, null=True, blank=True, db_index=True, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    gnumber = models.CharField(max_length=255, null=True, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='ssn_county')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='ssn_region')
    internalcode = models.CharField(max_length=100, null=True, blank=True)
    originofelement = models.CharField(max_length=255, null=True, blank=True)
    feederofelement = models.CharField(max_length=255, null=True, blank=True)
    physicallocation = models.CharField(max_length=255, null=True, blank=True)
    da = models.CharField(max_length=255, null=True, blank=True)
    lenghth = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=10, decimal_places=2)
    voltage = models.DecimalField(max_digits=10, decimal_places=2)
    yom = models.IntegerField()
    make = models.ForeignKey(Txmakes, on_delete=models.SET_NULL, null=True, related_name='ssn_make')
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    createdby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='ssn_createdby')
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.ssn

class Lvinspection(models.Model):
    YESNO = (
        ('', '----CHOOSE THE STATUS----'),
        ('yes', 'YES'),
        ('no', 'NO'),
    )

    CIRCUITS = (
        ('', '----CHOOSE THE STATUS----'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),

    )
    APRVKEY = (
        ('', '----CHOOSE THE STATUS----'),
        ('approved', 'APPROVED'),
        ('declined', 'DECLINED'),
    )
    KVARATING = (
        ('', '----CHOOSE THE STATUS----'),
        ('5', '5'),
        ('15', '15'),
        ('25', '25'),
        ('50', '50'),
        ('100', '100'),
        ('200', '200'),
        ('315', '315'),
        ('630', '630'),
        ('1000', '1000'),
        ('3*5', '3*5'),
        ('3*15', '3*15'),
        ('3*25', '3*25'),
    )
    substation = models.ForeignKey(Substation, on_delete=models.SET_NULL, null=True, related_name='substation_inspection', db_index=True)
    poor_sags_cl_cond = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    retention_req = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    retention_maintanance = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    retention_req_status = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    lvline_veg = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    traceclear_span = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    traceclear_span_status = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    trace_maintanance = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    conductors_uprate = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    conductors_uprate_status = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    conductors_uprate_span = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    conductors_uprate_span_status = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    upratingconduct_maintanance = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    pme_installed = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    pme_missing_poles = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    pme_missing_poles_status = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    pme_maintanance = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    lv_overdistance = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    lv_overdistance_l = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    lv_overdistance_l_status = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    lvoverdistance_maintanance = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    illegal_connections = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    illegal_connections_l = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    illegal_connections_l_status = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    illegalconn_maintanance = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    jumper_rehab_sect = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    jumperrehab_maintanance = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    reconducturing_pvc = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    reconducturing_pvc_l = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    reconducturing_pvc_l_status = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    reconductering_maintanance = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    circuits = models.CharField(max_length=50, choices=CIRCUITS, null=True, blank=True)
    c1_r =models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c1_b = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c1_y = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    C1_threephase = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c2_1r = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c2_1b = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c2_1y = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    C2_1threephase = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c2_2r = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c2_2b = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c2_2y =models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    C2_2threephase = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c3_1r = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c3_1b = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c3_1y = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    C3_1threephase = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c3_2r = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c3_2b = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c3_2y = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    C3_2threephase = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c3_3r = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c3_3b = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c3_3y = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    C3_3threephase = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    poshomills_onsingle_p = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    poshomills_onsingle_p_n = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    poshomills_onsingle_p_n_status = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    poshomill_maintenance = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    inspect_notes = models.TextField(blank=True, null=True)
    maitenance_notes = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    save_status = models.BooleanField(default=False, db_index=True)
    aprv_status = models.BooleanField(default=False, db_index=True)
    aprv_status_maintenance = models.BooleanField(default=False, db_index=True)
    aprv_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='lv_approved_by')
    aprv_by_maintenace = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='lv_approved_by_maintenance')
    aprv_notes = models.TextField(blank=True, null=True)
    aprv_notes_maintenace = models.TextField(blank=True, null=True)
    aprv_dt = models.DateField(null=True, blank=True)
    aprv_dt_maintenance = models.DateField(default=datetime.now)
    aprv_key = models.CharField(max_length=10, choices=APRVKEY, null=True, blank=True)
    aprv_key_maintenance = models.CharField(max_length=10, choices=APRVKEY, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    dt_maintenance = models.DateField(default=datetime.now)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True,  related_name='lv_inspected_by')
    inspectedby_maintenance = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='lv_inspected_by_maintenance')
    county = models.ForeignKey(County,on_delete=models.SET_NULL, null=True, related_name='inspected_county')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='lvinspection_region')
    lvsketch_img = models.ImageField(upload_to="images/lv/sketch/%Y/%m/%d/", default="images/default.jpg")
    kvarating = models.CharField(max_length=50, choices=KVARATING, null=True, blank=True)

    def __str__(self):
        return self.substation.ssn

class Lv_defaults(models.Model):
    lvinspection = models.ForeignKey(Lvinspection, on_delete=models.SET_NULL, null=True,related_name='lv_inspection_default', db_index=True)
    substation = models.ForeignKey(Substation, on_delete=models.SET_NULL, null=True,related_name='lvdefects_substation', db_index=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='lv_default_inspected_by')
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='lvdefaults_county')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='lvdefaults_region')
    poorsags = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    vegline = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    uprate_cond = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    pme = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    con_illegal = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    jumper_rehab = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    poshomill = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    overdistance = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    lvreconductor = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return self.lvinspection.substation.name


class Poledefects(models.Model):
    DEFECTTYPE = (
        ('', '----CHOOSE THE STATUS----'),
        ('rotten', 'ROTTEN'),
        ('leaning', 'LEANING'),
        ('midspanpole', 'MIDSPAN POLE'),
        ('brocken', 'BROCKEN'),
    )
    TYPEPOLE = (
        ('', '----CHOOSE THE STATUS----'),
        ('10mwooden', '10m WOODEN'),
        ('11mwooden', '11m WOODEN'),
        ('12mwooden', '12m WOODEN'),
        ('14mwooden', '14m WOODEN'),
        ('10mconcrete', '10m CONCRETE'),
        ('11mconcrete', '11m CONCRETE'),
        ('12mconcrete', '12m CONCRETE'),
        ('14mconcrete', '14m CONCRETE'),
    )
    lvinspection = models.ForeignKey(Lvinspection, on_delete=models.SET_NULL, null=True, related_name='poledefects_lvisnpections')
    substation = models.ForeignKey(Substation, on_delete=models.SET_NULL, null=True, related_name='poledefects_substation')
    defect_type = models.CharField(max_length=50, choices=DEFECTTYPE, null=True, blank=True)
    pole_type = models.CharField(max_length=50, choices=TYPEPOLE, null=True, blank=True)
    y = models.CharField(max_length=100, blank=True, null=True)
    x = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='poledefects_county')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='poledefects_region')
    status = models.BooleanField(default=False)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='lv_inspected_poles_d_by')

    def __str__(self):
        return self.substation.ssn

class MaintainLVinspection(models.Model):
    YESNO = (
        ('', '----CHOOSE THE STATUS----'),
        ('yes', 'YES'),
        ('no', 'NO'),
    )
    APRVKEY = (
        ('', '----CHOOSE THE STATUS----'),
        ('approved', 'APPROVED'),
        ('declined', 'DECLINED'),
    )
    TXPOSITION = (
        ('', '----CHOOSE----'),
        ('terminal', 'TERMINAL'),
        ('line', 'LINE'),
    )
    KVARATING = (
        ('', '----CHOOSE THE STATUS----'),
        ('5', '5'),
        ('15', '15'),
        ('25', '25'),
        ('50', '50'),
        ('100', '100'),
        ('200', '200'),
        ('315', '315'),
        ('630', '630'),
        ('1000', '1000'),
        ('3*5', '3*5'),
        ('3*15', '3*15'),
        ('3*25', '3*25'),
    )
    lvinspection = models.ForeignKey(Lvinspection, on_delete=models.SET_NULL, null=True, related_name='maintainlv_lv')
    retention_req = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    retention_req_status = models.BooleanField(default=False)
    traceclear_span = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    traceclear_span_status = models.BooleanField(default=False)
    conductors_uprate_status = models.BooleanField(default=False)
    conductors_uprate_span = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    pme_missing_poles = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    pme_missing_poles_status = models.BooleanField(default=False)
    lv_overdistance_l = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    lv_overdistance_l_status = models.BooleanField(default=False)
    illegal_connections_l = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    illegal_connections_l_status = models.BooleanField(default=False)
    jumper_rehab_sect = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    reconducturing_pvc_l = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    reconducturing_pvc_l_status = models.BooleanField(default=False)
    poshomills_onsingle_p_n = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    poshomills_onsingle_p_n_status = models.BooleanField(default=False)
    txposition = models.CharField(max_length=10, choices=TXPOSITION, null=True, blank=True)
    inspect_notes = models.TextField(blank=True, null=True)
    save_status = models.BooleanField(default=False, db_index=True)
    aprv_status = models.BooleanField(default=False)
    aprv_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='lv_maintain_approved_by')
    aprv_key = models.CharField(max_length=10, choices=APRVKEY, null=True, blank=True)
    aprv_notes = models.TextField()
    aprv_dt = models.DateField(null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='lv_maintain_by')
    kvarating = models.CharField(max_length=50, choices=KVARATING, null=True, blank=True)
    other_defects = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)


    def __str__(self):
        return self.lvinspection.ssn

class MaintainPoleDefects(models.Model):
    poledefect = models.ForeignKey(Poledefects, on_delete=models.SET_NULL, null=True)
    maitain_status = models.BooleanField(default=False)
    maintain_activity =  models.CharField(max_length=255, blank=True, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='lv_poles_by')

    def __str__(self):
        return self.poledefect.defect_type

class SubstationInspection(models.Model):
    YESNO = (
        ('', '----CHOOSE THE STATUS----'),
        ('yes', 'YES'),
        ('no', 'NO'),
    )
    VOLTAGE = (
        ('', '----CHOOSE THE STATUS----'),
        ('11', '11'),
        ('33', '33'),
    )
    KVARATING = (
        ('', '----CHOOSE THE STATUS----'),
        ('5', '5'),
        ('15', '15'),
        ('25', '25'),
        ('50', '50'),
        ('100', '100'),
        ('200', '200'),
        ('315', '315'),
        ('630', '630'),
        ('1000', '1000'),
        ('3*5', '3*5'),
        ('3*15', '3*15'),
        ('3*25', '3*25'),
    )
    FUSESIZES = (
        ("", "----CHOOSE A SIZE----"),
        ("63", "63A"),
        ("100", "100A"),
        ("125", "125A"),
        ("200", "200A"),
        ("315", "315A"),
        ("420", "420A"),
    )
    LEADSIZES = (
        ("", "----CHOOSE A SIZE----"),
        ("50", "50mm^2"),
        ("100", "100mm^2"),

    )
    CONDUCTORSIZES = (
        ("", "----CHOOSE A SIZE----"),
        ("50", "50mm^2"),
        ("75", "75mm^2"),
        ("100", "100mm^2"),

    )
    CIRCUITS = (
        ('', '----CHOOSE THE STATUS----'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
    )
    TXLOADING = (
        ('', '----CHOOSE THE STATUS----'),
        ('loadingokay', 'LOADING OKAY'),
    )
    LOADDISTRIBUTION = (
        ('', '----CHOOSE THE STATUS----'),
        ('phasebalancing', 'PHASE BALANCING'),
        ('additionalcircuit', 'ADDITIONAL CIRCUIT'),
        ('uprate', 'UPRATE'),
        ('relieve', 'RELIEVE'),
        ("derate", "DERATE"),
    )
    TXSTRUCTURE = (
        ('', '----CHOOSE THE STATUS----'),
        ('okay', 'OKAY'),
        ('leaning', 'LEANING'),
        ('rotten', 'ROTTEN'),
    )
    CFUSECARRIERS = (
        ('', '----CHOOSE THE STATUS----'),
        ('okay', 'OKAY'),
        ('needreplacement', 'NEED REPLACEMENT'),
    )
    FUSEBARTYPE = (
        ('', '----CHOOSE THE STATUS----'),
        ('wooden', 'WOODEN'),
        ('steadybar', 'STEADY BAR(METTALIC)'),
        ('fusecarriersonpole', 'FUSE CARRIERS ON POLE'),
        ("plasctic", "PLASTIC"),
    )
    FUSEBARCOND = (
        ('', '----CHOOSE THE STATUS----'),
        ('okay', 'OKAY'),
        ('rotten', 'ROTTEN'),
        ('broken', 'BROKEN'),
        ('loseconnected', 'LOOSELY CONNECTED'),
        ('missing', 'MISSING'),
    )
    TXWIRING = (
        ('', '----CHOOSE THE STATUS----'),
        ('okay', 'LEADS OKAY(LUGGED & CORRECT SIZE)'),
        ('burnt', 'LEADS BURNT'),
        ('notlugged', 'LEADS NOT LUGGED'),
        ('undersize', 'LEADS UNDERSIZE'),
    )
    APRVKEY = (
        ('', '----CHOOSE THE STATUS----'),
        ('approved', 'APPROVED'),
        ('declined', 'DECLINED'),
    )
    substation = models.ForeignKey(Substation, on_delete=models.SET_NULL, null=True)
    serialno = models.CharField(max_length=100, blank=True, null=True)
    voltage = models.CharField(max_length=50, choices=VOLTAGE, null=True, blank=True)
    kvarating = models.CharField(max_length=50, choices=KVARATING, null=True, blank=True)
    gnumber = models.CharField(max_length=100, blank=True, null=True)
    make = models.ForeignKey(Txmakes, on_delete=models.SET_NULL, null=True, related_name='make_substation')
    yom = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    fusesize = models.CharField(max_length=50, choices=FUSESIZES, null=True, blank=True)
    sizeoflvconductor = models.CharField(max_length=50, choices=CONDUCTORSIZES, null=True, blank=True)
    noofcircuits =  models.CharField(max_length=50, choices=CIRCUITS, null=True, blank=True)
    c_1_R =models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c_1_Y = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c_1_B = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c_1_rn = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c_1_yn = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c_1_bn = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c2_1_R = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c2_1_Y = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c2_1_B = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c2_1_rn = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c2_1_yn = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c2_1_bn = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c2_2_R = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c2_2_Y = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c2_2_B = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c2_2_rn = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c2_2_yn = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c2_2_bn = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c3_1_R = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c3_1_Y = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c3_1_B = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c3_1_rn = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c3_1_yn = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c3_1_bn = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c3_2_R = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c3_2_Y = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c3_2_B = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c3_2_rn = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c3_2_yn = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c3_2_bn = models.IntegerField(help_text='Enter a Number.If none input zero', default=0)
    c3_3_R = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c3_3_Y = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c3_3_B = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c3_3_rn = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c3_3_yn = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c3_3_bn = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    hvearth_intact = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    hvearth_values = models.CharField(max_length=100, blank=True, null=True)
    neutralearth_intact = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    neutralvearth_values = models.CharField(max_length=100, blank=True, null=True)
    surgearrestors = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    surgearrestors_values = models.CharField(max_length=100, blank=True, null=True)
    arcinghorns = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    gapset_values = models.CharField(max_length=100, blank=True, null=True)
    lvleads_size = models.CharField(max_length=50, choices=LEADSIZES, null=True, blank=True)
    txloading = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    txloading_yes = models.CharField(max_length=50, choices=TXLOADING, null=True, blank=True)
    load_distributionby = models.CharField(max_length=50, choices=LOADDISTRIBUTION, null=True, blank=True)
    c_tx_structure = models.CharField(max_length=50, choices=TXSTRUCTURE, null=True, blank=True)
    c_fuse_carriers = models.CharField(max_length=50, choices=CFUSECARRIERS, null=True, blank=True)
    t_fuse_bar = models.CharField(max_length=50, choices=FUSEBARTYPE, null=True, blank=True)
    c_fuse_bar = models.CharField(max_length=50, choices=FUSEBARCOND, null=True, blank=True)
    txwiring = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    c_txwiring = models.CharField(max_length=50, choices=TXWIRING, null=True, blank=True)
    inspect_notes = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    save_status = models.BooleanField(default=False)
    aprv_status = models.BooleanField(default=False)
    aprv_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='lv_substation_approved_by')
    aprv_notes = models.TextField(blank=True, null=True)
    aprv_dt = models.DateField(null=True, blank=True)
    aprv_key = models.CharField(max_length=10, choices=APRVKEY, null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='lv_substation_inspected_by')
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='substation_county')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='substation_region')
    hv_b_r = models.CharField(max_length=255, null=True, blank=True)
    hv_r_y = models.CharField(max_length=255, null=True, blank=True)
    hv_y_b = models.CharField(max_length=255, null=True, blank=True)
    lv_b_n = models.CharField(max_length=255, null=True, blank=True)
    lv_r_n = models.CharField(max_length=255, null=True, blank=True)
    lv_y_n = models.CharField(max_length=255, null=True, blank=True)
    insul_lve = models.CharField(max_length=255, null=True, blank=True)
    insul_hv_lv = models.CharField(max_length=255, null=True, blank=True)
    insul_hv_e = models.CharField(max_length=255, null=True, blank=True)
    txweight = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.substation.ssn

class Substation_defaults(models.Model):
    substation_inspection = models.ForeignKey(SubstationInspection, on_delete=models.SET_NULL, null=True,related_name='substation_inspection_default', db_index=True)
    substation = models.ForeignKey(Substation, on_delete=models.SET_NULL, null=True,related_name='substationdefects_substation', db_index=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='substation_default_inspected_by')
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='substationdefaults_county')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='substationdefaults_region')
    hvearthintact = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    neutralearthintact = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    surgearresters = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    arcinghones = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    txloading = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    txstructure = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fusecarriers = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fusebar = models.DecimalField(max_digits=6, decimal_places=2, default=0)


    def __str__(self):
        return self.substation_inspection.substation.name

class TxFailure(models.Model):
    VOLTAGE = (
        ('', '----CHOOSE THE STATUS----'),
        ('11', '11'),
        ('33', '33'),
    )
    FTYPE = (
        ('', '----CHOOSE THE TYPE----'),
        ('first', 'FIRST'),
        ('multiple', 'MULTIPLE'),
    )
    TXPOSITION = (
        ('', '----CHOOSE THE TYPE----'),
        ('line', 'LINE'),
        ('terminal', 'TERMINAL'),
    )
    TXSTATUS = (
        ('', '----CHOOSE THE STATUS----'),
        ('new', 'NEW'),
        ('refurbished', 'REFURBISHED'),
    )
    REFUBBY = (
        ('', '----CHOOSE THE STATUS----'),
        ('kplc', 'KPLC'),
        ('contractor', 'CONTRACTOR'),
    )
    WORKSHOP = (
        ('', '----CHOOSE THE WORKSHOP----'),
        ('isiolord', 'ISIOLO ROAD'),
        ('mbaraki', 'MBARAKI'),
        ('eldoret', 'ELDORET'),
    )
    CONTRACTOR = (
        ('', '----CHOOSE THE NAME----'),
        ('panafrica', 'PANAFRICA'),
        ('yocean', 'YOCEAN'),
        ('mahashakti', 'MAHASHAKTI(MKL)'),
    )
    WEATHER = (
        ('', '----CHOOSE THE STATUS----'),
        ('dry', 'DRY'),
        ('drywindy', 'DRY & WINDY'),
        ('rainy', 'RAINY'),
        ('rainywindy', 'RAINY & WINDY'),
    )
    YESNO = (
        ('', '----CHOOSE THE STATUS----'),
        ('yes', 'YES'),
        ('no', 'NO'),
    )
    TXISOLATION = (
        ('', '----CHOOSE THE STATUS----'),
        ('taplin', 'DRY'),
        ('expulsionfuses', 'EXPULSION FUSES'),
        ('noisolation', 'NO ISOLATION'),
        ('powderfuses', 'POWDER FUSES'),
        ('rmu', 'RMU'),
    )
    LVLEADS = (
        ('', '----CHOOSE THE STATUS----'),
        ('healthy', 'HEALTHY'),
        ('faulty', 'FAULTY'),
        ('nolugs', 'NO LUGS'),
        ('undersize', 'UNDER SIZE'),
        ('rmu', 'RMU'),
    )
    FUSECARRIERS = (
        ('', '----CHOOSE THE STATUS----'),
        ('good', 'GOOD'),
        ('damaged', 'DAMAGED'),
    )
    APRVKEY = (
        ('', '----CHOOSE THE STATUS----'),
        ('approved', 'APPROVED'),
        ('declined', 'DECLINED'),
    )
    HVEARTHMISSING = (
        ("", "----CHOOSE THE STATUS----"),
        ("vandalised", "VANDALISED"),
        ("missing", "MISSING"),
        ("corroded", "CORRODED"),
    )
    KVARATING = (
        ('', '----CHOOSE THE STATUS----'),
        ('5', '5'),
        ('15', '15'),
        ('25', '25'),
        ('50', '50'),
        ('100', '100'),
        ('200', '200'),
        ('315', '315'),
        ('630', '630'),
        ('1000', '1000'),
        ('3*5', '3*5'),
        ('3*15', '3*15'),
        ('3*25', '3*25'),
    )
    CAUSESOFFAILURE = (
        ("", "----CHOOSE THE STATUS----"),
        ("Insulation_failure", "Insulation failure"),
        ("Lack_poorprotection", "Lack/poor protection"),
        ("Fusegrading", "Fuse grading"),
        ("Shortcircuits", "Short circuits"),
        ("Singlephaseloading", "Single phase loading"),
        ("Imbalancedloading", "Imbalanced loading"),
        ("Generaloverload", "General overload"),
        ("faulty_operations_of_tap", "Faulty operation of tap changer switch"),
        ("Improperpoorterminations", "Improper/poor terminations"),
        (
            "Internaldefectsafterthoroughtesting",
            "Internal defects after thorough testing",
        ),
        ("Vandalism", "Vandalism"),
        ("Illegalconnections", "Illegal connections"),
        ("insufficient_oil_level", "Insufficient Oil level/leakage"),
        ("seepage_of_water_in_oil", "Seepage of water in oil"),
        ("lightning_strike", "Lightning strike"),
        ("lack_of_installation_check", "Lack of installation check"),
        ("poor_workmanship", "Poor Workmanship during installation"),
        ("improper_brazing_ofjoints", "Improper brazing of joints"),
        ("sharp_edges_winding_conductor", "Burr /sharp edges to the winding conductor"),
        ("incomplete_drying", "Incomplete drying"),
        ("clashing_conductors", "Clashing conductors"),
        ("overdistance_lv", "Over distance LV network"),
    )
    substation = models.ForeignKey(Substation, on_delete=models.SET_NULL, null=True)
    serialno = models.CharField(max_length=100, blank=True, null=True)
    voltage = models.CharField(max_length=50, choices=VOLTAGE, null=True, blank=True)
    kvarating = models.CharField(max_length=50, choices=KVARATING, null=True, blank=True)
    gnumber = models.CharField(max_length=100, blank=True, null=True)
    make = models.ForeignKey(Txmakes, on_delete=models.SET_NULL, null=True, related_name='make_failure')
    yom = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    tx_position = models.CharField(max_length=50, choices=TXPOSITION, null=True, blank=True)
    incidence_no = models.CharField(max_length=255, blank=True, null=True)
    dt_failure = models.DateField(auto_now_add=True)
    failure_type = models.CharField(max_length=50, choices=FTYPE, null=True, blank=True)
    last_failuredt = models.DateField(auto_now_add=True)
    tx_status = models.CharField(max_length=50, choices=TXSTATUS, null=True, blank=True)
    refubby = models.CharField(max_length=50, choices=REFUBBY, null=True, blank=True)
    workshop = models.CharField(max_length=50, choices=WORKSHOP, null=True, blank=True)
    contractor = models.CharField(max_length=50, choices=CONTRACTOR, null=True, blank=True)
    weathercond = models.CharField(max_length=50, choices=WEATHER, null=True, blank=True)
    hvearth_intact = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    hvearth_values_missing = models.CharField(max_length=50, choices=HVEARTHMISSING, null=True, blank=True)
    hvearth_values = models.CharField(max_length=100, blank=True, null=True)
    neutralearth_intact = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    neutralvearth_values = models.CharField(max_length=100, blank=True, null=True)
    surgearrestors = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)
    surgearrestors_values = models.CharField(max_length=100, blank=True, null=True)
    surge_arrestors_missing = models.CharField(max_length=50, choices=HVEARTHMISSING, null=True, blank=True)
    tx_isolation = models.CharField(max_length=50, choices=TXISOLATION, null=True, blank=True)
    expulsionondirectlink = models.CharField(max_length=100, blank=True, null=True)
    powderondirectlink = models.CharField(max_length=100, blank=True, null=True)
    c_lvleads = models.CharField(max_length=50, choices=LVLEADS, null=True, blank=True)
    c_fusecarriers = models.CharField(max_length=50, choices=FUSECARRIERS, null=True, blank=True)
    d_fusecarriers = models.CharField(max_length=100, blank=True, null=True)
    shortet_lv_c_1 = models.CharField(max_length=100, blank=True, null=True)
    shortet_lv_c_2 = models.CharField(max_length=100, blank=True, null=True)
    shortet_lv_c_3 = models.CharField(max_length=100, blank=True, null=True)
    fuse_size_c_1 = models.CharField(max_length=100, blank=True, null=True)
    fuse_size_c_2 = models.CharField(max_length=100, blank=True, null=True)
    fuse_size_c_3 = models.CharField(max_length=100, blank=True, null=True)
    hvlv_m_ohms = models.CharField(max_length=100, blank=True, null=True)
    hvearth_m_ohms = models.CharField(max_length=100, blank=True, null=True)
    lvearth_m_ohms = models.CharField(max_length=100, blank=True, null=True)
    R_Y = models.CharField(max_length=100, blank=True, null=True)
    Y_B = models.CharField(max_length=100, blank=True, null=True)
    B_R = models.CharField(max_length=100, blank=True, null=True)
    r_n = models.CharField(max_length=100, blank=True, null=True)
    y_n = models.CharField(max_length=100, blank=True, null=True)
    b_n = models.CharField(max_length=100, blank=True, null=True)
    causeoffailure = models.CharField(max_length=100, choices=CAUSESOFFAILURE, null=True, blank=True)
    recommendations = models.TextField(blank=True, null=True)
    save_status = models.BooleanField(default=False)
    aprv_status = models.BooleanField(default=False)
    aprv_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='failure_approved_by')
    aprv_notes = models.TextField(blank=True, null=True)
    aprv_key = models.CharField(max_length=10, choices=APRVKEY, null=True, blank=True)
    aprv_dt = models.DateField(null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='tx_failure_inspected_by')
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='tx_county')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='tx_region')
    txweight = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.substation.ssn

class Commission_substation(models.Model):
    TYPEOFCHANGE = (
        ('', '----CHOOSE THE TYPE----'),
        ('new', 'NEW'),
        ('replacement', 'REPLACEMENT'),
        ('shifting', 'SHIFTING'),
        ('modification', 'MODIFICATION'),
    )
    TYPEOFLOAD = (
        ('', '----CHOOSE THE TYPE----'),
        ('domestic', 'DOMESTIC'),
        ('commercial', 'COMMERCIAL'),
        ('mixed', 'MIXED'),
        ('dedicated', 'DEDICATED'),
    )
    VOLTAGE = (
        ('', '----CHOOSE THE TYPE----'),
        ('33', '33'),
        ('11', '11'),
    )
    TXSTATUS = (
        ('', '----CHOOSE THE TYPE----'),
        ('new', 'NEW'),
        ('refurbished', 'REFURBISHED'),
    )
    REFURBISHEDBY = (
        ('', '----CHOOSE THE TYPE----'),
        ('kplc', 'KPLC'),
        ('contractor', 'CONTRACTOR'),
    )
    KPLCWORKSHOP = (
        ('', '----CHOOSE THE TYPE----'),
        ('isiolord', 'ISIOLO RD'),
        ('mbaraki', 'MBARAKI'),
        ('eldoret', 'ELDORET'),
    )
    HTISOLATION = (
        ('', '----CHOOSE THE TYPE----'),
        ('fuse', 'FUSE'),
        ('taplin', 'TAPLIN'),
        ('solid(none)', 'SOLID(NONE)'),
        ('abs', 'ABS'),
        ('rmu', 'RMU'),
        ('livelinetap', 'LIVE LINE TAP'),
        ('od', 'OD'),
        ('powder', 'POWDER'),
    )
    NOOFCIRCUITS = (
        ('', '----CHOOSE THE TYPE----'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
    )
    LVPROTECTION = (
        ('', '----CHOOSE THE TYPE----'),
        ('fuses', 'FUSES'),
        ('circuitbreaker(mcb)', 'CIRCUIT BREAKER (MCB)'),
    )
    PHASEROTATION = (
        ('', '----CHOOSE THE TYPE----'),
        ('r-y-b', 'R-Y-B'),
        ('b-y-r', 'B-Y-R'),
    )
    TXPROTECTION = (
        ('', '----CHOOSE THE TYPE----'),
        ('surgediverters', 'SURGE DIVERTERS'),
        ('arcingorns', 'ARCING HORNS'),
        ('both', 'BOTH'),
    )
    APRVKEY = (
        ('', '----CHOOSE THE STATUS----'),
        ('approved', 'APPROVED'),
        ('declined', 'DECLINED'),
    )
    KVARATING = (
        ('', '----CHOOSE THE STATUS----'),
        ('5', '5'),
        ('15', '15'),
        ('25', '25'),
        ('50', '50'),
        ('100', '100'),
        ('200', '200'),
        ('315', '315'),
        ('630', '630'),
        ('1000', '1000'),
        ('3*5', '3*5'),
        ('3*15', '3*15'),
        ('3*25', '3*25'),
    )
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    substation = models.ForeignKey(Substation, on_delete=models.SET_NULL, null=True,related_name='substation_commission', db_index=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    dt_commission = models.CharField(max_length=255, null=True, blank=True)
    control_center = models.CharField(max_length=255, null=True, blank=True)
    ptw_no = models.CharField(max_length=255, null=True, blank=True)
    typeofchange = models.CharField(max_length=20, choices=TYPEOFCHANGE, null=True, blank=True)
    typeofload = models.CharField(max_length=10, choices=TYPEOFLOAD, null=True, blank=True)
    dcs_reference = models.CharField(max_length=255, null=True, blank=True)
    rerec_reference = models.CharField(max_length=255, null=True, blank=True)
    internalorder = models.CharField(max_length=255, null=True, blank=True)
    lastmile_reference = models.CharField(max_length=255, null=True, blank=True)
    make = models.ForeignKey(Txmakes, on_delete=models.SET_NULL, null=True, related_name='make_commission')
    gnumber = models.CharField(max_length=255, null=True, blank=True)
    yom = models.CharField(max_length=10, null=True, blank=True)
    kvarating = models.CharField(max_length=50, choices=KVARATING, null=True, blank=True)
    voltage =models.CharField(max_length=10, choices=VOLTAGE, null=True, blank=True)
    txweight = models.CharField(max_length=255, null=True, blank=True)
    txstatus = models.CharField(max_length=100, choices=TXSTATUS, null=True, blank=True)
    refurbishedby = models.CharField(max_length=100, choices=REFURBISHEDBY, null=True, blank=True)
    kplcworkshop = models.CharField(max_length=100, choices=KPLCWORKSHOP, null=True, blank=True)
    htisolation = models.CharField(max_length=100, choices=HTISOLATION, null=True, blank=True)
    noofcircuits = models.CharField(max_length=100, choices=NOOFCIRCUITS, null=True, blank=True)
    lvprotection = models.CharField(max_length=100, choices=LVPROTECTION, null=True, blank=True)
    txprotection = models.CharField(max_length=100, choices=TXPROTECTION, null=True, blank=True)
    surged_red  = models.CharField(max_length=255, null=True, blank=True)
    surged_yellow = models.CharField(max_length=255, null=True, blank=True)
    surged_blue = models.CharField(max_length=255, null=True, blank=True)
    arcinghorns_single = models.CharField(max_length=255, null=True, blank=True)
    arcinghorns_dublex = models.CharField(max_length=255, null=True, blank=True)
    nooftappositions = models.CharField(max_length=255, null=True, blank=True)
    voltagetappingsetattap = models.CharField(max_length=255, null=True, blank=True)
    earthval_at_structure_ht = models.CharField(max_length=255, null=True, blank=True)
    earthval_at_structure_sd = models.CharField(max_length=255, null=True, blank=True)
    lv_onespanaway = models.CharField(max_length=255, null=True, blank=True)
    hv_b_r = models.CharField(max_length=255, null=True, blank=True)
    hv_r_y = models.CharField(max_length=255, null=True, blank=True)
    hv_y_b = models.CharField(max_length=255, null=True, blank=True)
    lv_b_n =models.CharField(max_length=255, null=True, blank=True)
    lv_r_n = models.CharField(max_length=255, null=True, blank=True)
    lv_y_n =models.CharField(max_length=255, null=True, blank=True)
    insul_lve= models.CharField(max_length=255, null=True, blank=True)
    insul_hv_lv = models.CharField(max_length=255, null=True, blank=True)
    insul_hv_e = models.CharField(max_length=255, null=True, blank=True)
    volt_b_r = models.CharField(max_length=255, null=True, blank=True)
    volt_r_y = models.CharField(max_length=255, null=True, blank=True)
    volt_y_b = models.CharField(max_length=255, null=True, blank=True)
    volt_b_n = models.CharField(max_length=255, null=True, blank=True)
    volt_r_n = models.CharField(max_length=255, null=True, blank=True)
    volt_y_n = models.CharField(max_length=255, null=True, blank=True)
    htfuse_b = models.CharField(max_length=255, null=True, blank=True)
    htfuse_r = models.CharField(max_length=255, null=True, blank=True)
    htfuse_y = models.CharField(max_length=255, null=True, blank=True)
    phasetotation = models.CharField(max_length=100, choices=PHASEROTATION, null=True, blank=True)
    comments =models.TextField(null=True, blank=True)
    save_status = models.BooleanField(default=False)
    aprv_status = models.BooleanField(default=False)
    aprv_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='commission_approved_by')
    aprv_notes = models.TextField(blank=True, null=True)
    aprv_key = models.CharField(max_length=10, choices=APRVKEY, null=True, blank=True)
    aprv_dt = models.DateField(null=True, blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True,related_name='commission_inspected_by')
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='commision_county')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='commision_region')

    def __str__(self):
        return self.substation.ssn

class SubstationMaintenance(models.Model):
    EARTHINTACT = (
        ('', '----CHOOSE THE STATUS----'),
        ('repair', 'REINSTATED/REPAIRED'),
        ('new', 'NEW'),
    )
    TXSTRUCTURE = (
        ('', '----CHOOSE THE STATUS----'),
        ('straighten', 'STRAIGHTENED'),
        ('replaced', 'REPLACED'),
    )
    YESNO = (
        ('', '----CHOOSE THE STATUS----'),
        ('yes', 'YES'),
        ('no', 'NO'),
    )
    TXLOADING = (
        ('', '----CHOOSE THE STATUS----'),
        ('uprate', 'UPRATE'),
        ('relieve', 'RELIEVE'),
        ('phasebalancing', 'PHASE BALANCING'),
        ('additionalcircuit', 'ADDITIONAL CIRCUIT'),
    )
    LOADDISTRIBUTION = (
        ('', '----CHOOSE THE STATUS----'),
        ('phasebalancing', 'PHASE BALANCING'),
        ('additionalcircuit', 'ADDITIONAL CIRCUIT'),
    )
    APRVKEY = (
        ('', '----CHOOSE THE STATUS----'),
        ('approved', 'APPROVED'),
        ('declined', 'DECLINED'),
    )
    REPAIRREPLACE = (
        ('', '----CHOOSE THE STATUS----'),
        ('repair', 'REPAIRED'),
        ('replaced', 'REPLACED'),
    )
    TXPOSITION = (
        ('', '----CHOOSE----'),
        ('terminal', 'TERMINAL'),
        ('line', 'LINE'),
    )

    inspection = models.ForeignKey(SubstationInspection, on_delete=models.SET_NULL, null=True)
    fusesize = models.CharField(max_length=100, blank=True, null=True)
    sizeoflvconductor = models.CharField(max_length=100, blank=True, null=True)
    noofcircuits_added =  models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    hvearth_intact = models.CharField(max_length=50, choices=EARTHINTACT, null=True, blank=True)
    neutralearth_intact =models.CharField(max_length=50, choices=EARTHINTACT, null=True, blank=True)
    surgediverters_replaced = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    lvleads_size = models.CharField(max_length=50, choices=EARTHINTACT, null=True, blank=True)
    txloading = models.CharField(max_length=50, choices=TXLOADING, null=True, blank=True)
    c_tx_structure = models.CharField(max_length=50, choices=TXSTRUCTURE, null=True, blank=True)
    c_fuse_carriers_replaced = models.IntegerField(help_text='Enter a Number.If none input zero',default=0)
    c_fuse_bar = models.CharField(max_length=50, choices=REPAIRREPLACE, null=True, blank=True)
    txwiring = models.CharField(max_length=50, choices=REPAIRREPLACE, null=True, blank=True)
    txposition = models.CharField(max_length=10, choices=TXPOSITION, null=True, blank=True)
    maintenance_notes = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    save_status = models.BooleanField(default=False)
    aprv_status = models.BooleanField(default=False)
    aprv_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='substation_maintenance_approved_by')
    aprv_notes = models.TextField(blank=True, null=True)
    aprv_dt = models.DateField(null=True,blank=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='substation_makintenance_inspected_by')
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='county_sub_maintenance')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True,related_name='region_sub_maintenance')
    aprv_key = models.CharField(max_length=10, choices=APRVKEY, null=True, blank=True)
    other_defects = models.CharField(max_length=50, choices=YESNO, null=True, blank=True)

    def __str__(self):
        return self.inspection.substation.ssn

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
        ('14mwooden', '14m WOODEN'),
        ('10mconcrete', '10m CONCRETE'),
        ('11mconcrete', '11m CONCRETE'),
        ('12mconcrete', '12m CONCRETE'),
    )
    APRVKEY = (
        ('', '----CHOOSE THE STATUS----'),
        ('approved', 'APPROVED'),
        ('declined', 'DECLINED'),
    )
    poledefect = models.ForeignKey(Poledefects, on_delete=models.SET_NULL, null=True, related_name='poledefects_makintenance')
    pole_type = models.CharField(max_length=50, choices=TYPEPOLE, null=True, blank=True)
    defect_type = models.CharField(max_length=100, choices=DEFECTTYPE, null=True, blank=True)
    y = models.CharField(max_length=100, blank=True, null=True)
    x = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, related_name='poledefects_maintained_county')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True,related_name='poledefects_maintained_region')
    status = models.BooleanField(default=False)
    maintain_notes = models.TextField(blank=True, null=True)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='lv_mainteained_poles_d_by')
    save_status = models.BooleanField(default=False)
    aprv_status = models.BooleanField(default=False)
    aprv_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='poledefects_m_approved_by')
    aprv_notes = models.TextField(blank=True, null=True)
    aprv_key = models.CharField(max_length=10, choices=APRVKEY, null=True, blank=True)
    aprv_dt = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.poledefect.substation.ssn

class LoadChecks(models.Model):
    VOLTAGE = (
        ('', '----CHOOSE THE TYPE----'),
        ('33', '33'),
        ('11', '11'),
    )
    KVARATING = (
        ('', '----CHOOSE THE STATUS----'),
        ('5', '5'),
        ('15', '15'),
        ('25', '25'),
        ('50', '50'),
        ('100', '100'),
        ('200', '200'),
        ('315', '315'),
        ('630', '630'),
        ('1000', '1000'),
        ('3*5', '3*5'),
        ('3*15', '3*15'),
        ('3*25', '3*25'),
    )
    substation = models.ForeignKey(Substation, on_delete=models.SET_NULL, null=True,related_name='substation_loadchecks', db_index=True)
    primary_voltage = models.CharField(max_length=10, choices=VOLTAGE, null=True, blank=True)
    tx_rating = models.CharField(max_length=20, choices=KVARATING, null=True, blank=True)
    number_of_circuits = models.IntegerField(null=True, blank=True)
    voltage_ll_ry = models.CharField(max_length=10, null=True, blank=True)
    voltage_ll_yb = models.CharField(max_length=10, null=True, blank=True)
    voltage_ll_br = models.CharField(max_length=10, null=True, blank=True)
    voltage_ln_rn = models.CharField(max_length=10, null=True, blank=True)
    voltage_ln_yn = models.CharField(max_length=10, null=True, blank=True)
    voltage_ln_bn = models.CharField(max_length=10, null=True, blank=True)
    phase_loads_r = models.CharField(max_length=10, null=True, blank=True)
    phase_loads_y = models.CharField(max_length=10, null=True, blank=True)
    phase_loads_b = models.CharField(max_length=10, null=True, blank=True)
    phase_loads_r_2 = models.CharField(max_length=10, null=True, blank=True)
    phase_loads_y_2 = models.CharField(max_length=10, null=True, blank=True)
    phase_loads_b_2 = models.CharField(max_length=10, null=True, blank=True)
    phase_loads_r_3 = models.CharField(max_length=10, null=True, blank=True)
    phase_loads_y_3 = models.CharField(max_length=10, null=True, blank=True)
    phase_loads_b_3 = models.CharField(max_length=10, null=True, blank=True)
    phase_loads_r_4 = models.CharField(max_length=10, null=True, blank=True)
    phase_loads_y_4 = models.CharField(max_length=10, null=True, blank=True)
    phase_loads_b_4 = models.CharField(max_length=10, null=True, blank=True)
    phase_loads_r_5 = models.CharField(max_length=10, null=True, blank=True)
    phase_loads_y_5 = models.CharField(max_length=10, null=True, blank=True)
    phase_loads_b_5 = models.CharField(max_length=10, null=True, blank=True)
    save_status = models.BooleanField(default=False)
    aprv_status = models.BooleanField(default=False)
    dtadd = models.DateTimeField(auto_now_add=True)
    dtupdate = models.DateTimeField(auto_now=True)
    inspectedby = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True,related_name='inspectedby_loadchecks')
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True,related_name='county_loadchecks')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True,related_name='region_loadchecks')

    def __str__(self):
        return self.substation.substation.ssn

















