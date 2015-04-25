# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    """Clase para el Formulario para login"""
    Nombre = forms.CharField(widget=forms.TextInput())
    Contrasena = forms.CharField(widget=forms.PasswordInput(render_value=False))


class RecuperarContrasenaForm(forms.Form):
    """Clase para el Formulario para recuperar contraseña"""
    Correo = forms.CharField(widget=forms.TextInput())
