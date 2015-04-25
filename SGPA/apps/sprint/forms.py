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

class SprintForm(forms.Form):

    nombre = forms.CharField(required=False, label='NOMBRE')
    descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='DESCRIPCIÓN')
    fecha_inicio = forms.DateField(label='FECHA DE INICIO')
    fecha_fin = forms.DateField(label='FECHA DE FIN')

    #cantidad = forms.IntegerField( label = 'cantidad')
    #nro_secuencia = forms.IntegerField()
    #tipo_item = forms.IntegerField()
    #estado = forms.CharField(max_length=50, required=False, label='estado')
    #tipo_item = forms.ModelChoiceField(queryset=TipoItem.objects.all(), label='TIPO DE ITEM')

    class Meta:
        model = Sprint
        #fields = ('nombre','cantidad')

    def __init__(self, proyect_id, *args, **kwargs):
        super(SprintForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].queryset = Sprint.objects.filter(proyecto = proyect_id)

    def clean_nombre(self):
		if 'nombre' in self.cleaned_data:
			sprint = Sprint.objects.all()
			nombre = self.cleaned_data['nombre']
			for s in sprint:
				if nombre == s.nombre:
					raise forms.ValidationError('Ya existe ese nombre de sprint. Elija otro')
			return nombre

class ModSprintForm(forms.Form):
    """Formulario para la modificacion de Sprint."""
    nombre = forms.CharField(max_length=50, label='NOMBRE')
    #cantidad = forms.IntegerField()
    descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='DESCRIPCIÓN')
    #tipo_item = forms.ModelChoiceField(queryset=TipoItem.objects.all(), label='TIPO DE ITEM')

    def __init__(self, sprint, *args, **kwargs):
		super(ModSprintForm, self).__init__(*args, **kwargs)
		self.f = sprint

    def clean_nombre(self):
    	if 'nombre' in self.cleaned_data:
    		nuevo = self.cleaned_data['nombre']
    		if nuevo != self.f.nombre:
		    	sprint = Sprint.objects.all()
		    	nuevo = self.cleaned_data['nombre']
		    	for f in sprint:
		    		if f.nombre == nuevo:
		    			raise forms.ValidationError('Ya existe ese nombre. Elija otro')
    		return nuevo
