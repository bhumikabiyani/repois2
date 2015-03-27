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

class Permiso(models.Model):
	nombre = models.CharField(unique=True, max_length=50)
	categoria = models.IntegerField(max_length=1, choices=CATEGORY_CHOICES)

	def __unicode__(self):
		return self.nombre

class Rol(models.Model):
	nombre = models.CharField(unique=True, max_length=50)
	categoria = models.IntegerField(max_length=1, choices=CATEGORY_CHOICES)
	descripcion = models.TextField(null=True, blank=True)
	fecHor_creacion = models.DateTimeField(auto_now=False, auto_now_add=True, null=True, blank=True, editable=False)
	usuario_creador = models.ForeignKey(User, null=True)
	permisos = models.ManyToManyField(Permiso, through='RolPermiso')

	def __unicode__(self):
		return self.nombre

class RolPermiso(models.Model):
	rol = models.ForeignKey(Rol)
	permiso = models.ForeignKey(Permiso)

class UsuarioRolSistema (models.Model):
	usuario = models.ForeignKey(User)
	rol = models.ForeignKey(Rol)

	class Meta:
		unique_together = [("usuario", "rol")]


