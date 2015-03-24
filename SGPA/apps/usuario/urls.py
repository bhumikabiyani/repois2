from django.conf.urls import patterns,url

urlpatterns = patterns('SGPA.apps.usuario.views',
	url(r'^crear/$','add_user',name='vista_agregar_usuario'),
        #url(r'^login/$','login_view',name='vista_login'),
        #url(r'^logout/$','logout_view',name='vista_logout'),
	#url(r'^principal/$','principal_view',name='vista_p'),
)