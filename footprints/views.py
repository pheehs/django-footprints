#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import mail_admins
from smtplib import SMTPException
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
                                  {"in_name":in_station.station_name,
                                   "in_lon":in_station.lon,
                                   "in_lat":in_station.lat,
                                   "in_ss_pk":in_station.pk,
                                   "out_name":out_station.station_name,
                                   "out_lon":out_station.lon,
                                   "out_lat":out_station.lat,
                                   "out_ss_pk":out_station.pk},
                                  mimetype="application/xhtml+xml")

def get_balloon_view(request):
    if not request.user.is_authenticated():
        return render_to_response("footprints/error.xml",
                                  {"message":"Prease login before."},
                                  mimetype="application/xhtml+xml")
    else:
        station_pk = request.GET.get("station_pk")
        pks = request.GET.get("uh_pks")
        try:
            station = StationSummary.objects.get(pk=station_pk)
        except (ObjectDoesNotExist, TypeError, ValueError):
            return render_to_response("footprints/error.xml",
                                      {"message":"Prease specify correct station_name, longitude and latitude."},
                                      mimetype="application/xhtml+xml")
        if pks:
            pk_list = pks.split(",")
            if len(pk_list) > 0:
                uh_query = UsageHistory.objects.filter(Q(pk__in=pk_list), 
                                                      Q(in_area_code=station.area_code)|Q(out_area_code=station.area_code),
                                                      Q(in_line_code=station.line_code)|Q(out_line_code=station.line_code),
                                                      Q(in_station_code=station.station_code)|Q(out_station_code=station.station_code),
                                                      ).order_by("-date")
                uh_list = []
                for uh in uh_query:
                    if (uh.in_area_code == station.area_code) and (uh.in_line_code == station.line_code) and (uh.in_station_code == station.station_code):
                        uh_list.append(("in", uh.date.strftime("%Y/%m/%d"), uh.pk))
                    else:
                        uh_list.append(("out", uh.date.strftime("%Y/%m/%d"), uh.pk))
                return render_to_response("footprints/balloon.xml",
                                          {"uh_list":uh_list},
                                          mimetype="application/xhtml+xml")
        
        return render_to_response("footprints/error.xml",
                                  {"message":"Please specify correct uh_pk."},
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

def send_correction_view(request):
    if not request.user.is_authenticated():
        return render_to_response("footprints/error.xml",
                                  {"message":"Prease login before."},
                                  mimetype="application/xhtml+xml")
    else:
        ss_pk = request.GET.get("station_pk")
        lon = request.GET.get("lon")
        lat = request.GET.get("lat")

        try:
            ss = StationSummary.objects.get(pk=int(ss_pk))
        except (ObjectDoesNotExist, TypeError, ValueError):
            return render_to_response("footprints/error.xml",
                                      {"message":"Prease specify correct station_pk."},
                                      mimetype="application/xhtml+xml")
        try:
            lon_f = float(lon)
            lat_f = float(lat)
        except (TypeError, ValueError):
            return render_to_response("footprints/error.xml",
                                      {"message":"Prease specify correct lon and lat."},
                                      mimetype="application/xhtml+xml")
        if ss.lon != lon_f and ss.lat != lat_f:
            correction = StationCorrection(user=request.user, m_station=ss, lon=lon_f, lat=lat_f)
            correction.save()
            try:
                # Prease set EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER(, EMAIL_USE_TLS) and EMAIL_HOST_PASSWORD in settings.py
                mail_admins(u"New StationCorrection!",
                            (u"There is a new StationCorrection.\n\n\n" +
                             u"StationCorrection:\n" +
                             u"http://%(host)s/admin/footprints/stationcorrection/%(sc_pk)d/\n\n" +
                             u"StationSummary:\n" +
                             u"http://%(host)s/admin/footprints/stationsummary/%(ss_pk)d/\n\n") % \
                                {"host":request.get_host(), "sc_pk":correction.pk, "ss_pk":int(ss_pk)},
                            fail_silently=False)
            except SMTPException:
                return render_to_response("footprints/error.xml",
                                          {"message":"Error occured on sending correction."},
                                          mimetype="application/xhtml+xml")
            return render_to_response("footprints/corrected.xml",
                                      mimetype="application/xhtml+xml")

