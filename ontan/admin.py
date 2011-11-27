#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.contrib import admin
from pythxsh.ontan.models import *


class WordQuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields":["number", "question", "answer", "author", "create_at"],
                "description":u"<font color='red'><b>太字のものは必須入力事項です。</b></font>"}),
        ]
    list_display = ("number", "question", "answer")

class FillQuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields":["number", "question", "japanese", "answer", "author", "create_at"],
                "description":u"<font color='red'><b>太字のものは必須入力事項です。</b></font>"}),
        ]
    list_display = ("number", "question", "japanese")

admin.site.register(WordQuestion, WordQuestionAdmin)
admin.site.register(FillQuestion, FillQuestionAdmin)
