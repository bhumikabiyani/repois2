# -*- coding: utf-8 -*-
import base64
from django.core.context_processors import csrf
from django.db.models import Max
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
    usuarioPorProyecto = UsuarioRolProyecto.objects.filter(usuario = user.id)
    proys = []
    for rec in usuarioPorProyecto:
        if not rec.proyecto in proys:
            proys.append(rec.proyecto.id)
    print proys
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
            userLider = User.objects.get(username=form.cleaned_data['usuario_lider'])
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
    """Visualiza Datos de un Proyecto y muestra las operaciones que puede ejecutar"""
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
           'asignar_flujo' : 'asignar flujo' in permisosProy,
           'eliminar_miembro' : 'eliminar miembro' in permisosProy,
           'asignar_actividades_proyecto' : 'asignar actividades proyecto' in permisosProy
           }
    return render_to_response('proyectos/verProyecto.html', ctx, context_instance=RequestContext(request))


def mod_proyecto(request, proyecto_id):
    """Modifica un Proyecto"""
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
            actual.usuario_lider = User.objects.get(username=form.cleaned_data['usuario_lider'])
            actual.estado = form.cleaned_data['estado']
            actual.cantidad = form.cleaned_data['cantidad']
            actual.save()
            userRolProyActual = UsuarioRolProyecto.objects.filter(proyecto=proyecto_id, rol=2)
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
    """Visualiza Datos de un Proyecto y muestra las operaciones que puede ejecutar"""
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
    ctx = {'flujo':flujo,
           'proyecto':proyecto,
           'actividades':actDict,
           'ultActividad':ultActividad,
           'ver_flujo': 'ver flujo' in permisos,
           'asignar_actividades_proyecto': 'asignar actividades proyecto' in permisos
       }
    return render_to_response('proyectos/admin_actividades_proyecto.html', ctx, context_instance=RequestContext(request))

def subir_actividad_proyecto(request, flujo_id, actividad_id, proyecto_id):

    flujos = get_object_or_404(Flujo, id=flujo_id)
    actActual = FlujoActividadProyecto.objects.get(flujo = flujo_id, actividad = actividad_id)
    actSig = FlujoActividadProyecto.objects.get(flujo = flujo_id, orden = (int(actActual.orden)-1))
    actActual.orden = int(actActual.orden) - 1
    actSig.orden = int(actSig.orden) + 1
    actActual.save()
    actSig.save()
    return HttpResponseRedirect("/verActividadesProy/flujo&id=%s&&proyecto&id=%s/" %(flujo_id,proyecto_id))

def bajar_actividad_proyecto(request, flujo_id, actividad_id, proyecto_id):

    flujos = get_object_or_404(Flujo, id=flujo_id)
    actActual = FlujoActividadProyecto.objects.get(flujo = flujo_id, actividad = actividad_id)
    actSig = FlujoActividadProyecto.objects.get(flujo = flujo_id, orden = (int(actActual.orden)+1))
    actActual.orden = int(actActual.orden) + 1
    actSig.orden = int(actSig.orden) - 1
    actActual.save()
    actSig.save()
    return HttpResponseRedirect("/verActividadesProy/flujo&id=%s&&proyecto&id=%s/" %(flujo_id,proyecto_id))

                                                                  })
@login_required
def visualizar_kanban(request, flujo_id, proyecto_id):
    """Metodo para asignar Flujo a Proyecto"""
    user = User.objects.get(username=request.user.username)
    proy = Proyecto.objects.get(id = proyecto_id)
    #Validacion de permisos---------------------------------------------
    #roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proy).only('rol')
    #permisos_obj = []
    #for i in roles:
    #    permisos_obj.extend(i.rol.permisos.all())
    #permisos = []
    #for i in permisos_obj:
    #    permisos.append(i.nombre)
    #print permisos
    #-------------------------------------------------------------------
    proyactual = get_object_or_404(Proyecto, id=proyecto_id)
    flujoactual = get_object_or_404(Flujo, id=flujo_id)
    actividades = FlujoActividadProyecto.objects.filter(flujo=flujoactual, proyecto =proyactual)
    return render_to_response("proyectos/verkanban.html", {
                                                                  'proyecto': proyactual,
                                                                  'flujo': flujoactual,
                                                                  'user':user,
                                                                  'actividades':actividades

                                                                  })