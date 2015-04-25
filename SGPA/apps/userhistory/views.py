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
from SGPA.apps.userhistory.forms import *
from SGPA.apps.flujo.models import *
from SGPA.apps.userhistory.helper import *
# Create your views here.

@login_required
def admin_user_history(request,proyecto_id):
    """
    :param request:
    :return:
    Administracion de User History"""
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
    userRolProy = UsuarioRolProyecto.objects.filter(proyecto=proyecto_id)
    lista = UserHistory.objects.filter(proyecto=proyecto_id)
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
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
							    'crear_user_history':'crear user history' in permisos
							})


@login_required
def crear_user_history(request,proyecto_id):
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
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        form = UserHistoryForm(request.POST)
        if form.is_valid():
            r = UserHistory()
            r.nombre = form.cleaned_data['nombre']
            r.estado = form.cleaned_data['estado']
            r.tiempo_estimado = form.cleaned_data['tiempo_estimado']
            r.proyecto = proyecto
            r.save()
            return HttpResponseRedirect("/userHistory/proyecto&id=" + str(proyecto_id))

    else:
        form = UserHistoryForm()
    return render_to_response('userhistory/crear_userhistory.html',{'form':form,
                                                            'user':user,
                                                            'proyecto':proyecto,
                                                            'crear_user_history': 'crear user history' in permisos
			      })


def visualizar_user_history(request, userhistory_id):
    """Visualiza Flujos"""
    flujos = get_object_or_404(UserHistory, id=userhistory_id)
    user=  User.objects.get(username=request.user.username)
    permisos = get_permisos_sistema(user)
    lista = User.objects.all().order_by("id")
    ctx = {'lista':lista,
            'flujos':flujos,
            'ver_user_history': 'ver user history' in permisos,
            'crear_user_history': 'crear user history' in permisos,
            'mod_user_history': 'modificar user history' in permisos,
            'eliminar_user_history': 'eliminar user history' in permisos
	       }
    return render_to_response('userhistory/verUserHistory.html',ctx,context_instance=RequestContext(request))

def mod_user_history(request, userhistory_id):
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
    actual = get_object_or_404(UserHistory, id=userhistory_id)
    if request.method == 'POST':
        form = ModUserHistoryForm(request.POST)
        if form.is_valid():
            actual.estado = form.cleaned_data['estado']
            actual.tiempo_estimado = form.cleaned_data['tiempo_estimado']
            actual.save()
            return HttpResponseRedirect("/verUserHistory/ver&id=" + str(userhistory_id))
    else:
        form = ModUserHistoryForm()
        form.fields['estado'].initial = actual.estado
        form.fields['tiempo_estimado'].initial = actual.tiempo_estimado
    return render_to_response("userhistory/mod_user_history.html", {'user':user,
                                                           'form':form,
							   'flujo': actual,
                                                           'mod_user_history':'modificar user history' in permisos
						     })

def borrar_user_history(request, userhistory_id):
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
    actual = get_object_or_404(UserHistory, id=userhistory_id)

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
