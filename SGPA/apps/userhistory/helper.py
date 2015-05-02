from SGPA.apps.usuario.models import *
import datetime


def get_permisos_sistema(user):
    roles = UsuarioRolSistema.objects.filter(usuario = user).only('rol')
    permisos_obj = []
    for i in roles:
        permisos_obj.extend(i.rol.permisos.all())
    permisos = []
    for i in permisos_obj:
        permisos.append(i.nombre)
    return permisos

def registrar_log(userHistory,descripcion,usuario):
    log = Historia()
    log.descripcion = descripcion
    log.fecHor_creacion = datetime.datetime.now()
    log.userhistory = userHistory
    log.usuario = usuario
    log.save()
