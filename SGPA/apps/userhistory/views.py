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
from SGPA.apps.flujo.forms import *
from SGPA.apps.flujo.models import *
from SGPA.apps.flujo.helper import *
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
                                                        'pag': pag,
                                                        'ver_flujo':'ver flujo' in permisos,
							'crear_flujo':'crear flujo' in permisos
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
							    'pag': pag,
                                                            'ver_flujo':'ver flujo' in permisos,
							    'crear_flujo':'crear flujo' in permisos
							})
