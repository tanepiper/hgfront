from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
	url(r'^projects/',include('hgfront.project.urls')),
	url(r'^registration/',include('registration.urls')),
)
#static content
urlpatterns += patterns('',
    url(r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.HGFRONT_STATIC_PATH})
)
