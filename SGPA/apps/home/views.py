# -*- coding: utf-8 -*-
from random import choice
import string
from django.shortcuts import render_to_response
from django.template import RequestContext
from SGPA.apps.home.forms import LoginForm
from SGPA.apps.home.forms import RecuperarContrasenaForm
from django.core.mail import EmailMultiAlternatives  # Enviamos HTML
from django.contrib.auth.models import User
import django
from SGPA.settings import URL_LOGIN
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect, HttpResponse
# Paginacion en Django
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from SGPA.apps.usuario.forms import *


# Create your views here.
def index_view(request):
    """
    Muestra la Página de Inicio del Sistema
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :return: index.html, pagina principal
    """
    return render_to_response('home/index.html', context_instance=RequestContext(request))

def login_view(request):
    """
    Vista de Inicio de Sesion
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :return:login.html, pagina para inicio de Sesion
    """
    mensaje = ""
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        if request.method == "POST":
            form = LoginForm(request.POST)
            if form.is_valid():
                next = request.POST['next']
                username = form.cleaned_data['Nombre']
                password = form.cleaned_data['Contrasena']
                usuario = authenticate(username=username, password=password)
                if usuario is not None and usuario.is_active:
                    login(request, usuario)
                    return HttpResponseRedirect(next)
                else:
                    mensaje = "El nombre del Usuario o la Contraseña son incorrectos"
        next = request.REQUEST.get('next')
        form = LoginForm()
        ctx = {'form': form, 'mensaje': mensaje, 'next': next}
        return render_to_response('home/login.html', ctx, context_instance=RequestContext(request))


def logout_view(request):
    """Vista de logout"""
    logout(request)
    return HttpResponseRedirect('/')


def recuperarcontrasena_view(request):
    """Vista para recuperar contraseña"""
    if request.method == 'POST':
        form = RecuperarContrasenaForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['Correo']
            password = generar_nuevo_pass(request,correo)
            contenido = render_to_string('mailing/recuperacion_password.html',{'pass': password})
            correo = EmailMessage('Restablecimiento de Pass de SGPA', contenido, to=[form.cleaned_data['Correo']])
            correo.content_subtype = "html"
            correo.send()
            return HttpResponseRedirect('/')
    else:
        form = RecuperarContrasenaForm()
        ctx = {'form': form}
        return render_to_response('home/recuperarcontrasena.html', ctx, context_instance=RequestContext(request))

def generar_nuevo_pass(request, correo):
    """
    Metodo que genera el nuevo pass para el usuario.
    """
    if correo is not None:
        user = User.objects.get(email=correo)
        password = ''.join([choice(string.letters
                                   + string.digits) for i in range(10)])
        user.password = make_password(password)
        user.save()
        return str('Usuario: '+user.username+'\nPassword: '+password)
    return None
