#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.core.exceptions import ObjectDoesNotExist
#from django.core.urlresolvers import reverse
from django.contrib.auth import login, logout, authenticate

from pythxsh.footprints.models import *

def index_view(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/footprints/login/?next=/footprints/")
    else:
        return render_to_response("footprints/index.html",
                                  {"user":request.user,
                                   "history":UsageHistory.objects.filter(card__user=request.user).order_by("card__id")})

def get_lonlat_view(request):
    if not request.user.is_authenticated():
        return render_to_response("footprints/error.xml",
                                  {"message":"Prease login before."},
                                  mimetype="application/xhtml+xml")
    else:
        uh_pk = request.GET.get("uh")
        try:
            uh_pk = int(uh_pk)
            uh = UsageHistory.objects.get(pk=uh_pk, card__user=request.user)
        except (ValueError, TypeError, ObjectDoesNotExist):
            return render_to_response("footprints/error.xml",
                                      {"message":"Prease specify correct uh_pk."},
                                      mimetype="application/xhtml+xml")
        try:
            in_station = StationSummary.objects.get(area_code=uh.in_area_code, line_code=uh.in_line_code, station_code=uh.in_station_code)
        except ObjectDoesNotExist:
            return render_to_response("footprints/error.xml",
                                      {"message":"This in_StationCode is wrong."},
                                      mimetype="application/xhtml+xml")
        try:
            out_station = StationSummary.objects.get(area_code=uh.out_area_code, line_code=uh.out_line_code, station_code=uh.out_station_code)
        except ObjectDoesNotExist:
            return render_to_response("footprints/error.xml",
                                      {"message":"This out_StationCode is wrong."},
                                      mimetype="application/xhtml+xml")
        return render_to_response("footprints/lonlat.xml",
                                  {"date":uh.date.strftime("%Y/%m/%d"),
                                   "in_name":in_station.station_name,
                                   "in_lon":in_station.lon,
                                   "in_lat":in_station.lat,
                                   "out_name":out_station.station_name,
                                   "out_lon":out_station.lon,
                                   "out_lat":out_station.lat},
                                  mimetype="application/xhtml+xml")
    
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
                            nextpath = "/footprints/"
                        return HttpResponseRedirect(nextpath)
                    else:
                        request.session.set_test_cookie()
                        return render_to_response("footprints/login.html",
                                                  {"user":request.user,
                                                   "error":u"このアカウントは無効化されています。"})
                else:
                    request.session.set_test_cookie()
                    return render_to_response("footprints/login.html",
                                              {"user":request.user,
                                               "error":u"ユーザー名またはパスワードが違います。"})
            else:
                request.session.set_test_cookie()
                return render_to_response("footprints/login.html",
                                          {"user":request.user,
                                           "error":"クッキーを有効にしてからもう一度入力してください。"})
        else:
            request.session.set_test_cookie()
            return render_to_response("footprints/login.html",
                                      {"user":request.user,
                                       "error":""})


def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
        nextpath = request.GET.get("next")
        if not nextpath:
            nextpath = "/footprints/"
        return HttpResponseRedirect(nextpath)
    else:
        return HttpResponse("まだログインしていません。")

def correction_view(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/footprints/login/?next=/footprints/")
    else:
        if request.method == "POST":
            area_code = request.POST.get("area_code")
            line_code = request.POST.get("line_code")
            station_code = request.POST.get("station_code")
            lon = request.POST.get("lon")
            lat = request.POST.get("lat")
            
            blank = [s for s in range(5) if not [area_code, line_code, station_code, lon, lat][s]]
            
            

