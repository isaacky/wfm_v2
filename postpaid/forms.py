from django import forms
from django.forms import ModelForm, widgets, ValidationError
from main.models import County

from user.models import Account, UserProfile
from .models import *
import time

class AmcorderAnalysisForm(forms.ModelForm):

    class Meta:
        model = AmcorderAnalysis

        exclude=[
            "dtadd","dtupdate","meter","user_id","status"
        ]
        widgets = {
            "anomalies": forms.SelectMultiple(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super(AmcorderAnalysisForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"



class AmcorderRetrievalForm(forms.ModelForm):


    class Meta:
        model = AmcorderRetrieval

        exclude=[
            "dtadd","dtupdate","meter","user_id","status"
        ]

    def __init__(self, *args, **kwargs):
        super(AmcorderRetrievalForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
            self.fields["date_retrieved"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "yyyy-mm-dd",
                    "class": "form-control",
                }
            )



class AmcorderForm(forms.ModelForm):
    # profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    # meterno = forms.CharField(disabled=True)
    # accountno = forms.CharField(disabled=True)
    latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Amcorder
        # fields = (
        #     "id",
        #     "meterno",
        #     "accountno",
        #     "readings",
        #     "meterimg",
        #     "comment",
        #     "latitude",
        #     "longitude",
        #     'status4',
        # )
        exclude=[
            "dtadd","dtupdate","county","region","meter","user_id","status"
        ]

    def __init__(self, *args, **kwargs):
        super(AmcorderForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
            self.fields["date_installed"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "yyyy-mm-dd",
                    "class": "form-control",
                }
            )
            self.fields["time_installed"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "time",
                    "placeholder": "HH:MM",
                    "class": "form-control",
                }
            )
            self.fields["start_time"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "time",
                    "placeholder": "HH:MM",
                    "class": "form-control",
                }
            )


class Largepower_accounts_2024Form(forms.ModelForm):

    class Meta:
        model = Largepower_accounts_2024
        exclude = [
            "dtadd",
            "dtupdate",
            "asigned",
            "over_per",
            "currents_mismatch",
            "zera_failed",
            "ctvt_mismatch",
            "current",
            "final_sub",
            "otherinfo",
            "meter_rading",
            "zera_test",
            "ctvt_data",
            "sealing_data",
            "customer_data",
            "inspection_status",
            "status",
        ]
    def __init__(self, *args, **kwargs):
        super(Largepower_accounts_2024Form, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
class LPOtherinfoForm(forms.ModelForm):

    class Meta:
        model = Lp_inspect_info
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "lp"
        ]
    def __init__(self, *args, **kwargs):
        super(LPOtherinfoForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
            self.fields["dt_installation"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "yyyy-mm-dd",
                    "class": "form-control",
                }
            )
class ElsewedyReplacementForm(forms.ModelForm):


    class Meta:
        model = ElsewedyReplacement
        exclude = [
            "dtadd",
            "dtupdate",
            "inspector",
            "elsewedy",
            "county",
            "region",
            "validated",
            "billed",
            "consumption",
            "accountno"
        ]
    def __init__(self, *args, **kwargs):
        super(ElsewedyReplacementForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
class LPOtherinfoForm(forms.ModelForm):

    class Meta:
        model = Lp_inspect_info
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "lp"
        ]
    def __init__(self, *args, **kwargs):
        super(LPOtherinfoForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
            self.fields["dt_installation"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "yyyy-mm-dd",
                    "class": "form-control",
                }
            )

class LPMeterReadingsForm(forms.ModelForm):

    class Meta:
        model = LP_meter_readings
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "lp"
        ]
    def __init__(self, *args, **kwargs):
        super(LPMeterReadingsForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"

        self.fields["meter_date_actual"].widget = forms.widgets.DateInput(
            attrs={
                "type": "date",
                "placeholder": "yyyy-mm-dd",
                "class": "form-control",
            }
        )
        self.fields["meter_date_meter"].widget = forms.widgets.DateInput(
            attrs={
                "type": "date",
                "placeholder": "yyyy-mm-dd",
                "class": "form-control",
            }
        )
        self.fields["meter_time_meter"].widget = forms.widgets.DateInput(
            attrs={
                "type": "time",
                "placeholder": "HH:MM",
                "class": "form-control",
            }
        )
        self.fields["meter_time_actual"].widget = forms.widgets.DateInput(
            attrs={
                "type": "time",
                "placeholder": "HH:MM",
                "class": "form-control",
            }
        )
class LPCurrentsForm(forms.ModelForm):

    class Meta:
        model = Lp_inspect_current
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "lp"
        ]
    def __init__(self, *args, **kwargs):
        super(LPCurrentsForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
            self.fields["rphase_amcoder"].widget.attrs["required"] = "required"
            self.fields["rphase_meter"].widget.attrs["required"] = "required"
            self.fields["yphase_amcoder"].widget.attrs["required"] = "required"
            self.fields["yphase_meter"].widget.attrs["required"] = "required"
            self.fields["bphase_amcoder"].widget.attrs["required"] = "required"
            self.fields["bphase_meter"].widget.attrs["required"] = "required"
            self.fields["load_balancing"].widget.attrs["required"] = "required"
            self.fields["currents_range"].widget.attrs["required"] = "required"
class LPZeraTestForm(forms.ModelForm):

    class Meta:
        model = Lp_inspect_zeratest
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "lp"
        ]
    def __init__(self, *args, **kwargs):
        super(LPZeraTestForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
            # self.fields["meter_passed"].widget.attrs["required"] = 'False'
            self.fields["meter_passed"].initial = ''
class LPCtVtInspectionForm(forms.ModelForm):

    class Meta:
        model = Lp_inspect_ctvt
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "lp"
        ]
    def __init__(self, *args, **kwargs):
        super(LPCtVtInspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
class LPSealingInspectionForm(forms.ModelForm):

    class Meta:
        model = LP_inspection_sealing
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "lp"
        ]
    def __init__(self, *args, **kwargs):
        super(LPSealingInspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
            self.fields["term_sl_init"].widget.attrs["required"] = "required"
            self.fields["term_sl_fin"].widget.attrs["required"] = "required"
            self.fields["smart_meter_sl_init"].widget.attrs["required"] = "required"
            self.fields["smart_meter_sl_fin"].widget.attrs["required"] = "required"
            # self.fields["amr_sl_init"].widget.attrs["required"] = "required"
            # self.fields["amr_sl_fin"].widget.attrs["required"] = "required"

    # def clean(self):
    #     form_data = self.cleaned_data['term_sl_init']
    #     if form_data["term_sl_init"] == form_data["term_sl_fin"]:
    #         raise forms.ValidationError("The Initial & Final cannot be the same")
    #     return self.form_data



class LPCustomerDataInspectionForm(forms.ModelForm):

    class Meta:
        model = Lp_inspect_customerData
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "lp"
        ]
    def __init__(self, *args, **kwargs):
        super(LPCustomerDataInspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm required"
            self.fields["meterno"].widget.attrs["required"] = "required"
            self.fields["longitude"].widget.attrs["required"] = "required"
            self.fields["latitude"].widget.attrs["required"] = "required"

class LPNewInspectionForm(forms.ModelForm):

    class Meta:
        model = Lp_new_inspection
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "lp",
            "county",
            "region"
        ]
    def __init__(self, *args, **kwargs):
        super(LPNewInspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
            self.fields["declaration"].widget.attrs["class"] = "form-check-input"

    def clean(self):
        form_data = self.cleaned_data
        if form_data["declaration"] == False:
            raise ValidationError(
                "You Must Check the confirmation Checkbox for this information to be saved"
            )
        return form_data



STATUSCHOISES= (
        ('','----CHOOSE A STATUS----'),
        ('faulty','FAULTY'),
        ('bypasses','BY-PASSED'),
        ('tampered','TAMPERED'),
        ('idle','IDLE'),
        ('disconnected','DISCONNECTED'),
        ('notonsite','NOT-ON-SITE'),
        ('disconnected','DISCONNECTED'),
        ('notonsite','NOT-ON-SITE'),
        ('meterokay','METER OKAY & READ'),
        ('vacantpremises','VACANT PREMISES'),
           
        )
STATUSCHOISES2= (
        ('','----CHOOSE A STATUS----'),
        ('billing','BILLED'),
        ('irregularity','REGULARISED'),
        ('genuine','GENUINE ZEROBILL'),
        ('faulty','FAULTY'),
           
        )
        
class MeterForm(forms.ModelForm):
    # profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    meterno = forms.CharField(disabled=True)
    accountno = forms.CharField(disabled=True)
    meterimg = forms.ImageField(required=True)
    latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Zerobillresolved
        fields = (
            "id",
            "meterno",
            "accountno",
            "readings",
            "meterimg",
            "comment",
            "latitude",
            "longitude",
            'status4',
        )

    def __init__(self, *args, **kwargs):
        super(MeterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


METERINGSTATUS= (
        ('','----CHOOSE A METERING STATUS----'),
        ('okay','OKAY'),
        ('faulty','FAULTY'),
        ('tampered','TAMPERED'),
        ('bypassed','BYPASSED'), 
        ('nometer', 'NO METER'),          
        )
INSTALLATIONSTATUS= (
        ('','----CHOOSE AN INSTALLATION STATUS----'),
        ('okay','OKAY'),
        ('notokay','NOT OKAY'),        
        )
FAULTYSTATUS= (
        ('','----CHOOSE A FAULTY STATUS----'),
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
        ('','----CHOOSE A TAMPER STATUS----'),
        ('brokenseaals','BROKEN SEALS'),
        ('disabledvoltage','DISABLED VOLTAGE'), 
        ('disabledcurrent','DISABLED CURRENT'),
        ('brokenglass','BROKEN GLASS'),
        ('droppedlink','DROPPED LINK'),
        ('damagedmeter','DAMAGED METER'), 
        ('foreignobjects','FOREIGN OBJECTS INTRODUCED'),     
        )
BYPASSSTATUS= (
        ('','----CHOOSE A BYPASS STATUS----'),
        ('puncturedcable','PUNCTURED CABLE'),
        ('drilledcutout','DRILLED CUTOUT'),        
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
METERTYPE= (
        ('','----CHOOSE A METER TYPE----'),
        ('prepaid','PREPAID'),
        ('postpaid','POSTPAID'),        
        )
NOTOKAYSTATUS= (
        ('','----CHOOSE A NOTOKAY STATUS----'),
        ('loosejoints','LOOSE JOINTS'),
        ('noearth','NO EARTH'), 
        ('demolishedpremises','DEMOLISHED PREMISES'),
        ('vacant','VACANT'),
        ('nometertails','NO METER TAILS'),
        ('loosemeterbox','LOOSE METERBOX'),     
        )
PHASESTATUS = (
        ('', '----CHOOSE A STATUS----'),
        ('single', 'SINGLE PHASE'),
        ('threephase', 'THREE PHASE'),
    )

class ConsentTelcosForm(forms.ModelForm):

    class Meta:
        model = Telcos_replacement
        fields = ['concurrence','concurrence_notes']

    def __init__(self, *args, **kwargs):
        super(ConsentTelcosForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
           # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'
class Telcos_replacementForm(forms.ModelForm):
    # profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    phase = forms.ChoiceField(choices=PHASESTATUS, required=False)
    # telcosimg = forms.ImageField(required=True)
    x = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))
    y = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))

    meteringstatus = forms.ChoiceField(choices=METERINGSTATUS, required=True)
    faultystatus = forms.ChoiceField(choices=FAULTYSTATUS, required=False)
    tamperedstatus = forms.ChoiceField(choices=TAMPEREDSTATUS, required=False)
    bypassstatus = forms.ChoiceField(choices=BYPASSSTATUS, required=False)
    comment = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 4, "cols": 40})
    )

    # x = forms.CharField(disabled=True)

    class Meta:
        model = Telcos_replacement
        fields = (
            "id",
            "county",
            "oldmeter",
            "newmeter",
            "siteid",
            "sitename",
            "phase",
            "meteringstatus",
            "faultystatus",
            "tamperedstatus",
            "bypassstatus",
            "removal_reading",
            "install_reading",
            "install_img",
            "removal_img",
            "comment",
            "x",
            "y",
            'txnumber',
            'feeder_name',
            'dedicated_lv',
            'seal_terminalcover',
            'seal_gprs',
            'gprs_ariel',
        )

    def __init__(self, *args, **kwargs):
        super(Telcos_replacementForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
            # self.fields['faultystatus'].initial = None
            # ,initial={'faultystatus': None}

    # def clean(self):
    # if self.cleaned_data['meteringstatus'] != 'okay' and self.cleaned_data['meterimg'] is None:
    #         raise ValidationError('Image Required')
    # if self.cleaned_data['x'] is None and self.cleaned_data['y'] is None:
    #         raise ValidationError('Click on The Location Button')
    
class KaguaForm(forms.ModelForm):
    #profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    meterno = forms.CharField(disabled=True)
    accountno = forms.CharField(disabled=True)
    meterimg = forms.ImageField(required=False)
    reading = forms.CharField(label='search', required=False,
                    widget=forms.TextInput(attrs={'placeholder': 'ENTER METER READING'}))
    meteringstatus = forms.ChoiceField(choices = METERINGSTATUS, required=True)
    installationstatus = forms.ChoiceField(choices = INSTALLATIONSTATUS, required=True)
    faultystatus = forms.ChoiceField(choices = FAULTYSTATUS,required=False)
    tamperedstatus = forms.ChoiceField(choices = TAMPEREDSTATUS,required=False)
    bypassstatus = forms.ChoiceField(choices = BYPASSSTATUS,required=False)
    notokaystatus = forms.ChoiceField(choices = NOTOKAYSTATUS,required=False)
    metertype = forms.ChoiceField(choices = METERTYPE,required=True)
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))

    def clean(self):
        metertype = self.cleaned_data.get('postpaid')
        reading = self.cleaned_data.get('reading')

        if metertype and reading =="":
                raise forms.ValidationError('The reading field cannot be blank')
               
        else:
                self.cleaned_data.get('reading')
            
        return self.cleaned_data

    class Meta:
        model = Inspect_connection
        fields = ('id','meterno','accountno','metertype','meteringstatus','installationstatus','faultystatus','tamperedstatus','bypassstatus','notokaystatus','reading','meterimg','comment')

    def __init__(self, *args, **kwargs):
        super(KaguaForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            #self.fields['faultystatus'].initial = None
            #,initial={'faultystatus': None}
   

    

class ResolveForm(forms.ModelForm):
    
    status2 = forms.ChoiceField(choices = STATUSCHOISES2, required=True,label="Change Status")

    def __init__(self, *args, **kwargs):
        super(ResolveForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Zerobillresolved
        fields = ('status2',)

class Not_in_feederForm(forms.ModelForm):
    meterno = forms.CharField()
    meterimg = forms.ImageField(required=False)
    reading = forms.CharField(label='search', required=False,
                    widget=forms.TextInput(attrs={'placeholder': 'ENTER METER READING'}))
    meteringstatus = forms.ChoiceField(choices = METERINGSTATUS, required=True)
    installationstatus = forms.ChoiceField(choices = INSTALLATIONSTATUS, required=True)
    faultystatus = forms.ChoiceField(choices = FAULTYSTATUS,required=False)
    tamperedstatus = forms.ChoiceField(choices = TAMPEREDSTATUS,required=False)
    bypassstatus = forms.ChoiceField(choices = BYPASSSTATUS,required=False)
    notokaystatus = forms.ChoiceField(choices = NOTOKAYSTATUS,required=False)
    metertype = forms.ChoiceField(choices = METERTYPE,required=True)
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))

  
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(Not_in_feederForm, self).__init__(*args, **kwargs)
        self.fields["feeder"].queryset = Feeder.objects.filter(county=self.request.user.userprofile.county)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Not_in_feeder
        fields = ('id','meterno','feeder','txnumber','Neighbour_Meter','metertype','meteringstatus','installationstatus','faultystatus','tamperedstatus','bypassstatus','notokaystatus','reading','meterimg','comment')

class ThreepahseForm(forms.ModelForm):
    #profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    meterno = forms.CharField(disabled=True)
    accountno = forms.CharField(disabled=True)
    meterimg = forms.ImageField(required=False)
    reading = forms.CharField(label='search', required=False,
                    widget=forms.TextInput(attrs={'placeholder': 'ENTER METER READING'}))
    meteringstatus = forms.ChoiceField(choices = METERINGSTATUS, required=True)
    installationstatus = forms.ChoiceField(choices = INSTALLATIONSTATUS, required=True)
    faultystatus = forms.ChoiceField(choices = FAULTYSTATUS,required=False)
    tamperedstatus = forms.ChoiceField(choices = TAMPEREDSTATUS,required=False)
    bypassstatus = forms.ChoiceField(choices = BYPASSSTATUS,required=False)
    notokaystatus = forms.ChoiceField(choices = NOTOKAYSTATUS,required=False)
    metertype = forms.ChoiceField(choices = METERTYPE,required=True)
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))



    class Meta:
        model = Threephase_inspection
        fields = ('id','meterno','accountno','metertype','meteringstatus','installationstatus','faultystatus','tamperedstatus','bypassstatus','notokaystatus','reading','meterimg','comment','sealno')

    def __init__(self, *args, **kwargs):
        super(ThreepahseForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            #self.fields['faultystatus'].initial = None
            #,initial={'faultystatus': None}

    def clean(self):
        if self.cleaned_data['meteringstatus'] != 'okay' and self.cleaned_data['meterimg'] is None:
                raise ValidationError('Image Required')


class TelcosForm(forms.ModelForm):
    #profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    #telcosimg = forms.ImageField(required=True)
    phase = forms.ChoiceField(choices=PHASESTATUS, required=False)
    meteringstatus = forms.ChoiceField(choices = METERINGSTATUS, required=True)
    installationstatus = forms.ChoiceField(choices = INSTALLATIONSTATUS, required=True)
    faultystatus = forms.ChoiceField(choices = FAULTYSTATUS,required=False)
    tamperedstatus = forms.ChoiceField(choices = TAMPEREDSTATUS,required=False)
    bypassstatus = forms.ChoiceField(choices = BYPASSSTATUS,required=False)
    notokaystatus = forms.ChoiceField(choices = NOTOKAYSTATUS,required=False)
    metertype = forms.ChoiceField(choices = METERTYPE,required=True)
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))

    #x = forms.CharField(disabled=True)


    class Meta:
        model = Telcos_inspection
        fields = ('id','county','meterno','siteid','sitename','accountno','phase','metertype','meteringstatus','installationstatus','faultystatus','tamperedstatus','bypassstatus','notokaystatus','reading','telcosimg','diimg','comment','x','y')

    def __init__(self, *args, **kwargs):
        super(TelcosForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            #self.fields['faultystatus'].initial = None
            #,initial={'faultystatus': None}

    #def clean(self):
        # if self.cleaned_data['meteringstatus'] != 'okay' and self.cleaned_data['meterimg'] is None:
        #         raise ValidationError('Image Required')
        # if self.cleaned_data['x'] is None and self.cleaned_data['y'] is None:
        #         raise ValidationError('Click on The Location Button')


class PubliclightingForm(forms.ModelForm):
    #profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    phase = forms.ChoiceField(choices=PHASESTATUS, required=False)
    meterno = forms.CharField(disabled=True)
    accountno = forms.CharField(disabled=True)

    meteringstatus = forms.ChoiceField(choices = METERINGSTATUS, required=True)
    installationstatus = forms.ChoiceField(choices = INSTALLATIONSTATUS, required=True)
    faultystatus = forms.ChoiceField(choices = FAULTYSTATUS,required=False)
    tamperedstatus = forms.ChoiceField(choices = TAMPEREDSTATUS,required=False)
    bypassstatus = forms.ChoiceField(choices = BYPASSSTATUS,required=False)
    notokaystatus = forms.ChoiceField(choices = NOTOKAYSTATUS,required=False)
    metertype = forms.ChoiceField(choices = METERTYPE,required=True)
    meter_readable = forms.ChoiceField(choices=METERREADABLE, required=True)
    meter_type = forms.ChoiceField(choices=METERINSTALLTYPE, required=True)
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))

    #x = forms.CharField(disabled=True)


    class Meta:
        model = Public_lighting_inspection_25
        fields = ('id','meterno','accountno','phase','metertype','metertype','meteringstatus','meter_readable','installationstatus','faultystatus','tamperedstatus','bypassstatus','notokaystatus','reading','public_l_img','comment','x','y')

    def __init__(self, *args, **kwargs):
        super(PubliclightingForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            #self.fields['faultystatus'].initial = None
            #,initial={'faultystatus': None}

    #def clean(self):
        # if self.cleaned_data['meteringstatus'] != 'okay' and self.cleaned_data['meterimg'] is None:
        #         raise ValidationError('Image Required')
        # if self.cleaned_data['x'] is None and self.cleaned_data['y'] is None:
        #         raise ValidationError('Click on The Location Button')

class Public_lightint_direct_supplyForm(forms.ModelForm):
    x = forms.CharField( widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    y = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    class Meta:
        model = Public_lightint_direct_supply
        exclude = ['inspector','county','region','dtupdate','dtadd']

    def __init__(self, *args, **kwargs):
        super(Public_lightint_direct_supplyForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
           # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'


class Publiclighting_direcForm(forms.ModelForm):
    #profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))

    #x = forms.CharField(disabled=True)


    class Meta:
        model = Public_lighting_inspection_25
        fields = ('id','meterno','accountno','public_l_img','comment','x','y')

    def __init__(self, *args, **kwargs):
        super(Publiclighting_direcForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        form_data = self.cleaned_data
        if form_data['meterno'] == '':
            form_data['meterno'] = time.time()

        return form_data


class Publiclighting_not_in_targetForm(forms.ModelForm):
    #profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    phase = forms.ChoiceField(choices=PHASESTATUS, required=False)



    meteringstatus = forms.ChoiceField(choices = METERINGSTATUS, required=True)
    installationstatus = forms.ChoiceField(choices = INSTALLATIONSTATUS, required=True)
    faultystatus = forms.ChoiceField(choices = FAULTYSTATUS,required=False)
    tamperedstatus = forms.ChoiceField(choices = TAMPEREDSTATUS,required=False)
    bypassstatus = forms.ChoiceField(choices = BYPASSSTATUS,required=False)
    notokaystatus = forms.ChoiceField(choices = NOTOKAYSTATUS,required=False)
    metertype = forms.ChoiceField(choices = METERTYPE,required=True)
    meter_readable = forms.ChoiceField(choices=METERREADABLE, required=True)
    meter_type = forms.ChoiceField(choices=METERINSTALLTYPE, required=True)
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))

    #x = forms.CharField(disabled=True)


    class Meta:
        model = Public_lighting_inspection_25
        fields = ('id','meterno','accountno','phase','metertype','meteringstatus','installationstatus','faultystatus','tamperedstatus','meter_readable','meter_type','bypassstatus','notokaystatus','reading','public_l_img','diimg','comment','x','y')

    def __init__(self, *args, **kwargs):
        super(Publiclighting_not_in_targetForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class LpForm(forms.ModelForm):
    x = forms.CharField( widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    y = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Largepower_inspection
        fields =('meterno','accountno','smartmeter','type_of_industry','meterbox_enclosure_seal_b4','meterbox_enclosure_seal_after','meterbox_terminal_seal_b4','meterbox_terminal_seal_after','testblock_seal_b4','testblock_seal_after','meterbody_seal_b4', \
                 'meterbody_seal_after','ctchamber_seal_b4','ctchamber_seal_after','mpcc','metervoltage','ctratio_ci','ctratio_programed','ctratio_installedsite','ctratio_ci_match','ctratio_img','ctratio_ci_match_rsn','vtratio','amrrecovered', \
                 'total_180','total_180_img','max_kva_960','max_kw_150','t1_181','t2_182','reverse_consumption','reverse_consumption_rsn','moduleinstalled','modulecomm_ci','modulecom_not_rsn','civector_img', \
                 'sim_serial','sim_provider','zera_test','error_register','redphase_zera','redphase_meter','redphase_clamp','yellowphase_zera','yellowphase_meter','yellowphase_clamp','bluephase_zera','bluephase_meter','bluephase_clamp','loadbalance', \
                 'powerfactor_value','remarks','commit_inspection','current_red','current_yellow','current_blue','voltage_red','voltage_yellow','voltage_blue','r_energy','arethereanomalies','anomalies_list','anomalies_addressed_insp','anomalies_addressed_insp_list', \
                 'fallback_req','fallback_activities','commit_annomalies', 'oktoworkwith')
        # exclude = ['target','inspector','total_180_incms','dtupdate','dtadd']

    def __init__(self, *args, **kwargs):
        super(LpForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
            self.fields['commit_inspection'].widget.attrs['class'] = 'form-check-input'
            self.fields['commit_annomalies'].widget.attrs['class'] = 'form-check-input'
            

    def clean(self):
        form_data = self.cleaned_data
        if form_data['smartmeter'] == 'yes' and form_data['ctratio_ci'] =='none' :
            raise ValidationError("If this Account is a Smart Meter, Put the correct CT Ration in C&I")
        if form_data['moduleinstalled'] == 'yes' and form_data['modulecomm_ci'] == 'none':
            raise ValidationError("If this Account is a Smart Meter and Module Installed, Then Choose Whether The Module is communicating to C&I")
        if form_data['smartmeter'] == 'yes' and form_data['ctratio_ci_match'] == 'none':
            raise ValidationError(
                "If this Account is a Smart Meter, Then Choose Whether CT ratio in C&I & Installed CT are Correctly Matched")

        return form_data

class LPAccountsForm(forms.ModelForm):


    class Meta:
        model = Largepower_accounts
        fields =('meterno','accountno','srn','customer_name')
        # exclude = ['target','inspector','total_180_incms','dtupdate','dtadd']

    def __init__(self, *args, **kwargs):
        super(LPAccountsForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'


class Dc_customersForm(forms.ModelForm):
    x = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))
    y = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))
    dc_meterno = forms.CharField(disabled=True)
    dc_accountno = forms.CharField(disabled=True)

    class Meta:
        model = Dc_inspection
        fields = (
            "id",
            "dc_meterno",
            "dc_accountno",
            "dc_metertype",
            "dc_conf_type",
            "dc_meteringstatus",
            "dc_installationstatus",
            "dc_faultystatus",
            "dc_tamperedstatus",
            "dc_bypassstatus",
            "dc_notokaystatus",
            "dc_reading",
            "dc_meterimg",
            "dc_comment",
            "dc_sealno",
        )

    def __init__(self, *args, **kwargs):
        super(Dc_customersForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
        # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'

    def clean(self):
        form_data = self.cleaned_data
        if form_data["dc_conf_type"] == "postpaid" and form_data["dc_meterimg"] == "images/default.jpg":
            raise ValidationError(
                "An Image is required"
            )
        return form_data

class Dc_customersNotInTargetForm(forms.ModelForm):
    x = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))
    y = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))
    # x = forms.CharField(disabled=True)
    # y = forms.CharField(disabled=True)

    class Meta:
        model = Dc_inspection
        fields = (
            "id",
            "dc_meterno",
            "dc_metertype",
            "dc_conf_type",
            "dc_meteringstatus",
            "dc_installationstatus",
            "dc_faultystatus",
            "dc_tamperedstatus",
            "dc_bypassstatus",
            "dc_notokaystatus",
            "dc_reading",
            "dc_meterimg",
            "dc_comment",
            "dc_sealno",
            "x",
            "y",
        )

    def __init__(self, *args, **kwargs):
        super(Dc_customersNotInTargetForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
        # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'

    def clean(self):
        form_data = self.cleaned_data
        if (
            form_data["dc_conf_type"] == "postpaid"
            and form_data["dc_meterimg"] == "images/default.jpg"
        ):
            raise ValidationError("An Image is required")
        return form_data

class GenerationStationsForm(forms.ModelForm):
    x = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))
    y = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))

    class Meta:
        model = Generation_stations_inspection
        exclude = [
            "genstn",
            "ct_y_testobject",
            "ct_b_testobject",
            "ct_r_testobject",
            "vt_y_testobject",
            "vt_b_testobject",
            "vt_r_testobject",
            "inspector",
            "dtupdate",
            "dtadd",
        ]
       

    def __init__(self, *args, **kwargs):
        super(GenerationStationsForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
            self.fields["confirmation"].widget.attrs["class"] = "form-check-input"
            # self.fields["commit_annomalies"].widget.attrs["class"] = "form-check-input"

    def clean(self):
        form_data = self.cleaned_data
        if form_data["confirmation"] == False:
            raise ValidationError(
                "You Must Check the confirmation Checkbox for this information to be saved"
            )
        # if (
        #     form_data["moduleinstalled"] == "yes"
        #     and form_data["modulecomm_ci"] == "none"
        # ):
        #     raise ValidationError(
        #         "If this Account is a Smart Meter and Module Installed, Then Choose Whether The Module is communicating to C&I"
        #     )
        # if form_data["smartmeter"] == "yes" and form_data["ctratio_ci_match"] == "none":
        #     raise ValidationError(
        #         "If this Account is a Smart Meter, Then Choose Whether CT ratio in C&I & Installed CT are Correctly Matched"
        #     )

        return form_data
        
class AnomalousForm(forms.ModelForm):
    # profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    meterno = forms.CharField(disabled=True)

    latitude = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))
    longitude = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))

    class Meta:
        model = Anomalous_resolved
        fields = (
            "id",
            "meterno",
            "new_meterno",
            "faultystatus",
            "comment",
        )

    def __init__(self, *args, **kwargs):
        super(AnomalousForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
        