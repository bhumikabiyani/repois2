# -*- coding: utf-8 -*-
import base64
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from SGPA.apps.usuario.forms import UsuariosForm
from django.core.mail import EmailMultiAlternatives # Enviamos HTML
from django.contrib.auth.models import User
import django
from SGPA.settings import URL_LOGIN
from django.contrib.auth import login,logout,authenticate
from django.http import HttpResponseRedirect, HttpResponse, Http404
# Paginacion en Django
from django.core.paginator import Paginator,EmptyPage,InvalidPage
from django.contrib.auth.decorators import login_required
from django.template import *
from django.contrib import*
from django.template.loader import get_template
from django.forms.formsets import formset_factory
from SGPA.apps.flujo.forms import *
from SGPA.apps.flujo.models import *
from SGPA.apps.flujo.helper import *
from SGPA.apps.actividades.forms import *

@login_required
def admin_flujo(request):
    """
    :param request:
    :return:
    Administracion de flujo"""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)

    #-------------------------------------------------------------------
    lista = Flujo.objects.filter().order_by('id')
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Flujo.objects.filter(Q(nombre__icontains = palabra) | Q(descripcion__icontains = palabra) | Q(usuario_creador__username__icontains = palabra)).order_by('id')
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
            return render_to_response('flujo/admin_flujo.html',{'lista':lista, 'form': form,
                                                        'user':user,
                                                        'pag': pag,
                                                        'ver_flujo':'ver flujo' in permisos,
							'crear_flujo':'crear flujo' in permisos
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
    return render_to_response('flujo/admin_flujo.html',{'lista':lista, 'form':form,
                                                            'user':user,
							    'pag': pag,
                                                            'ver_flujo':'ver flujo' in permisos,
							    'crear_flujo':'crear flujo' in permisos    							        
							})

@login_required
def crear_flujo(request):
    """Agrega un nuevo flujo"""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)

    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = FlujoForm(request.POST)  
        if form.is_valid():
            r = Flujo()
            r.nombre = form.cleaned_data['nombre']
            r.descripcion = form.cleaned_data['descripcion']
            r.fecHor_creacion = datetime.datetime.now()
            r.usuario_creador = user
            r.save()
            return HttpResponseRedirect("/flujos")
	    
    else:
        form = FlujoForm()
    return render_to_response('flujo/crear_flujo.html',{'form':form, 
                                                            'user':user,
                                                            'crear_flujo': 'crear flujo' in permisos
			      })

def visualizar_flujo(request, flujo_id):
        """Visualiza Flujos"""
        flujos = get_object_or_404(Flujo, id=flujo_id)
        user=  User.objects.get(username=request.user.username)
        permisos = get_permisos_sistema(user)
        lista = User.objects.all().order_by("id")
        ctx = {'lista':lista,
               'flujos':flujos, 
               'ver_flujo': 'ver flujo' in permisos,
               'crear_flujo': 'crear flujo' in permisos,
               'mod_flujo': 'modificar flujo' in permisos,
               'eliminar_flujo': 'eliminar flujo' in permisos,
               'asignar_actividades': 'asignar actividades' in permisos
	       }
	return render_to_response('flujo/verFlujo.html',ctx,context_instance=RequestContext(request))

def mod_flujo(request, flujo_id):
    """Modifica un Flujo"""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for i in roles:
       permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
       permisos.append(i.nombre)

    #-------------------------------------------------------------------
    actual = get_object_or_404(Flujo, id=flujo_id)
    if request.method == 'POST':
        form = ModFlujoForm(request.POST)
        if form.is_valid():
            actual.descripcion = form.cleaned_data['descripcion']
            actual.save()
            return HttpResponseRedirect("/verFlujo/ver&id=" + str(flujo_id))
    else:
        form = ModFlujoForm()
        form.fields['descripcion'].initial = actual.descripcion
    return render_to_response("flujo/mod_flujo.html", {'user':user, 
                                                           'form':form,
							   'flujo': actual,
                                                           'mod_flujo':'modificar flujo' in permisos
						     })

def borrar_flujo(request, flujo_id):
    """Elimina un flujo si no està asignado a un Proyecto"""
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for i in roles:
       permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
       permisos.append(i.nombre)

    #-------------------------------------------------------------------
    actual = get_object_or_404(Flujo, id=flujo_id)
    relacionados = ProyectoFlujo.objects.filter(flujo = actual).count()

    if request.method == 'POST':
        actual.delete()
        return HttpResponseRedirect("/flujos")
    else:
        if relacionados > 0:
             error = "El Flujo esta relacionado."
             return render_to_response("flujo/flujo_confirm_delete.html", {'mensaje': error,
                                                                               'flujo':actual,
                                                                               'user':user,
                                                                               'eliminar_flujo':'eliminar flujo' in permisos})
    return render_to_response("flujo/flujo_confirm_delete.html", {'flujo':actual,
                                                                      'user':user,
                                                                      'eliminar_flujo':'eliminar flujo' in permisos
								})

def asignar_actividades(request, flujo_id):
    """Asigna actividades a un flujo"""
    user = User.objects.get(username=request.user.username)
    permisos = get_permisos_sistema(user)
    flujo = get_object_or_404(Flujo, id=flujo_id)
    lista_actividades = FlujoActividad.objects.filter(flujo = flujo)
    if request.method == 'POST':
        form = AsignarActividadesForm(request.POST)
        if form.is_valid():
            lista_nueva = form.cleaned_data['actividades']
            for i in lista_actividades:
                i.delete()
            for i in lista_nueva:
                nuevo = FlujoActividad()
                nuevo.flujo = flujo
                nuevo.actividad = i
                nuevo.save()
            return HttpResponseRedirect("/verFlujo/ver&id=" + str(flujo_id))
    else:
        dict = {}
        for i in lista_actividades:
            print i.actividad
            dict[i.actividad.id] = True
        form = AsignarActividadesForm(initial = {'actividades': dict})
    return render_to_response("flujo/asignar_actividades.html", {'form':form, 'flujo':flujo, 'user':user, 'asignar_actividades': 'asignar actividades' in permisos
                                                                 })

