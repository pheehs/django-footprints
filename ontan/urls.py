#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.conf.urls.defaults import *

urlpatterns = patterns(
    'pythxsh.ontan.views',
    (r'^$', "index_view"),
    (r'^accounts/login/$', "login_view"),
    (r'^accounts/login_ajax/$', "login_ajax_view"),
    (r'^accounts/logout/$', "logout_view"),
    (r'^accounts/adduser/$', "adduser_view"),
    (r'^accounts/profile/checkedlist/(?P<cl_pk>\d+)/wordquestions/$', "checkedlist_wordquestions_view"),
    (r'^accounts/profile/checkedlist/(?P<cl_pk>\d+)/fillquestions/$', "checkedlist_fillquestions_view"),
#    (r'^accounts/profile/checkedlist/(?P<cl_pk>\d+)/exam_wordquestions/$', "checkedlist_exam_wordquestions_view"),
#    (r'^accounts/profile/checkedlist/(?P<cl_pk>\d+)/exam_fillquestions/$', "checkedlist_exam_fillquestions_view"),
    (r'^accounts/profile/checkedlist/(?P<cl_pk>\d+)/$', "checkedlist_view"),
    (r'^accounts/profile/checkedlist/$', "checkedlist_view"),
    (r'^accounts/profile/$', "userinfo_view"),
#    (r'^accounts/user/(?P<username>\s+)/$', "others_view"),
    
    (r'^question/post_wordquestion/$', "post_wordquestion_view"),
    (r'^question/wordquestions/(?P<pagenum>\d+)/$', "wordquestions_view"),
    (r'^question/wordquestions/exam/$', "exam_wordquestions_view"),
    (r'^question/post_fillquestion/$', "post_fillquestion_view"),
    (r'^question/fillquestions/(?P<pagenum>\d+)/$', "fillquestions_view"),
    (r'^question/fillquestions/exam/$', "exam_fillquestions_view"),
    (r'^question/$', "questions_view"),
    
    (r'^contact/$', "contact_view"),
    (r'^change_lang$', "change_lang_view"),
    (r'^add_to_checkedlist$', "add_to_checkedlist_view"),
)

