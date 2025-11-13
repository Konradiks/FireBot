# forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nazwa użytkownika"
    )
    password = forms.CharField(
        label="Hasło"
    )
