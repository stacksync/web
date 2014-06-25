#encoding:utf-8 
from django.forms import ModelForm
from django import forms


class ContactForm(forms.Form): 
	subject = forms.CharField(max_length=100) 
	email = forms.EmailField(required=False, label='Your e-mail address') 
	message = forms.CharField(widget=forms.Textarea) 
	

class ArchivoForm(forms.Form):
	archivo = forms.FileField()



