# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
	Nombre = forms.CharField(widget=forms.TextInput())
	Contrasena = forms.CharField(widget=forms.PasswordInput(render_value=False))


