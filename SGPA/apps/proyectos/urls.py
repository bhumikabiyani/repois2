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
	url(r'^eliminarProyecto/del&id=(?P<proyecto_id>\d+)/$','borrar_proyecto',name='vista_delProyecto'),
    url(r'^eliminarMiembro/del&id=(?P<miembro_id>\d+)/$','borrar_miembro',name='vista_delMiembro'),
	url(r'^proyectos/flujos&id=(?P<rol_id>\d+)/$','admin_flujos',name='vista_flujos'),
	url(r'^asignarMiembro/proyecto&id=(?P<proyecto_id>\d+)/$','asignar_miembro',name='vista_miembros'),
    url(r'^asignarFlujo/proyecto&id=(?P<proyecto_id>\d+)/$','asignar_flujo',name='vista_asignarflujo'),
	url(r'^modificarMiembro/miembro&id=(?P<proyecto_id>\d+)/$','mod_miembro',name='vista_modMiembro'),
    url(r'^asignarActividadProy/flujo&id=(?P<flujo_id>\d+)&&proyecto&id=(?P<proyecto_id>\d+)/$','asignar_actividad_proy',name='vista_asignarActividadProy'),
    url(r'^verActividadesProy/flujo&id=(?P<flujo_id>\d+)&&proyecto&id=(?P<proyecto_id>\d+)/$', 'ver_actividades_proyecto', name='vista_actividades_proyecto'),
    url(r'^bajarActividadProy/flujo&id=(?P<flujo_id>\d+)&&actividad&id=(?P<actividad_id>\d+)&&proyecto&id=(?P<proyecto_id>\d+)/$','bajar_actividad_proyecto',name='vista_bajarActividadProyecto'),
    url(r'^subirActividadProy/flujo&id=(?P<flujo_id>\d+)&&actividad&id=(?P<actividad_id>\d+)&&proyecto&id=(?P<proyecto_id>\d+)/$','subir_actividad_proyecto',name='vista_subirActividadProyecto'),
    url(r'^verkanban/ver&id=(?P<proyecto_id>\d+)/$', 'visualizar_kanban', name='vista_kanban'),
    url(r'^verburn/ver&id=(?P<proyecto_id>\d+)&&sprint&id=(?P<sprint_id>\d+)/$', 'visualizar_burndownChart', name='vista_burn'),
    url(r'^reporte/$', 'reporte_pdf', name='vista_reportePdf'),
    url(r'^reporte1/ver&id=(?P<proyecto_id>\d+)/$', 'reporte1_pdf', name='vista_reporte1Pdf'),
    url(r'^reporte2/ver&id=(?P<proyecto_id>\d+)/$', 'reporte2_pdf', name='vista_reporte2Pdf'),
    url(r'^reporte3/ver&id=(?P<proyecto_id>\d+)/$', 'reporte3_pdf', name='vista_reporte3Pdf'),
    url(r'^reporte4/ver&id=(?P<proyecto_id>\d+)/$', 'reporte4_pdf', name='vista_reporte4Pdf'),
    url(r'^reporte5/ver&id=(?P<proyecto_id>\d+)/$', 'reporte5_pdf', name='vista_reporte5Pdf'),
    url(r'^reporte6/ver&id=(?P<proyecto_id>\d+)/$', 'reporte6_pdf', name='vista_reporte6Pdf'),
    url(r'^finalizarProyecto/proy&id=(?P<proyecto_id>\d+)/$', 'finalizar_proyecto', name='vista_finalizarProyecto')

)

