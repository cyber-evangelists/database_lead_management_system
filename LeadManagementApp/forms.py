from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'validate', 'required': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'required': True}))

class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['password', 'first_name', 'last_name','email']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['password', 'first_name', 'last_name','email','username']

