#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.contrib.auth import login, logout, authenticate
#from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from pythxsh.ontan.models import *
import random


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
            raise Http404 # for debug
            return render_to_response("ontan/post_fillquestion.html",
                                      {"user":request.user,
                                       "error":"問題分(%d)と答え(%d)で空白の数が違います。" % (question.count("( )"), len(answer.split(","))) })
        # save
        wq = FillQuestion(number=number, question=question, japanese=japanese, answer=answer, author=request.user)
        wq.save()
        return render_to_response("ontan/post_fillquestion.html",
                                  {"user":request.user,
                                   "error":"保存しました：穴埋め問題(%d)" % number,})
    else: # GET
        return render_to_response("ontan/post_fillquestion.html",
                                  {"user":request.user,})
    
def wordquestions_view(request, pagenum):
    pagenum = int(pagenum)
    maxpage = (WordQuestion.objects.count()+1) / 100
    if maxpage < pagenum:
        return HttpResponseRedirect("/ontan/")
    else:
        return render_to_response("ontan/wordquestions.html",
                                  {"user":request.user,
                                   "questions":WordQuestion.objects.all()[(pagenum-1)*100:pagenum*100],
                                   "pages":[(p, "/ontan/wordquestions/%d/" % p) for p in xrange(1, maxpage+1)],
                                   "cur_page":pagenum, 
                                   "next_page":"/ontan/wordquestions/%d/" % (pagenum+1),
                                   "prev_page":"/ontan/wordquestions/%d/" % (pagenum-1), 
                                   "max_page":maxpage})

    
def fillquestions_view(request, pagenum):
    pagenum = int(pagenum)
    maxpage = (FillQuestion.objects.count()+1) / 100
    if maxpage < pagenum:
        return HttpResponseRedirect("/ontan/")
    else:
        questions = []
        for fq in FillQuestion.objects.all()[(pagenum-1)*100:pagenum*100]:
            question_html = []
            for i in range(len(fq.answer.split(","))):
                question_html.append((False, fq.question.split("( )")[i]))
                question_html.append((True, fq.answer.split(",")[i]))
            question_html.append((False, fq.question.split("( )")[-1]))
            questions.append((fq, question_html))
        return render_to_response("ontan/fillquestions.html",
                                  {"user":request.user,
                                   "questions":questions,
                                   "pages":[(p, "/ontan/fillquestions/%d/" % p) for p in xrange(1, maxpage+1)],
                                   "cur_page":pagenum, 
                                   "next_page":"/ontan/fillquestions/%d/" % (pagenum+1),
                                   "prev_page":"/ontan/fillquestions/%d/" % (pagenum-1),
                                   "max_page":maxpage})

def exam_wordquestions_view(request):
    show_num = request.GET.get("show", "50")
    start_num = request.GET.get("start", "1")
    end_num = request.GET.get("end", "1200")
    all_wq_num = WordQuestion.objects.count()
    try:
        show_num = int(show_num)
    except (ValueError, TypeError):
        show_num = 50
    else:
        if 0 > show_num or show_num > all_wq_num:
            show_num = 50
    try:
        start_num = int(start_num)
    except (ValueError, TypeError):
        start_num = 1
    else:
        if 1 > start_num or start_num > all_wq_num:
            start_num = 1
    try:
        end_num = int(end_num)
    except (ValueError, TypeError):
        end_num = 1200
    else:
        if 1 > end_num or end_num > all_wq_num:
            end_num = 1200
    all_questions_pk = [wq.pk for wq in WordQuestion.objects.all()[start_num-1:end_num+1]]
    rand_questions_pk = []
    for i in xrange(show_num):
        r = random.randint(0, len(all_questions_pk)-1)
        rand_questions_pk.append(all_questions_pk.pop(r))
        
    return render_to_response("ontan/exam_wordquestions.html",
                              {"user":request.user,
                               "questions":[WordQuestion.objects.get(pk=pk) for pk in rand_questions_pk]})

def exam_fillquestions_view(request):
    show_num = request.GET.get("show", "50")
    start_num = request.GET.get("start", "1")
    end_num = request.GET.get("end", "1200")
    all_fq_num = FillQuestion.objects.count()
    try:
        show_num = int(show_num)
    except (ValueError, TypeError):
        show_num = 50
    else:
        if 0 > show_num or show_num > all_fq_num:
            show_num = 50
    try:
        start_num = int(start_num)
    except (ValueError, TypeError):
        start_num = 1
    else:
        if 1 > start_num or start_num > all_fq_num:
            start_num = 1
    try:
        end_num = int(end_num)
    except (ValueError, TypeError):
        end_num = 1200
    else:
        if 1 > end_num or end_num > all_fq_num:
            end_num = 1200
    all_questions_pk = [fq.pk for fq in FillQuestion.objects.all()[start_num-1:end_num+1]]
    rand_questions_pk = []
    for i in xrange(show_num):
        r = random.randint(0, len(all_questions_pk)-1)
        rand_questions_pk.append(all_questions_pk.pop(r))
        
    questions = []
    for pk in rand_questions_pk:
        fq = FillQuestion.objects.get(pk=pk)
        question_html = []
        for i in range(len(fq.answer.split(","))):
            question_html.append((False, fq.question.split("( )")[i]))
            question_html.append((True, fq.answer.split(",")[i]))
        question_html.append((False, fq.question.split("( )")[-1]))
        questions.append((fq, question_html))

    return render_to_response("ontan/exam_fillquestions.html",
                              {"user":request.user,
                               "questions":questions,
                               })
    
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
