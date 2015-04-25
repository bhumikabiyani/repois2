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
from SGPA.apps.actividades.forms import *
from SGPA.apps.actividades.models import *
from SGPA.apps.actividades.helper import *

@login_required
def admin_actividades(request):
    """
    Vista para la Administración de actividades
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :return: admin_actividades.html, pagina en la cual se trabaja con las actividades
    """
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
    lista = Actividad.objects.filter().order_by('id')
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Actividad.objects.filter(Q(nombre__icontains = palabra) | Q(descripcion__icontains = palabra) | Q(usuario_creador__username__icontains = palabra)).order_by('id')
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
            return render_to_response('actividades/admin_actividades.html',{'lista':lista, 'form': form,
                                                        'user':user,
                                                        'pag': pag,
                                                        'ver_actividades':'ver actividades' in permisos,
							'crear_actividades':'crear actividades' in permisos
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
    return render_to_response('actividades/admin_actividades.html',{'lista':lista, 'form':form,
                                                            'user':user,
                                                            'pag': pag,
                                                            'ver_actividades':'ver actividades' in permisos,
                                                            'crear_actividades':'crear actividades' in permisos
							})

@login_required
def crear_actividad(request):
    """
    Vista para agregar una nueva actividad
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :return: crear_actividad.html, pagina en la cual se crea la actividad
    """
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
        form = ActividadForm(request.POST)
        if form.is_valid():
            r = Actividad()
            r.nombre = form.cleaned_data['nombre']
            r.descripcion = form.cleaned_data['descripcion']
            r.fecHor_creacion = datetime.datetime.now()
            r.usuario_creador = user
            r.save()
            return HttpResponseRedirect("/actividades")
	    
    else:
        form = ActividadForm()
    return render_to_response('actividades/crear_actividad.html',{'form':form,
                                                            'user':user,
                                                            'crear_actividades': 'crear actividades' in permisos
			      })

def visualizar_actividad(request, actividad_id):
        """
        Metodo para visualizar Actividad
        :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
        :param actividad_id: id de la actividad que se desea actualizar
        :return: verActividad.html,página en el cual se visualiza la actividad
        """
        actividades = get_object_or_404(Actividad, id=actividad_id)
        user=  User.objects.get(username=request.user.username)
        permisos = get_permisos_sistema(user)
        lista = User.objects.all().order_by("id")
        ctx = {'lista':lista,
               'actividades':actividades,
               'ver_actividades': 'ver actividades' in permisos,
               'crear_actividades': 'crear actividades' in permisos,
               'mod_actividad': 'modificar actividad' in permisos,
               'eliminar_actividad': 'eliminar actividad' in permisos
	       }
	return render_to_response('actividades/verActividad.html',ctx,context_instance=RequestContext(request))

def mod_actividad(request, actividad_id):
    """
    Metodo que modifica una actividad
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param actividad_id: id de la actividad que se desea modificar
    :return:mod_actividad.htm, pagina en la cual se modifica la actividad
    """
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
    actual = get_object_or_404(Actividad, id=actividad_id)
    if request.method == 'POST':
        form = ModActividadForm(request.POST)
        if form.is_valid():
            actual.descripcion = form.cleaned_data['descripcion']
            actual.save()
            return HttpResponseRedirect("/verActividad/ver&id=" + str(actividad_id))
    else:
        form = ModActividadForm()
        form.fields['descripcion'].initial = actual.descripcion
    return render_to_response("actividades/mod_actividad.html", {'user':user,
                                                           'form':form,
                                                           'actividad': actual,
                                                           'mod_actividad':'modificar actividad' in permisos
						     })

def borrar_actividad(request, actividad_id):
    """
    Metodo que Elimina una actividad
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param actividad_id: id de la actividad que se desea eliminar
    :return:actividad_confirm_delete.html, pagina en la cual se eliminará la actividad
    """
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
    actual = get_object_or_404(Actividad, id=actividad_id)
    relacionados = FlujoActividad.objects.filter(actividad = actual).count()

    if request.method == 'POST':
        actual.delete()
        return HttpResponseRedirect("/actividades")
    else:
        if relacionados > 0:
             error = "La actividad esta relacionada."
             return render_to_response("actividades/actividad_confirm_delete.html", {'mensaje': error,
                                                                               'actividad':actual,
                                                                               'user':user,
                                                                               'eliminar_actividad':'eliminar actividad' in permisos})
    return render_to_response("actividades/actividad_confirm_delete.html", {'actividad':actual,
                                                                      'user':user,
                                                                      'eliminar_actividad':'eliminar actividad' in permisos
								})
