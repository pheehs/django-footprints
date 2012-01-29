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
from django.contrib.auth.models import User
import random, re

ALLOWED_CHAR = re.compile(r"^[a-zA-Z0-9@+\._-]+$")
ALLOWED_EMAIL = re.compile(r"^([a-zA-Z0-9])+([a-zA-Z0-9\._-])*@([a-zA-Z0-9_-])+([a-zA-Z0-9\._-]+)+$")

def index_view(request):
    # Later changeable
    selected_tests = [18]
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

def questions_view(request):
    return render_to_response("ontan/questions.html",
                              {"user":request.user,})
    
def post_wordquestion_view(request):
    if not request.user.is_authenticated():
        return render_to_response("ontan/post_wordquestion.html",
                                  {"user":request.user,
                                   "error":u"ログインしてください。",
                                   "redirect":u"<a href='/ontan/accounts/login/?next=%s'>ログイン</a>" % request.path})
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
                                       "error":u"入力エラー：問題番号"})
        if WordQuestion.objects.filter(number=number).count() > 0:
            return render_to_response("ontan/post_wordquestion.html",
                                      {"user":request.user,
                                       "error":u"問題番号の重複あり:%d" % WordQuestion.objects.filter(number=number).count()})
        if not question:
            return render_to_response("ontan/post_wordquestion.html",
                                      {"user":request.user,
                                       "error":u"入力エラー：日本語"})
        if not answer:
            return render_to_response("ontan/post_wordquestion.html",
                                      {"user":request.user,
                                       "error":u"入力エラー：英語"})
        # save
        wq = WordQuestion(number=number, question=question, answer=answer, author=request.user)
        wq.save()
        return render_to_response("ontan/post_wordquestion.html",
                                  {"user":request.user,
                                   "error":u"保存しました：一問一答(%d)" % number,})
    else: # GET
        return render_to_response("ontan/post_wordquestion.html",
                                  {"user":request.user,})
    
def post_fillquestion_view(request):
    if not request.user.is_authenticated():
        return render_to_response("ontan/post_fillquestion.html",
                                  {"user":request.user,
                                   "error":u"ログインしてください。",
                                   "redirect":"<a href='/ontan/accounts/login/?next=%s'>ログイン</a>" % request.path})
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
                                       "error":u"入力エラー：問題番号"})
        if FillQuestion.objects.filter(number=number).count() > 0:
            return render_to_response("ontan/post_fillquestion.html",
                                      {"user":request.user,
                                       "error":u"問題番号の重複あり"})
        if not question:
            return render_to_response("ontan/post_fillquestion.html",
                                      {"user":request.user,
                                       "error":u"入力エラー：問題文"})
        if not japanese:
            return render_to_response("ontan/post_fillquestion.html",
                                      {"user":request.user,
                                       "error":u"入力エラー：和訳"})
        if not answer:
            return render_to_response("ontan/post_fillquestion.html",
                                      {"user":request.user,
                                       "error":u"入力エラー：答え"})
        if question.count("( )") != len(answer.split(",")):
            raise Http404 # for debug
            return render_to_response("ontan/post_fillquestion.html",
                                      {"user":request.user,
                                       "error":u"問題分(%d)と答え(%d)で空白の数が違います。" % (question.count("( )"), len(answer.split(","))) })
        # save
        wq = FillQuestion(number=number, question=question, japanese=japanese, answer=answer, author=request.user)
        wq.save()
        return render_to_response("ontan/post_fillquestion.html",
                                  {"user":request.user,
                                   "error":u"保存しました：穴埋め問題(%d)" % number,})
    else: # GET
        return render_to_response("ontan/post_fillquestion.html",
                                  {"user":request.user,})
    
def wordquestions_view(request, pagenum):
    pagenum = int(pagenum)
    maxpage = (WordQuestion.objects.count()+1) / 100
    if maxpage < pagenum:
        raise Http404
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
                                   "lang":request.session.get("lang", "en"),
                                   "secnums":secnums,
                                   "sections":sections,
                                   "pages":[(p, "/ontan/question/wordquestions/%d/" % p) for p in xrange(1, maxpage+1)],
                                   "cur_page":pagenum, 
                                   "next_page":"/ontan/question/wordquestions/%d/" % (pagenum+1),
                                   "prev_page":"/ontan/question/wordquestions/%d/" % (pagenum-1), 
                                   "max_page":maxpage})

    
def fillquestions_view(request, pagenum):
    pagenum = int(pagenum)
    maxpage = (FillQuestion.objects.count()+1) / 100
    if maxpage < pagenum:
        raise Http404
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
                                   "pages":[(p, "/ontan/question/fillquestions/%d/" % p) for p in xrange(1, maxpage+1)],
                                   "cur_page":pagenum, 
                                   "next_page":"/ontan/question/fillquestions/%d/" % (pagenum+1),
                                   "prev_page":"/ontan/question/fillquestions/%d/" % (pagenum-1),
                                   "max_page":maxpage})

def exam_wordquestions_view(request):
    # const;
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
                               "lang":request.session.get("lang", "en"),
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
        return render_to_response("ontan/error.html",
                                  {"message":u"すでにログインしています。",
                                   "user":request.user,})
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
                        nextpath = request.GET.get("next", "/ontan/")
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
                                           "error":u"クッキーを有効にしてからもう一度入力してください。"})
        else:
            request.session.set_test_cookie()
            return render_to_response("ontan/login.html",
                                      {"user":request.user,
                                       "error":""})
def login_ajax_view(request):
    if request.user.is_authenticated():
        return HttpResponse(u"すでにログインしています。")
    else:
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(username=username, password=password)
            if user != None:
                if user.is_active:
                    login(request, user)
                    nextpath = request.GET.get("next", "/ontan/")
                    return HttpResponse(u"1")
                else:
                    return HttpResponse(u"このアカウントは無効化されています。")
            else:
                return HttpResponse(u"ユーザー名またはパスワードが違います。")
        else:
            return HttpResponseRedirect("/ontan/accounts/login/")

def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
        return HttpResponse(u"1")
    else:
        return HttpResponse(u"まだログインしていません。")

def adduser_view(request):
    if request.user.is_authenticated():
        return render_to_response("ontan/error.html",
                                  {"message":u"すでにログインしています。",
                                   "user":request.user,})
    else:
        if request.method == "POST":
            error = {}
            if not request.session.test_cookie_worked():
                error["top"] = u"クッキーを有効にしてください"
            request.session.delete_test_cookie()

            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            password_ =  request.POST.get("password_")
    
            if not username: 
                error["username"] = u"ユーザー名を入力してください"
            else:
                if not ALLOWED_CHAR.match(username): error["username"] = u"ユーザー名は半角英数字と@/+/./-のみ使えます"
                else:
                    try:
                        User.objects.get(username=username)
                    except ObjectDoesNotExist:
                        pass # this username is unique and ok!
                    else:
                        error["username"] = u"このユーザー名はすでに使われています"
            if email: 
                if not ALLOWED_EMAIL.match(email): error["email"] = u"Emailアドレスが正しくありません"
            if not password: 
                error["password"] = u"パスワードを入力してください"
            else:
                if not password_: 
                    error["password_"] = u"パスワードを入力してください"
                else:
                    if password != password_: 
                        error["password_"] = u"パスワードが一致しません"
                    else:
                        if not ALLOWED_CHAR.match(password): error["password"] = u"パスワードは半角英数字と@/+/./-のみ使えます"

            if len(error):
                request.session.set_test_cookie()
                return render_to_response("ontan/adduser_input.html",
                                          {"user":request.user, 
                                           "error":error})
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                cl = CheckedList(user=user, name="とりあえずリスト")
                cl.save()
                user = authenticate(username=username, password=password)
                if user != None:
                    login(request, user)
                return render_to_response("ontan/adduser_successful.html",
                                         {"user":request.user, })
        else:
            request.session.set_test_cookie()            
            return render_to_response("ontan/adduser_input.html",
                                      {"user":request.user, })
    
def contact_view(request):
    error = {}
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        title = request.POST.get("title")
        body = request.POST.get("body")

        if not body:
            error["body"] = u"何か入力してください。"
        try:
            mail_admins("From:%s Title:%s" % (name, title),
                       "Email: %s\n" % email +
                       "Message:\n" + 
                       body,
                       fail_silently=False)
            return render_to_response("ontan/contact_.html",
                                      {"user":request.user,})
        except SMTPException:
            error["top"] = u"送信エラー"

    return render_to_response("ontan/contact.html",
                              {"user":request.user,
                               "error":error,})

def userinfo_view(request):
    if request.user.is_authenticated():
        clists = [(cl, CheckedQuestion.objects.filter(belong=cl).count())
                      for cl in CheckedList.objects.filter(user=request.user) ]
        return render_to_response("ontan/userinfo.html",
                                  {"user":request.user,
                                   "clists":clists, })
    else:
        return HttpResponseRedirect("/ontan/accounts/login/?next=%s" % request.path)

def add_to_checkedlist_view(request):
    if not request.user.is_authenticated():
        return HttpResponse(u"ログインしてください")
    else:
        if request.method == "POST":
            try:
                qnum = int(request.POST.get("qnum"))
                WordQuestion.objects.get(number=qnum)
            except (ValueError, TypeError, ObjectDoesNotExist):
                return HttpResponse(u"無効なリクエストです")
            else:
                cl = CheckedList.objects.get(user=request.user, name="とりあえずリスト")
                try:
                    CheckedQuestion.objects.get(belong=cl, qnum=qnum)
                except ObjectDoesNotExist:
                    cq = CheckedQuestion(belong=cl, qnum=qnum)
                    cq.save()
                    return HttpResponse(u"問題番号%dを%sに保存しました" % (qnum, cl.name))
                else:
                    return HttpResponse(u"問題番号%dは%sに保存済みです" % (qnum, cl.name))
        else:
            raise Http404
        
    
def checkedlist_wordquestions_view(request, cl_pk):
    if request.user.is_authenticated():
        try:
            cl_pk = int(cl_pk)
        except (ValueError, TypeError):
            raise Http404
        else:
            cl = get_object_or_404(CheckedList, pk=cl_pk, user=request.user)
            try:
                cq = CheckedQuestion.objects.filter(belong=cl)
            except ObjectDoesNotExist:
                questions = []
            else:
                questions = [WordQuestion.objects.get(number=q.qnum) for q in cq]
            return render_to_response("ontan/checkedlist_wordquestions.html",
                                      {"user":request.user,
                                       "questions":questions,
                                       "clist":cl })
    else:
        return HttpResponseRedirect("/ontan/accounts/login/?next=%s" % request.path)
    
def checkedlist_fillquestions_view(request, cl_pk):
    if request.user.is_authenticated():
        try:
            cl_pk = int(cl_pk)
        except (ValueError, TypeError):
            raise Http404
        else:
            cl = get_object_or_404(CheckedList, pk=cl_pk, user=request.user)
            questions = []
            try:
                cq = CheckedQuestion.objects.filter(belong=cl)
            except ObjectDoesNotExist:
                pass # not to Http404!
            else:
                for q in cq:
                    fq = FillQuestion.objects.get(number=q.qnum)
                    question_html = []
                    for i in range(len(fq.answer.split(","))):
                        question_html.append((False, fq.question.split("( )")[i]))
                        question_html.append((True, fq.answer.split(",")[i]))
                    question_html.append((False, fq.question.split("( )")[-1]))
                    questions.append((fq, question_html))
            return render_to_response("ontan/checkedlist_fillquestions.html",
                                      {"user":request.user,
                                       "questions":questions,
                                       "clist":cl })
    else:
        return HttpResponseRedirect("/ontan/accounts/login/?next=%s" % request.path)

    
def checkedlist_view(request, cl_pk=None):
    if request.user.is_authenticated():
        try:
            cl_pk = int(cl_pk)
            cl = get_object_or_404(CheckedList, pk=cl_pk, user=request.user)
        except (ValueError, TypeError):
            clists = [(cl, CheckedQuestion.objects.filter(belong=cl).count())
                      for cl in CheckedList.objects.filter(user=request.user) ]
            return render_to_response("ontan/checkedlists.html",
                                      {"user":request.user,
                                       "clists":clists, })
        else:
            return render_to_response("ontan/checkedlist_outline.html",
                                      {"user":request.user, 
                                       "clist":cl})
    else:
        return HttpResponseRedirect("/ontan/accounts/login/?next=%s" % request.path)

def change_lang_view(request):
    lang = request.GET.get("lang")
    if lang in ["en", "ja"]:
        request.session["lang"] = lang
        return HttpResponse(u"1")
    else:
        return HttpResponse(u"存在しない言語です。")

