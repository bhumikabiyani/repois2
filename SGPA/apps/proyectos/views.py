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
from SGPA.apps.proyectos.forms import *
from SGPA.apps.proyectos.models import *
from SGPA.apps.proyectos.helper import *

# @login_required
# def admin_proyectos(request):
#     """Administracion general de proyectos"""
#     user = User.objects.get(username=request.user.username)
#     permisos = get_permisos_sistema(user)
#     return render_to_response('proyectos/proyectos.html',{'user':user,
#                                                   'crear_proyecto': 'crear proyecto' in permisos}
#                                                   )

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
            lista = Proyecto.objects.filter(Q(nombrelargo__icontains = palabra) | Q(descripcion__icontains = palabra) | Q(usuario_lider__icontains = palabra)).order_by('id')
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
            return render_to_response('proyectos/proyectos.html',{'pag': pag,
                                                        'form': form,
                                                        'lista':lista,
                                                        'user':user,
                                                        'ver_proyectos':'ver proyectos' in permisos,
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
    return render_to_response('proyectos/proyectos.html',{'lista':lista, 'form':form,
                                                            'user':user,
                                                            'pag': pag,
                                                            'ver_proyectos':'ver proyectos' in permisos,
                                                            'crear_proyecto': 'crear proyecto' in permisos,
    							  })
@login_required
def admin_roles_proy(request):
    """Administracion de roles de proyecto"""
    user = User.objects.get(username=request.user.username)
    permisos = get_permisos_sistema(user)
    lista = Rol.objects.filter(categoria=2).order_by('id')
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Rol.objects.filter(Q(categoria = 2), Q(nombre__icontains = palabra) | Q(descripcion__icontains = palabra) | Q(usuario_creador__username__icontains = palabra)).order_by('id')
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
            return render_to_response('roles/roles_sistema.html',{'lista':lista,'form':form,
                                                        'user':user,
						        'pag': pag,
                                                        'ver_rol':'ver rol' in permisos,
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
    return render_to_response('roles/roles_proyecto.html',{'lista':lista,'form':form,
                                                        'user':user,
						        'pag': pag,
                                                        'ver_rol':'ver rol' in permisos,
                                                        'crear_proyecto': 'crear proyecto' in permisos,
                                                           })

@login_required
def crear_proyecto(request):
    """Agrega un nuevo proyecto"""
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
        form = ProyectosForm(request.POST)
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
            proy.save()
        return HttpResponseRedirect("/proyectos")
    else:
        form = ProyectosForm()
    return render_to_response('proyectos/crear_proyecto.html', {'form': form,
                                                            'user': user,
                                                            'crear_proyecto': 'crear proyecto' in permisos
                                                            })

def visualizar_proyectos(request, proyecto_id):
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        user=  User.objects.get(username=request.user.username)
        permisos = get_permisos_sistema(user)
        lista = User.objects.all().order_by("id")
        ctx = {'lista':lista,
               'proyecto': proyecto,
               'ver_proyectos': 'ver proyectos' in permisos,
               'crear_proyecto': 'crear proyecto' in permisos,
               'mod_proyecto': 'modificar proyecto' in permisos,
               'eliminar_proyecto': 'eliminar proyecto' in permisos,
	       'asignar_miembros' : 'asignar proyectos' in permisos
	       }
	return render_to_response('proyectos/verProyecto.html',ctx,context_instance=RequestContext(request))

def mod_proyecto(request, proyecto_id):
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
    if request.method == 'POST':
        form = ModProyectoForm(request.POST)
        if form.is_valid():
            actual.descripcion = form.cleaned_data['descripcion']
            actual.save()
            return HttpResponseRedirect("/verProyecto/ver&id=" + str(proyecto_id))
    else:
        form = ModProyectoForm()
        form.fields['descripcion'].initial = actual.descripcion
    return render_to_response("proyectos/mod_proyecto.html", {'user':user,
                                                           'form':form,
                                                           'proyecto': actual,
                                                           'mod_proyecto':'modificar proyecto' in permisos
						     })

# @login_required
# def asignar_roles_sistema(request, usuario_id):
#     """Asigna roles de sistema a un usuario"""
#     user = User.objects.get(username=request.user.username)
#     permisos = get_permisos_sistema(user)
#     usuario = get_object_or_404(User, id=usuario_id)
#     lista_roles = UsuarioRolSistema.objects.filter(usuario = usuario)
#     print lista_roles
#     if request.method == 'POST':
#         form = AsignarRolesForm(1, request.POST)
#         if form.is_valid():
#             lista_nueva = form.cleaned_data['roles']
#             for i in lista_roles:
#                 i.delete()
#             for i in lista_nueva:
#                 nuevo = UsuarioRolSistema()
#                 nuevo.usuario = usuario
#                 nuevo.rol = i
#                 nuevo.save()
#             return HttpResponseRedirect("visualizar/ver&id=" + str(usuario_id))
#     else:
#         if usuario.id == 1:
#             error = "No se puede editar roles sobre el superusuario."
#             return render_to_response("usuario/asignar_roles.html", {'mensaje': error,
#                                                                             'usuario':usuario,
#                                                                             'user': user,
#                                                                             'asignar_rol': 'asignar rol' in permisos
# 							          })
#         dict = {}
#         for i in lista_roles:
#             print i.rol
#             dict[i.rol.id] = True
#         form = AsignarRolesForm(1,initial = {'roles': dict})
#     return render_to_response("roles/asignar_roles.html", {'form':form, 'usuario':usuario, 'user':user, 'asignar_rol': 'asignar rol' in permisos
# })

@login_required
def admin_permisos(request, rol_id):
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
    actual = get_object_or_404(Rol, id=rol_id)
    if request.method == 'POST':
        if actual.categoria == 1:
            form = PermisosForm(request.POST)
        else:
            form = PermisosProyectoForm(request.POST)
        if form.is_valid():
               actual.permisos.clear()
               if actual.categoria == 1:
                  lista = form.cleaned_data['permisos']
                  for i in lista:
                    nuevo = RolPermiso()
                    nuevo.rol = actual
                    nuevo.permiso = i
                    nuevo.save()
               else:
                    lista_req = form.cleaned_data['permisos1']
                    lista_dis = form.cleaned_data['permisos2']
                    lista_impl = form.cleaned_data['permisos3']
                    for i in lista_req:
                      nuevo = RolPermiso()
                      nuevo.rol = actual
                      nuevo.permiso = i
                    #nuevo.fase = Fase.objects.get(pk=1)
                      nuevo.save()
                    for i in lista_dis:
                      nuevo = RolPermiso()
                      nuevo.rol = actual
                      nuevo.permiso = i
                    #nuevo.fase = Fase.objects.get(pk=2)
                      nuevo.save()
                    for i in lista_impl:
                      nuevo = RolPermiso()
                      nuevo.rol = actual
                      nuevo.permiso = i
                    #nuevo.fase = Fase.objects.get(pk=3)
                      nuevo.save()
        return HttpResponseRedirect("/verRol/ver&id=" + str(rol_id))
    else:
        if actual.categoria == 1:
            dict = {}
         
            for i in actual.permisos.all():
                dict[i.id] = True
            form = PermisosForm(initial={'permisos': dict})
        else:
	 
            dict1 = {}
            for i in actual.permisos.all():
                dict1[i.id] = True

            dict2 = {}
            for i in actual.permisos.filter():
                dict2[i.id] = True
            dict3 = {}
            for i in actual.permisos.filter():
                dict3[i.id] = True
            form = PermisosProyectoForm(initial={'permisos1': dict1, 'permisos2': dict2, 'permisos3': dict3})
    return render_to_response("roles/admin_permisos.html", {'form': form, 
                                                                  'roles': actual, 
                                                                  'user':user,
                                                                  })

@login_required 
def borrar_rol(request, rol_id):
    """Borra un rol con las comprobaciones de consistencia"""
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
    #-------------------------------------------------------
    actual = get_object_or_404(Rol, id=rol_id)
    #Obtener todas las posibles dependencias
    if actual.categoria == 1:
        relacionados = UsuarioRolSistema.objects.filter(rol = actual).count()
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
                                                                              'rol':actual, 
                                                                              'user':user,
                                                                              'eliminar_rol':'eliminar rol' in permisos
									})
        # if relacionados > 0:
        #     error = "El rol se esta utilizando."
        #     return render_to_response("roles/rol_confirm_delete.html", {'mensaje': error,
        #                                                                       'rol':actual,
        #                                                                       'user':user,
        #                                                                       'eliminar_rol':'eliminar rol' in permisos
			# 						})
    return render_to_response("roles/rol_confirm_delete.html", {'rol':actual, 
                                                                      'user':user, 
                                                                      'eliminar_rol':'eliminar rol' in permisos
								})

