from django.shortcuts import render_to_response
from django.template import RequestContext
from SGPA.apps.usuario.forms import UsuariosForm
from django.core.mail import EmailMultiAlternatives # Enviamos HTML
from django.contrib.auth.models import User
import django
from SGPA.settings import URL_LOGIN
from django.contrib.auth import login,logout,authenticate
from django.http import HttpResponseRedirect, HttpResponse
# Paginacion en Django
from django.core.paginator import Paginator,EmptyPage,InvalidPage
from django.contrib.auth.decorators import login_required

def crearUsuario_view(request):
	form = UsuariosForm()
	if request.method == "POST":
		form = UsuariosForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			first_name = form.cleaned_data['first_name']
                        last_name = form.cleaned_data['last_name']
			email = form.cleaned_data['email']
			password_one = form.cleaned_data['password_one']
			password_two = form.cleaned_data['password_two']
			u = User.objects.create_user(username=username,email=email,password=password_one)
			u.save() # Guardar el objeto
			return render_to_response('usuario/adminUsuario',context_instance=RequestContext(request))
		else:
			ctx = {'form':form}
			return 	render_to_response('usuario/crearUsuario.html',ctx,context_instance=RequestContext(request))
	ctx = {'form':form}
	return render_to_response('usuario/crearUsuario.html',ctx,context_instance=RequestContext(request))
