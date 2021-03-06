# General Libraries
# Django Libraries
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

# Project Libraries

urlpatterns = patterns('member.views',
    url(r'^register/$','member_register', name='member-register'),
    url(r'^login/$','member_login', name='member-login'),
    url(r'^logout/$','member_logout', name='member-logout'),
    url(r'^home/$','member_home', name='member-home'),
    url(r'^profile/(?P<member_name>[-\w]+)/$','member_profile', name='member-profile'),
    url(r'^passwordreset/$','member_password', name='member-password'),
    url(r'^verifyusername/$','member_verifyusername', name='member-verifyusername'),
    url(r'^verifyuseremail/$','member_verifyuseremail', name='member-verifyuseremail'),
)

#urlpatterns += patterns('core.openidconsumer.views',
#    url(r'^openid/$', 'begin', name='user-openid'),
#    url(r'^openid/complete/$', 'complete', name='user-openid-complete'),
#    url(r'^openid/signout/$', 'signout', name='user-openid-signout'),
#)

# TODO this should be optional
from core.libs.htpasswdutils import monkeypatch_user_model
monkeypatch_user_model()