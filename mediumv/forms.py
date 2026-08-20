from django import forms
from .models import Mvinspection, Mv_poledefects, Mvmaitenance, Poledefects_maintenance
from main.models import Feeder_sections

class MvmaintenanceApproveForm(forms.ModelForm):
    class Meta:
        model = Mvmaitenance
        fields = ["aprv_notes", "aprv_key"]

    def __init__(self, *args, **kwargs):
        super(MvmaintenanceApproveForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
        # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'

class MvinspectionApproveForm(forms.ModelForm):
    class Meta:
        model = Mvinspection
        fields = ["aprv_notes", "aprv_key"]

    def __init__(self, *args, **kwargs):
        super(MvinspectionApproveForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
        # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'


class MvinspectionForm(forms.ModelForm):
    class Meta:
        model = Mvinspection
        exclude = [
            "feeder",
            "aprv_status",
            "aprv_by",
            "aprv_notes",
            "aprv_dt",
            "aprv_key",
            "dtadd",
            "dtupdate",
            "inspectedby",
            "county",
        ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        print(self.request)
        super(MvinspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
            self.fields["save_status"].widget.attrs["class"] = "form-check-input"
            self.fields["feeder_section"].widget.attrs[
                "class"
            ] = "form-control select2 text-uppercase"
            self.fields["feeder_section"].queryset = Feeder_sections.objects.filter(
                feeder_id=self.request
            )


class MvPoledefectsForm(forms.ModelForm):
    y = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))
    x = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))

    class Meta:
        model = Mv_poledefects
        fields = ["defect_type", "x", "y", "pole_type","polefitting_type", "location"]

    def __init__(self, *args, **kwargs):
        super(MvPoledefectsForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"


class MvmaintenanceForm(forms.ModelForm):
    class Meta:
        model = Mvmaitenance
        exclude = [
            "mvinspection",
            "feeder_section",
            "feeder",
            "aprv_status",
            "aprv_by",
            "aprv_notes",
            "aprv_dt",
            "aprv_key",
            "dtadd",
            "dtupdate",
            "inspectedby",
            "county",
        ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(MvmaintenanceForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"

class Poledefects_maintenanceForm(forms.ModelForm):
    x = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    y = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Poledefects_maintenance
        fields = ['pole_type','location','maintain_notes','defect_type']

    def __init__(self, *args, **kwargs):
        super(Poledefects_maintenanceForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
           # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'