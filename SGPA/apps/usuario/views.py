# -*- coding: utf-8 -*-
import base64
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from SGPA.apps.roles.forms import AsignarRolesForm, AsignarRolesProyForm
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
from SGPA.apps.usuario.forms import *
from SGPA.apps.usuario.models import *
from SGPA.apps.usuario.helper import *
from django.contrib import messages

@login_required
def crearUsuario_view(request):
    """
    :param request: contiene los datos de la pagina que lo llamo
    :return: crearUsuario.html, pagina en la cual se crea el usuario
    Metodo para crear un nuevo usuario
    """
    user = User.objects.get(username=request.user.username)
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
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
            u = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email,password=password_one)
            u.save()
            return HttpResponseRedirect("/admin")
    else:
        ctx = {'form':form,
               'user':user,
               'crear_usuario': 'crear usuario' in permisos}
        return 	render_to_response('usuario/crearUsuario.html',ctx,context_instance=RequestContext(request))
    ctx = {'form':form,
           'user':user,
           'crear_usuario': 'crear usuario' in permisos}
    return render_to_response('usuario/crearUsuario.html',ctx,context_instance=RequestContext(request))

def lista(request, tipo):
    """
    Metodo para listar usuarios
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param tipo: contiene el tipo de objeto a listar
    :return: lista.html, pagina en la que se lista los objetos
    """
    user = User.objects.get(username=request.user.username)
    if tipo == 'usuarios':
        lista = User.objects.all()
    else:
        return render_to_response('error.html');
    return render_to_response('lista.html',{'lista':lista, 'user':user, 'tipo':tipo})

@login_required
def admin_usuarios(request):
    """
    Administracion general de usuarios
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :return:usuarios.html, pagina en la cual se trabaja con los usuarios
    """
    user = User.objects.get(username=request.user.username)
    permisos = get_permisos_sistema(user)
    lista = User.objects.all().order_by("id")
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = User.objects.filter(Q(username__icontains = palabra) | Q(first_name__icontains = palabra) | Q(last_name__icontains = palabra) | Q(email__icontains = palabra)).order_by('id')
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
            return render_to_response('usuario/usuarios.html',{'pag': pag,
                                                               'form': form,
                                                               'lista':lista,
                                                               'user':user,
							       'ver_usuarios': 'ver usuarios' in permisos,
							       'crear_usuario': 'crear usuario' in permisos,})
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
    return render_to_response('usuario/usuarios.html',{ 'pag':pag,
                                                               'form': form,
                                                               'lista':lista,
                                                               'user':user,
							       'ver_usuarios': 'ver usuarios' in permisos,
							       'crear_usuario': 'crear usuario' in permisos,})

@login_required
def mod_user(request, usuario_id):
    """
    Modifica los datos de un usuario.
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param usuario_id: contine el id del usuario a modificar
    :return: mod_usuario.html, pagina en la que se modifica datos del usuario
    """
    user = User.objects.get(username=request.user.username)
    
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)  
    
    usuario = get_object_or_404(User, id=usuario_id)
    if request.method == 'POST':
        form = ModUsuariosForm(request.POST)
        if form.is_valid():
            usuario.first_name = form.cleaned_data['first_name']
            usuario.last_name = form.cleaned_data['last_name']
            usuario.email = form.cleaned_data['email']
            usuario.save()
            return HttpResponseRedirect("/visualizar/ver&id=" + str(usuario_id))
    else:
        form = ModUsuariosForm(initial={'first_name':usuario.first_name, 'last_name': usuario.last_name,'email':usuario.email})
    return render_to_response('usuario/mod_usuario.html',{'form':form, 
                                                          'user':user, 
                                                          'usuario':usuario, 
                                                          'mod_usuario': 'modificar usuario' in permisos
							})

@login_required
def eliminar_usuario(request, usuario_id):
    """
    Elimina los datos de un usuario.
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param usuario_id: contine el id del usuario a eliminar
    :return: se cambia el estado del usuario a desactivado
    """
    user = User.objects.get(id=usuario_id)
    user.is_active = False
    nombre = user.username
    user.save()
    messages.error(request, 'El usuario "' + nombre + '" ha sido eliminado')
    return HttpResponseRedirect("/visualizar/ver&id=" + str(usuario_id))

@login_required
def activar_usuario(request, usuario_id):
    """
    vista utilizada para activar un usuario que fue dado de baja
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param usuario_id: contine el id del usuario que fue dado de baja
    :return: se activa al usuario que se ha dado de baja
    """
    user = User.objects.get(id=usuario_id)
    user.is_active = True
    nombre = user.username
    user.save()
    messages.error(request, 'El usuario "' + nombre + '" ha sido restablecido')
    return HttpResponseRedirect("/visualizar/ver&id=" + str(usuario_id))



@login_required
def cambiar_password(request):
    """
    vista utilizada para cambiar la contraseña del usuario autenticado
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :return: cambiar _password.html, pagina para cambiar la contraseña del usuario autenticado
    """
    user = User.objects.get(username=request.user.username)
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            if request.user.check_password(form.cleaned_data['passwordactual'])==True:
                user.set_password(form.cleaned_data['password1'])
                user.save()
                return HttpResponseRedirect("/")
    else:
        form = CambiarPasswordForm()
    return render_to_response('usuario/cambiar_password.html', {'form': form, 'user': user})

def visualizar_usuario(request, usuario_id):
     """
    vista utilizada para listar los usuario del sistema
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param usuario_id: contiene el id del usuario
    :return: se lista todos los usuarios del sistema
    """
     usuario = User.objects.get(id=usuario_id)
     user=  User.objects.get(username=request.user.username)
     permisos = get_permisos_sistema(user)
     lista = User.objects.all().order_by("id")
     ctx = {'lista':lista,
            'usuario':usuario,
            'ver_usuarios': 'ver usuarios' in permisos,
            'crear_usuario': 'crear usuario' in permisos,
            'mod_usuario': 'modificar usuario' in permisos,
            'eliminar_usuario': 'eliminar usuario' in permisos,
            'asignar_rol': 'asignar rol' in permisos}
     return render_to_response('usuario/verUsuario.html',ctx,context_instance=RequestContext(request))


@login_required
def asignar_roles_sistema(request, usuario_id):
    """
    Asigna Roles de Sistema a Usuario
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param usuario_id: contiene el id del usuario al que se le va a asignar el rol
    :return: asignar_roles.html, pagina que muestra las opciones para asignar rol del sistema
    """
    user = User.objects.get(username=request.user.username)
    permisos = get_permisos_sistema(user)
    usuario = get_object_or_404(User, id=usuario_id)
    lista_roles = UsuarioRolSistema.objects.filter(usuario = usuario)
    if request.method == 'POST':
        form = AsignarRolesForm(1, request.POST)
        if form.is_valid():
            lista_nueva = form.cleaned_data['roles']
            for i in lista_roles:
                i.delete()
            for i in lista_nueva:
                nuevo = UsuarioRolSistema()
                nuevo.usuario = usuario
                nuevo.rol = i
                nuevo.save()
            return HttpResponseRedirect("/visualizar/ver&id=" + str(usuario_id))
    else:
        if usuario.id == 1:
            error = "No se puede editar roles sobre el superusuario."
            return render_to_response("usuario/asignar_roles.html", {'mensaje': error,
                                                                            'usuario':usuario,
                                                                            'user': user,
                                                                            'asignar_rol': 'asignar rol' in permisos
							          })
        dict = {}
        for i in lista_roles:
            print i.rol
            dict[i.rol.id] = True
        form = AsignarRolesForm(1,initial = {'roles': dict})
    return render_to_response("usuario/asignar_roles.html", {'form':form, 'usuario':usuario, 'user':user, 'asignar_rol': 'asignar rol' in permisos
})

@login_required
def asignar_roles_proyecto(request, usuario_id):
     """
    Asigna Roles de Proyecto a Usuario
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param usuario_id: contiene el id del usuario al que se le va a asignar el rol
    :return: asignar_roles_proyecto.html, pagina que muestra las opciones para asignar rol de proyecto
    """
     user = User.objects.get(username=request.user.username)
     permisos = get_permisos_sistema(user)
     usuario = get_object_or_404(User, id=usuario_id)
     lista_roles = UsuarioRolSistema.objects.filter(usuario = usuario)
     if request.method == 'POST':
         form = AsignarRolesProyForm(2, request.POST)
         if form.is_valid():
             lista_nueva = form.cleaned_data['roles']
             for i in lista_roles:
                 i.delete()
             for i in lista_nueva:
                 nuevo = UsuarioRolSistema()
                 nuevo.usuario = usuario
                 nuevo.rol = i
                 nuevo.save()
                 return HttpResponseRedirect("/visualizar/ver&id=" + str(usuario_id))
         else:
             if usuario.id == 1:
                 error = "No se puede editar roles sobre el superusuario."
                 return render_to_response("usuario/asignar_roles.html", {'mensaje': error,
                                                                          'usuario':usuario,
                                                                          'user': user,
                                                                          'asignar_rol': 'asignar rol' in permisos
                                                                          })
             dict = {}
             for i in lista_roles:
                 print i.rol
                 dict[i.rol.id] = True
             form = AsignarRolesProyForm(2,initial = {'roles': dict})
             return render_to_response("usuario/asignar_roles_proyecto.html", {'form':form, 'usuario':usuario, 'user':user, 'asignar_rol': 'asignar rol' in permisos
})
