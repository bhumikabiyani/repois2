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
    url(r'^verLogUserHistory/ver&id=(?P<userhistory_id>\d+)/$', 'ver_log_user_history', name='vista_logUserHistory')
)