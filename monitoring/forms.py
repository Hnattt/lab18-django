from django import forms
from .models import Device, Measurement
class MeasurementForm(forms.ModelForm):
    class Meta:
        model=Measurement
        fields=['device','temperature','measured_at']
    def __init__(self,*args,user,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['device'].queryset=Device.objects.filter(owner=user).order_by('serial')
