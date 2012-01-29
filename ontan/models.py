#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
import datetime


class WordQuestion(models.Model):
    #一問一答
    number = models.IntegerField("問題番号")
    question = models.CharField("問題文", max_length=50)
    answer = models.CharField("答え", max_length=20)
    author = models.ForeignKey(User)
    create_at = models.DateTimeField("作成日時", default=datetime.datetime.now())

    def __unicode__(self):
        return "WordQuestion(%d)" % self.number
    def get_section(self):
        return (self.number - 1) / 25 + 1
    def get_book(self):
        if 1 <= self.number <= 2000:
            return "ontan"
        elif 2001 <= self.number <= 2500:
            return "sockohtan"

class FillQuestion(models.Model):
    #穴埋め問題
    number = models.IntegerField("問題番号")
    question = models.CharField("問題文", max_length=80, help_text="穴埋めの空白は「( )」で表す。")
    japanese = models.CharField("和訳", max_length=80)
    answer = models.CharField("答え", max_length=50, help_text="答えは「,」(カンマ)で区切る。")
    author = models.ForeignKey(User)
    create_at = models.DateTimeField("作成日時", default=datetime.datetime.now())
    
    def __unicode__(self):
        return "FillQuestion(%d)" % self.number
    def get_section(self):
        return (self.number - 1) / 25 + 1
    def get_book(self):
        if 1 <= self.number <= 2000:
            return "ontan"
        elif 2001 <= self.number <= 2500:
            return "sockohtan"


class CheckedList(models.Model):
    #リスト
    user = models.ForeignKey(User)
    name = models.CharField("リスト名", max_length=20)
    
    def __unicode__(self):
        return "CheckedList(%s)" % self.name
    
class CheckedQuestion(models.Model):
    #チェックした問題
    belong = models.ForeignKey("CheckedList")
    create_at = models.DateTimeField("追加日時", default=datetime.datetime.now())
    qnum = models.IntegerField("問題番号")
    
    def __unicode__(self):
        return "CheckedQuestion(No.%d)" % self.qnum
