# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from SGPA.apps.usuario.models import *
from SGPA.apps.usuario.helper import *
import datetime

class FilterForm(forms.Form):
    filtro = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')
    
class FilterForm2(forms.Form):
    filtro1 = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas1 = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')
    filtro2 = forms.CharField(max_length = 30, label = 'BUSCAR', required=False)
    paginas2 = forms.CharField(max_length=2, widget=forms.Select(choices=(('5','5'),('10','10'),('15','15'),('20','20'))), label='MOSTRAR')

class RolesForm(forms.Form):
	nombre = forms.CharField(max_length=50, label='NOMBRE')
	descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='DESCRIPCIÓN')
	categoria = forms.CharField(max_length=1, widget=forms.Select(choices=CATEGORY_CHOICES), label='ELIJA UNA CATEGORIA')
	#permisos = forms.ModelMultipleChoiceField(queryset = None, widget=forms.CheckboxSelectMultiple, required = False)
		
	def clean_nombre(self):
		if 'nombre' in self.cleaned_data:
			roles = Rol.objects.all()
			nombre = self.cleaned_data['nombre']
			for i in roles: 
				if nombre == i.nombre:
					raise forms.ValidationError('Ya existe ese nombre de rol. Elija otro')
			return nombre

class ModRolesForm(forms.Form):
	descripcion = forms.CharField(widget=forms.Textarea(), required=False, label='DESCRIPCIÓN')

class AsignarRolesForm(forms.Form):
	roles = forms.ModelMultipleChoiceField(queryset = None, widget = forms.CheckboxSelectMultiple, label = 'ROLES DISPONIBLES', required=False)
	
	def __init__(self, cat, *args, **kwargs):
		super(AsignarRolesForm, self).__init__(*args, **kwargs)
		self.fields['roles'].queryset = Rol.objects.filter(categoria = cat)

class PermisosForm(forms.Form):
	permisos = forms.ModelMultipleChoiceField(queryset = Permiso.objects.filter(categoria = 1), widget = forms.CheckboxSelectMultiple, required = False)

class UsuarioProyectoForm(forms.Form):
    usuario = forms.ModelChoiceField(queryset = User.objects.all())
    roles = forms.ModelMultipleChoiceField(queryset = Rol.objects.filter(categoria=2).exclude(id=2), widget = forms.CheckboxSelectMultiple, required=False)
    #proyecto = Proyecto()
    
    def __init__(self, proyecto, *args, **kwargs):
        super(UsuarioProyectoForm, self).__init__(*args, **kwargs)
        self.fields['usuario'].queryset = User.objects.filter(~Q(id = proyecto.usuario_lider.id))


    def clean_usuario(self):
        if 'usuario' in self.cleaned_data:
            usuarios_existentes = UsuarioRolProyecto.objects.filter(id = self.proyecto.id)
            for i in usuarios_existentes:
                if(usuarios_existentes.usuario == form.clean_data['usuario']):
                    raise forms.ValidationError('Ya existe este usuario')
            return self.cleaned_data['usuario']

class PermisosProyectoForm(forms.Form):
	permisos = forms.ModelMultipleChoiceField(queryset = Permiso.objects.filter(categoria = 2), widget = forms.CheckboxSelectMultiple, required = False)
