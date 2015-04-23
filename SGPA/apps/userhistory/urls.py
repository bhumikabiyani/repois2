# -*- coding: utf-8 -*-
from django.conf.urls import *


urlpatterns = patterns('SGPA.apps.userhistory.views',
	url(r'^proyectos/$', 'admin_proyectos', name='vista_adminP'),
	#url(r'^verProyecto/ver&id=(?P<proyecto_id>\d+)/$', 'visualizar_proyectos', name='vista_proyectos'),
	#url(r'^crearProyecto/$','crear_proyecto',name='vista_crearProyecto'),
	#url(r'^modificarProyecto/mod&id=(?P<proyecto_id>\d+)/$','mod_proyecto',name='vista_modProyecto'),
	#url(r'^eliminarProyecto/del&id=(?P<proyecto_id>\d+)/$','borrar_proyecto',name='vista_delProyecto'),
    #url(r'^eliminarMiembro/del&id=(?P<miembro_id>\d+)/$','borrar_miembro',name='vista_delMiembro'),
	#url(r'^proyectos/flujos&id=(?P<rol_id>\d+)/$','admin_flujos',name='vista_flujos'),
	#url(r'^asignarMiembro/proyecto&id=(?P<proyecto_id>\d+)/$','asignar_miembro',name='vista_miembros'),
    #url(r'^asignarFlujo/proyecto&id=(?P<proyecto_id>\d+)/$','asignar_flujo',name='vista_asignarflujo'),
	#url(r'^modificarMiembro/miembro&id=(?P<proyecto_id>\d+)/$','mod_miembro',name='vista_modMiembro')
)
