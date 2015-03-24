# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from SGPA.apps.usuario import *
import datetime

class UsuariosForm(forms.Form):
	username = forms.CharField(max_length=30, label='USUARIO')
	first_name = forms.CharField(max_length=30, label='NOMBRE')
	last_name = forms.CharField(max_length=30, label='APELLIDO')
	email = forms.EmailField(max_length=75, label='EMAIL')
	password = forms.CharField(max_length=128, label='CONTRASEÑA', widget=forms.PasswordInput())
	password2 = forms.CharField(max_length=128, label='CONFIRMAR CONTRASEÑA', widget=forms.PasswordInput())

	def clean_password2(self):
		#comprobar que las contrasenas dadas sean iguales
		if 'password' in self.cleaned_data:
			password = self.cleaned_data['password']
			password2 = self.cleaned_data['password2']
			if password == password2:
				return password2
		raise forms.ValidationError('Las contraseñas no coinciden')

	def clean_username(self):
		#controlar que ya no existe el nombre de usuario
		if 'username' in self.cleaned_data:
			usuarios = User.objects.all()
			nuevo = self.cleaned_data['username']
			for i in usuarios:
				if i.username == nuevo:
					raise forms.ValidationError('Ya existe ese nombre de usuario. Elija otro')
			return nuevo

class ModUsuariosForm(forms.Form):
        username = forms.CharField(max_length=30, label='USUARIO')
	first_name = forms.CharField(max_length=30, label='NOMBRE')
	last_name = forms.CharField(max_length=30, label='APELLIDO')
	email = forms.EmailField(max_length=75, label='EMAIL')

        def clean_username(self):
		#controlar que ya no existe el nombre de usuario
		if 'username' in self.cleaned_data:
			usuarios = User.objects.all()
			nuevo = self.cleaned_data['username']
			for i in usuarios:
				if i.username == nuevo:
					raise forms.ValidationError('Ya existe ese nombre de usuario. Elija otro')
			return nuevo

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

class FilterForm(forms.Form):
    filtro = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')

class FilterForm2(forms.Form):
    filtro1 = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas1 = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')
    filtro2 = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas2 = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')
