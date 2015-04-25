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
# Create your views here.

@login_required
def admin_sprint(request,proyecto_id):
    """
    :param request:
    :return:
    Administracion de Sprint"""
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

    lista = Sprint.objects.filter(proyecto=proyecto_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
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
            return render_to_response('sprint/sprint.html',{'lista':lista, 'form': form,

                                                        'user':user,
                                                        'proyecto':proyecto,
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
    return render_to_response('sprint/sprint.html',{'lista':lista, 'form':form,
                                                            'user':user,
                                                            'proyecto':proyecto,
							    'pag': pag,
                                                            'ver_sprint':'ver sprint' in permisos,
							    'crear_sprint':'crear sprint' in permisos
							})

@login_required
def crear_sprint(request, proyecto_id):
    """Administracion general de sprint"""

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
    proyecto = get_object_or_404(Proyecto, id = proyecto_id)
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
        """Visualiza Sprint"""
        sprint = get_object_or_404(Sprint, id=sprint_id)
        user=  User.objects.get(username=request.user.username)
        permisos = get_permisos_sistema(user)
        lista = User.objects.all().order_by("id")
        ctx = {'lista':lista,
               'sprint':sprint,
               'ver_sprint': 'ver sprint' in permisos,
               'crear_sprint': 'crear sprint' in permisos,
               'mod_sprint': 'modificar sprint' in permisos,
               'eliminar_sprint': 'eliminar sprint' in permisos
	          }
	return render_to_response('sprint/verSprint.html',ctx,context_instance=RequestContext(request))

@login_required
def mod_sprint(request, sprint_id):
    user = User.objects.get(username=request.user.username)
    f = get_object_or_404( Sprint, id = sprint_id)
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

    :param request:
    :param sprint_id:
    :return:
    Elimina un Sprint si su Proyecto aun no ha iniciado"""
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
                                                                            'eliminar_sprint':'eliminar sprint' in permisos
                                                                             })
    return render_to_response("sprint/sprint_confirm_delete.html", {'sprint':actual,
                                                                  'user':user,
                                                                  'eliminar_sprint':'eliminar sprint' in permisos
								})
