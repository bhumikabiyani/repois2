from django.conf.urls import patterns,url


urlpatterns = patterns('SGPA.apps.home.views',
	url(r'^$','index_view',name='vista_principal'),
        url(r'^login/$','login_view',name='vista_login'),
        url(r'^logout/$','logout_view',name='vista_logout'),
)
