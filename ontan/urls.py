#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns(
    'pythxsh.ontan.views',
    (r'^$', "index_view"),
    (r'^login/$', "login_view"),
    (r'^logout/$', "logout_view"),
    
    (r'^post_wordquestion/$', "post_wordquestion_view"),
    (r'^wordquestions/(?P<pagenum>\d+)/$', "wordquestions_view"),
    (r'^wordquestions/exam/$', "exam_wordquestions_view"),

    
    (r'^post_fillquestion/$', "post_fillquestion_view"),
    (r'^fillquestions/(?P<pagenum>\d+)/$', "fillquestions_view"),
    (r'^fillquestions/exam/$', "exam_fillquestions_view"),
    (r'^contact/$', "contact_view"),
)

