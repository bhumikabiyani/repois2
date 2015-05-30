from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
# Paginacion en Django
from django.core.paginator import Paginator,EmptyPage,InvalidPage
from django.contrib.auth.decorators import login_required
from django.template import *
from django.contrib import*
from django.template.loader import get_template
from django.forms.formsets import formset_factory
import base64
from SGPA.apps.userhistory.forms import *
from SGPA.apps.flujo.models import *
from SGPA.apps.userhistory.helper import *
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
# Create your views here.

@login_required
def admin_user_history(request,proyecto_id):
    """
    Administracion de User History
    :param request:contiene la informacion sobre la solicitud de la pagina que lo llamo
    :return: admin_user_history.html, pagina en la cual se trabaja con los user history
    """
    user = User.objects.get(username=request.user.username)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyecto).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)

    #-------------------------------------------------------------------
    userRolProy = UsuarioRolProyecto.objects.filter(proyecto=proyecto_id)
    lista = UserHistory.objects.filter(proyecto=proyecto_id)

    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = UserHistory.objects.filter(Q(nombre__icontains = palabra) | Q(estado__icontains = palabra) | Q(tiempo_estimado__icontains = palabra)).order_by('id')
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
            return render_to_response('userhistory/admin_user_history.html',{'lista':lista, 'form': form,
                                                 
                                                        'user':user,
                                                        'proyecto':proyecto,
                                                        'pag': pag,
                                                        'ver_user_history':'ver user history' in permisos,
                                                        'ver_log_userhistory':'ver log user history' in permisos,
							                            'crear_user_history':'crear user history' in permisos
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
    return render_to_response('userhistory/admin_user_history.html',{'lista':lista, 'form':form,
                                                            'user':user,
                                                            'proyecto':proyecto,
                                                            'pag': pag,
                                                            'ver_user_history':'ver user history' in permisos,
                                                            'ver_log_userhistory':'ver log user history' in permisos,
                                                            'crear_user_history':'crear user history' in permisos
                                                            })


@login_required
def crear_user_history(request,proyecto_id):
    """
    Crear un nuevo user history
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param proyecto_id: id del proyecto en el cual se desea crear el User History
    :return:crear_userhistory.html, pagina en la cual se crea los user history
    """
    user = User.objects.get(username=request.user.username)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user,proyecto = proyecto).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)

    #-------------------------------------------------------------------

    if request.method == 'POST':
        form = UserHistoryForm(proyecto_id, request.POST)
        if form.is_valid():
            r = UserHistory()
            r.nombre = form.cleaned_data['nombre']
            r.descripcion = form.cleaned_data['descripcion']
            r.estado = "pendiente"
            r.valor_negocio = form.cleaned_data['valor_negocio']
            r.valor_tecnico = form.cleaned_data['valor_tecnico']
            r.tiempo_estimado = form.cleaned_data['tiempo_estimado']
            # r.encargado =  User.objects.get(username=form.cleaned_data['encargado'])
            # r.flujo = Flujo.objects.get(nombre=form.cleaned_data['flujo'])
            # fap = FlujoActividadProyecto.objects.get(flujo = r.flujo, proyecto = proyecto, orden = 1)
            # r.actividad = fap.actividad
            # r.estadokanban = 'To do'
            # r.sprint = Sprint.objects.get(nombre=form.cleaned_data['sprint'])
            r.proyecto = proyecto
            r.save()
            registrar_log(r,"Creacion",user)
            return HttpResponseRedirect("/userHistory/proyecto&id=" + str(proyecto_id))

    else:
        form = UserHistoryForm(proyecto_id)
    return render_to_response('userhistory/crear_userhistory.html',{'form':form,
                                                            'user':user,
                                                            'proyecto':proyecto,
                                                            'crear_user_history': 'crear user history' in permisos
			      })


def visualizar_user_history(request, userhistory_id):
    """
    Visualiza los detalles del User History
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param userhistory_id: id del user history con el que se trabajara
    :return:verUserHistory.html, pagina en la cual se visualiza los user history
    """
    userHist = get_object_or_404(UserHistory, id=userhistory_id)
    user =  User.objects.get(username=request.user.username)
    proyecto = get_object_or_404(Proyecto, id=userHist.proyecto.id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user,proyecto = proyecto).only('rol')
    comments = Comentarios.objects.filter(userhistory = userHist)
    adjuntos = Adjunto.objects.filter(us = userHist)
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)

    lista = User.objects.all().order_by("id")
    ctx = {'lista':lista,
            'userhistory':userHist,
            'comments':comments,
            'adjuntos': adjuntos,
            'ver_user_history': 'ver user history' in permisos,
            'crear_user_history': 'crear user history' in permisos,
            'mod_user_history': 'modificar user history' in permisos,
            'eliminar_user_history': 'eliminar user history' in permisos,
            'add_comment': 'agregar comentario' in permisos,
            'asignar_encargado': 'asignar encargado' in permisos,
            'asignar_sprint': 'asignar sprint a us' in permisos,
            'asignar_flujo': 'asignar flujo a us' in permisos
	       }
    return render_to_response('userhistory/verUserHistory.html',ctx,context_instance=RequestContext(request))

def mod_user_history(request, userhistory_id):
    """
    Modifica un userhistory
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param userhistory_id: id del userhistory que sera modificado
    :return: mod_user_history.html,pagina en la cual se modificara el User History
    """
    user = User.objects.get(username=request.user.username)
    actual = get_object_or_404(UserHistory, id=userhistory_id)
    proyecto = Proyecto.objects.get(nombrelargo = actual.proyecto)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user,proyecto = proyecto).only('rol')
    permisos_obj = []
    for i in roles:
       permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
       permisos.append(i.nombre)

    #-------------------------------------------------------------------

    if request.method == 'POST':
        form = ModUserHistoryForm(proyecto.id, request.POST)
        if form.is_valid():
            actual.descripcion = form.cleaned_data['descripcion']
            actual.tiempo_estimado = form.cleaned_data['tiempo_estimado']
            actual.valor_tecnico = form.cleaned_data['valor_tecnico']
            actual.valor_negocio = form.cleaned_data['valor_negocio']
            # actual.encargado =  User.objects.get(username=form.cleaned_data['encargado'])
            # actual.flujo = Flujo.objects.get(nombre=form.cleaned_data['flujo'])
            # actual.sprint = Sprint.objects.get(nombre=form.cleaned_data['sprint'])
            actual.save()
            registrar_log(actual,"Modificacion",user)
             #---Enviar Correo----#
            if actual.encargado != None:
                contenido = render_to_string('mailing/modificar_userstorie.html',{'ustorie':actual.nombre,
                                         'owner':user.first_name,'proyecto':proyecto.nombrelargo,
                                         'estado':actual.estado})
                correo = EmailMessage('Notificacion de SGPA', contenido, to=[actual.encargado.email])
                correo.content_subtype = "html"
                correo.send()
            #-------------------#
            return HttpResponseRedirect("/verUserHistory/ver&id=" + str(userhistory_id))
    else:
        form = ModUserHistoryForm(proyecto.id)
        form.fields['descripcion'].initial = actual.descripcion
        form.fields['tiempo_estimado'].initial = actual.tiempo_estimado
        form.fields['valor_tecnico'].initial = actual.valor_tecnico
        form.fields['valor_negocio'].initial = actual.valor_negocio
        # form.fields['encargado'].initial = actual.encargado
        # form.fields['flujo'].initial = actual.flujo
        # form.fields['sprint'].initial = actual.sprint
    return render_to_response("userhistory/mod_user_history.html", {'user':user,
                                                           'form':form,
							   'flujo': actual,
                                                           'mod_user_history':'modificar user history' in permisos
						     })

def borrar_user_history(request, userhistory_id):
    """
    Metodo para eliminar un userhistory
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param userhistory_id: id del user history a ser eliminado
    :return: user_history_confirm_delete.html, pagina en la cual se elimina el user history
    """
    user = User.objects.get(username=request.user.username)
    actual = get_object_or_404(UserHistory, id=userhistory_id)
    proyecto = Proyecto.objects.get(nombrelargo = actual.proyecto)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyecto).only('rol')
    permisos_obj = []
    for i in roles:
       permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
       permisos.append(i.nombre)

    #-------------------------------------------------------------------
    if request.method == 'POST':
        actual.delete()
        return HttpResponseRedirect("/userHistory/proyecto&id=" + str(actual.proyecto_id))
    else:
        if actual.estado == 'doing':
             error = "El User History esta en desarrollo."
             return render_to_response("userhistory/user_history_confirm_delete.html", {'mensaje': error,
                                                                               'flujo':actual,
                                                                               'user':user,
                                                                               'eliminar_user_history':'eliminar user history' in permisos})
    return render_to_response("userhistory/user_history_confirm_delete.html", {'flujo':actual,
                                                                      'user':user,
                                                                      'eliminar_user_history':'eliminar user history' in permisos
								})

def ver_log_user_history(request, userhistory_id):
    """
    Metodo para ver Historial del User Storie
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param userhistory_id: id del user history del cual se desea guardar el historial
    :return: log_user:history.html, pagina en la cual se visualiza el historial
    """
    userHist = get_object_or_404(UserHistory, id=userhistory_id)
    user =  User.objects.get(username=request.user.username)
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = userHist.proyecto).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    historial = Historia.objects.filter(userhistory = userHist).order_by("fecHor_creacion")
    ctx = {'historial':historial,
            'proyecto':userHist.proyecto,
            'userHist':userHist,
            'ver_log_userhistory': 'ver log user history' in permisos
	       }
    return render_to_response('userhistory/log_user_history.html',ctx,context_instance=RequestContext(request))

@login_required
def agregar_comentario(request, userhistory_id):
    """
    Metodo para agregar comentario al User Storie
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param userhistory_id:  id del user history en la cual se desea agregar el comentario
    :return: add_comment.html, pagina en la cual se guarda el comentario
    """
    user = User.objects.get(username=request.user.username)
    us = get_object_or_404( UserHistory, id = userhistory_id)
    proyecto = Proyecto.objects.get(nombrelargo = us.proyecto)
    ussprint = UserHistorySprint.objects.get(userhistory = us, sprint = us.sprint)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyecto).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)

    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = AddCommentForm(us, request.POST, request.FILES)
        if form.is_valid():
            comment = Comentarios()
            comment.asunto = form.cleaned_data['asunto']
            comment.descripcion = form.cleaned_data['descripcion']
            comment.userhistory = us
            comment.horas = form.cleaned_data['horas']
            comment.save()
            ussprint.horas_ejec += comment.horas
            ussprint.save()
            #registrar_log(us,"Trabajo ({Asunto: "+comment.asunto+"} {Descripcion: "+comment.descripcion+"} {Horas: "+comment.horas+"})",user)
            #---Enviar Correo----#
            if us.encargado != None:
                contenido = render_to_string('mailing/agregar_comentario.html',{'ustorie': us.nombre,
                                         'owner':user.first_name,'proyecto':proyecto.nombrelargo,
                                         'comentario':comment.descripcion})
                correo = EmailMessage('Notificacion de SGPA', contenido, to=[us.encargado.email])
                correo.content_subtype = "html"
                correo.send()
            #-------------------#
            return HttpResponseRedirect("/verkanban/ver&id=" + str(us.proyecto.id))
    else:
        form = AddCommentForm(us)

    return render_to_response('userhistory/add_comment.html',{'form':form,
                                                        'user':user,
                                                        'userhistory': us,
                                                        'add_comment':'agregar comentario' in permisos
                                                         })

def asignar_encargado_userhistory(request, userhistory_id):
    """
    Metodo en el cual se asigna encargado al User History
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param userhistory_id: userhistory_id:  id del user history al cual se asignara un encargado
    :return: asignar_encargado.html, pagina en la cual se asigna el encargado
    """
    user = User.objects.get(username=request.user.username)
    actual = get_object_or_404(UserHistory, id=userhistory_id)
    proyecto = Proyecto.objects.get(nombrelargo = actual.proyecto)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user,proyecto = proyecto).only('rol')
    permisos_obj = []
    for i in roles:
       permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
       permisos.append(i.nombre)

    #-------------------------------------------------------------------

    if request.method == 'POST':
        form = AsignarEncargadoUSForm(proyecto.id, request.POST)
        if form.is_valid():
            userEncargado = form.cleaned_data['encargado']
            actual.encargado = User.objects.get(username = userEncargado)
            actual.save()
            registrar_log(actual,"Asignacion de Encargado: "+actual.encargado.username,user)
            #---Enviar Correo----#
            if actual.encargado !=None:
                contenido = render_to_string('mailing/asignar_userstory.html',{'ustorie': actual.nombre,
                                         'owner':user.first_name,'proyecto':proyecto.nombrelargo})
                correo = EmailMessage('Notificacion de SGPA', contenido, to=[actual.encargado.email])
                correo.content_subtype = "html"
                correo.send()
            #-------------------#
            return HttpResponseRedirect("/verUserHistory/ver&id=" + str(userhistory_id))
    else:
        form = AsignarEncargadoUSForm(proyecto.id)
        form.fields['encargado'].initial = actual.encargado
    return render_to_response("userhistory/asignar_encargado.html", {'user':user,
                                                                     'form':form,
                                                                     'userhistory': actual,
                                                                     'asignar_encargado':'asignar encargado' in permisos
						     })

def asignar_sprint_userhistory(request, userhistory_id):
    """
    Metodo en el cual se asigna el User History a un Sprint
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param userhistory_id: id del User History que sera asignado al Sprint
    :return: asignar_sprint.html, pagina en la cual se asigna el user history al sprint
    """
    user = User.objects.get(username=request.user.username)
    actual = get_object_or_404(UserHistory, id=userhistory_id)
    proyecto = Proyecto.objects.get(nombrelargo = actual.proyecto)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user,proyecto = proyecto).only('rol')
    permisos_obj = []
    for i in roles:
       permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
       permisos.append(i.nombre)

    #-------------------------------------------------------------------

    if request.method == 'POST':
        form = AsignarSprintUSForm(proyecto.id, request.POST)
        if form.is_valid():
            sprint = form.cleaned_data['sprint']
            actual.sprint = Sprint.objects.get(nombre = sprint)
            actual.estado = "iniciado"
            res = actual.save()
            ussprint = UserHistorySprint()
            ussprint.userhistory = actual
            ussprint.sprint = actual.sprint
            ussprint.horas_plan = actual.tiempo_estimado
            ussprint.horas_ejec = 0
            ussprint.save()
            registrar_log(actual,"Asignacion de Sprint: "+actual.sprint.nombre,user)
             #---Enviar Correo----#
            if actual.encargado != None:
                contenido = render_to_string('mailing/asignar_sprint.html',{'ustorie': actual.nombre,
                                         'owner':user.first_name,'proyecto':proyecto.nombrelargo,
                                         'sprint':sprint})
                correo = EmailMessage('Notificacion de SGPA', contenido, to=[actual.encargado.email])
                correo.content_subtype = "html"
                correo.send()
            #-------------------#
            return HttpResponseRedirect("/verUserHistory/ver&id=" + str(userhistory_id))
    else:
        form = AsignarSprintUSForm(proyecto.id)
        form.fields['sprint'].initial = actual.sprint
    return render_to_response("userhistory/asignar_sprint.html", {'user':user,
                                                                     'form':form,
                                                                     'userhistory': actual,
                                                                     'asignar_sprint':'asignar sprint a us' in permisos
                                                                     })

def asignar_flujo_userhistory(request, userhistory_id):
    """
    Metodo en el cual se asigna el user history al Flujo
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param userhistory_id: id del User History que sera asignado al Flujo
    :return: asignar_flujo.html, pagina en la cual se asigna el user history al Flujo
    """
    user = User.objects.get(username=request.user.username)
    actual = get_object_or_404(UserHistory, id=userhistory_id)
    proyecto = Proyecto.objects.get(nombrelargo = actual.proyecto)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user,proyecto = proyecto).only('rol')
    permisos_obj = []
    for i in roles:
       permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
       permisos.append(i.nombre)

    #-------------------------------------------------------------------

    if request.method == 'POST':
        form = AsignarFlujoUSForm(proyecto.id, request.POST)
        if form.is_valid():
            flujo = form.cleaned_data['flujo']
            actual.flujo = Flujo.objects.get(nombre = flujo)
            fap = FlujoActividadProyecto.objects.get(flujo = actual.flujo, proyecto = proyecto, orden = 1)
            actual.actividad = fap.actividad
            actual.estadokanban = 'to-do'
            actual.save()
            registrar_log(actual,"Asignacion de Flujo: "+actual.flujo.nombre,user)
             #---Enviar Correo----#
            if actual.encargado != None:
                contenido = render_to_string('mailing/asignar_flujo.html',{'ustorie': actual.nombre,
                                         'owner':user.first_name,'proyecto':proyecto.nombrelargo,
                                         'flujo':flujo})
                correo = EmailMessage('Notificacion de SGPA', contenido, to=[actual.encargado.email])
                correo.content_subtype = "html"
                correo.send()
            #-------------------#
            return HttpResponseRedirect("/verUserHistory/ver&id=" + str(userhistory_id))
    else:
        form = AsignarFlujoUSForm(proyecto.id)
        form.fields['flujo'].initial = actual.flujo
    return render_to_response("userhistory/asignar_flujo.html", {'user':user,
                                                                     'form':form,
                                                                     'userhistory': actual,
                                                                     'asignar_flujo':'asignar flujo a us' in permisos
						     })

# def archivos_adjuntos(request, userhistory_id):
#     """
#     Metodo en el cual se adjuntan archivos al User History
#     :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
#     :param userhistory_id: id del user history al cual se le adjunta el archivo
#     :return: archivos_adjuntosOriginal.html, pagina en el cualse adjunta archivo
#     """
#     user = User.objects.get(username=request.user.username)
#     us = get_object_or_404( UserHistory, id = userhistory_id)
#     proyecto = Proyecto.objects.get(nombrelargo = us.proyecto)
#     #Validacion de permisos---------------------------------------------
#     roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyecto).only('rol')
#     permisos_obj = []
#     for i in roles:
#         permisos_obj.extend(i.rol.permisos.all())
#     permisos = []
#     for i in permisos_obj:
#         permisos.append(i.nombre)
#
#     #-------------------------------------------------------------------
#     if request.method == 'POST':
#         form = ArchivosAdjuntosForm(us,request.POST, request.FILES)
#         if form.is_valid():
#             newdoc = ArchivosAdjuntos(nombre = request.POST['nombre'],docfile = request.FILES['docfile'], userhistory = us)
#             newdoc.save(form)
#             registrar_log(us,"Archivo Adjunto (Nombre: "+newdoc.nombre+")",user)
#         return HttpResponseRedirect("/verkanban/ver&id=" + str(us.proyecto.id))
#     else:
#         form = ArchivosAdjuntosForm(us)
#     return render(request, 'userhistory/archivos_adjuntosOriginal.html', {'form': form, 'user':user, 'userhistory':us, 'adjuntar_archivos':'adjuntar archivos' in permisos})

    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = ArchivosAdjuntosForm(us,request.POST, request.FILES)
        if form.is_valid():
            newdoc = ArchivosAdjuntos(nombre = request.POST['nombre'],docfile = request.FILES['docfile'], userhistory = us)
            newdoc.save(form)
            registrar_log(us,"Archivo Adjunto (Nombre: "+newdoc.nombre+")",user)
        return HttpResponseRedirect("/verkanban/ver&id=" + str(us.proyecto.id))
    else:
        form = ArchivosAdjuntosForm(us)
    return render(request, 'userhistory/archivos_adjuntos.html', {'form': form, 'user':user, 'userhistory':us, 'adjuntar_archivos':'adjuntar archivos' in permisos})

def cambiar_estados(request, userhistory_id):
    """
    Metodo en el cual se cambia de estado kanban al us
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param userhistory_id: id del User History que sera cambiado de estado
    :return: cambiar_estados.html, pagina en la cual se cambia de estado al user history
    """
    user = User.objects.get(username=request.user.username)
    actual = get_object_or_404(UserHistory, id=userhistory_id)
    proyecto = Proyecto.objects.get(nombrelargo = actual.proyecto)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user,proyecto = proyecto).only('rol')
    permisos_obj = []
    for i in roles:
       permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
       permisos.append(i.nombre)

    #-------------------------------------------------------------------

    if request.method == 'POST':
        form = CambiarEstadosUSForm(request.POST)
        if form.is_valid():
            actual.estadokanban =form.cleaned_data['estadokanban']
            actual.save()
            registrar_log(actual,"Cambio de Estado: "+actual.estadokanban,user )
            return HttpResponseRedirect("/verkanban/ver&id=" + str(actual.proyecto.id))
    else:
        form = CambiarEstadosUSForm()
        form.fields['estadokanban'].initial = actual.estadokanban
    return render_to_response("userhistory/cambiar_estados.html", {'user':user,
                                                                     'form':form,
                                                                     'userhistory': actual,
                                                                     'asignar_encargado':'asignar encargado' in permisos
						     })


def cambiar_actividad(request, userhistory_id):
    """
    Metodo en el cual se cambia de actividad al us
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param userhistory_id: id del User History que sera cambiado de actividad
    :return: cambiar_actividad.html, pagina en la cual se cambia de actividad al user history
    """
    user = User.objects.get(username=request.user.username)
    actual = get_object_or_404(UserHistory, id=userhistory_id)
    proyecto = Proyecto.objects.get(nombrelargo = actual.proyecto)
    userhistory = UserHistory.objects.get(id = userhistory_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user,proyecto = proyecto).only('rol')
    permisos_obj = []
    for i in roles:
       permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
       permisos.append(i.nombre)

    #-------------------------------------------------------------------

    if request.method == 'POST':
        form = CambiarActividadUSForm(userhistory.id, request.POST)
        if form.is_valid():
            actividad = form.cleaned_data['actividad']
            actual.actividad = Actividad.objects.get(nombre = actividad)
            actual.estadokanban = "to-do"
            actual.save()
            registrar_log(actual,"Cambio de Actividad: "+actual.actividad.nombre,user)
             #---Enviar Correo----#
            if actual.encargado != None:
                contenido = render_to_string('mailing/asignar_flujo.html',{'ustorie': actual.nombre,
                                         'owner':user.first_name,'proyecto':proyecto.nombrelargo,
                                         'actividad':actividad})
                correo = EmailMessage('Notificacion de SGPA', contenido, to=[actual.encargado.email])
                correo.content_subtype = "html"
                correo.send()
            #-------------------#
            return HttpResponseRedirect("/verkanban/ver&id=" + str(userhistory.proyecto.id))

    else:
        form = CambiarActividadUSForm(userhistory.id)
        form.fields['actividad'].initial = actual.actividad
    return render_to_response("userhistory/cambiar_actividad.html", {'user':user,
                                                                     'form':form,
                                                                     'userhistory': actual,
                                                                     'asignar_flujo':'asignar flujo a us' in permisos
                                                                     })

def finalizar_userhistory(request, userhistory_id):

    actual = get_object_or_404(UserHistory, id=userhistory_id)
    proyecto = Proyecto.objects.get(nombrelargo = actual.proyecto)
    actual.estado = 'finalizado'
    actual.save()
    return HttpResponseRedirect("/verkanban/ver&id=" + str(actual.proyecto.id))

@login_required
def add_adjunto(request, userhistory_id):
    user = User.objects.get(username=request.user.username)
    us = get_object_or_404(UserHistory, id=userhistory_id)
    AdjuntoFormSet = formset_factory(AdjuntoForm)
    if request.method == 'POST':
        formset = AdjuntoFormSet(request.POST, request.FILES)
        if formset.is_valid():
            archivos = Adjunto.objects.filter(us= us)
            archivos_nuevos = request.FILES.values()
            for f in archivos_nuevos:
                nuevo = Adjunto()
                nuevo.nombre =f
                nuevo.tamano = f.size
                nuevo.mimetype = f.content_type
                nuevo.contenido = base64.b64encode(f.read())
                nuevo.us = us
                nuevo.save()
            return HttpResponseRedirect("/verkanban/ver&id=" + str(us.proyecto.id))
        #return render_to_response('error.html', {'form': form})
    else:
        formset = AdjuntoFormSet()
        return render_to_response('userhistory/crear_adjunto.html', {'formset':formset,'us':us,
                                                                                      'user':user})


@login_required
def retornar_archivo(request, userhistory_id, arch_id):
    user = User.objects.get(username=request.user.username)
    us = get_object_or_404(UserHistory, id=userhistory_id)
    adjunto = get_object_or_404(Adjunto, id=arch_id)
    if request.method == 'GET':
        respuesta = HttpResponse(base64.b64decode(adjunto.contenido), content_type= adjunto.mimetype)
        respuesta['Content-Disposition'] = 'attachment; filename=' + adjunto.nombre
        #respuesta['Content-Length'] = adjunto.tamano
        return respuesta
    return HttpResponseRedirect("/verkanban/ver&id=" + str(us.proyecto.id))


