from django import forms
from .models import (
    TrnsGroundInspection,
    InsulatorInspection,
    ConductorInspection,
    EarthOPGW,
    TowerFoundations,
)

class TrnsGroundInspectionForm(forms.ModelForm):
    latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = TrnsGroundInspection
        exclude = ["inspectedby", "save_status","dtadd","dtupdate","aprv_status","aprv_by","aprv_notes","aprv_dt"]

    def __init__(self, *args, **kwargs):
        super(TrnsGroundInspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class InsulatorInspectionForm(forms.ModelForm):
    class Meta:
        model = InsulatorInspection
        exclude = ["line","save_status"]
    def __init__(self, *args, **kwargs):
        super(InsulatorInspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"


class ConductorInspectionForm(forms.ModelForm):
    class Meta:
        model = ConductorInspection
        exclude = ["line","save_status"]
    def __init__(self, *args, **kwargs):
        super(ConductorInspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

class EarthOPGWForm(forms.ModelForm):
    class Meta:
        model = EarthOPGW
        exclude = ["line","save_status"]
    def __init__(self, *args, **kwargs):
        super(EarthOPGWForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"

class TowerFoundationsForm(forms.ModelForm):
    class Meta:
        model = TowerFoundations
        exclude = ["line","save_status"]

    def __init__(self, *args, **kwargs):
        super(TowerFoundationsForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"