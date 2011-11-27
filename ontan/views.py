#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import mail_admins
from smtplib import SMTPException
from pythxsh.ontan.models import *


def index_view(request):
    return render_to_response("ontan/index.html",
                              {"user":request.user})

def post_wordquestion_view(request):
    if not request.user.is_authenticated():
        return render_to_response("ontan/post_wordquestion.html",
                                  {"user":request.user,
                                   "error":"ログインしてください。",
                                   "redirect":"<a href='/ontan/login/?next=/ontan/post_wordquestion/'>ログイン</a>"})
    if request.method == "POST":
        number = request.POST.get("number")
        question = request.POST.get("question")
        answer = request.POST.get("answer")
        # catch errors
        try:
            number = int(number)
        except (TypeError, ValueError):
            return render_to_response("ontan/post_wordquestion.html",
                                      {"user":request.user,
                                       "error":"入力エラー：問題番号"})
        if WordQuestion.objects.filter(number=number).count() > 0:
            return render_to_response("ontan/post_wordquestion.html",
                                      {"user":request.user,
                                       "error":"問題番号の重複あり:%d" % WordQuestion.objects.filter(number=number).count()})
        if not question:
            return render_to_response("ontan/post_wordquestion.html",
                                      {"user":request.user,
                                       "error":"入力エラー：日本語"})
        if not answer:
            return render_to_response("ontan/post_wordquestion.html",
                                      {"user":request.user,
                                       "error":"入力エラー：英語"})
        # save
        wq = WordQuestion(number=number, question=question, answer=answer, author=request.user)
        wq.save()
        return render_to_response("ontan/post_wordquestion.html",
                                  {"user":request.user,
                                   "error":"保存しました：一問一答(%d)" % number,})
    else: # GET
        return render_to_response("ontan/post_wordquestion.html",
                                  {"user":request.user,})
    
def post_fillquestion_view(request):
    if not request.user.is_authenticated():
        return render_to_response("ontan/post_fillquestion.html",
                                  {"user":request.user,
                                   "error":"ログインしてください。",
                                   "redirect":"<a href='/ontan/login/?next=/ontan/post_fillquestion/'>ログイン</a>"})
    if request.method == "POST":
        number = request.POST.get("number")
        question = request.POST.get("question")
        japanese = request.POST.get("japanese")
        answer = request.POST.get("answer")
        # catch errors
        try:
            number = int(number)
        except (TypeError, ValueError, ):
            return render_to_response("ontan/post_fillquestion.html",
                                      {"user":request.user,
                                       "error":"入力エラー：問題番号"})
        if FillQuestion.objects.filter(number=number).count() > 0:
            return render_to_response("ontan/post_fillquestion.html",
                                      {"user":request.user,
                                       "error":"問題番号の重複あり"})
        if not question:
            return render_to_response("ontan/post_fillquestion.html",
                                      {"user":request.user,
                                       "error":"入力エラー：問題文"})
        if not japanese:
            return render_to_response("ontan/post_fillquestion.html",
                                      {"user":request.user,
                                       "error":"入力エラー：和訳"})
        if not answer:
            return render_to_response("ontan/post_fillquestion.html",
                                      {"user":request.user,
                                       "error":"入力エラー：答え"})
        if question.count("( )") != len(answer.split(",")):
            return render_to_response("ontan/post_fillquestion.html",
                                      {"user":request.user,
                                       "error":"問題分と和訳で空白の数が違います。"})
        # save
        wq = FillQuestion(number=number, question=question, japanese=japanese, answer=answer, author=request.user)
        wq.save()
        return render_to_response("ontan/post_fillquestion.html",
                                  {"user":request.user,
                                   "error":"保存しました：穴埋め問題(%d)" % number,})
    else: # GET
        return render_to_response("ontan/post_fillquestion.html",
                                  {"user":request.user,})
    
def wordquestions_view(request):
    return render_to_response("ontan/wordquestions.html",
                              {"user":request.user,
                               "questions":WordQuestion.objects.all()})
    
def fillquestions_view(request):
    return render_to_response("ontan/fillquestions.html",
                              {"user":request.user,
                               "questions":FillQuestion.objects.all()})

def login_view(request):
    if request.user.is_authenticated():
        return HttpResponse("すでにログインしています。")
    else:
        if request.method == "POST":
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
                username = request.POST["username"]
                password = request.POST["password"]
                user = authenticate(username=username, password=password)
                if user != None:
                    if user.is_active:
                        login(request, user)
                        request.session.set_test_cookie()
                        nextpath = request.GET.get("next")
                        if not nextpath:
                            nextpath = "/ontan/"
                        return HttpResponseRedirect(nextpath)
                    else:
                        request.session.set_test_cookie()
                        return render_to_response("ontan/login.html",
                                                  {"user":request.user,
                                                   "error":u"このアカウントは無効化されています。"})
                else:
                    request.session.set_test_cookie()
                    return render_to_response("ontan/login.html",
                                              {"user":request.user,
                                               "error":u"ユーザー名またはパスワードが違います。"})
            else:
                request.session.set_test_cookie()
                return render_to_response("ontan/login.html",
                                          {"user":request.user,
                                           "error":"クッキーを有効にしてからもう一度入力してください。"})
        else:
            request.session.set_test_cookie()
            return render_to_response("ontan/login.html",
                                      {"user":request.user,
                                       "error":""})


def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
        nextpath = request.GET.get("next")
        if not nextpath:
            nextpath = "/ontan/"
        return HttpResponseRedirect(nextpath)
    else:
        return HttpResponse("まだログインしていません。")
