# -*- coding: utf-8 -*-
import base64
from django.core.context_processors import csrf
from django.db.models import Max, Count
from django.shortcuts import render_to_response, get_object_or_404, render
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
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import random
from matplotlib.dates import DateFormatter
import numpy as np
import matplotlib.pyplot as plt
import django
import datetime
from datetime import timedelta
from io import BytesIO
from django.http import HttpResponse
from django.views.generic import ListView
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table
from reportlab.platypus import Spacer
from reportlab.lib.pagesizes import A4
from dateutil import rrule


def dateTimeViewBootstrap2(request):
    """
    Metodo para visualizar fecha en formato calendario
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :return:crear_proyecto.html,pagina en el cual se carga la fecha
    """
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            return render_to_response(request, 'sprint/crear_proyecto.html', {
                'form': form,'bootstrap':2
            })
    else:
        if request.GET.get('id',None):
            form = ProyectoForm(instance=ProyectoForm.objects.get(id=request.GET.get('id',None)))
        else:
            form = ProyectoForm()

    return render_to_response(request, 'sprint/crear_proyecto.html', {
             'form': form,'bootstrap':2
            })

@login_required
def admin_proyectos(request):
    """
    Metodo para la administracion de Proyectos
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :return:proyectos.html,pagina utilizada para la administracion de los proyectos creados
    """
    user = User.objects.get(username=request.user.username)
    permisos = get_permisos_sistema(user)
    usuarioPorProyecto = UsuarioRolProyecto.objects.filter(usuario = user.id)
    proys = []
    for rec in usuarioPorProyecto:
        if not rec.proyecto in proys:
            proys.append(rec.proyecto.id)
    lista = Proyecto.objects.filter(id__in = proys).order_by('id')
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Proyecto.objects.filter(
                Q(nombrelargo__icontains=palabra) | Q(descripcion__icontains=palabra), Q(id__in = proys)).order_by('id')
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
    """
    Metodo para agregar un nuevo proyecto
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :return:crear_proyecto.html, pagina en el cual se crea un nuevo proyecto.
    """
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
            userLider = User.objects.get(username=form.cleaned_data['usuario_lider'])
            proy.usuario_lider = userLider
            proy.fecha_inicio = form.cleaned_data['fecha_inicio']
            proy.fecha_fin = form.cleaned_data['fecha_fin']
            proy.cantidad = form.cleaned_data['cantidad']
            proy.estado = 1
            proy.save()
            urp = UsuarioRolProyecto()
            urp.usuario = userLider
            rol = Rol.objects.get(nombre='team leader')
            urp.horas = 0
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
    """Visualiza Datos de un Proyecto y muestra las operaciones que puede ejecutar"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    sprints = Sprint.objects.filter(proyecto=proyecto_id)
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
    fluActProy = FlujoActividadProyecto.objects.filter(proyecto=proyecto_id).only('flujo')
    fapList = []
    for rec in fluActProy:
        if not rec.flujo in fapList:
            fapList.append(rec.flujo)
    flujos = Flujo.objects.filter(Q(nombre__in = fapList))
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisosProy = []
    for i in permisos_obj:
        permisosProy.append(i.nombre)
    print permisosProy
    lista = User.objects.all().order_by("id")
    print proyecto.flujos
    proyPend = False
    proyIni = False
    proyEnd = False
    if proyecto.estado == 1:
        proyPend = True
    if proyecto.estado == 2:
        proyIni = True
    if proyecto.estado == 3:
        proyEnd = True

    ctx = {'lista': lista,
           'proyecto': proyecto,
           'status': status,
           'miembros': userRolProy,
           'flujos': flujos,
           'proyPend': proyPend,
           'proyIni': proyIni,
           'proyEnd' : proyEnd,
           'sprints' : sprints,
           'ver_proyectos': 'ver proyectos' in permisosSys,
           'crear_proyecto': 'crear proyecto' in permisosSys,
           'mod_proyecto': 'modificar proyecto' in permisosProy,
           'eliminar_proyecto': 'eliminar proyecto' in permisosProy,
           'asignar_miembros': 'asignar miembros' in permisosProy,
           'asignar_flujo' : 'asignar flujo' in permisosProy,
           'eliminar_miembro' : 'eliminar miembro' in permisosProy,
           'admin_sprint' : 'admin sprint' in permisosProy,
           'admin_user_history' : 'admin user history' in permisosProy,
           'asignar_actividades_proyecto' : 'asignar actividades proyecto' in permisosProy,
           'finalizar_proyecto' : 'finalizar proyecto' in permisosProy,
           'iniciar_proyecto' : 'iniciar proyecto' in permisosProy,
           'ver_reportes': 'ver reportes' in permisosProy,
           'ver_reporte1': 'ver reporte1' in permisosProy,
           'ver_reporte2': 'ver reporte2' in permisosProy,
           'ver_reporte3': 'ver reporte3' in permisosProy,
           'ver_reporte4': 'ver reporte4' in permisosProy,
           'ver_reporte5': 'ver reporte5' in permisosProy,
           'ver_reporte6': 'ver reporte6' in permisosProy
           }
    return render_to_response('proyectos/verProyecto.html', ctx, context_instance=RequestContext(request))


def mod_proyecto(request, proyecto_id):
    """Modifica un Proyecto"""
    user = User.objects.get(username=request.user.username)
    actual = get_object_or_404(Proyecto, id=proyecto_id)
    # Validacion de permisos---------------------------------------------
    permisos = get_permisos_sistema(user)
    roles = UsuarioRolProyecto.objects.filter(usuario=user,proyecto = actual).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    for i in permisos_obj:
        permisos.append(i.nombre)

    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = ModProyectoForm(request.POST)
        if form.is_valid():
            actual.descripcion = form.cleaned_data['descripcion']
            actual.fecha_inicio = form.cleaned_data['fecha_inicio']
            actual.fecha_fin = form.cleaned_data['fecha_fin']
            actual.usuario_lider = User.objects.get(username=form.cleaned_data['usuario_lider'])
            actual.estado = form.cleaned_data['estado']
            actual.cantidad = form.cleaned_data['cantidad']
            actual.save()
            rol = Rol.objects.get(nombre = 'team leader')
            userRolProyActual = UsuarioRolProyecto.objects.filter(proyecto=proyecto_id, rol=rol)
            liderActual = UsuarioRolProyecto.objects.get(id=userRolProyActual)
            liderActual.usuario = actual.usuario_lider
            liderActual.save()
            return HttpResponseRedirect("/verProyecto/ver&id=" + str(proyecto_id))
    else:
        form = ModProyectoForm()
        form.fields['descripcion'].initial = actual.descripcion
        form.fields['fecha_inicio'].initial = actual.fecha_inicio
        form.fields['fecha_fin'].initial = actual.fecha_fin
        form.fields['usuario_lider'].initial = actual.usuario_lider
        form.fields['estado'].initial = actual.estado
        form.fields['cantidad'].initial = actual.cantidad
    return render_to_response("proyectos/mod_proyecto.html", {'user': user,
                                                              'form': form,
                                                              'proyecto': actual,
                                                              'mod_proyecto': 'modificar proyecto' in permisos
                                                              })


@login_required
def asignar_miembro(request, proyecto_id):
    """Metodo para asignar miembro a proyecto"""
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
        if form.is_valid():
            urp = UsuarioRolProyecto()
            miembro = User.objects.get(username=form.cleaned_data['usuario'])
            rol = Rol.objects.get(nombre=form.cleaned_data['rol'])
            urp.usuario = miembro
            urp.proyecto = proyecto
            urp.rol = rol
            urp.horas = form.cleaned_data['horas']
            urp.save()
            return HttpResponseRedirect("/verProyecto/ver&id=" + str(proyecto_id))
    else:
        form = NuevoMiembroForm(proyecto,initial={'horas': 0})
    return render_to_response('proyectos/asignar_miembro.html', {'form': form,
                                                                 'user': user,
                                                                 'proyecto': proyecto,
                                                                 'asignar_miembros': 'asignar miembros' in permisos
                                                                 })

@login_required
def asignar_flujo(request, proyecto_id):
    """Metodo para asignar Flujo a Proyecto"""
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
                for flujo in lista:
                    lista_actividades = FlujoActividad.objects.filter(flujo = flujo).only('actividad')
                    for act in lista_actividades:
                        fap = FlujoActividadProyecto()
                        fap.proyecto = actual
                        fap.flujo = flujo
                        fap.actividad = act.actividad
                        fap.orden = act.orden
                        fap.save()


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
def borrar_proyecto(request, proyecto_id):
    """Metodo para borrar Proyecto"""
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
    actual = get_object_or_404(Proyecto, id=proyecto_id)
    relacionados = ProyectoFlujo.objects.filter(flujo = actual).count()

    if request.method == 'POST':
        actual.delete()
        return HttpResponseRedirect("/proyectos")
    else:
        if relacionados > 0:
             error = "El Proyecto esta relacionado."
             return render_to_response("proyectos/proyecto_confirm_delete.html", {'mensaje': error,
                                                                               'proyecto':actual,
                                                                               'user':user,
                                                                               'eliminar_proyecto':'eliminar proyecto' in permisos})
    return render_to_response("proyectos/proyecto_confirm_delete.html", {'proyecto':actual,
                                                                      'user':user,
                                                                      'eliminar_proyecto':'eliminar proyecto' in permisos
								})

def borrar_miembro(request, miembro_id):
    """Metodo para eliminar un miembro del Proyecto"""
    user = User.objects.get(username=request.user.username)
    urp = UsuarioRolProyecto.objects.get(id=miembro_id)
    rol = Rol.objects.get(nombre=urp.rol)
    proyecto = Proyecto.objects.get(nombrelargo=urp.proyecto)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user,proyecto=proyecto).only('rol')
    print roles
    permisos_obj = []
    for i in roles:
       permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
       permisos.append(i.nombre)
    print permisos
    #-------------------------------------------------------------------
    actual = get_object_or_404(UsuarioRolProyecto, id=miembro_id)
    #relacionados = UsuarioRolProyecto.objects.filter(flujo = actual).count()

    if request.method == 'POST':
        actual.delete()
        return HttpResponseRedirect("/verProyecto/ver&id=" + str(proyecto.id))
    # else:
    #     if relacionados > 0:
    #          error = "El Flujo esta relacionado."
    #          return render_to_response("flujo/flujo_confirm_delete.html", {'mensaje': error,
    #                                                                            'flujo':actual,
    #                                                                            'user':user,
    #                                                                            'eliminar_flujo':'eliminar flujo' in permisos})
    return render_to_response("proyectos/miembro_confirm_delete.html", {'usuariorolproyecto':actual,
                                                                      'user':user,
                                                                      'proyecto': proyecto,
                                                                      'eliminar_miembro':'eliminar miembro' in permisos
								})

@login_required
def asignar_actividad_proy(request, flujo_id, proyecto_id):
    """Metodo para asignar Flujo a Proyecto"""
    user = User.objects.get(username=request.user.username)
    proy = Proyecto.objects.get(id = proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proy).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    print permisos
    #-------------------------------------------------------------------
    proyactual = get_object_or_404(Proyecto, id=proyecto_id)
    flujoactual = get_object_or_404(Flujo, id=flujo_id)
    lista_actividades = FlujoActividadProyecto.objects.filter(flujo = flujo_id,  proyecto = proyecto_id)
    if request.method == 'POST':
        form = AsignarActividadesProyForm(request.POST)
        if form.is_valid():
            lista_nueva = form.cleaned_data['actividades']
            for i in lista_actividades:
                i.delete()
            # actual.flujos.clear()
            for i in lista_nueva:
                fapmax = FlujoActividadProyecto.objects.filter(flujo = flujoactual,proyecto = proyactual).aggregate(Max('orden'))
                fap = FlujoActividadProyecto()
                fap.proyecto = proyactual
                fap.flujo = flujoactual
                fap.actividad = i
                if fapmax['orden__max']:
                    fap.orden = (int(fapmax['orden__max']) + 1)
                else:
                    fap.orden = 1
                fap.save()
        return HttpResponseRedirect("/verProyecto/ver&id=" + str(proyecto_id))
    else:
        dict = {}
        for i in lista_actividades:
            dict[i.actividad.id] = True
        form = AsignarActividadesProyForm(initial={'actividades': dict})
    return render_to_response("proyectos/asignar_actividades_proy.html", {'form': form,
                                                                  'proyecto': proyactual,
                                                                  'flujo': flujoactual,
                                                                  'user':user,
                                                                  })

def ver_actividades_proyecto(request, flujo_id, proyecto_id):
    """
    Metodo para ver las actividades de un proyecto
    :param request:contiene la informacion de la pagina que lo llamo
    :param flujo_id: codigo del flujo que se quieren conocer sus actividades
    :param proyecto_id: codigo del proyecto que se quieren conocer sus actividades
    :return: admin_actividades_proyectos.html, pagina en la cual se ven las actividades
    """
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    flujo = get_object_or_404(Flujo, id=flujo_id)
    user = User.objects.get(username=request.user.username)
    userRolProy = UsuarioRolProyecto.objects.filter(proyecto=proyecto_id)
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyecto).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    fluActProy = FlujoActividadProyecto.objects.filter(flujo = flujo_id, proyecto = proyecto_id).order_by('orden')
    actList = {}
    ultActividad = 0
    for rec in fluActProy:
        if not actList.has_key(rec.flujo.id):
            actList[rec.flujo.id] = {}
        if not actList[rec.flujo.id].has_key(int(rec.orden)):
            actList[rec.flujo.id][int(rec.orden)] = {}
        if not actList[rec.flujo.id][int(rec.orden)].has_key(rec.actividad.id):
            actList[rec.flujo.id][int(rec.orden)][rec.actividad.id] = []
        act = Actividad.objects.get(nombre = rec.actividad)
        actList[rec.flujo.id][int(rec.orden)][rec.actividad.id].append(act.nombre)
        actList[rec.flujo.id][int(rec.orden)][rec.actividad.id].append(act.descripcion)
        ultActividad = int(rec.orden)
    if actList:
        actDict = actList[int(flujo_id)]
    else:
        actDict = None
    lista = User.objects.all().order_by("id")
    proyPend = False
    if proyecto.estado == 1:
        proyPend = True
    ctx = {'flujo':flujo,
           'proyecto':proyecto,
           'actividades':actDict,
           'proyPend':proyPend,
           'ultActividad':ultActividad,
           'ver_flujo': 'ver flujo' in permisos,
           'asignar_actividades_proyecto': 'asignar actividades proyecto' in permisos
       }
    return render_to_response('proyectos/admin_actividades_proyecto.html', ctx, context_instance=RequestContext(request))

def subir_actividad_proyecto(request, flujo_id, actividad_id, proyecto_id):
    """
    Medodo con el cual se cambia el orden de una actividad
    :param request: contiene la informacion sobre la pagina que lo llamo
    :param flujo_id: codigo del flujo al cual esta asociado la actividad
    :param actividad_id: codigo de la actividad
    :param proyecto_id: codigo del proyecto
    :return: se sube el orden de la actividad
    """
    flujos = get_object_or_404(Flujo, id=flujo_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    actActual = FlujoActividadProyecto.objects.get(flujo = flujo_id, actividad = actividad_id,proyecto = proyecto)
    actSig = FlujoActividadProyecto.objects.get(flujo = flujo_id, orden = (int(actActual.orden)-1), proyecto = proyecto)
    actActual.orden = int(actActual.orden) - 1
    actSig.orden = int(actSig.orden) + 1
    actActual.save()
    actSig.save()
    return HttpResponseRedirect("/verActividadesProy/flujo&id=%s&&proyecto&id=%s/" %(flujo_id,proyecto_id))

def bajar_actividad_proyecto(request, flujo_id, actividad_id, proyecto_id):
    """
    Medodo con el cual se cambia el orden de una actividad
    :param request: contiene la informacion sobre la pagina que lo llamo
    :param flujo_id: codigo del flujo al cual esta asociado la actividad
    :param actividad_id: codigo de la actividad
    :param proyecto_id: codigo del proyecto
    :return: se baja el orden de la actividad
    """
    flujos = get_object_or_404(Flujo, id=flujo_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    actActual = FlujoActividadProyecto.objects.get(flujo = flujo_id, actividad = actividad_id, proyecto = proyecto)
    actSig = FlujoActividadProyecto.objects.get(flujo = flujo_id, orden = (int(actActual.orden)+1), proyecto = proyecto)
    actActual.orden = int(actActual.orden) + 1
    actSig.orden = int(actSig.orden) - 1
    actActual.save()
    actSig.save()
    return HttpResponseRedirect("/verActividadesProy/flujo&id=%s&&proyecto&id=%s/" %(flujo_id,proyecto_id))

@login_required
def visualizar_kanban(request, proyecto_id):
    """
    Metodo para visualizar la tabla kanban de un proyecto
    :param request: contiene la informacion de la pagina que lo llamo
    :param proyecto_id: codigo del proyecto que se desea graficar su tabla kanban
    :return: tabla kanban
    """
    user = User.objects.get(username=request.user.username)
    proy = Proyecto.objects.get(id = proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proy).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    notSprintInit = True
    proyIni = False
    if proy.estado == 2:
        proyIni = True
    sprintInitList = Sprint.objects.filter(proyecto = proy, estado = 'iniciado')
    if sprintInitList:
        notSprintInit = False
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proy).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    #print permisos
    #-------------------------------------------------------------------
    US = UserHistory.objects.filter(proyecto = proyecto_id).order_by('valor_tecnico')
    usExcSprint = UserHistory.objects.filter(proyecto = proyecto_id,sprint = None).order_by('sprint')
    proyactual = get_object_or_404(Proyecto, id=proyecto_id)
    fluAps = FlujoActividadProyecto.objects.filter(proyecto = proyecto_id)
    listflu = []
    for fap in fluAps:
        if not fap.flujo in listflu:
            listflu.append(fap.flujo)
    nro = 0
    dictAct = {}
    kanbanxflujo = {}
    dictUltAct = {}
    for flujo in listflu:
        flujoactual = get_object_or_404(Flujo, nombre=flujo.nombre)
        actividades = FlujoActividadProyecto.objects.filter(flujo=flujoactual, proyecto =proyactual).order_by('orden')
        if not dictAct.has_key(flujoactual.nombre):
            dictAct[flujoactual.nombre] = []
        dictAct[flujoactual.nombre] = actividades
        faps = FlujoActividadProyecto.objects.filter(flujo=flujoactual, proyecto =proyactual).order_by('-orden')
        ultimaActividad = Actividad.objects.get(nombre = faps[0].actividad)
        if not dictUltAct.has_key(flujoactual.nombre):
            dictUltAct[flujoactual.nombre] = []
        dictUltAct[flujoactual.nombre].append(ultimaActividad)
        sprints = Sprint.objects.filter(proyecto = proyecto_id).order_by('fecha_inicio')
        sprintList = []
        sprintList.append("BACKLOG")

        for rec in sprints:
            if not rec.nombre in sprintList:
                sprintList.append(str(rec.nombre))
        newList = []
        for rec in sprintList:
            newList.append("")
        # print newList
        # print sprintList
        dict = {}
        for rec in sprints:
            if not dict.has_key(rec.nombre):
                dict[rec.nombre] = {}

        for rec in US:
            if rec.sprint:
                sprint = Sprint.objects.get(nombre = rec.sprint)
                nombre = sprint.nombre
            else:
                nombre = "BACKLOG"
            valor_tecnico = rec.valor_tecnico * -1
            if not dict.has_key(nombre):
                dict[nombre] = {}
            if not dict[nombre].has_key(valor_tecnico):
                dict[nombre][valor_tecnico] = {}
            if not dict[nombre][valor_tecnico].has_key(rec.id):
                dict[nombre][valor_tecnico][rec.id] = []
                for sp in sprintList:
                    dict[nombre][valor_tecnico][rec.id].append(['',''])
            # if not dict[rec.sprint.nombre].has_key(rec.nombre):
            #     dict[rec.sprint.nombre][rec.id] = []

            cont = 0
            for sp in sprintList:
                # print sp
                if sp == nombre:
                    dict[nombre][valor_tecnico][rec.id][cont] = [str(rec.nombre),str(rec.estado)]
                cont += 1
        actList = []
        # actList.append("BACKLOG")
        for rec in actividades:
            acti = Actividad.objects.get(nombre = rec.actividad)
            if not acti.nombre in actList:
                actList.append(acti.nombre)
                actList.append(acti.nombre)
                actList.append(acti.nombre)
        actList.append("DONE")
        newList = []
        for rec in actList:
            newList.append("")
        # print newList
        # print sprintList
        dictKanban = {}

        for rec in actividades:
            acti = Actividad.objects.get(nombre = rec.actividad)
            if not dictKanban.has_key(acti.nombre):
                dictKanban[acti.nombre] = {}
        usFllujo = UserHistory.objects.filter(proyecto = proyecto_id, flujo = flujoactual).order_by('valor_tecnico')

        for rec in usFllujo:
            if rec.flujo:
                acti = Actividad.objects.get(nombre = rec.actividad)
                nombreAct = acti.nombre
                if acti == ultimaActividad:
                    if rec.estado == 'finalizado':
                        nombreAct = 'DONE'
            # valor_tecnico = rec.valor_tecnico * -1
            if not dictKanban.has_key(nombreAct):
                dictKanban[nombreAct] = {}
            # if not dict[nombre].has_key(valor_tecnico):
            #     dict[nombre][valor_tecnico] = {}
            # if not dictKanban[nombreAct].has_key(rec.estadokanban):
            #     dictKanban[nombreAct][rec.estadokanban] = {}
            if not dictKanban[nombreAct].has_key(rec.id):
                dictKanban[nombreAct][rec.id] = []
                for act in actList:
                    dictKanban[nombreAct][rec.id].append(["","","","",""])
            # if not dict[rec.sprint.nombre].has_key(rec.nombre):
            #     dict[rec.sprint.nombre][rec.id] = []

            cont = 0
            for act in actList:
                if act == nombreAct:
                    if nombreAct == 'DONE':
                        dictKanban[nombreAct][rec.id][-1][0] = str(rec.nombre)
                        dictKanban[nombreAct][rec.id][-1][1] = str("DONE")
                        dictKanban[nombreAct][rec.id][-1][2] = str(rec.estado)
                        dictKanban[nombreAct][rec.id][-1][3] = str(rec.encargado)
                        dictKanban[nombreAct][rec.id][-1][4] = str(ultimaActividad.id)
                        break
                    if rec.estadokanban == 'to-do':
                        dictKanban[nombreAct][rec.id][cont][0] = str(rec.nombre)
                        dictKanban[nombreAct][rec.id][cont][1] = str("to-do")
                        dictKanban[nombreAct][rec.id][cont][2] = str(rec.estado)
                        dictKanban[nombreAct][rec.id][cont][3] = str(rec.encargado)
                        dictKanban[nombreAct][rec.id][cont][4] = str(ultimaActividad.id)
                        break
                    elif rec.estadokanban == 'doing':
                        dictKanban[nombreAct][rec.id][cont+1][0] = str(rec.nombre)
                        dictKanban[nombreAct][rec.id][cont+1][1] = str("doing")
                        dictKanban[nombreAct][rec.id][cont+1][2] = str(rec.estado)
                        dictKanban[nombreAct][rec.id][cont+1][3] = str(rec.encargado)
                        dictKanban[nombreAct][rec.id][cont+1][4] = str(ultimaActividad.id)
                        break
                    elif rec.estadokanban == 'done':
                        dictKanban[nombreAct][rec.id][cont+2][0] = str(rec.nombre)
                        dictKanban[nombreAct][rec.id][cont+2][1] = str("done")
                        dictKanban[nombreAct][rec.id][cont+2][2] = str(rec.estado)
                        dictKanban[nombreAct][rec.id][cont+2][3] = str(rec.encargado)
                        dictKanban[nombreAct][rec.id][cont+2][4] = str(ultimaActividad.id)
                        break
                cont += 1
        if not kanbanxflujo.has_key(flujoactual.nombre):
            kanbanxflujo[flujoactual.nombre] = []
        kanbanxflujo[flujoactual.nombre] = dictKanban
            # dict[nombre].append(rec.nombre)
            # dict[rec.sprint.id][rec.id].append(rec.sprint.nombre)
            # actList[rec.flujo.id][int(rec.orden)][rec.actividad.id].append(act.descripcion)
            #ultActividad = int(rec.orden)
    return render_to_response("proyectos/verkanban.html", {
                                                                  'proyecto': proyactual,
                                                                  'user' : user,
                                                                  'listflu': listflu,
                                                                  'dict': dict,
                                                                  'kanbanxflujo': kanbanxflujo,
                                                                  'user':user,
                                                                  'US' : US,
                                                                  'sprint' : sprints,
                                                                  'notSprintInit' : notSprintInit,
                                                                  'proyIni' : proyIni,
                                                                  'dictAct': dictAct,
                                                                  'dictUltAct' : dictUltAct,
                                                                  'finalizar_us' : 'finalizar user history' in permisos,
                                                                  'agregar_trabajo' : 'agregar comentario' in permisos,
                                                                  'adjuntar_archivo' : 'adjuntar archivos' in permisos,
                                                                  'cambiar_estado' : 'cambiar estado kanban' in permisos,
                                                                  'cambiar_actividad' : 'cambiar actividad kanban' in permisos
                                                                  })

@login_required
def visualizar_burndownChart(request, proyecto_id, sprint_id):
    """
    Metodo para visualizar el Grafico BurnDownChart
    :param request: contiene informacion de la pagina que lo llamo
    :param proyecto_id: codigo del proyecto que se quiere graficar
    :param sprint_id: codigo de sprint que se quiere graficar
    :return: Grafico del BurndownChart
    """
    user = User.objects.get(username=request.user.username)
    proy = Proyecto.objects.get(id = proyecto_id)
    sprint = get_object_or_404(Sprint, id=sprint_id)
    x = []
    y = []
    y1 = []
    fechaactual = sprint.fecha_inicio
    fecha = fechaactual-timedelta(days=1)
    y.append(0)
    x.append(fecha)
    total = 0
    totalplan =0
    uh = UserHistorySprint.objects.filter(sprint=sprint)
    for rec in uh:
        totalplan += rec.horas_plan
    y1.append(totalplan)
    while fechaactual <= sprint.fecha_fin:
        x.append(fechaactual)

        US = UserHistorySprint.objects.filter(sprint = sprint)
        sumahora = 0
        for u in US:
            ust = UserHistory.objects.get(id = u.userhistory.id)
            trabajo = Comentarios.objects.filter(userhistory = ust, fecha = fechaactual)

            for j in trabajo:
                sumahora = sumahora + j.horas
        fechaactual = fechaactual + timedelta(days=1)
        total+= sumahora
        y.append(total)
    div = totalplan / float(len(x)-1)
    i = 0
    listX = []
    for rec in x:
        listX.append(i)
        # if i == 0:
        #     listX.append("0")
        # else:
        #     listX.append("DIA "+str(i))
        i += 1
    listY = []
    i = 0
    listEjec = []
    for rec in x:
        aux = totalplan - i *div
        ejec = totalplan - y[i]
        listY.append(round(aux,2))
        listEjec.append(ejec)
        i += 1

    return render_to_response("proyectos/grafica.html", {
                                                            'user':user, 'proyecto': proy,
                                                            'X' : listX,
                                                            'Y' : listEjec,
                                                            'Y2' : listY,
                                                            'sprint' : sprint
                                                        })

def reporte_pdf(request):
         user = User.objects.get(username=request.user.username)
         usuarioPorProyecto = UsuarioRolProyecto.objects.filter(usuario = user.id)
         proys = []
         for rec in usuarioPorProyecto:
             if not rec.proyecto in proys:
                 proys.append(rec.proyecto.id)
         lista = Proyecto.objects.filter(id__in = proys).order_by('id')
         return render_to_response("proyectos/reportes.html", { 'proy' : lista,
                                                                  'user' : user
                                                                  })

def reporte1_pdf(request,proyecto_id):
    """
    Metodo para generar el reporte 1 del proyecto
    :param request: contiene la informacion de la pagina que lo llamo
    :param proyecto_id: id del proyecto del cual se generara el reporte
    :return: reporte en pdf
    """
    proyecto_actual= Proyecto.objects.get(id=proyecto_id)
    uh = UserHistory.objects.filter(proyecto = proyecto_actual)

    estiloHoja = getSampleStyleSheet()
    style = [
        ('GRID',(0,0),(-1,-1),0.5,colors.white),
        ('BOX',(0,0),(-1,-1),2,colors.black),
        ('SPAN',(0,0),(-1,0)),
        ('ROWBACKGROUNDS', (0, 3), (-1, -1), (colors.Color(0.9, 0.9, 0.9),colors.white)),
        ('BACKGROUND', (0, 2), (-1, 2), colors.fidlightblue),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('LINEABOVE',(0,0),(-1,0),1.5,colors.black),
        ('LINEBELOW',(0,0),(-1,0),1.5,colors.black),
        ('SIZE',(0,0),(-1,0),12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.black),
        ]

    story = []
    cabecera = estiloHoja['Heading2']
    cabecera.pageBreakBefore=0
    cabecera.keepWithNext=0
    cabecera.backColor=colors.white
    cabecera.spaceAfter = 0
    cabecera.spaceBefore = 0
    parrafo = Paragraph('',cabecera)
    story.append(parrafo)
    parrafo = Paragraph('PRIMER INFORME DEL'+ '"' +proyecto_actual.nombrelargo+'" : ',cabecera)
    story.append(parrafo)
    parrafo = Paragraph('_'*66,cabecera)
    story.append(parrafo)
    cabecera2 = estiloHoja['Heading1']
    cabecera2.pageBreakBefore=0
    cabecera2.keepWithNext=0
    cabecera2.backColor=colors.white
    parrafo = Paragraph('   ',cabecera2)
    story.append(parrafo)

    ltrabajoequipo = []
    ltrabajoequipo.append(['1. CANTIDAD DE TRABAJOS EN CURSO POR EQUIPO','',''])
    ltrabajoequipo.append([' ',' ',' '])
    ltrabajoequipo.append(['EQUIPO DE DESARROLLADORES','CANTIDAD DE TRABAJOS', 'ESTADO'])
    canttrabajo = 0
    for u in uh:
        if u.estado == 'iniciado':
            canttrabajo = canttrabajo + 1

    ltrabajoequipo.append(['Equipo 1',canttrabajo, 'iniciado'])

    t=Table( ltrabajoequipo, style=style)
    story.append(t)
    story.append(Spacer(0,20))
    story.append(parrafo)
    parrafo = Paragraph('_'*66,cabecera)
    story.append(parrafo)
    parrafo = Paragraph('FIN DE PRIMER INFORME' + ' '*100 + '('+str(datetime.date.today()) + ')' ,cabecera)
    story.append(parrafo)
    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=letter,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=18,
                            )
    doc.build(story)
    response = HttpResponse(content_type='application/pdf')
    pdf_name = "Reporte.pdf"
    response.write(buff.getvalue())
    buff.close()
    return response


def reporte2_pdf(request,proyecto_id):
    """
    Metodo que genera el reporte 2
    :param request: contiene la informacion sobre la pagina que lo llamo
    :param proyecto_id: id del proyecto del cual se generara el reporte
    :return: reporte en pdf
    """
    proyecto_actual= Proyecto.objects.get(id=proyecto_id)
    uh = UserHistory.objects.filter(proyecto = proyecto_actual)

    estiloHoja = getSampleStyleSheet()
    style = [
        ('GRID',(0,0),(-1,-1),0.5,colors.white),
        ('BOX',(0,0),(-1,-1),2,colors.black),
        ('SPAN',(0,0),(-1,0)),
        ('ROWBACKGROUNDS', (0, 3), (-1, -1), (colors.Color(0.9, 0.9, 0.9),colors.white)),
        ('BACKGROUND', (0, 2), (-1, 2), colors.fidlightblue),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('LINEABOVE',(0,0),(-1,0),1.5,colors.black),
        ('LINEBELOW',(0,0),(-1,0),1.5,colors.black),
        ('SIZE',(0,0),(-1,0),12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.black),
        ]

    story = []
    cabecera = estiloHoja['Heading2']
    cabecera.pageBreakBefore=0
    cabecera.keepWithNext=0
    cabecera.backColor=colors.white
    cabecera.spaceAfter = 0
    cabecera.spaceBefore = 0
    parrafo = Paragraph('',cabecera)
    story.append(parrafo)
    parrafo = Paragraph('SEGUNDO INFORME DEL'+ '"' +proyecto_actual.nombrelargo+'" : ',cabecera)
    story.append(parrafo)
    parrafo = Paragraph('_'*66,cabecera)
    story.append(parrafo)
    cabecera2 = estiloHoja['Heading1']
    cabecera2.pageBreakBefore=0
    cabecera2.keepWithNext=0
    cabecera2.backColor=colors.white
    parrafo = Paragraph('   ',cabecera2)
    story.append(parrafo)
    ltrabajoequipo = []
    ltrabajoequipo.append(['2. CANTIDAD DE TRABAJOS POR USUARIO','','',''])
    ltrabajoequipo.append([' ',' ',' ',' '])
    ltrabajoequipo.append(['USUARIO','TRABAJOS PENDIENTES', 'TRABAJOS INICIADOS','TRABAJOS FINALIZADOS'])
    urp = UsuarioRolProyecto.objects.filter(proyecto = proyecto_actual)
    for i in urp:
        if i.rol.nombre == 'Desarrollador':
            usp = UserHistory.objects.filter(encargado = i.usuario,proyecto = proyecto_actual, estado = 'pendiente')
            usi = UserHistory.objects.filter(encargado = i.usuario,proyecto = proyecto_actual, estado = 'iniciado')
            usf = UserHistory.objects.filter(encargado = i.usuario,proyecto = proyecto_actual, estado = 'finalizado')
            ltrabajoequipo.append([i.usuario.username, len(usp), len(usi), len(usf)])


    t=Table( ltrabajoequipo, style=style)
    story.append(t)
    story.append(Spacer(0,20))
    story.append(parrafo)
    parrafo = Paragraph('_'*66,cabecera)
    story.append(parrafo)
    parrafo = Paragraph('FIN DE SEGUNDO INFORME' + ' '*100 + '('+str(datetime.date.today()) + ')' ,cabecera)
    story.append(parrafo)
    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=letter,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=18,
                            )
    doc.build(story)
    response = HttpResponse(content_type='application/pdf')
    pdf_name = "Reporte.pdf"
    response.write(buff.getvalue())
    buff.close()
    return response


def reporte3_pdf(request,proyecto_id):
    """
    Metodo que genera el reporte 3
    :param request: contiene informacion sobre la pagina que lo llamo
    :param proyecto_id: id del proyecto del cual se generara el reporte
    :return: reporte en formato pdf
    """
    proyecto_actual= Proyecto.objects.get(id=proyecto_id)
    uh = UserHistory.objects.filter(proyecto = proyecto_actual).order_by('-valor_tecnico')

    estiloHoja = getSampleStyleSheet()
    style = [
        ('GRID',(0,0),(-1,-1),0.5,colors.white),
        ('BOX',(0,0),(-1,-1),2,colors.black),
        ('SPAN',(0,0),(-1,0)),
        ('ROWBACKGROUNDS', (0, 3), (-1, -1), (colors.Color(0.9, 0.9, 0.9),colors.white)),
        ('BACKGROUND', (0, 2), (-1, 2), colors.fidlightblue),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('LINEABOVE',(0,0),(-1,0),1.5,colors.black),
        ('LINEBELOW',(0,0),(-1,0),1.5,colors.black),
        ('SIZE',(0,0),(-1,0),12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.black),
        ]

    story = []
    cabecera = estiloHoja['Heading2']
    cabecera.pageBreakBefore=0
    cabecera.keepWithNext=0
    cabecera.backColor=colors.white
    cabecera.spaceAfter = 0
    cabecera.spaceBefore = 0
    parrafo = Paragraph('',cabecera)
    story.append(parrafo)
    parrafo = Paragraph('TERCER INFORME DEL'+ '"' +proyecto_actual.nombrelargo+'" : ',cabecera)
    story.append(parrafo)
    parrafo = Paragraph('_'*66,cabecera)
    story.append(parrafo)
    cabecera2 = estiloHoja['Heading1']
    cabecera2.pageBreakBefore=0
    cabecera2.keepWithNext=0
    cabecera2.backColor=colors.white
    parrafo = Paragraph('   ',cabecera2)
    story.append(parrafo)

    ltrabajoequipo = []
    ltrabajoequipo.append(['3. LISTA DE ACTIVIDADES PARA COMPLETAR EL PROYECTO','', ''])
    ltrabajoequipo.append([' ',' ',''])
    ltrabajoequipo.append(['PRIORIDAD','ACTIVIDADES', 'ESTADO'])
    for u in uh:
        if u.estado != 'finalizado' and u.estado != 'cancelado':
            ltrabajoequipo.append([u.valor_tecnico,u.nombre, u.estado])

    t=Table( ltrabajoequipo, style=style)
    story.append(t)
    story.append(Spacer(0,20))
    story.append(parrafo)
    parrafo = Paragraph('_'*66,cabecera)
    story.append(parrafo)
    parrafo = Paragraph('FIN DE TERCER INFORME' + ' '*100 + '('+str(datetime.date.today()) + ')' ,cabecera)
    story.append(parrafo)
    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=letter,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=18,
                            )
    doc.build(story)
    response = HttpResponse(content_type='application/pdf')
    pdf_name = "Reporte.pdf"
    response.write(buff.getvalue())
    buff.close()
    return response


def reporte4_pdf(request,proyecto_id):

    from reportlab.graphics.shapes import Drawing, Rect, String, Group, Line
    from reportlab.graphics.charts.barcharts import VerticalBarChart

    proy = Proyecto.objects.get(id = proyecto_id)
    story = []
    estilo = getSampleStyleSheet()
    import pprint
    estiloHoja = getSampleStyleSheet()
    cabecera = estiloHoja['Heading2']
    cabecera.pageBreakBefore=0
    cabecera.keepWithNext=0
    cabecera.backColor=colors.white
    cabecera.spaceAfter = 0
    cabecera.spaceBefore = 0
    parrafo = Paragraph('',cabecera)
    story.append(parrafo)
    parrafo = Paragraph('CUARTO INFORME DEL'+ '"' +proy.nombrelargo+'" : ',cabecera)
    story.append(parrafo)
    parrafo = Paragraph('_'*66,cabecera)
    story.append(parrafo)
    cabecera2 = estiloHoja['Heading2']
    cabecera2.pageBreakBefore=0
    cabecera2.keepWithNext=0
    cabecera2.backColor=colors.white
    parrafo = Paragraph('GRAFICO DE TIEMPO ESTIMADO Y EJECUTADO POR SPRINT DEL PROYECTO'+'"'+proy.nombrelargo+'"',cabecera2)
    story.append(parrafo)
    d = Drawing(400, 200)

    sprints = Sprint.objects.filter(proyecto = proy)
    listasprint = []
    listaplan = []
    listaejec = []
    for sp in sprints:
        listasprint.append(sp.nombre)
        US = UserHistorySprint.objects.filter(sprint = sp)
        sumahora = 0
        totalplan =0
        for u in US:
            totalplan += u.horas_plan
            ust = UserHistory.objects.get(id = u.userhistory.id)
            sumahora+=u.horas_ejec
            # trabajo = Comentarios.objects.filter(userhistory = ust)
            #
            # for j in trabajo:
            #     sumahora = sumahora + j.horas
        listaejec.append(sumahora)
        listaplan.append(totalplan)
    mayor  = 0
    for j in listaejec:
        if j > mayor:
            mayor = j
    for j in listaplan:
        if j > mayor:
            mayor = j

    data = [listaplan,listaejec]
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 125
    bc.width = 300
    bc.data = data
    bc.strokeColor = colors.black
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = mayor + 10
    bc.valueAxis.valueStep = 10  #paso de distancia entre punto y punto
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.categoryNames = listasprint
    bc.groupSpacing = 10
    bc.barSpacing = 2
    #bc.categoryAxis.style = 'stacked'  # Una variación del gráfico
    d.add(bc)
    pprint.pprint(bc.getProperties())
    story.append(d)
    cabecera2 = estiloHoja['Heading2']
    cabecera2.pageBreakBefore=0
    cabecera2.keepWithNext=0
    cabecera2.backColor=colors.white
    parrafo = Paragraph('ROJO = TIEMPO ESTIMADO',cabecera2)
    story.append(parrafo)
    cabecera2 = estiloHoja['Heading2']
    cabecera2.pageBreakBefore=0
    cabecera2.keepWithNext=0
    cabecera2.backColor=colors.white
    parrafo = Paragraph('VERDE = TIEMPO EJECUTADO',cabecera2)
    story.append(parrafo)
    story.append(Spacer(0,20))
    parrafo = Paragraph('_'*66,cabecera)
    story.append(parrafo)
    parrafo = Paragraph('FIN DE CUARTO INFORME' + ' '*100 + '('+str(datetime.date.today()) + ')' ,cabecera)
    story.append(parrafo)
    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=letter,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=18,
                            )
    doc.build(story)
    response = HttpResponse(content_type='application/pdf')
    pdf_name = "Reporte.pdf"
    response.write(buff.getvalue())
    buff.close()
    return response

def reporte5_pdf(request,proyecto_id):
    """
    Metodo para generar reporte 5
    :param request: contiene la informacion de la pagina que lo llamo
    :param proyecto_id: id del proyecto del cual se genera el reporte
    :return: reporte en formato pdf
    """
    proyecto_actual= Proyecto.objects.get(id=proyecto_id)
    uh = UserHistory.objects.filter(proyecto = proyecto_actual).order_by('-valor_tecnico')

    estiloHoja = getSampleStyleSheet()
    style = [
        ('GRID',(0,0),(-1,-1),0.5,colors.white),
        ('BOX',(0,0),(-1,-1),2,colors.black),
        ('SPAN',(0,0),(-1,0)),
        ('ROWBACKGROUNDS', (0, 3), (-1, -1), (colors.Color(0.9, 0.9, 0.9),colors.white)),
        ('BACKGROUND', (0, 2), (-1, 2), colors.fidlightblue),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('LINEABOVE',(0,0),(-1,0),1.5,colors.black),
        ('LINEBELOW',(0,0),(-1,0),1.5,colors.black),
        ('SIZE',(0,0),(-1,0),12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.black),
        ]

    story = []
    cabecera = estiloHoja['Heading2']
    cabecera.pageBreakBefore=0
    cabecera.keepWithNext=0
    cabecera.backColor=colors.white
    cabecera.spaceAfter = 0
    cabecera.spaceBefore = 0
    parrafo = Paragraph('',cabecera)
    story.append(parrafo)
    parrafo = Paragraph('QUINTO INFORME DEL'+ '"' +proyecto_actual.nombrelargo+'" : ',cabecera)
    story.append(parrafo)
    parrafo = Paragraph('_'*66,cabecera)
    story.append(parrafo)
    cabecera2 = estiloHoja['Heading1']
    cabecera2.pageBreakBefore=0
    cabecera2.keepWithNext=0
    cabecera2.backColor=colors.white
    parrafo = Paragraph('   ',cabecera2)
    story.append(parrafo)

    ltrabajoequipo = []
    ltrabajoequipo.append(['5. BACKLOG DEL PRODUCTO','', '', ''])
    ltrabajoequipo.append([' ',' ',' ', ' '])
    ltrabajoequipo.append(['NOMBRE','DESCRIPCION','ORDEN', 'ESTADO'])
    for u in uh:
        if u.estado != 'cancelado':
            ltrabajoequipo.append([u.nombre, u.descripcion, u.valor_tecnico, u.estado])

    t=Table( ltrabajoequipo, style=style)
    story.append(t)
    story.append(Spacer(0,20))
    story.append(parrafo)
    parrafo = Paragraph('_'*66,cabecera)
    story.append(parrafo)
    parrafo = Paragraph('FIN DE QUINTO INFORME' + ' '*100 + '('+str(datetime.date.today()) + ')' ,cabecera)
    story.append(parrafo)
    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=letter,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=18,
                            )
    doc.build(story)
    response = HttpResponse(content_type='application/pdf')
    pdf_name = "Reporte.pdf"
    response.write(buff.getvalue())
    buff.close()
    return response


def reporte6_pdf(request,proyecto_id):
    """
    Metodo con el cual se crea el reporte 6 en formato pdf
    :param request: contiene la informacion de la pagino que lo llamo
    :param proyecto_id: id del proyecto del cual se genera el reporte
    :return: reporte en formato pdf
    """
    proyecto_actual= Proyecto.objects.get(id=proyecto_id)
    uh = UserHistory.objects.filter(proyecto = proyecto_actual)

    estiloHoja = getSampleStyleSheet()
    style = [
        ('GRID',(0,0),(-1,-1),0.5,colors.white),
        ('BOX',(0,0),(-1,-1),2,colors.black),
        ('SPAN',(0,0),(-1,0)),
        ('ROWBACKGROUNDS', (0, 3), (-1, -1), (colors.Color(0.9, 0.9, 0.9),colors.white)),
        ('BACKGROUND', (0, 2), (-1, 2), colors.fidlightblue),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('LINEABOVE',(0,0),(-1,0),1.5,colors.black),
        ('LINEBELOW',(0,0),(-1,0),1.5,colors.black),
        ('SIZE',(0,0),(-1,0),12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.black),
        ]

    story = []
    cabecera = estiloHoja['Heading2']
    cabecera.pageBreakBefore=0
    cabecera.keepWithNext=0
    cabecera.backColor=colors.white
    cabecera.spaceAfter = 0
    cabecera.spaceBefore = 0
    parrafo = Paragraph('',cabecera)
    story.append(parrafo)
    parrafo = Paragraph('SEXTO INFORME DEL'+ '"' +proyecto_actual.nombrelargo+'" : ',cabecera)
    story.append(parrafo)
    parrafo = Paragraph('_'*66,cabecera)
    story.append(parrafo)
    cabecera2 = estiloHoja['Heading1']
    cabecera2.pageBreakBefore=0
    cabecera2.keepWithNext=0
    cabecera2.backColor=colors.white
    parrafo = Paragraph('   ',cabecera2)
    story.append(parrafo)
    ltrabajoequipo = []
    ltrabajoequipo.append(['6. SPRINT BACKLOG','', ''])
    ltrabajoequipo.append([' ',' ',''])
    ltrabajoequipo.append(['NOMBRE','ACTIVIDADES', 'ESTADO'])
    for u in uh:
        if u.sprint.estado == 'iniciado':
            ltrabajoequipo.append([u.sprint.nombre,u.nombre, u.sprint.estado])

    t=Table( ltrabajoequipo, style=style)
    story.append(t)
    story.append(Spacer(0,20))
    story.append(parrafo)
    parrafo = Paragraph('_'*66,cabecera)
    story.append(parrafo)
    parrafo = Paragraph('FIN DE SEXTO INFORME' + ' '*100 + '('+str(datetime.date.today()) + ')' ,cabecera)
    story.append(parrafo)
    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=letter,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=60,
                            bottomMargin=18,
                            )
    doc.build(story)
    response = HttpResponse(content_type='application/pdf')
    pdf_name = "Reporte.pdf"
    response.write(buff.getvalue())
    buff.close()
    return response


def finalizar_proyecto(request, proyecto_id):
    """
    Metodo para finalizar Proyecto
    :param request: contiene la informacion de la pagina que lo llamo
    :param proyecto_id: id del proyecto a ser finalizado
    :return: Se finaliza el proyecto
    """
    actual = get_object_or_404(Proyecto, id=proyecto_id)
    actual.estado = '3'
    actual.save()
    return HttpResponseRedirect("/verProyecto/ver&id=" + str(actual.id))

def iniciar_proyecto(request, proyecto_id):

    actual = get_object_or_404(Proyecto, id=proyecto_id)
    rol = Rol.objects.get(nombre = 'Cliente')
    urp = UsuarioRolProyecto.objects.filter(proyecto = actual, rol = rol)
    rol2 = Rol.objects.get(nombre = 'Desarrollador')
    urp2 = UsuarioRolProyecto.objects.filter(proyecto = actual, rol = rol)
    fap = FlujoActividadProyecto.objects.filter(proyecto = actual)
    sprint = Sprint.objects.filter(proyecto = actual)
    if not sprint:
        error = "No se ha creado ningun sprint para este proyecto."
        return render_to_response("proyectos/can_t_init_proyecto.html", {'mensaje': error,'proyecto': actual })
    if not urp:
        error = "No se puede iniciar el proyecto, no se ha asignado ningun Cliente."
        return render_to_response("proyectos/can_t_init_proyecto.html", {'mensaje': error,'proyecto': actual })
    if not fap:
        error = "No se puede iniciar el proyecto, no se ha asignado ningun flujo al Proyecto."
        return render_to_response("proyectos/can_t_init_proyecto.html", {'mensaje': error,'proyecto': actual })
    if not urp2:
        error = "No se puede iniciar el proyecto, no se ha asignado ningun Desarrollador."
        return render_to_response("proyectos/can_t_init_proyecto.html", {'mensaje': error,'proyecto': actual })




    actual.estado = '2'
    actual.save()
    return HttpResponseRedirect("/verProyecto/ver&id=" + str(actual.id))