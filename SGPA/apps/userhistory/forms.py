# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from SGPA.apps.usuario.models import *
from SGPA.apps.usuario.helper import *
import datetime
import django
django.setup()
from django.forms.widgets import *
from datetimewidget.widgets import DateTimeWidget, DateWidget, TimeWidget

class FilterForm(forms.Form):
    """
    Clase para el formulario Busqueda y Paginacion de UserHistory
    """
    filtro = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')

class UserHistoryForm(forms.Form):
    """
    Clase para el formulario de Creación de UserHistory
    """
    nombre = forms.CharField(max_length=50, label='NOMBRE')
    descripcion = forms.CharField(max_length=500, label='DESCRIPCION')
    valor_tecnico = forms.IntegerField(label='VALOR TECNICO')
    valor_negocio = forms.IntegerField(label='VALOR NEGOCIO')
    tiempo_estimado = forms.IntegerField(label='TIEMPO ESTIMADO')
    fecha_estimada = forms.DateField(widget=DateWidget(usel10n=True, bootstrap_version=2), label='FECHA ESTIMADA')

    class Meta:
        model = UserHistory
        widgets = {
            'date': DateWidget(attrs={'id':"fecha_estimada"}, usel10n = True, bootstrap_version=2)
        }
    # flujo = forms.ModelChoiceField(queryset=Flujo.objects.filter())
    # sprint = forms.ModelChoiceField(queryset=Sprint.objects.filter())
    #usuario_lider = forms.ModelChoiceField(queryset=User.objects.all())
    proyecto = Proyecto()

    def __init__(self, proyecto, *args, **kwargs):
        super(UserHistoryForm, self).__init__(*args, **kwargs)
        self.proyecto = proyecto
        urp = UsuarioRolProyecto.objects.filter(proyecto = proyecto)
        listUser = []
        for rec in urp:
            if not rec.usuario.id in listUser:
                listUser.append(rec.usuario.id)
        # self.fields['encargado'].queryset = User.objects.filter(Q(id__in = listUser))

        fap = FlujoActividadProyecto.objects.filter(proyecto = proyecto)
        listFlujo = []
        for i in fap:
            if not i.flujo.id in listFlujo:
                listFlujo.append(i.flujo.id)
        # self.fields['flujo'].queryset = Flujo.objects.filter(Q(id__in = listFlujo))

        sp = Sprint.objects.filter(proyecto = proyecto)
        # self.fields['sprint'].queryset = sp

class ModUserHistoryForm(forms.Form):
    """
    Clase para el formulario de modificar User History
    """
    descripcion =forms.CharField(max_length=500, label='DESCRIPCION')
    tiempo_estimado = forms.IntegerField(label='TIEMPO ESTIMADO')
    valor_tecnico = forms.IntegerField(label='VALOR TECNICO')
    valor_negocio = forms.IntegerField(label='VALOR NEGOCIO')
    # encargado = forms.ModelChoiceField(queryset=User.objects.filter())
    # flujo = forms.ModelChoiceField(queryset=Flujo.objects.filter())
    # sprint = forms.ModelChoiceField(queryset=Sprint.objects.filter())
    proyecto = Proyecto()

    def __init__(self, proyecto, *args, **kwargs):
        super(ModUserHistoryForm, self).__init__(*args, **kwargs)
        self.proyecto = proyecto
        urp = UsuarioRolProyecto.objects.filter(proyecto = proyecto)
        listUser = []
        for rec in urp:
            if not rec.usuario.id in listUser:
                listUser.append(rec.usuario.id)
        # self.fields['encargado'].queryset = User.objects.filter(Q(id__in = listUser))

        fap = FlujoActividadProyecto.objects.filter(proyecto = proyecto)
        listFlujo = []
        for i in fap:
            if not i.flujo.id in listFlujo:
                listFlujo.append(i.flujo.id)
        # self.fields['flujo'].queryset = Flujo.objects.filter(Q(id__in = listFlujo))

        sp = Sprint.objects.filter(proyecto = proyecto)
        # self.fields['sprint'].queryset = sp

class AddCommentForm(forms.Form):
    asunto = forms.CharField(max_length=500, label='ASUNTO')
    descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='DESCRIPCIÓN')
    horas = forms.IntegerField(label='HORAS')
    #tipo_item = forms.ModelChoiceField(queryset=TipoItem.objects.all(), label='TIPO DE ITEM')

    def __init__(self, userhistory, *args, **kwargs):
        super(AddCommentForm, self).__init__(*args, **kwargs)
        self.us = userhistory

    def clean_asunto(self):
		if 'asunto' in self.cleaned_data:
			comment = Comentarios.objects.filter(userhistory = self.us)
			asunto = self.cleaned_data['asunto']
			for rec in comment:
				if asunto == rec.asunto:
					raise forms.ValidationError('Ya existe ese asunto. Elija otro')
			return asunto

class AsignarEncargadoUSForm(forms.Form):
    encargado = forms.ModelChoiceField(queryset=User.objects.filter())

    def __init__(self, proyecto, *args, **kwargs):
        super(AsignarEncargadoUSForm, self).__init__(*args, **kwargs)
        self.proyecto = proyecto
        cliente = Rol.objects.get(nombre = "Cliente")
        urp = UsuarioRolProyecto.objects.filter(proyecto = proyecto).exclude(rol=cliente)
        listUser = []
        for rec in urp:
            if not rec.usuario.id in listUser:
                listUser.append(rec.usuario.id)
        self.fields['encargado'].queryset = User.objects.filter(Q(id__in = listUser))

class AsignarSprintUSForm(forms.Form):
    sprint = forms.ModelChoiceField(queryset=Sprint.objects.filter())

    def __init__(self, proyecto, *args, **kwargs):
        super(AsignarSprintUSForm, self).__init__(*args, **kwargs)
        self.proyecto = proyecto
        sp = Sprint.objects.filter(proyecto = proyecto, estado = 'planificacion')
        self.fields['sprint'].queryset = sp

class AsignarFlujoUSForm(forms.Form):
    flujo = forms.ModelChoiceField(queryset=Flujo.objects.filter())

    def __init__(self, proyecto, *args, **kwargs):
        super(AsignarFlujoUSForm, self).__init__(*args, **kwargs)
        self.proyecto = proyecto
        fap = FlujoActividadProyecto.objects.filter(proyecto = proyecto)
        listFlujo = []
        for i in fap:
            if not i.flujo.id in listFlujo:
                listFlujo.append(i.flujo.id)
        self.fields['flujo'].queryset = Flujo.objects.filter(Q(id__in = listFlujo))

class CambiarEstadosUSForm(forms.Form):
    estadokanban = forms.CharField(widget=forms.Select(choices=ESTADO_KANBAN))

class CambiarActividadUSForm(forms.Form):
    actividad = forms.ModelChoiceField(queryset=Actividad.objects.filter())

    def __init__(self, us, *args, **kwargs):
        super(CambiarActividadUSForm, self).__init__(*args, **kwargs)
        self.us = us
        userhistory = UserHistory.objects.get(id = us)
        fap = FlujoActividadProyecto.objects.filter(proyecto = userhistory.proyecto,flujo = userhistory.flujo)
        listAct = []
        for i in fap:
            if not i.actividad.id in listAct:
                listAct.append(i.actividad.id)
        self.fields['actividad'].queryset = Actividad.objects.filter(Q(id__in = listAct))

class AdjuntoForm(forms.Form):
	archivo = forms.FileField(required = False, label='ADJUNTAR ARCHIVO')

class ReasignarSprintUSForm(forms.Form):
    horas = forms.IntegerField(label='HORAS')
    sprint = forms.ModelChoiceField(queryset=Sprint.objects.filter())

    def __init__(self, proyecto, *args, **kwargs):
        super(ReasignarSprintUSForm, self).__init__(*args, **kwargs)
        self.proyecto = proyecto
        sp = Sprint.objects.filter(proyecto = proyecto)
        self.fields['sprint'].queryset = sp
