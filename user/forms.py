from django import forms
from django.contrib.auth.forms import UserCreationForm

from main.models import Sector,County
from .models import Account, UserProfile
from django.forms import ModelForm, Select, TextInput, FileInput, NumberInput, Textarea, PasswordInput, \
    ClearableFileInput


class RegistrationForm(forms.ModelForm):

    mobile = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": 'Enter The Staff Mobile Number',
    }))
    name = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": 'Enter The Full Name',
    }))
    stid = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": 'Enter The Staff Number(Without KPL)',
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": 'Enter The Email Address',
    }))

    class Meta:
        model = Account
        fields = ('stid', 'mobile', 'email', 'name')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('county','region','campaign')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class ChangeSectorForm(forms.ModelForm):

    county = forms.ModelChoiceField(queryset=County.objects.all(), widget=forms.Select(attrs={
        "class" : "form-control form-control-sm col-sm-10",
    }))
    class Meta:
        model = UserProfile
        fields = ('county',)
