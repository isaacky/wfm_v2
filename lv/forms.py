from django import forms

from .models import Poledefects,Lvinspection,MaintainLVinspection, MaintainPoleDefects, SubstationInspection,\
    TxFailure,Commission_substation, Poledefects_maintenance,Substation,SubstationMaintenance, LoadChecks

class LoadChecksForm(forms.ModelForm):

    class Meta:
        model = LoadChecks
        exclude =['dtadd','dtupdate','inspectedby','county','region','substation']

    def __init__(self, *args, **kwargs):
        super(LoadChecksForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'


            # comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))


class SubstationForm(forms.ModelForm):

    class Meta:
        model = Substation
        exclude =['longitude','latitude','dtadd','dtupdate','createdby','county','region']

    def __init__(self, *args, **kwargs):
        super(SubstationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'


            # comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))



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

class MaintainPoleApproveForm(forms.ModelForm):

    class Meta:
        model = Poledefects_maintenance
        fields = ['aprv_notes','aprv_key']

    def __init__(self, *args, **kwargs):
        super(MaintainPoleApproveForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
           # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'

class CommissionApproveForm(forms.ModelForm):

    class Meta:
        model = Commission_substation
        fields = ['aprv_notes','aprv_key']

    def __init__(self, *args, **kwargs):
        super(CommissionApproveForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
           # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'
class Commission_substationForm(forms.ModelForm):
    latitude = forms.CharField( widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Commission_substation
        exclude =['substation','county','inspectedby','dtupdate','dtadd','aprv_dt','aprv_by','aprv_notes', 'aprv_status','region']

    def __init__(self, *args, **kwargs):
        super(Commission_substationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
            self.fields['comments'].widget.attrs={'rows': 4, 'cols': 60}
            self.fields["dt_commission"].widget = forms.widgets.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "yyyy-mm-dd",
                    "class": "form-control",
                }
            )

            # comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))
class PoledefectsForm(forms.ModelForm):
    y = forms.CharField( widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    x = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Poledefects
        fields = ['defect_type','x','y','pole_type','location']

    def __init__(self, *args, **kwargs):
        super(PoledefectsForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'

class LvinspectionForm(forms.ModelForm):
    latitude = forms.CharField( widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Lvinspection
        exclude =['substation','county','inspectedby','dtupdate','dtadd','aprv_dt','aprv_by','aprv_notes', 'aprv_status','maitenance_notes','aprv_status_maintenance',
                 'aprv_by_maintenace','aprv_notes_maintenace','aprv_dt_maintenance','aprv_key_maintenance','aprv_key','dt_maintenance','inspectedby_maintenance','region']

    def __init__(self, *args, **kwargs):
        super(LvinspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
            self.fields['save_status'].widget.attrs['class'] = 'form-check-input'
            self.fields['c1_r'].widget.attrs.update({'placeholder': 'CCT1R'})
            self.fields['inspect_notes'].widget.attrs={'rows': 4, 'cols': 60}

            # comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))

class LvinspectionApproveForm(forms.ModelForm):

    class Meta:
        model = Lvinspection
        fields = ['aprv_notes','aprv_key']

    def __init__(self, *args, **kwargs):
        super(LvinspectionApproveForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
           # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'

class TxFailureForm(forms.ModelForm):
    latitude = forms.CharField( widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    class Meta:
        model = TxFailure
        exclude = ['substation','county','inspectedby','dtupdate','dtadd','aprv_dt','aprv_by','aprv_notes', 'save_status','aprv_status','region']

    def __init__(self, *args, **kwargs):
        super(TxFailureForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
           # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'

class MaintainLVinspectionForm(forms.ModelForm):

    class Meta:
        model = MaintainLVinspection
        exclude = ['lvinspection','county','inspectedby','dtupdate','dtadd','aprv_dt','aprv_by','aprv_notes','aprv_status']

    def __init__(self, *args, **kwargs):
        super(MaintainLVinspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
            self.fields['save_status'].widget.attrs['class'] = 'form-check-input'

class SubstationInspectionForm(forms.ModelForm):
    latitude = forms.CharField( widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    class Meta:
        model = SubstationInspection
        exclude = ['substation','county','inspectedby','dtupdate','dtadd','aprv_dt','aprv_by','aprv_notes','region']

    def __init__(self, *args, **kwargs):
        super(SubstationInspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
           # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'

class LvmaintenanceApproveForm(forms.ModelForm):

    class Meta:
        model = MaintainLVinspection
        fields = ['aprv_notes','aprv_key']

    def __init__(self, *args, **kwargs):
        super(LvmaintenanceApproveForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
           # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'

class LvfailureApproveForm(forms.ModelForm):

    class Meta:
        model = TxFailure
        fields = ['aprv_notes','aprv_key']

    def __init__(self, *args, **kwargs):
        super(LvfailureApproveForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
           # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'

class SubstationApproveForm(forms.ModelForm):

    class Meta:
        model = TxFailure
        fields = ['aprv_notes','aprv_key']

    def __init__(self, *args, **kwargs):
        super(SubstationApproveForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
           # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'
           
class MaintainSubstationinspectionForm(forms.ModelForm):
    latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = SubstationMaintenance
        exclude = ['inspection','county','inspectedby','dtupdate','dtadd','aprv_dt','aprv_by','aprv_notes','aprv_status','region']

    def __init__(self, *args, **kwargs):
        super(MaintainSubstationinspectionForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
            self.fields['save_status'].widget.attrs['class'] = 'form-check-input'
           
class GlobalSubstationForm(forms.ModelForm):

    class Meta:
        model = Substation
        exclude =['longitude','latitude','dtadd','dtupdate','createdby']

    def __init__(self, *args, **kwargs):
        super(GlobalSubstationForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
        # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'
        
class SubstationMaintenanceApproveForm(forms.ModelForm):

    class Meta:
        model = SubstationMaintenance
        fields = ['aprv_notes','aprv_key']

    def __init__(self, *args, **kwargs):
        super(SubstationMaintenanceApproveForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
           # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'