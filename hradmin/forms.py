from django import forms
from .models import Inventory_list, Inventory_group
class InventoryGroupForm(forms.ModelForm):

    class Meta:
        model = Inventory_group
        fields =['name','description']

    def __init__(self, *args, **kwargs):
        super(InventoryGroupForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'

class InventoryListForm(forms.ModelForm):
    dt_purchase = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}))

    class Meta:
        model = Inventory_list
        exclude =['inspector','status','dtupdate','dtadd']

    def __init__(self, *args, **kwargs):
        super(InventoryListForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control form-control-sm'
            self.fields['county'].widget.attrs['class'] = 'select2'
            