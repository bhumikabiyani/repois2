# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from SGPA.apps.usuario.models import *
from SGPA.apps.usuario.helper import *
import datetime

class UsuariosForm(forms.Form):
	username = forms.CharField(label="USUARIO",widget=forms.TextInput())
	first_name = forms.CharField(label="NOMBRE",widget=forms.TextInput())
	last_name = forms.CharField(label="APELLIDO",widget=forms.TextInput())
	email    = forms.EmailField(label="CORREO ELECTRONICO",widget=forms.TextInput())
	password_one = forms.CharField(label="CANTRASEÑA",widget=forms.PasswordInput(render_value=False))
	password_two = forms.CharField(label="CONFIRMAR CONTRASEÑA",widget=forms.PasswordInput(render_value=False))

	def clean_username(self):
		username = self.cleaned_data['username']
		try:
			u = User.objects.get(username=username)
		except User.DoesNotExist:
			return username
		raise forms.ValidationError('Nombre de usuario ya existe')

	def clean_email(self):
		email = self.cleaned_data['email']
		try:
			u = User.objects.get(email=email)
		except User.DoesNotExist:
			return email
		raise forms.ValidationError('Email ya registrado')

	def clean_password_two(self):
		password_one = self.cleaned_data['password_one']
		password_two = self.cleaned_data['password_two']
		if password_one == password_two:
			pass
		else:
			raise forms.ValidationError('Contraseñas no coinciden')

class FilterForm(forms.Form):
    filtro = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')

class FilterForm2(forms.Form):
    filtro1 = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas1 = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')
    filtro2 = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas2 = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')

class ModUsuariosForm(forms.Form):
	first_name = forms.CharField(label="NOMBRE",widget=forms.TextInput())
	last_name = forms.CharField(label="APELLIDO",widget=forms.TextInput())
	email = forms.EmailField(label="CORREO ELECTRONICO",widget=forms.TextInput())

class CambiarPasswordForm(forms.Form):
	password1 = forms.CharField(widget = forms.PasswordInput, max_length=128, label = u'ESCRIBA SU NUEVA CONTRASEÑA')
	password2 = forms.CharField(widget = forms.PasswordInput, max_length=128, label = u'REPITA SU NUEVA CONTRASEÑA')

	def clean_password2(self):
		if 'password1' in self.cleaned_data:
			password1 = self.cleaned_data['password1']
			password2 = self.cleaned_data['password2']
			if password1 == password2:
				return password2
		raise forms.ValidationError('Las contraseñas no coinciden')