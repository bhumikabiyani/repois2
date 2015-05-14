# -*- coding: iso-8859-15 -*-
from django.db import models
from django.contrib.auth.models import User

CATEGORY_CHOICES = (
    ('1', 'Rol de Sistema'),
    ('2', 'Rol de Proyecto'),
    )

COMPLEXITY_CHOICES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    )

STATUS_CHOICES = (
    ('1', 'Pendiente'),
    ('2', 'Modificado'),
    ('3', 'Revisado'),
    )

PROJECT_STATUS_CHOICES = (
    ('1', 'Pendiente'),
    ('2', 'Iniciado'),
    ('3', 'Terminado'),
    ('4', 'Anulado'),
    )

class Permiso(models.Model):
    """Clase que representa a los Permisos"""
    nombre = models.CharField(unique=True, max_length=50)
    categoria = models.IntegerField(max_length=1, choices=CATEGORY_CHOICES)

    def __unicode__(self):
        return self.nombre

class Rol(models.Model):
    """
    Clase que representa a los roles
    """
    nombre = models.CharField(unique=True, max_length=50)
    categoria = models.IntegerField(max_length=1, choices=CATEGORY_CHOICES)
    descripcion = models.TextField(null=True, blank=True)
    fecHor_creacion = models.DateTimeField(auto_now=False, auto_now_add=True, null=True, blank=True, editable=False)
    usuario_creador = models.ForeignKey(User, null=True)
    permisos = models.ManyToManyField(Permiso, through='RolPermiso')

    def __unicode__(self):
        return self.nombre

class RolPermiso(models.Model):
    """Clase que relaciona Rol con Permiso"""
    rol = models.ForeignKey(Rol)
    permiso = models.ForeignKey(Permiso)

class UsuarioRolSistema (models.Model):
    """Clase que relaciona Usuario, Rol y Sistema"""
    usuario = models.ForeignKey(User)
    rol = models.ForeignKey(Rol)

    class Meta:
        unique_together = [("usuario", "rol")]

class Flujo(models.Model):
    """Esta clase representa el flujo para proyecto"""
    nombre = models.CharField(unique=True, max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    fecHor_creacion = models.DateTimeField(auto_now=False, auto_now_add=True, null=True, blank=True, editable=False)
    usuario_creador = models.ForeignKey(User, null=True)
    #proyecto= models.IntegerField()

    def __unicode__(self):
        return self.nombre


class Proyecto(models.Model):
    """Clase que representa un proyecto."""
    nombrelargo = models.CharField(unique=True, max_length=50)
    usuario_lider = models.ForeignKey(User)
    #fase = models.ForeignKey(Fase)
    descripcion = models.TextField(null=True, blank=True)
    fecha_inicio = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    fecha_fin = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    # cronograma = models.FileField(upload_to='cronogramas', null=True, blank=True)
    cantidad = models.IntegerField()
    cant_actual = models.IntegerField(null=True)
    estado = models.IntegerField(max_length=1, choices=PROJECT_STATUS_CHOICES)
    flujos = models.ManyToManyField(Flujo, through='FlujoActividadProyecto')

    def __unicode__(self):
        return self.nombrelargo

class ProyectoFlujo(models.Model):
    """
    Clase que relaciona Proyecto con Flujo
    """
    proyecto = models.ForeignKey(Proyecto)
    flujo = models.ForeignKey(Flujo)

    class Meta:
        unique_together = [("proyecto", "flujo")]

class UsuarioRolProyecto(models.Model):
    """
    Clase que relaciona Usuario, Rol y Proyecto
    """
    usuario = models.ForeignKey(User)
    rol = models.ForeignKey(Rol, null=True)
    proyecto = models.ForeignKey(Proyecto)
    horas = models.IntegerField(null=False)

    class Meta:
        unique_together = [("usuario", "rol", "proyecto")]

class Sprint(models.Model):
    """Clase que representa un sprint"""
    proyecto = models.ForeignKey(Proyecto)
    nombre = models.CharField(unique=True, max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    fecha_inicio = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    fecha_fin = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)

    def __unicode__(self):
        return self.nombre

class Actividad(models.Model):
    """Esta clase representa las actividades"""
    nombre = models.CharField(unique=True, max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    fecHor_creacion = models.DateTimeField(auto_now=False, auto_now_add=True, null=True, blank=True, editable=False)
    usuario_creador = models.ForeignKey(User, null=True)
    #proyecto= models.IntegerField()

    def __unicode__(self):
        return self.nombre

class FlujoActividad(models.Model):
    """
    Clase que relaciona Flujo con Actividad
    """
    actividad = models.ForeignKey(Actividad)
    flujo = models.ForeignKey(Flujo)
    orden = models.CharField(max_length=50)

    class Meta:
        unique_together = [("actividad", "flujo", "orden")]

class FlujoActividadProyecto(models.Model):
    """
    Clase que relaciona Flujo, Actividad y Proyecto
    """
    flujo = models.ForeignKey(Flujo)
    actividad = models.ForeignKey(Actividad)
    proyecto = models.ForeignKey(Proyecto)
    orden = models.CharField(max_length=50)

    class Meta:
        unique_together = [("flujo", "actividad", "proyecto", "orden")]

ESTADO_CHOICES=(('pendiente','Pendiente'),('iniciado','Iniciado'),('en-curso','En Curso'),('cancelado','Cancelado')
                ,('finalizado','Finalizado'))

ESTADO_KANBAN=(('to-do','To do'),('doing','Doing'),('done','Done'))

class UserHistory(models.Model):
    """
    Clase que representa a un User Storie
    """
    nombre = models.CharField(unique=True, max_length=50)
    descripcion = models.CharField(max_length=500)
    valor_tecnico = models.IntegerField(null=True)
    valor_negocio = models.IntegerField(null=True)
    prioridad = models.IntegerField(null=True)
    proyecto = models.ForeignKey(Proyecto)
    encargado = models.ForeignKey(User,null=True)
    flujo = models.ForeignKey(Flujo,null=True)
    actividad = models.ForeignKey(Actividad,null=True)
    sprint = models.ForeignKey(Sprint,null=True)
    estado = models.CharField(max_length=12, choices=ESTADO_CHOICES)
    estadokanban = models.CharField(max_length=6, choices=ESTADO_KANBAN)
    tiempo_estimado = models.IntegerField(null=True)
    tiempo_utilizado = models.IntegerField(null=True)

    def __unicode__(self):
        return self.nombre

class Historia(models.Model):
    """
    Clase que representa el Historial de User Storie
    """
    descripcion = models.CharField(max_length=500)
    fecHor_creacion = models.DateTimeField(auto_now=False, auto_now_add=True, null=True, blank=True, editable=False)
    userhistory = models.ForeignKey(UserHistory)
    usuario = models.ForeignKey(User)
    estadokanban = models.CharField(max_length=6, choices=ESTADO_KANBAN)
    estado = models.CharField(max_length=12, choices=ESTADO_CHOICES)
    sprint = models.ForeignKey(Sprint,null=True)
    actividad = models.ForeignKey(Actividad,null=True)
    flujo = models.ForeignKey(Flujo,null=True)

    def __unicode__(self):
        return self.descripcion

class ArchivosAdjuntos(models.Model):
    userhistory = models.ForeignKey(UserHistory)
    nombre=models.CharField(max_length=50,)
    docfile = models.FileField(upload_to='documents')

    def __unicode__(self):
        return self.nombre

class Comentarios(models.Model):
    asunto = models.CharField(max_length=30,null=False)
    descripcion = models.CharField(max_length=200,null=False)
    userhistory = models.ForeignKey(UserHistory)

    def __unicode__(self):
        return self.asunto