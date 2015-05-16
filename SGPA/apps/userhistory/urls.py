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
    url(r'^archivosAdjuntos/adjuntos&id=(?P<userhistory_id>\d+)/$', 'archivos_adjuntos', name='vista_archivosAdjuntosUserHistory'),
    url(r'^encargadoUserHistory/us&id=(?P<userhistory_id>\d+)/$','asignar_encargado_userhistory',name='vista_asignarEncargadoUS')
)