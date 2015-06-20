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
from SGPA.apps.sprint.forms import *
from SGPA.apps.usuario.models import *
from SGPA.apps.sprint.helper import *
from datetime import datetime, date, time, timedelta
from dateutil import rrule
# Create your views here.

def dateTimeViewBootstrap2(request):

    if request.method == 'POST':

        form = SprintForm(request.POST)
        if form.is_valid():
            return render(request, 'sprint/crear_sprint.html', {
                'form': form,'bootstrap':2
            })
    else:
        if request.GET.get('id',None):
            form = SprintForm(instance=SprintForm.objects.get(id=request.GET.get('id',None)))
        else:
            form = SprintForm()

    return render(request, 'sprint/crear_sprint.html', {
             'form': form,'bootstrap':2
            })

@login_required
def admin_sprint(request,proyecto_id):
    """
    Administracion general de Sprint
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param proyecto_id: contiene el id del proyecto al cual esta relacionado el sprint
    :return:sprint.html, pagina en la cual se trabaja con los sprint
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

    lista = Sprint.objects.filter(proyecto=proyecto_id).order_by('fecha_inicio')
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            palabra = form.cleaned_data['filtro']
            lista = Sprint.objects.filter(Q(nombre__icontains = palabra) | Q(descripcion__icontains = palabra)).order_by('id')
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
            proyPend = False
            if proyecto.estado == 1:
                proyPend = True
            return render_to_response('sprint/sprint.html',{'lista':lista, 'form': form,
                                                            'user':user,
                                                            'proyecto':proyecto,
                                                            'proyPend':proyPend,
                                                            'pag': pag,
                                                            'ver_sprint':'ver sprint' in permisos,
                                                            'crear_sprint':'crear sprint' in permisos
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
    proyPend = False
    if proyecto.estado == 1:
        proyPend = True
    return render_to_response('sprint/sprint.html',{'lista':lista, 'form':form,
                                                            'user':user,
                                                            'proyecto':proyecto,
                                                            'proyPend':proyPend,
                                                            'pag': pag,
                                                            'ver_sprint':'ver sprint' in permisos,
                                                            'crear_sprint':'crear sprint' in permisos
							})

@login_required
def crear_sprint(request, proyecto_id):
    """
    Metodo para crear un nuevo sprint
    :param request: contiene los datos de la pagina que lo llamo
    :param proyecto_id: contiene el id del proyecto al cual esta relacionado el sprint a crearse
    :return: crearSprint.html, pagina en la cual se crea el sprint

    """

    user = User.objects.get(username=request.user.username)
    proyecto = get_object_or_404(Proyecto, id = proyecto_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyecto).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    #-------------------------------------------------------------------
    if proyecto.estado ==  1:
    	if request.method == 'POST':
		form = SprintForm(proyecto_id, request.POST)
        	if form.is_valid():
     	     	   r = Sprint()
            	   r.nombre = form.cleaned_data['nombre']
                   r.descripcion = form.cleaned_data['descripcion']
                   r.fecha_inicio = form.cleaned_data['fecha_inicio']
                   r.fecha_fin = form.cleaned_data['fecha_fin']
                   r.proyecto = proyecto
                   r.estado = "planificacion"
                   r.save()
		   return HttpResponseRedirect("/sprint/sprint&id="+ str(proyecto_id))
    	else:
        		form = SprintForm(proyecto_id)
    	return render_to_response('sprint/crear_sprint.html', {'form':form,
                                                            'user':user,
                                                            'proyecto' : proyecto,
                                                            'crear_sprint': 'crear sprint' in permisos
				})
    return HttpResponseRedirect("/sprint/sprint&id="+ str(proyecto_id))

def visualizar_sprint(request, sprint_id):
    """
    vista utilizada para listar los sprint
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param sprint_id: contiene el id del sprint
    :return: se lista todos los sprint
    """
    sprint = get_object_or_404(Sprint, id=sprint_id)
    sprintus = UserHistorySprint.objects.filter(sprint = sprint)
    capSem = necesidad = consumidas = 0
    sabdom= 5, 6         # si no tienes vacaciones no trabajas sab y dom
    laborales = [dia for dia in range(7) if dia not in sabdom]
    totalDias= rrule.rrule(rrule.DAILY, dtstart=sprint.fecha_inicio, until=sprint.fecha_fin,byweekday=laborales)
    print totalDias.count()
    duracionSprintDias = totalDias.count()
    duracionSprintSem = duracionSprintDias / 5
    # duracionS = abs((sprint.fecha_fin - sprint.fecha_inicio)/5)
    # duracionSprint = duracionS.days
    urp = UsuarioRolProyecto.objects.filter(proyecto=sprint.proyecto)
    for rec in urp:
        capSem += rec.horas
    capacidad = capSem * duracionSprintSem
    for i in sprintus:
        necesidad += i.horas_plan
        consumidas += i.horas_ejec
    disponibles = capacidad - consumidas
    user = User.objects.get(username=request.user.username)
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = sprint.proyecto).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    lista = User.objects.all().order_by("id")
    sprintPlan = False
    if sprint.estado == 'planificacion': sprintPlan = True
    sprintIni = False
    if sprint.estado == 'iniciado': sprintIni = True
    proyInit = False
    print sprint.proyecto.estado
    if sprint.proyecto.estado == 2: proyInit = True
    sprintInitList = Sprint.objects.filter(proyecto = sprint.proyecto, estado = 'iniciado')
    if sprintInitList:
        sprintPlan = False
    else:
        pass
    ctx = {'lista':lista,
           'sprint':sprint,
           'sprintus': sprintus,
           'capacidad' : capacidad,
           'necesidad' : necesidad,
           'disponibles' : disponibles,
           'consumidas' : consumidas,
           'sprintPlan' : sprintPlan,
           'sprintIni' : sprintIni,
           'proyInit' : proyInit,
           'duracionSprint': duracionSprintSem,
           'ver_sprint': 'ver sprint' in permisos,
           'crear_sprint': 'crear sprint' in permisos,
           'mod_sprint': 'modificar sprint' in permisos,
           'eliminar_sprint': 'eliminar sprint' in permisos,
           'ver_user_history': 'ver user history' in permisos,
           'iniciar_sprint': 'iniciar sprint' in permisos,
           'asignar_us_sprint': 'asignar us a sprint' in permisos,
           'finalizar_sprint': 'finalizar sprint' in permisos
          }
    return render_to_response('sprint/verSprint.html',ctx,context_instance=RequestContext(request))

@login_required
def mod_sprint(request, sprint_id):
    """
    Modifica los datos de un Sprint
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param sprint_id: contine el id del sprint a modificar
    :return: mod_sprint.html, pagina en la que se modifica datos del sprint
    """
    user = User.objects.get(username=request.user.username)
    f = get_object_or_404( Sprint, id = sprint_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = f.proyecto).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    print permisos
    #-------------------------------------------------------------------
    if request.method == 'POST':
        form = ModSprintForm(f,request.POST, request.FILES)
        if form.is_valid():
            f.descripcion = form.cleaned_data['descripcion']
            f.save()
            return HttpResponseRedirect("/verSprint/ver&id=" + str(sprint_id))
    else:
        form = ModSprintForm(f, initial = {'descripcion': f.descripcion})
    return render_to_response('sprint/mod_sprint.html',{'form':form,
                                                        'user':user,
                                                        'sprint': f,
                                                        'mod_sprint':'modificar sprint' in permisos
                                                         })

def borrar_sprint(request, sprint_id):
    """
    Elimina un Sprint
    :param request: contiene la informacion sobre la solicitud de la pagina que lo llamo
    :param sprint_id: contiene el id del sprint a eliminar
    :return: se elimina el sprint si el proyecto no inicio
    """
    user = User.objects.get(username=request.user.username)
    actual = get_object_or_404(Sprint, id=sprint_id)
    #Validacion de permisos---------------------------------------------
    roles = UsuarioRolProyecto.objects.filter(usuario = user,proyecto = actual.proyecto).only('rol')
    permisos_obj = []
    for i in roles:
       permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
       permisos.append(i.nombre)

    #-------------------------------------------------------------------

    if request.method == 'POST':
        actual.delete()
        return HttpResponseRedirect("/sprint/sprint&id=" + str(actual.proyecto_id))
    else:
        if actual.proyecto.estado != 1:
             error = "El Proyecto al cual esta relacionado se ha Iniciado"
             return render_to_response("sprint/sprint_confirm_delete.html", {'mensaje': error,
                                                                            'sprint':actual,
                                                                            'user':user,
                                                                            'eliminar_sprint':'eliminar sprint' in permisos
                                                                             })
    return render_to_response("sprint/sprint_confirm_delete.html", {'sprint':actual,
                                                                    'user':user,
                                                                    'eliminar_sprint':'eliminar sprint' in permisos
                                                                    })

def iniciar_sprint(request, sprint_id):

    sprint = get_object_or_404(Sprint, id=sprint_id)
    US = UserHistory.objects.filter(sprint = sprint)
    for rec in US:
        if not rec.flujo:
            for i in US:
                i.estado = 'pendiente'
                i.save()
            error = "No se puede iniciar el sprint, existen User Histories sin flujo asignado."
            return render_to_response("sprint/can_t_init_sprint.html", {'mensaje': error,'sprint': sprint })
        rec.estado = 'iniciado'
        rec.save()
    sprint.estado = "iniciado"
    sprint.save()
    return HttpResponseRedirect("/verSprint/ver&id=%s/" %sprint_id)

def finalizar_sprint(request, sprint_id):
    sprint = get_object_or_404(Sprint, id=sprint_id)
    US = UserHistory.objects.filter(sprint = sprint,estado = 'iniciado')
    for rec in US:
        rec.estado = 'reasignar'
        rec.save()
    sprint.estado = "finalizado"
    sprint.save()
    return HttpResponseRedirect("/verSprint/ver&id=%s/" %sprint_id)

def asignar_us_sprint(request, sprint_id):

    user = User.objects.get(username=request.user.username)
    sprint = get_object_or_404(Sprint, id=sprint_id)
    roles = UsuarioRolProyecto.objects.filter(usuario = user,proyecto = sprint.proyecto).only('rol')
    permisos_obj = []
    for i in roles:
       permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
       permisos.append(i.nombre)
    uss = UserHistory.objects.filter(proyecto = sprint.proyecto, sprint = None)
    if request.method == 'POST':
        form = AsignarUSSprintForm(sprint, request.POST)
        if form.is_valid():
            lista_us = form.cleaned_data['userstories']
            for us in lista_us:
                nuevo = UserHistorySprint()
                nuevo.userhistory = us
                nuevo.sprint = sprint
                nuevo.horas_ejec = 0
                nuevo.horas_plan = us.tiempo_estimado
                nuevo.save()
                us.sprint = sprint
                us.estado = 'pendiente'
                us.save()
            return HttpResponseRedirect("/verSprint/ver&id=" + str(sprint_id))
    else:
        form = AsignarUSSprintForm(sprint)
    return render_to_response("sprint/asignar_us_sprint.html", {'form':form, 'sprint':sprint, 'user':user, 'asignar_us_sprint': 'asignar us a sprint' in permisos
                                                                 })
