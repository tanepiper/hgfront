# General Libraries
# Django Libraries
from django.conf import settings
from django.conf.urls.defaults import *
# Project Libraries

urlpatterns = patterns('hgfront.landing.views',
    url(r'^$','landing_page', name='landing-page'),
)