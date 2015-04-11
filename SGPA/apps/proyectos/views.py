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


@login_required
def admin_proyectos(request):
    """Administracion de Proyectos"""
    user = User.objects.get(username=request.user.username)
    permisos = get_permisos_sistema(user)
    lista = Proyecto.objects.filter().order_by('id')
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Proyecto.objects.filter(
                Q(nombrelargo__icontains=palabra) | Q(descripcion__icontains=palabra)).order_by('id')
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
            return render_to_response('proyectos/proyectos.html', {'pag': pag,
                                                                   'form': form,
                                                                   'lista': lista,
                                                                   'user': user,
                                                                   'ver_proyectos': 'ver proyectos' in permisos,
                                                                   'crear_proyecto': 'crear proyecto' in permisos,
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
    return render_to_response('proyectos/proyectos.html', {'lista': lista, 'form': form,
                                                           'user': user,
                                                           'pag': pag,
                                                           'ver_proyectos': 'ver proyectos' in permisos,
                                                           'crear_proyecto': 'crear proyecto' in permisos,
                                                           })


@login_required
def crear_proyecto(request):
    """Agrega un nuevo proyecto"""
    user = User.objects.get(username=request.user.username)
    # Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario=user).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)

    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proy = Proyecto()
            proy.nombrelargo = form.cleaned_data['nombrelargo']
            proy.descripcion = form.cleaned_data['descripcion']
            # proy.fecHor_creacion = datetime.datetime.now()
            # proy.usuario_creador = user
            userLider = User.objects.get(id=form.cleaned_data['usuario_lider'])
            proy.usuario_lider = userLider
            proy.fecha_inicio = form.cleaned_data['fecha_inicio']
            proy.fecha_fin = form.cleaned_data['fecha_fin']
            proy.cantidad = form.cleaned_data['cantidad']
            proy.estado = 1
            proy.save()
            urp = UsuarioRolProyecto()
            urp.usuario = userLider
            rol = Rol.objects.get(id=2)
            urp.rol = rol
            urp.proyecto = proy
            urp.save()
        return HttpResponseRedirect("/proyectos")
    else:
        form = ProyectoForm()
    return render_to_response('proyectos/crear_proyecto.html', {'form': form,
                                                                'user': user,
                                                                'crear_proyecto': 'crear proyecto' in permisos
                                                                })


def visualizar_proyectos(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    status = ""
    if proyecto.estado == 1:
        status = "Pendiente"
    elif proyecto.estado == 2:
        status = "Iniciado"
    elif proyecto.estado == 3:
        status = "Terminado"
    else:
        status = "Anulado"
    user = User.objects.get(username=request.user.username)
    userRolProy = UsuarioRolProyecto.objects.filter(proyecto=proyecto_id)
    permisosSys = get_permisos_sistema(user)
    roles = UsuarioRolProyecto.objects.filter(usuario=user, proyecto=proyecto_id).only('rol')
    flujos = ProyectoFlujo.objects.filter(proyecto=proyecto_id)
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisosProy = []
    for i in permisos_obj:
        permisosProy.append(i.nombre)
    print permisosProy
    lista = User.objects.all().order_by("id")
    ctx = {'lista': lista,
           'proyecto': proyecto,
           'status': status,
           'miembros': userRolProy,
           'flujos': flujos,
           'ver_proyectos': 'ver proyectos' in permisosSys,
           'crear_proyecto': 'crear proyecto' in permisosSys,
           'mod_proyecto': 'modificar proyecto' in permisosProy,
           'eliminar_proyecto': 'eliminar proyecto' in permisosProy,
           'asignar_miembros': 'asignar miembros' in permisosProy,
           'asignar_flujo' : 'asignar flujo' in permisosProy
           }
    return render_to_response('proyectos/verProyecto.html', ctx, context_instance=RequestContext(request))


def mod_proyecto(request, proyecto_id):
    user = User.objects.get(username=request.user.username)
    # Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario=user).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)

    #-------------------------------------------------------------------
    actual = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        form = ModProyectoForm(request.POST)
        if form.is_valid():
            actual.descripcion = form.cleaned_data['descripcion']
            actual.fecha_inicio = form.cleaned_data['fecha_inicio']
            actual.fecha_fin = form.cleaned_data['fecha_fin']
            actual.estado = form.cleaned_data['estado']
            actual.cantidad = form.cleaned_data['cantidad']
            actual.save()
            return HttpResponseRedirect("/verProyecto/ver&id=" + str(proyecto_id))
    else:
        form = ModProyectoForm()
        form.fields['descripcion'].initial = actual.descripcion
        form.fields['fecha_inicio'].initial = actual.fecha_inicio
        form.fields['fecha_fin'].initial = actual.fecha_fin
        form.fields['estado'].initial = actual.estado
        form.fields['cantidad'].initial = actual.cantidad
    return render_to_response("proyectos/mod_proyecto.html", {'user': user,
                                                              'form': form,
                                                              'proyecto': actual,
                                                              'mod_proyecto': 'modificar proyecto' in permisos
                                                              })


@login_required
def asignar_miembro(request, proyecto_id):
    user = User.objects.get(username=request.user.username)
    proyecto = Proyecto.objects.get(id=proyecto_id)
    # Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario=user, proyecto=proyecto_id).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    print permisos
    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = NuevoMiembroForm(proyecto,request.POST)
        print 'llega'
        if form.is_valid():
            urp = UsuarioRolProyecto()
            miembro = User.objects.get(id=form.cleaned_data['usuario'])
            rol = Rol.objects.get(id=form.cleaned_data['rol'])
            urp.usuario = miembro
            urp.proyecto = proyecto
            urp.rol = rol
            urp.save()
            return HttpResponseRedirect("/verProyecto/ver&id=" + str(proyecto_id))
    else:
        form = NuevoMiembroForm(proyecto)
    return render_to_response('proyectos/asignar_miembro.html', {'form': form,
                                                                 'user': user,
                                                                 'proyecto': proyecto,
                                                                 'asignar_miembros': 'asignar miembros' in permisos
                                                                 })


@login_required
def borrar_rol(request, rol_id):
    """Borra un rol con las comprobaciones de consistencia"""
    user = User.objects.get(username=request.user.username)
    # Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario=user).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    print permisos
    #-------------------------------------------------------
    actual = get_object_or_404(Rol, id=rol_id)
    #Obtener todas las posibles dependencias
    if actual.categoria == 1:
        relacionados = UsuarioRolSistema.objects.filter(rol=actual).count()
    elif actual.categoria == 2:
        pass
        #relacionados = UsuarioRolProyecto.objects.filter(rol = actual).count()
    if request.method == 'POST':
        actual.delete()
        if actual.categoria == 1:
            return HttpResponseRedirect("/rolesSist")
        return HttpResponseRedirect("/rolesProy")
    else:
        if actual.id == 1:
            error = "No se puede borrar el rol de superusuario"
            return render_to_response("roles/rol_confirm_delete.html", {'mensaje': error,
                                                                        'rol': actual,
                                                                        'user': user,
                                                                        'eliminar_rol': 'eliminar rol' in permisos
                                                                        })
            # if relacionados > 0:
            #     error = "El rol se esta utilizando."
            #     return render_to_response("roles/rol_confirm_delete.html", {'mensaje': error,
            #                                                                       'rol':actual,
            #                                                                       'user':user,
            #                                                                       'eliminar_rol':'eliminar rol' in permisos
        # 						})
    return render_to_response("roles/rol_confirm_delete.html", {'rol': actual,
                                                                'user': user,
                                                                'eliminar_rol': 'eliminar rol' in permisos
                                                                })


@login_required
def asignar_flujo(request, proyecto_id):
    user = User.objects.get(username=request.user.username)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    print permisos
    #-------------------------------------------------------------------
    actual = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
	if 1 == 1:
            form = AsignarFlujoForm(request.POST)
            if form.is_valid():
               actual.flujos.clear()
               lista = form.cleaned_data['flujos']
               for i in lista:
			nuevo = ProyectoFlujo()
                    	nuevo.proyecto = actual
                    	nuevo.flujo = i
                    	nuevo.save()

        return HttpResponseRedirect("/verProyecto/ver&id=" + str(proyecto_id))
    else:

	    dict = {}

            for i in actual.flujos.all():
                dict[i.id] = True
            form = AsignarFlujoForm(initial={'flujos': dict})
    return render_to_response("proyectos/asignar_flujos.html", {'form': form,
                                                                  'proyecto': actual,
                                                                  'user':user,
                                                                  })
