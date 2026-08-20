from django import forms
from django.forms import ModelForm, widgets

from user.models import Account, UserProfile
from . models import Debtlist, Revenuerecollection

STATUSCHOISES= (
        ('','----CHOOSE A STATUS----'),
        ('paid','PAID'),
        ('fdc','FDC'),
        ('disconnected', 'DISCONNECTED'),
        ('poledisconnection', 'POLE DISCONNECTION'),
        ('cablerecovery', 'CABLE RECOVERY'),
        ('notonsite','NOT-ON-SITE'),
        ('faulty', 'FAULTY'),
        ('wrongreading', 'WRONG READING'),
        )
        
class MeterForm(forms.ModelForm):
    #profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    meterno = forms.CharField(disabled=True)
    accountno = forms.CharField(disabled=True)
    collection_status = forms.ChoiceField(choices = STATUSCHOISES, required=True)

    class Meta:
        model = Revenuerecollection
        fields = ('id','meterno','accountno','reading','amountpaid','collection_status','comment')
       

    def __init__(self, *args, **kwargs):
        super(MeterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class DebtListForm(forms.ModelForm):
    # dt_asigned = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}))

    class Meta:
        model = Debtlist
        fields = ('id', 'asigned_to')


    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(DebtListForm, self).__init__(*args, **kwargs)
        self.fields["asigned_to"].queryset = UserProfile.objects.select_related('county','user').filter(
            county=self.request.user.userprofile.county, campaign='revenue'
        )
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
            self.fields['asigned_to'].widget.attrs['class'] = 'form-control select2'