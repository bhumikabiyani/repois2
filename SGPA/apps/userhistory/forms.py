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
    """
    Clase para el formulario Busqueda y Paginacion de UserHistory
    """
    filtro = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')

class UserHistoryForm(forms.Form):
    """
    Clase para el formulario de UserHistory
    """
    nombre = forms.CharField(max_length=50, label='NOMBRE')
    estado = forms.CharField(max_length=6, widget=forms.Select(choices=ESTADO_CHOICES), label = 'ESTADO')
    tiempo_estimado = forms.IntegerField(label='TIEMPO ESTIMADO')
    def clean_nombre(self):
        if 'nombre' in self.cleaned_data:
            userHistory = UserHistory.objects.all()
            nombre = self.cleaned_data['nombre']
            for i in userHistory:
                if nombre == i.nombre:
                    raise forms.ValidationError('Ya existe ese nombre de User History. Elija otro')
            return nombre

class ModUserHistoryForm(forms.Form):
    """
    Clase para el formulario de modificar User History
    """
    estado = forms.CharField(max_length=6, widget=forms.Select(choices=ESTADO_CHOICES), label = 'ESTADO')
    tiempo_estimado = forms.IntegerField(label='TIEMPO ESTIMADO')