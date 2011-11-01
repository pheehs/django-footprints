#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.contrib import admin
from pythxsh.footprints.models import *


class CardAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields":["user", "card_type", "name", "balance", "IDm", "PMm", "create_at"],
                "description":u"<font color='red'><b>太字のものは必須入力事項です。</b></font>"}),
        ]
    list_display = ("user", "card_type", "name")

class StationSummaryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields":["station_name", "area_code", "line_code", "station_code", "lon", "lat", "m_stationcode", "m_mstation", "update_at"],
              "description":u"<font color='red'><b>太字のものは必須入力事項です。</b></font>"}),
        ]
    list_display = ("station_name", "area_code", "line_code", "station_code", "lon", "lat")

class UsageHistoryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields":["card", "equipment", "is_together", "usage", "payment", "enter", "date", "in_line_code", "in_station_code", "out_line_code", "out_station_code", "company_code", "stop_code", "buy_time", "buy_id", "balance", "in_area_code", "out_area_code", ],
                "description":u"<font color='red'><b>太字のものは必須入力事項です。</b></font>"}),
        ]
    list_display = ("card", "date", "usage", "equipment", "balance")
    
admin.site.register(Card, CardAdmin)
admin.site.register(StationCode)
admin.site.register(MStation)
admin.site.register(StationExtension)
admin.site.register(StationSummary, StationSummaryAdmin)
admin.site.register(UsageHistory, UsageHistoryAdmin)
