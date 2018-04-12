from django import forms
from .models import Recruter, JobOffer
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class JobOfferForm(forms.ModelForm):
    class Meta():
        model = JobOffer
        exclude = ['recruter']
        txt_arr = forms.Textarea(attrs={'rows': 2, 'cols': 40})
        widgets = {
            'technologies': txt_arr,
            'languages': txt_arr,
            'qualities': txt_arr
        }


class UserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class RecruterForm(forms.ModelForm):
    class Meta:
        model = Recruter
        exclude = ['user']
        widgets = {
            'location': forms.Textarea(attrs={'rows': 2, 'cols': 40})
        }
