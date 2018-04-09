from django import forms
from .models import Recruter
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class JobOfferForm(forms.Form):
    # Required fields:
    title = forms.CharField(label="Job title", max_length=100)
    degree = forms.CharField(label="Education Level", max_length=10)
    experience = forms.IntegerField(label="Experience years")
    salary = forms.CharField(label="Salary range", max_length=20)
    schedule = forms.CharField(label="Working schedule", max_length=20)
    # Requirements:
    txt_arr = forms.Textarea(attrs={'rows': 2, 'cols': 40})
    technologies = forms.CharField(max_length=50, required=False, widget=txt_arr)
    languages = forms.CharField(max_length=50, required=False, widget=txt_arr)
    qualities = forms.CharField(max_length=50, required=False, widget=txt_arr)

    # Brief job description
    description = forms.CharField(widget=forms.Textarea, required=False)


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
