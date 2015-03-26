# -*- coding: iso-8859-15 -*-
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

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
LB_CHOICES = ( ('1','Abierta'), ('2','CERRADA'),)
FASE_ESTADO = (('1','Abierta'),('2','CERRADA'),)
class Permiso(models.Model):
    descripcion = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.nombre

class Rol(models.Model):
    nombre = models.CharField(unique=True, max_length=50)
    descripcion = models.TextField(null=True, blank=True)
    fecHor_creacion = models.DateTimeField(auto_now=False, auto_now_add=True, null=True, blank=True, editable=False)
    usuario_creador = models.ForeignKey(User, null=True)
    permisos = models.ManyToManyField(Permiso, through='RolPermiso')
    
    def __unicode__(self):
        return self.nombre

class RolPermiso(models.Model):
    rol = models.ForeignKey(Rol)
    permiso = models.ForeignKey(Permiso)
    #fase = models.ForeignKey(Fase, null = True)


class Proyecto(models.Model):
    """Clase que representa un proyecto."""
    nombre = models.CharField(unique=True, max_length=50)
    # usuario_lider = models.ForeignKey(User)
    # #fase = models.ForeignKey(Fase)
    # descripcion = models.TextField(null=True, blank=True)
    # fecha_inicio = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    # fecha_fin = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    # cronograma = models.FileField(upload_to='cronogramas', null=True, blank=True)
    # cantidad = models.IntegerField()
    # cant_actual = models.IntegerField(null=True)

    def __unicode__(self):
        return self.nombre

class RolUsuarioProyecto(models.Model):
    rol = models.ForeignKey(Rol)
    user = models.ForeignKey(User)
    proyecto = models.ForeignKey(Proyecto)

#class Fase(models.Model):
 #   """Esta clase representa la fase del proyecto."""
  #  nombre = models.CharField(unique=True, max_length=50)
   # cantidad= models.IntegerField()  
    #proyecto_id= models.IntegerField(Proyecto, through='Proyecto')
   # def __unicode__(self):
   #     return self.nombre
    
#class RolPermiso(models.Model):
 #   rol = models.ForeignKey(Rol)
  #  permiso = models.ForeignKey(Permiso)
  #  fase = models.ForeignKey(Fase, null = True)

    
#class Fase(models.Model):
 #   """Esta clase representa la fase del proyecto."""
  #  nombre = models.CharField(unique=True, max_length=50)
   # descripcion = models.TextField(null=True, blank=True) 
    #nro_secuencia = models.IntegerField()
    #tipo_item = models.ForeignKey(TipoItem)
    #proyecto= models.IntegerField()
    #estado = models.CharField(max_length=50)
    #def __unicode__(self):
     #   return self.nombre

class TipoItem(models.Model):
    """"Esta clase representa a que tipo pertenece un item."""
    nombre = models.CharField(unique=True, max_length=50)
    descripcion = models.CharField(max_length=50)
    #claves foraneas
    #fase = models.ForeignKey(Fase)
    
    def __unicode__(self):
        return self.nombre



class Fase(models.Model):
    """Esta clase representa la fase del proyecto."""
    nombre = models.CharField(unique=True, max_length=50)
    descripcion = models.TextField(null=True, blank=True)      
#    nro_secuencia = models.IntegerField()
    tipo_item = models.ForeignKey(TipoItem)
    proyecto= models.IntegerField()
    estado = models.CharField(max_length=50,choices=FASE_ESTADO)
    def __unicode__(self):
        return self.nombre

class TipoItemFase(models.Model):
    """Tabla que relaciona el tipo de item a una fase por proyecto."""
    fase = models.ForeignKey(Fase)
    #fase = models.ForeignKey(Fase)
    tipo_item = models.ForeignKey(TipoItem)
    cant = models.IntegerField(null=0)

    def __unicode__(self):
        return self.tipo_item.descripcion

    class Meta:
        unique_together = [("tipo_item",  "fase")]
#class TipoItem(models.Model):
 #   """"Esta clase representa a que tipo pertenece un item."""
  #  nombre = models.CharField(unique=True, max_length=50)
   # descripcion = models.CharField(max_length=50)
    #claves foraneas
    #fase = models.ForeignKey(Fase)

    #def __unicode__(self):
     #   return self.nombre

#class TipoItemFaseProyecto(models.Model):
 #   """Tabla que relaciona el tipo de item a una fase por proyecto."""
  #  proyecto = models.ForeignKey(Proyecto)
    #fase = models.ForeignKey(Fase)
   # tipo_item = models.ForeignKey(TipoItem)
    #cant = models.IntegerField(max_length = 4)
  
    #def __unicode__(self):
     #   return self.tipo_item.descripcion

    #class Meta:
     #   unique_together = [("tipo_item",  "proyecto")]

class LineaBase(models.Model):
    #fecha_creacion = models.DateField(auto_now=False, auto_now_add=True, editable=False)
    #relaciones con otras tablas
    #proyectos = models.ForeignKey(Proyecto)
    #fase = models.ForeignKey(Fase)
     nombre = models.CharField(max_length=50)
    # items = models.IntegerField()
     #estado = modesl.CharField(max_length=50)
     estado = models.CharField(max_length=1, choices=LB_CHOICES)
     fase = models.ForeignKey(Fase)


class Item(models.Model):
    """Clase que representa a los items."""
    nombre = models.CharField(max_length=50)
    usuario = models.ForeignKey(User)
    fecha_creacion = models.DateField(auto_now_add=True, editable = False)
    estado = models.IntegerField(max_length=1, choices=STATUS_CHOICES, default=1)    
    version = models.PositiveIntegerField()
    complejidad = models.IntegerField(max_length=1, choices=COMPLEXITY_CHOICES)
    descripcion_corta = models.TextField(null=True, blank=True)
    descripcion_larga = models.TextField(null=True, blank=True)
    habilitado = models.BooleanField(default=True)
    icono = models.FileField(upload_to='icono', null=True, blank=True)
    #claves foraneas
    proyecto = models.ForeignKey(Proyecto)
    tipo = models.ForeignKey(TipoItemFase)
    fase = models.ForeignKey(Fase)
    lbase= models.ForeignKey(LineaBase) 
    def __unicode__(self):
        return self.nombre

class RelItem(models.Model):
    padre = models.ForeignKey(Item, related_name = 'padre')
    hijo = models.ForeignKey(Item, related_name = 'hijo')
    habilitado = models.BooleanField(default=True)
    
    class Meta:
        unique_together = [("padre", "hijo")]

class Historial(models.Model):
    """Clase que representa el historial de los items"""
    usuario = models.ForeignKey(User)
    fecha_creacion = models.DateField(auto_now =False, auto_now_add=True, editable=False)
    #claves foraneas
    item = models.OneToOneField(Item, parent_link=False)
    
class RegistroHistorial(models.Model):
    """Clase que representa el Registro de versiones de los items"""
    version = models.PositiveIntegerField()
    complejidad = models.IntegerField()
    descripcion_corta = models.TextField(null=True, blank=True)
    descripcion_larga = models.TextField(null=True, blank=True)
    habilitado = models.BooleanField()
    icono = models.FileField(upload_to='icono', null=True, blank=True)
    tipo = models.ForeignKey(TipoItemFase)
    fecha_modificacion = models.DateTimeField(auto_now=True, auto_now_add=False, editable=False)
    #claves foraneas
    historial = models.ForeignKey(Historial)
   
    
class Adjunto(models.Model):
    #archivo = models.FileField(upload_to='items')
    nombre = models.CharField(max_length = 100)
    contenido = models.TextField(null=True)
    tamano = models.IntegerField()
    mimetype = models.CharField(max_length = 255)  
    #claves foraneas
    item = models.ForeignKey(Item)
    habilitado = models.BooleanField(default = True)
LB_CHOICES = ( ('R','REVISADO'),
	       ('NR','NO REVISADO'),
		('L','LIBERADO'),
	)
#class LineaBase(models.Model):
    #fecha_creacion = models.DateField(auto_now=False, auto_now_add=True, editable=False)
    #relaciones con otras tablas
    #proyectos = models.ForeignKey(Proyecto)
    #fase = models.ForeignKey(Fase)
 #    nombre = models.CharField(max_length=50)
    # items = models.IntegerField()
     #estado = modesl.CharField(max_length=50)
  #   estado = models.CharField(max_length=1, choices=LB_CHOICES)
   #  fase = models.ForeignKey(Fase)     
class UsuarioRolProyecto(models.Model):   
    usuario = models.ForeignKey(User)
    rol = models.ForeignKey(Rol, null=True)
    proyecto = models.ForeignKey(Proyecto)

    class Meta:
        unique_together = [("usuario", "rol", "proyecto")]
        
class UsuarioRolSistema(models.Model):
    usuario = models.ForeignKey(User)
    rol = models.ForeignKey(Rol)
    
    class Meta:
        unique_together = [("usuario", "rol")]
        
class RegHistoRel(models.Model):
    itm_padre = models.ForeignKey(Item, related_name = 'itm_padre')
    itm_hijo = models.ForeignKey(Item, related_name = 'itm_hijo')
    registro = models.ForeignKey(RegistroHistorial)
    
    class Meta:
        unique_together = [("itm_padre", "itm_hijo", "registro")]
        
class RegHistoAdj(models.Model):
    #archivo = models.FileField(upload_to='items')
    nombre = models.CharField(max_length = 100)
    contenido = models.TextField(null=True)
    tamano = models.IntegerField()
    mimetype = models.CharField(max_length = 255)  
    #claves foraneas
    item = models.ForeignKey(Item)
    #habilitado = models.BooleanField(default = True)
    registro = models.ForeignKey(RegistroHistorial)


class LineaBaseItems(models.Model):
    linea = models.ForeignKey(LineaBase)
    items = models.ForeignKey(Item)
    #procesos = models.CharField(max_length=1, choices=ACCIONES_CHOICES)

    class Meta:
        unique_together = [("linea", "items")]


ESTADO_SOLICITUD = (
                 ('A', 'Aprobado'),
                 ('P', 'Pendiente'),
		 ('R', 'Rechazado'),
             )

class Comite(models.Model):
	usuarios = models.ForeignKey(User)
        proyecto= models.ForeignKey(Proyecto)

class Solicitud(models.Model):
	usuario_solicitante = models.ForeignKey(User)
	estado = models.CharField(max_length=1, choices=ESTADO_SOLICITUD)

	def __unicode__(self):
		return self.usuario_solicitante
ACCIONES_CHOICES = ( ('M', 'Modificar'),
		     ('B', 'Borrar'),)
class Acciones(models.Model):
    procesos = models.CharField(max_length=1, choices=ACCIONES_CHOICES)
    items = models.ForeignKey(Item)
    usu_solicitante = models.ForeignKey(User)
    proyecto =models.ForeignKey(Proyecto)
    aceptado = models.IntegerField(default=0)	
    rechazado = models.IntegerField(default=0)
    votante= models.IntegerField()
    estado = models.CharField(max_length=1, choices=ESTADO_SOLICITUD)
