from django import forms
from django.forms import ModelForm, widgets, ValidationError
from .models import (
    Transdist_insp,
    Feeder_inspection,
    Power_tx_inspection,
    Aux_tx_inspection,
    Feeder_inspection_outgoing,
    Sixtysix_kv_customer,
    Sixtysix_kv_substation,
    Sixtysix_kv_meter,
    Sixtysix_kv_sealing,
Sixtysix_kv_testeqipment,
Sixtysix_kv_current,
Sixtysix_kv_ctvt_redphase,
Sixtysix_kv_ctvt_yellowphase,
Sixtysix_kv_ctvt_bluephase,
Sixtysix_kv_meter_readings,
Sixtysix_kv_otherinfo
)
from main.models import County

class Sixtysix_kv_inspection_finalForm(forms.ModelForm):

    class Meta:
        model = Sixtysix_kv_substation
        fields = ("customer",
            "save_status")


    def __init__(self, *args, **kwargs):
        super(Sixtysix_kv_inspection_finalForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"


class Sixtysix_otherinfoForm(forms.ModelForm):

    class Meta:
        model = Sixtysix_kv_otherinfo
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "customer"
        ]
    def __init__(self, *args, **kwargs):
        super(Sixtysix_otherinfoForm, self).__init__(*args, **kwargs)
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

class Sixtysix_kv_meterreadingsForm(forms.ModelForm):

    class Meta:
        model = Sixtysix_kv_meter_readings
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "customer"
        ]
    def __init__(self, *args, **kwargs):
        super(Sixtysix_kv_meterreadingsForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
            self.fields["meter_date_cur"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "yyyy-mm-dd",
                    "class": "form-control",
                }
            )
            self.fields["meter_date_mem"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "yyyy-mm-dd",
                    "class": "form-control",
                }
            )
            self.fields["meter_time_mem"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "time",
                    "placeholder": "HH:MM",
                    "class": "form-control",
                }
            )
            self.fields["meter_time_curr"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "time",
                    "placeholder": "HH:MM",
                    "class": "form-control",
                }
            )

class Sixtysix_kv_ctvt_blueForm(forms.ModelForm):

    class Meta:
        model = Sixtysix_kv_ctvt_bluephase
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "customer"
        ]
    def __init__(self, *args, **kwargs):
        super(Sixtysix_kv_ctvt_blueForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
class Sixtysix_kv_ctvt_yellowForm(forms.ModelForm):

    class Meta:
        model = Sixtysix_kv_ctvt_yellowphase
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "customer"
        ]
    def __init__(self, *args, **kwargs):
        super(Sixtysix_kv_ctvt_yellowForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
class Sixtysix_kv_ctvt_redForm(forms.ModelForm):

    class Meta:
        model = Sixtysix_kv_ctvt_redphase
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "customer"
        ]
    def __init__(self, *args, **kwargs):
        super(Sixtysix_kv_ctvt_redForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"

class Sixtysix_kv_currentForm(forms.ModelForm):

    class Meta:
        model = Sixtysix_kv_current
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "customer"
        ]
    def __init__(self, *args, **kwargs):
        super(Sixtysix_kv_currentForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
class Sixtysix_kv_testequipmentForm(forms.ModelForm):

    class Meta:
        model = Sixtysix_kv_testeqipment
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "customer"
        ]
    def __init__(self, *args, **kwargs):
        super(Sixtysix_kv_testequipmentForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"

class Sixtysix_kv_sealingForm(forms.ModelForm):

    class Meta:
        model = Sixtysix_kv_sealing
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "customer"
        ]
    def __init__(self, *args, **kwargs):
        super(Sixtysix_kv_sealingForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
class Sixtysix_kv_meteringForm(forms.ModelForm):

    class Meta:
        model = Sixtysix_kv_meter
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "customer"
        ]
    def __init__(self, *args, **kwargs):
        super(Sixtysix_kv_meteringForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"

class Sixtysix_kv_inspectionForm(forms.ModelForm):
    latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Sixtysix_kv_substation
        exclude = [
            "dtadd",
            "dtupdate",
            "inspectedby",
            "county",
            "region",
            "customer"
        ]
    def __init__(self, *args, **kwargs):
        super(Sixtysix_kv_inspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"

class SixtysixTargetForm(forms.ModelForm):

    class Meta:
        model = Sixtysix_kv_customer
        fields = (
            "id",
            "meter_number",
            "account_number",
            "new_account_number",
            "name",
            "feeder",

        )

    def __init__(self, *args, **kwargs):
        super(SixtysixTargetForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
        # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'

    # def clean(self):
    #     form_data = self.cleaned_data
    #     if (
    #         form_data["dc_conf_type"] == "postpaid"
    #         and form_data["dc_meterimg"] == "images/default.jpg"
    #     ):
    #         raise ValidationError("An Image is required")
    #     return form_data

class SixtysixSubmitForm(forms.ModelForm):

    class Meta:
        model = Sixtysix_kv_customer
        fields = (
            "id",

        )

    def __init__(self, *args, **kwargs):
        super(SixtysixSubmitForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"

class Aux_tx_inspectionForm(forms.ModelForm):
    class Meta:
        model = Aux_tx_inspection
        exclude = [
            "dtadd",
            "dtupdate",
            "inspector",
            "transdist",
        ]

    def __init__(self, *args, **kwargs):
        super(Aux_tx_inspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"


class Power_tx_inspectionForm(forms.ModelForm):
    class Meta:
        model = Power_tx_inspection
        exclude = [
            "dtadd",
            "dtupdate",
            "inspector",
            "transdist",
        ]

    def __init__(self, *args, **kwargs):
        super(Power_tx_inspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
            self.fields["remarks"].widget.attrs = {"rows": 4, "cols": 60}
            self.fields["recommendation"].widget.attrs = {"rows": 4, "cols": 60}
            self.fields["dt_visit"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "yyyy-mm-dd",
                    "class": "form-control",
                }
            )
            self.fields["dt_on_meter_during_visit"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "yyyy-mm-dd",
                    "class": "form-control",
                }
            )
            self.fields["tm_visit"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "time",
                    "placeholder": "HH:MM",
                    "class": "form-control",
                }
            )
            self.fields["tm_on_meter_during_visit"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "time",
                    "placeholder": "HH:MM",
                    "class": "form-control",
                }
            )


class Feeder_inspectionForm(forms.ModelForm):
    class Meta:
        model = Feeder_inspection
        exclude = [
            "dtadd",
            "dtupdate",
            "inspector",
            "transdist",
        ]

    def __init__(self, *args, **kwargs):
        super(Feeder_inspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
            self.fields["remarks"].widget.attrs = {"rows": 4, "cols": 60}
            self.fields["recommendation"].widget.attrs = {"rows": 4, "cols": 60}
            self.fields["dt_visit"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "yyyy-mm-dd",
                    "class": "form-control",
                }
            )
            self.fields["dt_on_meter_during_visit"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "yyyy-mm-dd",
                    "class": "form-control",
                }
            )
            self.fields["tm_visit"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "time",
                    "placeholder": "HH:MM",
                    "class": "form-control",
                }
            )
            self.fields["tm_on_meter_during_visit"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "time",
                    "placeholder": "HH:MM",
                    "class": "form-control",
                }
            )


class Feeder_inspection_outgoingForm(forms.ModelForm):
    class Meta:
        model = Feeder_inspection_outgoing
        exclude = [
            "dtadd",
            "dtupdate",
            "inspector",
            "transdist",
        ]

    def __init__(self, *args, **kwargs):
        super(Feeder_inspection_outgoingForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
            self.fields["remarks"].widget.attrs = {"rows": 4, "cols": 60}
            self.fields["recommendation"].widget.attrs = {"rows": 4, "cols": 60}
            self.fields["dt_visit"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "yyyy-mm-dd",
                    "class": "form-control",
                }
            )
            self.fields["dt_on_meter_during_visit"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "yyyy-mm-dd",
                    "class": "form-control",
                }
            )
            self.fields["tm_visit"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "time",
                    "placeholder": "HH:MM",
                    "class": "form-control",
                }
            )
            self.fields["tm_on_meter_during_visit"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "time",
                    "placeholder": "HH:MM",
                    "class": "form-control",
                }
            )


class TransdistForm(forms.ModelForm):
    county = forms.ModelChoiceField(
        queryset=County.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-control form-control-sm col-sm-10",
            }
        ),
    )

    class Meta:
        model = Transdist_insp
        exclude = [
            "dtadd",
            "dtupdate",
            "status",
            "inspector",
            "transdist",
        ]

    def __init__(self, *args, **kwargs):
        super(TransdistForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
