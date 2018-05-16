from django import forms
from .models import Recruiter, JobOffer, Candidate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class JobOfferForm(forms.ModelForm):
    class Meta():
        model = JobOffer
        exclude = ['recruiter']
        labels = {
            'experience': 'Experience (in months):'
        }
        txt_arr = forms.Textarea(attrs={'rows': 2, 'cols': 40, 'style': 'background: #eee; border: 1px solid #ddd;width:95%;'})
        txt_arr1 = forms.Textarea(attrs={'rows': 6, 'cols': 40, 'style': 'background: #eee; border: 1px solid #ddd;width:95%;'})
        widgets = {
            'programming_languages': txt_arr,
            'programming_frameworks': txt_arr,
            'technologies': txt_arr,
            'languages': txt_arr,
            'qualities': txt_arr,
            'description': txt_arr1
        }


class CandidateForm(forms.ModelForm):
    class Meta():
        model = Candidate
        exclude = ['email', 'address', 'phone', 'cv_file', 'user', 'recruiter']


class ContactForm(forms.Form):
    subject = forms.CharField(label='Subject', max_length=100)
    sender = forms.EmailField()
    reciever = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 20, 'cols': 70, 'style': 'background: #eee; border: 1px solid #ddd;width:95%;'}))


class UserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class RecruiterForm(forms.ModelForm):
    class Meta:
        model = Recruiter
        exclude = ['user']
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 6, 'cols': 70, 'style': 'background: #eee; border: 1px solid #ddd;width:95%;'}),
            'location': forms.Textarea(attrs={'rows': 2, 'cols': 40, 'style': 'background: #eee; border: 1px solid #ddd;width:95%;'})
        }


class FileFieldForm(forms.Form):
    file_field = forms.FileField(label="", widget=forms.ClearableFileInput(attrs={'multiple': True, 'style': "margin:0 auto;text-align: center;font-size: 20px; color: #444;font-weight: bold; width: 30%; background: #ccc"}))
