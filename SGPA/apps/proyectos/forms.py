# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from SGPA.apps.usuario.models import *
from SGPA.apps.usuario.helper import *
import datetime
import django
django.setup()
from datetimewidget.widgets import DateTimeWidget, DateWidget, TimeWidget

class FilterForm(forms.Form):
    filtro = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')

class FilterForm2(forms.Form):
    filtro1 = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas1 = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')
    filtro2 = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas2 = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')

class ProyectoForm(forms.Form):
    nombrelargo = forms.CharField(max_length=50, label='NOMBRE')
    descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='DESCRIPCIÓN')
    fecha_inicio = forms.DateField(widget=DateWidget(usel10n=True, bootstrap_version=2),label='FECHA DE INICIO')
    fecha_fin = forms.DateField(widget=DateWidget(usel10n=True, bootstrap_version=2),label='FECHA DE FIN')
    usuario_lider = forms.ModelChoiceField(queryset=User.objects.all(), label= 'USUARIO LIDER')
    # usuario_lider = forms.CharField(widget=forms.Select(choices=User.objects.all().values_list('id','username')))
    cantidad = forms.IntegerField(label='HORAS')
    #permisos = forms.ModelMultipleChoiceField(queryset = None, widget=forms.CheckboxSelectMultiple, required = False)
    estado = forms.CharField(max_length=1, widget=forms.Select(choices=PROJECT_STATUS_CHOICES), label = 'ESTADO')

    class Meta:
        model = Proyecto
        widgets = {
            'date': DateWidget(attrs={'id':"fecha_inicio"}, usel10n = True, bootstrap_version=2)
        }

    def clean_fecha_fin(self):
        if 'fecha_fin' in self.cleaned_data:
            fecha_fin = self.cleaned_data['fecha_fin']
            fecha_inicio = self.cleaned_data['fecha_inicio']
            if fecha_fin < fecha_inicio:
                raise forms.ValidationError('La fecha de fin es menor a la fecha de inicio.')
            return fecha_fin

    def clean_nombrelargo(self):
		if 'nombrelargo' in self.cleaned_data:
			proyectos = Proyecto.objects.all()
			nombrelargo = self.cleaned_data['nombrelargo']
			for proy in proyectos:
				if nombrelargo == proy.nombrelargo:
					raise forms.ValidationError('Ya existe ese nombre de proyecto. Elija otro')
			return nombrelargo

class ModProyectoForm(forms.Form):
    descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='DESCRIPCIÓN')
    fecha_inicio = forms.DateField(label='INICIO')
    fecha_fin = forms.DateField(label='FIN')
    # usuario_lider = forms.CharField(widget=forms.Select(choices=User.objects.all().values_list('id','username')))
    usuario_lider = forms.ModelChoiceField(queryset=User.objects.all())
    cantidad = forms.IntegerField(label='HORAS')
    estado = forms.CharField(max_length=1, widget=forms.Select(choices=PROJECT_STATUS_CHOICES_MOD), label = 'ESTADO')
    # def __init__(self,  *args, **kwargs):
    #     super(ModProyectoForm, self).__init__(*args, **kwargs)
    #     # self.fields['usuario_lider'].queryset = User.objects.all().values_list('id','username')
    #     self.fields['usuario_lider'].queryset = User.objects.none().values_list('id','username')
    #     print 'hola'

class NuevoMiembroForm(forms.Form):
    lider = 0
    usuario = forms.ModelChoiceField(queryset=User.objects.filter().exclude(id=lider))
    print  lider
    # usuario = forms.CharField(widget=forms.Select(choices=User.objects.all().values_list('id','username')))
    rol = forms.ModelChoiceField(queryset=Rol.objects.filter(categoria=2).exclude(nombre='team leader'))
    horas = forms.IntegerField(label='Horas semanales')
    # rol = forms.CharField(widget=forms.Select(choices=Rol.objects.filter(categoria = 2).values_list('id','descripcion')))
    proyecto = Proyecto()


    def __init__(self, proyecto, *args, **kwargs):
        super(NuevoMiembroForm, self).__init__(*args, **kwargs)
        self.proyecto = proyecto
        rol = Rol.objects.get(nombre = "team leader")
        if rol:
            urp = UsuarioRolProyecto.objects.get(rol = rol, proyecto = proyecto)
        self.lider = User.objects.get(id = urp.usuario.id)
        print self.lider
        self.fields['usuario'].queryset = User.objects.filter().exclude(id = self.lider.id)

    def clean_usuario(self):
		if 'usuario' in self.cleaned_data:
			return self.cleaned_data['usuario']

    def clean_rol(self):
        if 'rol' in self.cleaned_data and 'usuario' in self.cleaned_data:
            proy = Proyecto.objects.get(nombrelargo = self.proyecto)
            userRolProy = UsuarioRolProyecto.objects.filter(proyecto=proy)
            usuario = User.objects.get(username = self.cleaned_data['usuario'])
            rol = Rol.objects.get(nombre = self.cleaned_data['rol'])
            if self.cleaned_data['rol'] == 'Cliente':
                self.cleaned_data['horas'] = 0
            for i in userRolProy:
                if rol == i.rol and usuario == i.usuario and proy == i.proyecto:
                    raise forms.ValidationError('El usuario ' + usuario.username + ' ya tiene este rol')
            return self.cleaned_data['rol']

    def clean_horas(self):
        if 'rol' in self.cleaned_data and 'horas' in self.cleaned_data:
            rol = Rol.objects.get(nombre = self.cleaned_data['rol'])
            if rol.nombre == 'Cliente' and self.cleaned_data['horas'] != 0:
                raise forms.ValidationError('El cliente no debe tener horas ')
            return self.cleaned_data['horas']

class AsignarFlujoForm(forms.Form):
	flujos = forms.ModelMultipleChoiceField(queryset = Flujo.objects.all(), widget = forms.CheckboxSelectMultiple, required = False)

class AsignarActividadesProyForm(forms.Form):
    actividades = forms.ModelMultipleChoiceField(queryset = None, widget = forms.CheckboxSelectMultiple, label = 'ACTIVIDADES', required=False)

    def __init__(self, *args, **kwargs):
        super(AsignarActividadesProyForm, self).__init__(*args, **kwargs)
        self.fields['actividades'].queryset = Actividad.objects.all()

class AsignarEncargadoUSForm(forms.Form):
    encargado = forms.ModelChoiceField(queryset=User.objects.filter())
