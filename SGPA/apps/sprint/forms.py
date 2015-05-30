# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from SGPA.apps.usuario.models import *
from SGPA.apps.usuario.helper import *
import datetime
import django
from django import forms
from django.forms.extras.widgets import SelectDateWidget
django.setup()
from datetimewidget.widgets import DateTimeWidget, DateWidget, TimeWidget

class FilterForm(forms.Form):
    filtro = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')

class SprintForm(forms.Form):

    nombre = forms.CharField(required=False, label='NOMBRE')
    descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='DESCRIPCIÓN')
    fecha_inicio = forms.DateField(widget=DateWidget(usel10n=True, bootstrap_version=2), label='FECHA DE INICIO')
    fecha_fin = forms.DateField(widget=DateWidget(usel10n=True, bootstrap_version=2), label= 'FECHA DE FIN')

    class Meta:
        model = Sprint
        widgets = {
            'date': DateWidget(attrs={'id':"fecha_inicio"}, usel10n = True, bootstrap_version=2)
        }

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

    def clean_fecha_fin(self):
        if 'fecha_fin' in self.cleaned_data:
            fecha_fin = self.cleaned_data['fecha_fin']
            fecha_inicio = self.cleaned_data['fecha_inicio']
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError('La fecha de fin es menor a la fecha de inicio.')
            return fecha_fin


class ModSprintForm(forms.Form):
    """Formulario para la modificacion de Sprint."""
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

class AsignarUSSprintForm(forms.Form):
    userstories = forms.ModelMultipleChoiceField(queryset = None, widget = forms.CheckboxSelectMultiple, label = 'USER HISTORIES', required=False)

    def __init__(self, sprint, *args, **kwargs):
        super(AsignarUSSprintForm, self).__init__(*args, **kwargs)
        self.fields['userstories'].queryset = UserHistory.objects.filter(proyecto = sprint.proyecto, sprint = None)