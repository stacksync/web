#encoding:utf-8 
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User


class contact_form(forms.Form):
    subject = forms.CharField(max_length=100)
    email = forms.EmailField(required=False, label='Your e-mail address')
    message = forms.CharField(widget=forms.Textarea)

class file_form(forms.Form):
    file = forms.FileField()



