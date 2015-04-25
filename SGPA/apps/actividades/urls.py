# -*- coding: utf-8 -*-
from django.conf.urls import patterns,url
from django.conf.urls import *
from django.views.generic import *
from django.contrib.auth.models import User
from django.template import *
import os.path

from SGPA.apps.flujo.forms import *
from SGPA.apps.flujo.models import *
from SGPA.apps.flujo.views import *

urlpatterns = patterns('SGPA.apps.actividades.views',
	url(r'^actividades/$', 'admin_actividades', name='vista_admiA'),
	url(r'^verActividad/ver&id=(?P<actividad_id>\d+)/$', 'visualizar_actividad', name='vista_actividad'),
	url(r'^crearActividad/$','crear_actividad',name='vista_crearActividad'),
	url(r'^modificarActividad/mod&id=(?P<actividad_id>\d+)/$','mod_actividad',name='vista_modActividad'),
	url(r'^eliminarActividad/del&id=(?P<actividad_id>\d+)/$','borrar_actividad',name='vista_delActividad')
)


