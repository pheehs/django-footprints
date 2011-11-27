#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns(
    'pythxsh.ontan.views',
    (r'^$', "index_view"),
    (r'^login/$', "login_view"),
    (r'^logout/$', "logout_view"),
    (r'^post_wordquestion/$', "post_wordquestion_view"),
    (r'^post_fillquestion/$', "post_fillquestion_view"),
    (r'^wordquestions/$', "wordquestions_view"),
    (r'^fillquestions/$', "fillquestions_view"),
)

