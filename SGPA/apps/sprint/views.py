# -*- coding: utf-8 -*-
import base64
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from SGPA.apps.usuario.forms import UsuariosForm
from django.core.mail import EmailMultiAlternatives  # Enviamos HTML
from django.contrib.auth.models import User
import django
from SGPA.settings import URL_LOGIN
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect, HttpResponse, Http404
# Paginacion en Django
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.auth.decorators import login_required
from django.template import *
from django.contrib import *
from django.template.loader import get_template
from django.forms.formsets import formset_factory
from SGPA.apps.proyectos.forms import *
from SGPA.apps.proyectos.models import *
from SGPA.apps.proyectos.helper import *
from SGPA.apps.sprint.forms import *

@login_required
def admin_sprint(request,proyecto_id):
    """Administracion general de sprint"""
    user = User.objects.get(username=request.user.username)
    #permisos = get_permisos_sistema(user)
    proyecto=get_object_or_404(Proyecto, id=proyecto_id)
    lista =  Sprint.objects.filter(proyecto=proyecto_id).order_by('id')
    #listaitem = Item.objects.filter(proyecto=proyecto_id, habilitado=True).order_by('id')
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Sprint.objects.filter(
                Q(nombre=palabra)).order_by('id')
            paginas = form.cleaned_data['paginas']
            request.session['nro_items'] = paginas
            paginator = Paginator(lista, int(paginas))
            try:
                page = int(request.GET.get('page', '1'))
            except ValueError:
                page = 1
            try:
                pag = paginator.page(page)
            except (EmptyPage, InvalidPage):
                pag = paginator.page(paginator.num_pages)
            return render_to_response('sprint/sprint.html', {'pag': pag,
                                                                   'form': form,
                                                                   'lista': lista,
                                                                   'user': user,
                                                                   'proyecto' : proyecto
                                                                   #'ver_proyectos': 'ver proyectos' in permisos,
                                                                   #'crear_proyecto': 'crear proyecto' in permisos,
                                                                   })
    else:
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        if not 'nro_items' in request.session:
            request.session['nro_items'] = 5
        paginas = request.session['nro_items']
        paginator = Paginator(lista, int(paginas))
        try:
            pag = paginator.page(page)
        except (EmptyPage, InvalidPage):
            pag = paginator.page(paginator.num_pages)
        form = FilterForm(initial={'paginas': paginas})
    return render_to_response('sprint/sprint.html', {'lista': lista, 'form': form,
                                                           'user': user,
                                                           'pag': pag,
                                                           'proyecto' : proyecto
                                                           #'ver_proyectos': 'ver proyectos' in permisos,
                                                           #'crear_proyecto': 'crear proyecto' in permisos,
                                                           })
@login_required
def crear_sprint(request, proyecto_id):
    """Administracion general de sprint"""

    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    #roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    #permisos_obj = []
    #for i in roles:
     #   permisos_obj.extend(i.rol.permisos.all())
    #permisos = []
    #for i in permisos_obj:
     #   permisos.append(i.nombre)
    #print permisos
    #-------------------------------------------------------------------
    proyecto = get_object_or_404(Proyecto, id = proyecto_id)
    if proyecto.cantidad >  proyecto.cant_actual:
    	if request.method == 'POST':

		form = SprintForm(proyecto_id, request.POST)
        	if form.is_valid():
		   #tf= TipoItemFase()
		   #tf.cant=0
     	     	   r = Sprint()
            	   r.nombre = form.cleaned_data['nombre']
                   r.descripcion = form.cleaned_data['descripcion']
                   r.fecha_inicio = form.cleaned_data['fecha_inicio']
                   r.fecha_fin = form.cleaned_data['fecha_fin']
              #     r.tipo_item = form.cleaned_data['tipo_item']
                 #r.num_secuencia =
		# p.r.cant_actual = form.cleaned_data['cant_actual']
                   r.proyecto = proyecto
                   r.save()
		   #tf.fase=r
		   #tf.tipo_item=r.tipo_item
		   #tf.cant = tf.cant + 1
		   #tf.save()
                   #proyecto.cant_actual = proyecto.cant_actual + 1
                 #p.cant_actual = form.cleaned_data['cant_actual']
                   #proyecto.save()
		   return HttpResponseRedirect("/sprint/sprint&id="+ str(proyecto_id))
    	else:
        		form = SprintForm(proyecto_id)
			#p.cant_actual = p.cant_actual + 1
                       # p.cant_actual = form.cleaned_data['cant_actual']
			#p.save()
    	return render_to_response('sprint/crear_sprint.html', {'form':form,
                                                            'user':user,
                                                            'proyecto' : proyecto
                                                            #'crear_sprint': 'crear sprint'
				})
    return HttpResponseRedirect("/sprint/sprint&id="+ str(proyecto_id))

def visualizar_sprint(request, sprint_id):
        """Visualiza Sprint"""
        sprint = get_object_or_404(Sprint, id=sprint_id)
        user=  User.objects.get(username=request.user.username)
        #permisos = get_permisos_sistema(user)
        lista = User.objects.all().order_by("id")
        ctx = {'lista':lista,
               'sprint':sprint,
               #'ver_flujo': 'ver flujo' in permisos,
               #'crear_flujo': 'crear flujo' in permisos,
               #'mod_flujo': 'modificar flujo' in permisos,
               #'eliminar_flujo': 'eliminar flujo' in permisos
	       }
	return render_to_response('sprint/verSprint.html',ctx,context_instance=RequestContext(request))

@login_required
def mod_sprint(request, sprint_id):
    user = User.objects.get(username=request.user.username)
    f = get_object_or_404( Sprint, id = sprint_id)
    #Validacion de permisos---------------------------------------------
    #roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    #permisos_obj = []
    #for i in roles:
    #    permisos_obj.extend(i.rol.permisos.all())
    #permisos = []
    #for i in permisos_obj:
    #    permisos.append(i.nombre)
    #print permisos
    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = ModSprintForm(f,request.POST, request.FILES)
        if form.is_valid():
            f.nombre = form.cleaned_data['nombre']
            f.save()
            return HttpResponseRedirect("/verSprint/ver&id=" + str(sprint_id))
    else:
        form = ModSprintForm(f, initial = {'nombre': f.nombre})
    return render_to_response('sprint/mod_sprint.html',{'form':form,
                                                        'user':user,
                                                        'sprint': f,
                                                        #'mod_fase':'Modificar fase' in permisos
                                                         })

def borrar_sprint(request, sprint_id):
    """Elimina un flujo si no està asignado a un Proyecto"""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    #roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    #permisos_obj = []
    #for i in roles:
    #   permisos_obj.extend(i.rol.permisos.all())
    #permisos = []
    #for i in permisos_obj:
    #   permisos.append(i.nombre)

    #-------------------------------------------------------------------
    actual = get_object_or_404(Sprint, id=sprint_id)
    #relacionados = ProyectoFlujo.objects.filter(flujo = actual).count()

    if request.method == 'POST':
        actual.delete()
        return HttpResponseRedirect("/sprint/sprint&id=" + str(actual.proyecto_id))
    else:
        if actual.proyecto.estado != 1:
             error = "El Proyecto al cual esta relacionado se ha Iniciado"
             return render_to_response("sprint/sprint_confirm_delete.html", {'mensaje': error,
                                                                            'sprint':actual,
                                                                            'user':user,
                                                                            #'eliminar_flujo':'eliminar flujo' in permisos
                                                                             })
    return render_to_response("sprint/sprint_confirm_delete.html", {'sprint':actual,
                                                                  'user':user,
                                                                  #'eliminar_flujo':'eliminar flujo' in permisos
								})
