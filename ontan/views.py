#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.contrib.auth import login, logout, authenticate
#from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import mail_admins
from smtplib import SMTPException
from pythxsh.ontan.models import *
import random


def index_view(request):
    # Later changeable
    selected_tests = [17]
    # data for template
    tests_data = []
    for i in xrange(1, WordQuestion.objects.count() / 50 + 1):
        if i in selected_tests:
            tests_data.append((i*2-1, i*2, True))
        else:
            tests_data.append((i*2-1, i*2, False))
    
    return render_to_response("ontan/index.html",
                              {"user":request.user,
                               "tests":tests_data, })

def post_wordquestion_view(request):
    if not request.user.is_authenticated():
        return render_to_response("ontan/post_wordquestion.html",
                                  {"user":request.user,
                                   "error":"ログインしてください。",
                                   "redirect":"<a href='/ontan/login/?next=%s'>ログイン</a>" % request.path})
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
                                   "redirect":"<a href='/ontan/login/?next=%s'>ログイン</a>" % request.path})
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
        questions = WordQuestion.objects.all()[(pagenum-1)*100:pagenum*100]
        sections = [{"secnum":(pagenum-1)*4+1, "questions":[]}]
        secnums = [(pagenum-1)*4+1, ]
        for q in questions:
            if len(sections[-1]["questions"]) >= 25:
                sections.append({"secnum":q.get_section(), "questions":[]})
                secnums.append(q.get_section())
            sections[-1]["questions"].append(q)
        return render_to_response("ontan/wordquestions.html",
                                  {"user":request.user,
                                   "secnums":secnums,
                                   "sections":sections,
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
        sections = [{"secnum":(pagenum-1)*4+1, "questions":[]}]
        secnums = [(pagenum-1)*4+1, ]
        for fq in FillQuestion.objects.all()[(pagenum-1)*100:pagenum*100]:
            if len(sections[-1]["questions"]) >= 25:
                sections.append({"secnum":fq.get_section(), "questions":[]})
                secnums.append(fq.get_section())
            sections[-1]["questions"].append((fq, []))
            for i in range(len(fq.answer.split(","))):
                sections[-1]["questions"][-1][1].append((False, fq.question.split("( )")[i]))
                sections[-1]["questions"][-1][1].append((True, fq.answer.split(",")[i]))
            sections[-1]["questions"][-1][1].append((False, fq.question.split("( )")[-1]))
        return render_to_response("ontan/fillquestions.html",
                                  {"user":request.user,
                                   "sections":sections,
                                   "secnums":secnums,
                                   "pages":[(p, "/ontan/fillquestions/%d/" % p) for p in xrange(1, maxpage+1)],
                                   "cur_page":pagenum, 
                                   "next_page":"/ontan/fillquestions/%d/" % (pagenum+1),
                                   "prev_page":"/ontan/fillquestions/%d/" % (pagenum-1),
                                   "max_page":maxpage})

def exam_wordquestions_view(request):
    # const
    test_list = []
    test_num = WordQuestion.objects.count() / 50
    # GET parameters
    show_num = request.GET.get("show", "15")
    query = request.GET.copy()
    query.setlistdefault("range", [str(i) for i in range(1, test_num+1)])
    test_range = query.getlist("range")
    # show_num input validation
    try:
        show_num = int(show_num)
    except (ValueError, TypeError):
        show_num = 15
    else:
        if 0 > show_num or show_num > 1000:
            show_num = 15
    # test_range input validation
    for tr in test_range:
        try:
            tr = int(tr)
        except (ValueError, TypeError):
            pass
        else:
            if 1 <= tr <= test_num:
                test_list.append(tr)
    # validate
    if show_num > len(test_list) * 25:
        show_num = 15
        
    all_questions_pk = [WordQuestion.objects.get(number=i).pk  for t in test_list for i in xrange((t-1)*50+1, t*50+1)]
    rand_questions_pk = []
    for i in xrange(show_num):
        r = random.randint(0, len(all_questions_pk)-1)
        rand_questions_pk.append(all_questions_pk.pop(r))
        
    return render_to_response("ontan/exam_wordquestions.html",
                              {"user":request.user,
                               "questions":[WordQuestion.objects.get(pk=pk) for pk in rand_questions_pk]})

def exam_fillquestions_view(request):
    # const
    test_list = []
    test_num = FillQuestion.objects.count() / 50
    # GET parameters
    show_num = request.GET.get("show", "15")
    query = request.GET.copy()
    query.setlistdefault("range", [str(i) for i in range(1, test_num+1)])
    test_range = query.getlist("range")
    # show_num input validation
    try:
        show_num = int(show_num)
    except (ValueError, TypeError):
        show_num = 15
    else:
        if 0 > show_num or show_num > 1000:
            show_num = 15
    # test_range input validation
    for tr in test_range:
        try:
            tr = int(tr)
        except (ValueError, TypeError):
            pass
        else:
            if 1 <= tr <= test_num:
                test_list.append(tr)
    all_questions_pk = [FillQuestion.objects.get(number=i).pk  for t in test_list for i in xrange((t-1)*50+1, t*50+1)]
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
"""
def search_questions_view(request):
    Qobj = Q()
    keywords = request.GET.get("keywords", "").strip()
    if not keywords:
        return render_to_response("ontan/search_questions.html",
                                  {"user":request.user, })
    wquery = WordQuestion.objects
    fquery = FillQuestion.objects
    for keyword in keywords.split(" "):
        wquery = wquery.filter(
            Q(question__icontain=keyword) | Q(answer__icontain=keyword)
            )
        fquery = fquery.filter(
            Q(question__icontain=keyword) | Q(japanese__icontain=keyword) | Q(answer__icontain=keyword)
            )
    if wquery.count() > 0:
        
    return render_to_response("ontan/result_questions.html",
                              {"user":request.user, })
"""
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

def contact_view(request):
    error = {}
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        title = request.POST.get("title")
        body = request.POST.get("body")

        if not body:
            error["body"] = "何か入力してください。"
        try:
            mail_admins("From:%s Title:%s" % (name, title),
                       "Email: %s\n" % email +
                       "Message:\n" + 
                       body,
                       fail_silently=False)
            return render_to_response("ontan/contact_.html",
                                      {"user":request.user,})
        except SMTPException:
            error["top"] = "送信エラー"

    return render_to_response("ontan/contact.html",
                              {"user":request.user,
                               "error":error,})

def userinfo_view(request):
    return HttpResponse("準備中")

def checkedlist_view(request, cl_pk=None):
    if request.user.is_authenticated():
        try:
            cl_pk = int(cl_pk)
        except (ValueError, TypeError):
            clists = CheckedList.objects.filter(user=request.user)
            return render_to_response("ontan/checkedlists.html",
                                      {"user":request.user,
                                       "clists":clists, })
        else:
            cl = CheckedList.objects.get(pk=cl_pk)
            questions = CheckedQuestion.objects.filter(belong=cl)
            return render_to_response("ontan/checkedlist_detail.html",
                                      {"user":request.user,
                                       "clist":cl,
                                       "questions":questions, })
    else:
        return HttpResponseRedirect("/ontan/login/?next=%s" % request.path)
