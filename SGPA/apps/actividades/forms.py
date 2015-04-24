# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from SGPA.apps.usuario.models import *
from SGPA.apps.usuario.helper import *
import datetime
import django
django.setup()

class FilterForm(forms.Form):
    filtro = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')
    
class FilterForm2(forms.Form):
    filtro1 = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas1 = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')
    filtro2 = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas2 = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')

class ActividadForm(forms.Form):
	nombre = forms.CharField(max_length=50, label='NOMBRE')
	descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='DESCRIPCIÓN')
		
	def clean_nombre(self):
		if 'nombre' in self.cleaned_data:
			actividades = Actividad.objects.all()
			nombre = self.cleaned_data['nombre']
			for i in actividades:
				if nombre == i.nombre:
					raise forms.ValidationError('Ya existe ese nombre de actividad. Elija otro')
			return nombre

class ModActividadForm(forms.Form):
	descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='DESCRIPCIÓN')
