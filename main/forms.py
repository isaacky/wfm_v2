from django import forms
from django.forms import ModelForm, widgets

from user.models import Account, UserProfile
from . models import Meters, County, Sector,Feeder_sections,Feeder


class Feeder_sectionsForm(forms.ModelForm):

    # feeder = forms.ModelChoiceField(queryset=Feeder.objects.filter(county=request.user.userprofile.county), widget=forms.Select(attrs={
    #     "class": "form-control form-control-sm col-sm-10",
    # }))

    class Meta:
        model = Feeder_sections
        fields = ('feeder','name','aprx_length')


    def __init__(self, *args, **kwargs):
        """ Grants access to the request object so that only members of the current user
        are given as options"""

        self.request = kwargs.pop("request")
        feeders = Feeder.objects.all()
            
        super(Feeder_sectionsForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control form-control-sm"
            self.fields['feeder'].widget.attrs['class'] = 'select2'
            self.fields['feeder'].queryset = feeders



        

class MeterForm(forms.ModelForm):
    meterimg = forms.ImageField(required=True)
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(MeterForm, self).__init__(*args, **kwargs)
        self.fields["sector"].queryset = Sector.objects.filter(county=self.request.user.userprofile.county)

    
    
    
    
    # def __init__(self, *args, **kwargs):
    #     self.request = kwargs.pop("request") # store value of request 
    #     super().__init__(*args, **kwargs)
    #     self.fields['sector'].queryset = Sector.objects.filter(county=self.request.user.userprofile.county)
        
    class Meta:
       
        model = Meters
        fields = ('sector','anomalytype','meternumber','customername','customercontact','readings','naration','meterimg','physicallocation')


class CountyForm(forms.ModelForm):
    class Meta:
       
        model = County
        fields = ('name','cse_name','cse_stid','cse_mobile','cse_email')


class ResolveForm(forms.ModelForm):
    class Meta:
       
        model = Meters
        fields = ('asigned_narration',)

class AsignForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.county = kwargs.pop("county") # store value of request 
        super().__init__(*args, **kwargs)
        print(self.county)
        self.fields['asigned'].queryset = UserProfile.objects.filter(profiletype='input', county=1)
       
        
    
   
    class Meta:
        model = Meters
        fields = ('asigned',)
