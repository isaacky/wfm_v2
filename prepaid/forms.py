from django import forms
from django.forms import ModelForm, widgets

from user.models import Account, UserProfile
from . models import Tid_inspection
STATUSCHOISES= (
        ('','----CHOOSE A STATUS----'),
        ('vended','VENDED'),
        ('recovered','RECOVERED'),
        ('faulty','FAULTY'),
        ('notonsite','NOT-ON-SITE'),
        ('pendingrerec','PENDING REREC COMM'),
        
           
        )

class TidForm(forms.ModelForm):
    x = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))
    y = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))

    class Meta:
        model = Tid_inspection
        exclude = ["inspector", "county", "region", "dtupdate", "dtadd",'r_units','tid']

    def __init__(self, *args, **kwargs):
        super(TidForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
        # self.fields['maitain_status'].widget.attrs['class'] = 'custom-control-input'



