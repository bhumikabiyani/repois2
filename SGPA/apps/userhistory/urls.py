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

urlpatterns = patterns('SGPA.apps.userhistory.views',
	url(r'^userHistory/proyecto&id=(?P<proyecto_id>\d+)/$', 'admin_user_history', name='vista_adminUH'),
    url(r'^verUserHistory/ver&id=(?P<userhistory_id>\d+)/$', 'visualizar_user_history', name='vista_userHistory'),
    url(r'^modificarUserHistory/mod&id=(?P<userhistory_id>\d+)/$','mod_user_history',name='vista_moduserHistory'),
    url(r'^eliminarUserHistory/del&id=(?P<userhistory_id>\d+)/$','borrar_user_history',name='vista_delUserHistory'),
    url(r'^crearUserHistory/proyecto&id=(?P<proyecto_id>\d+)/$','crear_user_history',name='vista_crearUserHistory'),
    url(r'^verLogUserHistory/ver&id=(?P<userhistory_id>\d+)/$', 'ver_log_user_history', name='vista_logUserHistory'),
    url(r'^addComment/comment&id=(?P<userhistory_id>\d+)/$', 'agregar_comentario', name='vista_addCommentUserHistory'),
    url(r'^encargadoUserHistory/us&id=(?P<userhistory_id>\d+)/$','asignar_encargado_userhistory',name='vista_asignarEncargadoUS'),
    url(r'^sprintUserHistory/us&id=(?P<userhistory_id>\d+)/$','asignar_sprint_userhistory',name='vista_asignarSprintUS'),
    url(r'^flujoUserHistory/us&id=(?P<userhistory_id>\d+)/$','asignar_flujo_userhistory',name='vista_asignarFlujoUS'),
    url(r'^archivosAdjuntos/adjuntos&id=(?P<userhistory_id>\d+)/$', 'add_adjunto', name='vista_archivosAdjuntosUserHistory'),
    url(r'^desAdjuntos/adjunto&id=(?P<userhistory_id>\d+)&&archivo&id=(?P<arch_id>\d+)/$', 'retornar_archivo', name='vista_descargarAdjuntosUserHistory'),
    url(r'^cambiarEstados/us&id=(?P<userhistory_id>\d+)&&ultimo&estado=(?P<ultimo_estado>\d+)/$', 'cambiar_estados', name='vista_cambiarEstado'),
    url(r'^cambiarActividad/us&id=(?P<userhistory_id>\d+)/$', 'cambiar_actividad', name='vista_cambiarActividad'),
    url(r'^encargadoUserHistory/us&id=(?P<userhistory_id>\d+)/$','asignar_encargado_userhistory',name='vista_asignarEncargadoUS'),
    url(r'^finalizarUS/us&id=(?P<userhistory_id>\d+)/$', 'finalizar_userhistory', name='vista_finalizarUS'),
    url(r'^reasignar/us&id=(?P<userhistory_id>\d+)/$','reasignar_sprint_userhistory',name='vista_reasignarSprintUS')
)