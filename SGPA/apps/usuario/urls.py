from django.conf.urls import patterns,url

urlpatterns = patterns('SGPA.apps.usuario.views',
	url(r'^add/usuario/$','crearUsuario_view',name='vista_crearUsuario'),
)

