# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from SGPA.apps.home.forms import LoginForm
from django.core.mail import EmailMultiAlternatives # Enviamos HTML
from django.contrib.auth.models import User
import django
from SGPA.settings import URL_LOGIN
from django.contrib.auth import login,logout,authenticate
from django.http import HttpResponseRedirect, HttpResponse
# Paginacion en Django
from django.core.paginator import Paginator,EmptyPage,InvalidPage
from django.contrib.auth.decorators import login_required

# Create your views here.
def index_view(request):
	return render_to_response('home/index.html',context_instance=RequestContext(request))

def login_view(request):
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
				usuario = authenticate(username=username,password=password)
				if usuario is not None and usuario.is_active:
					login(request,usuario)
					return HttpResponseRedirect(next)
				else:
					mensaje = "El nombre del Usuario o la Contraseña son incorrectos"
		next = request.REQUEST.get('next')
		form = LoginForm()
		ctx = {'form':form,'mensaje':mensaje,'next':next}
		return render_to_response('home/login.html',ctx,context_instance=RequestContext(request))

def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')

#def principal_view(request):
#	logout(request)
#	return render_to_response('home/principal.html')

