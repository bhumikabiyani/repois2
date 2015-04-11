# -*- coding: utf-8 -*-
from django.conf.urls import patterns,url
from django.conf.urls import *
from django.views.generic import *
from django.contrib.auth.models import User
from django.template import *
import os.path

from SGPA.apps.roles.forms import *
from SGPA.apps.roles.models import *
from SGPA.apps.roles.views import *

urlpatterns = patterns('SGPA.apps.proyectos.views',
	url(r'^proyectos/$', 'admin_proyectos', name='vista_adminP'),
	url(r'^verProyecto/ver&id=(?P<proyecto_id>\d+)/$', 'visualizar_proyectos', name='vista_proyectos'),
	url(r'^crearProyecto/$','crear_proyecto',name='vista_crearProyecto'),
	url(r'^modificarProyecto/mod&id=(?P<proyecto_id>\d+)/$','mod_proyecto',name='vista_modProyecto'),
	url(r'^eliminarProyecto/del&id=(?P<rol_id>\d+)/$','borrar_proyecto',name='vista_delProyecto'),
	url(r'^proyectos/flujos&id=(?P<rol_id>\d+)/$','admin_flujos',name='vista_flujos'),
	url(r'^asignarMiembro/proyecto&id=(?P<proyecto_id>\d+)/$','asignar_miembro',name='vista_miembros'),
    url(r'^asignarFlujo/proyecto&id=(?P<proyecto_id>\d+)/$','asignar_flujo',name='vista_asignarflujo'),
	url(r'^modificarMiembro/miembro&id=(?P<proyecto_id>\d+)/$','mod_miembro',name='vista_modMiembro')
)

