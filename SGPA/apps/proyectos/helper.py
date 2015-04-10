from SGPA.apps.usuario.models import *
import datetime

#def validar_fase(proyecto, fase):
    #print proyecto.fase.id
   # print fase
 #   if profase.id == 1: 
  #      if int(fase) == 2 or int(fase) == 3: return False;
   #     return True
    #if proyecto.fase.id == 2:
     #   if int(fase) == 1 or int(fase) == 2: return True
      #  return False
    #if proyecto.fase.id == 3:
     #   if int(fase) == 2 or int(fase) == 3: return True
      #  return False
    #return False

def obtener_relaciones_izq(itm, lista_existentes):
    relaciones = RelItem.objects.filter(hijo = itm, habilitado = True)
    ret = [itm]
    if relaciones:
        if itm.id in lista_existentes:
            return None
        lista_existentes.append(itm.id)
        for i in relaciones:
            aux = obtener_relaciones_izq(i.padre, lista_existentes)
            if aux:
                ret.extend(aux)
    return ret

def obtener_relaciones_der(itm, lista_existentes):
    relaciones = RelItem.objects.filter(padre = itm, habilitado = True)
    ret = [itm]
    if relaciones:
        if itm.id in lista_existentes:
            return None
        lista_existentes.append(itm.id)
        for i in relaciones:
            aux = obtener_relaciones_der(i.hijo, lista_existentes)
            if aux:
                ret.extend(aux)
    return ret

def get_permisos_proyecto(user, proyecto):
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyecto).only('rol')
    permisos_obj = []
   # for i in roles:
    #    permisos_obj.extend(i.rol.permisos.filter(rolpermiso__fase = proyecto.fase))
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    return permisos

def get_permisos_fase(user, proyecto):
    roles = UsuarioRolProyecto.objects.filter(usuario=user, proyecto= proyecto).only('rol')
    permisos_obj = []
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    return permisos
	
def get_permisos_proyecto_ant(user, proyecto, fase):
    roles = UsuarioRolProyecto.objects.filter(usuario = user, proyecto = proyecto).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.filter(rolpermiso__fase = fase))
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    return permisos

def get_permisos_sistema(user):
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    return permisos

def registrar_version(itm, relaciones, archivos):
    """Se ingresa la version antigua al registro"""
    reg = RegistroHistorial()
    reg.version = itm.version
    reg.estado = itm.estado
    reg.complejidad = itm.complejidad
    reg.descripcion_corta = itm.descripcion_corta
    reg.descripcion_larga = itm.descripcion_larga
    reg.habilitado = itm.habilitado
    reg.icono = itm.icono
    reg.tipo = itm.tipo
    reg.fecha_modificacion = datetime.datetime.today()
    historial = Historial.objects.get(item = itm)
    reg.historial = historial
    reg.save()
    if (relaciones):
        for i in relaciones:
            nuevo = RegHistoRel()
            nuevo.itm_padre = i.padre
            nuevo.itm_hijo = i.hijo
            nuevo.registro = reg
            nuevo.save()
    if (archivos):
        for i in archivos:
            adj = RegHistoAdj()
            adj.nombre = i.nombre
            adj.contenido = i.contenido
            adj.tamano = i.tamano
            adj.mimetype = i.mimetype
            adj.i = itm
            adj.registro = reg
            adj.save()
    """Se cambia el estado del item"""
    itm.estado = 2            
    """Se incrementa la version actual"""
    itm.version = itm.version + 1
    itm.save()           

def tiene_padre (hijo, padres):
    for i in padres:
        if (i.fase.id == hijo.fase.id - 1):
            return True
        else:
            relaciones = RelItem.objects.filter(hijo=i, habilitado=True).values_list('padre', flat=True)
            if (relaciones):
                padres = Item.objects.filter(id__in = relaciones)
                return tiene_padre (i, padres)
    return False

def tiene_hijo (padre, hijos):
    for i in hijos:
        if (i.fase.id == padre.fase.id + 1):
            return True
        else:
            relaciones = RelItem.objects.filter(padre=i, habilitado=True).values_list('hijo', flat=True)
            if (relaciones):
                hijos = Item.objects.filter(id__in = relaciones)
                return tiene_hijo (i, hijos)
    return False
