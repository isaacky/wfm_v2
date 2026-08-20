from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, stid, name, mobile, password=None):
        if not email:
            raise ValueError('Users Must have An Email Address.')
        if not username:
            raise ValueError('Users Must Have A Username.')
        if not stid:
            raise ValueError('Users Must Have A Staff ID.')
        if not name:
            raise ValueError('Users Must have a name.')
        if not mobile:
            raise ValueError('Users Must have a Mobile.')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            stid=stid,
            name=name,
            mobile=mobile,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, stid, name, mobile, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            stid=stid,
            name=name,
            mobile=mobile,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name='email', max_length=100, unique=True)
    username = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255, null=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='Last Login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    stid = models.IntegerField(unique=True,db_index=True)
    mobile = models.CharField(max_length=100, blank=True, null=True)

    USERNAME_FIELD = 'stid'
    REQUIRED_FIELDS = ['username', 'email', 'name', 'mobile']

    objects = MyAccountManager()
    
    class Meta:
        indexes = [models.Index(fields=["stid"])]
        ordering = ['-stid',]

    def __str__(self):
        return str(self.stid)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True

class UserProfile(models.Model):
    PROFILETYPE = (("cse", "CSE"), ("input", "INPUT"), ("other", "OTHER"))
    CAMPAIGNCHOICES = (
        # ('zerovends','ZERO VENDS CAMPAIGN'),
        ('zerobills','ZERO BILLS CAMPAIGN'),
        ('revenue','REVENUE COLLECTION'),
        ("dc", "DOMESTIC CUSTOMERS"),
        ("threephase", "HIGH END ACCOUNTS"),
        ("telcos", "TELCOS INSPECTION"),
        ("publiclighting", "PUBLIC LIGHTING"),
        ("elsewedy_replacement", "ELSEWEDY REPLACEMENTS"),
        ("lp", "LARGE POWER"),
        ("network_technician", "NETWORK TECHNICIAN"),
        ("network_supervisors", "NETWORK SUPERVISORS"),
        ("other", "OTHER"),
        ("transdist", "TRANSMISSION & PRIMARY SUBSTATIONS"),
        ("contractor_allandick", "CONTRACTOR"),
        ("hradmin", "HRADMIN"),
    )
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    county = models.ForeignKey("main.County", on_delete=models.SET_NULL, null=True)
    region = models.ForeignKey("main.Region", on_delete=models.SET_NULL, null=True)
    profiletype = models.CharField(max_length=6, choices=PROFILETYPE, default="other")
    campaign = models.CharField(max_length=20, choices=CAMPAIGNCHOICES, default="other")

    class Meta:
        indexes = [models.Index(fields=["user"])]
        ordering = [
            "-user",
        ]

    def __str__(self):
        # return str(self.county)
        return str(self.user.stid)
        # return f'{str(self.stid)} {self.name}'

    def full_address(self):
        return f"{self.county}"

    @property
    def staffname(self):
        return self.user.name