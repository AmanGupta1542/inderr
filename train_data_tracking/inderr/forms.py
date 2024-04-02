from django import forms
from django.forms import ModelForm

from .models import UploadImage, ConfigInfo

class UserLogin(forms.Form):
    username = forms.CharField(label="Username", max_length=100)
    password = forms.CharField(label="Password", max_length=100, widget = forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(UserLogin, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class UserImage(forms.ModelForm):  
    class Meta:  
        # To specify the model to be used to create form  
        model = UploadImage  
        # It includes all the fields of model  
        fields = '__all__'  


class ConfigInfoForm(forms.ModelForm):
    class Meta:
        model = ConfigInfo
        fields = ['train', 'coach_no']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['train'].widget.attrs.update({'class': 'form-control select2', 'style': 'width: 100%'})
        self.fields['coach_no'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter coach number'})