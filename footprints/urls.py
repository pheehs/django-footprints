#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns(
    'pythxsh.footprints.views',
    (r'^$', "index_view"),
    (r'^login/$', "login_view"),
    (r'^logout/$', "logout_view"),
    (r'get_lonlat$', "get_lonlat_view"),
    (r'get_balloon$', "get_balloon_view"),
    (r'send_correction$', "send_correction_view"),
)
