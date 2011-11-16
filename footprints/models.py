#!/usr/bin/env python
#-*- coding:utf-8 -*-

#Reference
# http://

from django.db import models
from django.contrib.auth.models import User
import datetime


class Card(models.Model):
    user = models.ForeignKey(User)
    TYPE_CHOICE = (
        ("suica", "Suica"),
        ("pasmo", "PASMO"),
        ("icoca", "ICOCA"),
        ("pitapa", "PiTaPa"),
        ("toica", "TOICA"),
        ("iruca", "IruCa"),
        ("nanaco", "nanaco"),
        ("edy", "Edy"),
        ("waon", "WAON"),
        ("quicpay", "QUICPay"),
        ("others", u"その他"),
        )
    card_type = models.CharField(u"カードの種類", max_length=7, choices=TYPE_CHOICE)
    name = models.CharField(u"名前", max_length=50)
    balance = models.IntegerField(u"残高", )
    IDm = models.CharField(u"IDm", max_length=20)
    PMm = models.CharField(u"PMm", max_length=20)
    create_at = models.DateTimeField(u"登録日", default=datetime.datetime.now())
    
    def __unicode__(self):
        return u"Card(%s/%s)" % (self.name, self.card_type)

class StationCode(models.Model):
    AreaCode = models.PositiveIntegerField(u"エリアコード")
    LineCode = models.PositiveIntegerField(u"路線コード")
    StationCode = models.PositiveIntegerField(u"駅コード")
    CompanyName = models.CharField(u"会社名", max_length=20)
    LineName = models.CharField(u"線区名", max_length=30)
    StationName = models.CharField(u"駅名", max_length=20)
    Note = models.CharField(u"備考", max_length=30, null=True, blank=True)
    
    def __unicode__(self):
        return u"StationCode(%s)" % self.StationName

class MStation(models.Model):
    rr_cd = models.PositiveIntegerField(u"鉄道概要コード")
    line_cd = models.PositiveIntegerField(u"路線コード")
    station_cd = models.PositiveIntegerField(u"駅コード", unique=True)
    line_sort = models.PositiveIntegerField(u"路線並び順", null=True, blank=True)
    station_sort = models.PositiveIntegerField(u"駅並び順", null=True, blank=True)
    station_g_cd = models.PositiveIntegerField(u"駅グループコード")
    r_type = models.PositiveIntegerField(u"駅タイプ")
    rr_name = models.CharField(u"鉄道概要名", max_length=40)
    line_name = models.CharField(u"路線名", max_length=80)
    station_name = models.CharField(u"駅名", max_length=80)
    pref_cd = models.PositiveIntegerField(u"都道府県コード")
    lon = models.FloatField(u"経度", null=True, blank=True)
    lat = models.FloatField(u"緯度", null=True, blank=True)
    f_flag = models.BooleanField(u"表示フラグ")
    
    def __unicode__(self):
        return u"MStation(%s)" % self.station_name

class StationExtension(models.Model):
    mstation = models.ForeignKey("MStation")
    rr_name = models.CharField(u"鉄道概要名", max_length=40)
    line_name = models.CharField(u"路線名", max_length=80)
    
    def __unicode__(self):
        return u"StationExtension(%s)" % self.mstation.station_name

class StationSummary(models.Model):
    station_name = models.CharField(u"駅名", max_length=80)
    area_code = models.PositiveIntegerField(u"エリアコード")
    line_code = models.PositiveIntegerField(u"路線コード")
    station_code = models.PositiveIntegerField(u"駅コード")
    lon = models.FloatField(u"経度", null=True, blank=True) ## null=True
    lat = models.FloatField(u"緯度", null=True, blank=True) ## null=True
    m_stationcode = models.ForeignKey(u"StationCode")
    m_mstation = models.ForeignKey(u"MStation", null=True, blank=True)
    update_at = models.DateTimeField(u"更新日時", default=datetime.datetime.now())

    def __unicode__(self):
        return u"StationSummary(%s)" % self.station_name

class StationCorrection(models.Model):
    user = models.ForeignKey(User)
    m_station = models.ForeignKey(u"StationSummary")
    lon = models.FloatField(u"経度")
    lat = models.FloatField(u"緯度")
    date = models.DateTimeField(u"送信日時", default=datetime.datetime.now())
    checked = models.BooleanField(u"確認済み", default=False)

    def __unicode__(self):
        return u"StationCorrection(%s)" % self.m_station.station_name
    
class UsageHistory(models.Model):
    card = models.ForeignKey(u"Card")
    EQP_TYPES = (
        (0x03, u"のりこし精算機"),
        (0x04, u"携帯端末(ことでん)"),
        (0x05, u"バス等車載機"),
        (0x07, u"カード発売機"),
        (0x08, u"自動券売機"),
        (0x09, u"SMART ICOCA クイックチャージ機"),
        (0x12, u"自動券売機(東京モノレール)"),
        (0x14, u"駅務機器(PASMO発行機)(相互利用記念PASMO)"),
        (0x15, u"定期券発売機"),
        (0x16, u"自動改札機"),
        (0x17, u"簡易改札機"),
        (0x18, u"駅務機器(発行機)"),
        (0x19, u"窓口処理機(みどりの窓口)"),
        (0x1A, u"窓口処理機(有人改札)"),
        (0x1B, u"モバイルFeliCa"),
        (0x1C, u"入場券券売機(JRE新幹線乗り換え改札)"),
        (0x1D, u"他社乗り換え自動改札機"),
        (0x1F, u"入金機(JRW/ことでん/PASMO等)"),
        (0x20, u"発行機(モノレール)"),
        (0x22, u"簡易改札機(ことでん)"),
        (0x34, u"カード発売機(せたまる)"),
        (0x35, u"バス等車載機(せたまる車内入金機)"),
        (0x36, u"バス等車載機(車内簡易改札機)"),
        (0x46, u"VIEW ALTTE端末"),
        (0x48, u"VIEW ALTTE端末"),
        (0xC7, u"物販端末"),
        (0xC8, u"自販機"),
        )
    equipment = models.PositiveIntegerField(u"機器種別", choices=EQP_TYPES)
    is_together = models.BooleanField(u"現金、カード類の併用")
    USAGE_TYPES = (
        (0x01, u"自動改札機出場"),
        (0x02, u"SFチャージ"),
        (0x03, u"切符購入"),
        (0x04, u"磁気券精算"),
        (0x05, u"乗り越し精算"),
        (0x06, u"窓口出場"),
        (0x07, u"新規"),
        (0x08, u"控除"),
        (0x0D, u"バス等均一運賃"),
        (0x0F, u"バス等"),
        (0x11, u"再発行"),
        (0x13, u"料金出場"),
        (0x14, u"オートチャージ"),
        (0x1F, u"バス等チャージ"),
        (0x46, u"物販"),
        (0x48, u"ポイントチャージ"),
        (0x4B, u"入場・物販"),
        )
    usage = models.PositiveIntegerField(u"利用種別", choices=USAGE_TYPES)
    PAY_TYPES = (
        (0x00, u"現金・なし"),
        (0x02, u"VIEW"),
        (0x0B, u"PiTaPa"),
        (0x0D, u"オートチャージ対応PASMO"),
        (0x3F, u"モバイルSuica(VIEW決済以外)"),
        )
    payment = models.PositiveIntegerField(u"支払い種別", choices=PAY_TYPES)
    ENTER_TYPES = (
        (0x01, u"入場"),
        (0x02, u"入場出場"),
        (0x03, u"定期入場出場"),
        (0x04, u"入場定期出場"),
        (0x0E, u"窓口出場"),
        (0x0F, u"入場出場(バス等)"),
        (0x12, u"料金定期入場料金出場"),
        (0x17, u"入場出場(乗り継ぎ割引)"),
        (0x21, u"入場出場(バス等乗り継ぎ割引)"),
        )
    enter = models.PositiveIntegerField(u"入出場種別", choices=ENTER_TYPES)
    date = models.DateField(u"処理日付")
    # switch
    in_line_code = models.PositiveIntegerField(u"入場路線コード", null=True, blank=True, help_text=u"鉄道利用時")
    in_station_code = models.PositiveIntegerField(u"入場駅順コード", null=True, blank=True, help_text=u"鉄道利用時")
    
    out_line_code = models.PositiveIntegerField(u"出場路線コード", null=True, blank=True, help_text=u"鉄道利用時")
    out_station_code = models.PositiveIntegerField(u"出場駅順コード", null=True, blank=True, help_text=u"鉄道利用時")
    company_code = models.PositiveIntegerField(u"事業者コード", null=True, blank=True, help_text=u"バス利用時")
    stop_code = models.PositiveIntegerField(u"停留所コード", null=True, blank=True, help_text=u"バス利用時")
    buy_time = models.TimeField(u"利用時刻", null=True, blank=True, help_text=u"物販利用時")
    buy_id = models.PositiveIntegerField(u"物販端末ID", null=True, blank=True, help_text=u"物販利用時")
    
    balance = models.IntegerField(u"残高", )
    AREA_CODE = (
        (0x0, u"首都圏"),
        (0x1, u"???"),
        (0x2, u"関西圏"),
        (0x3, u"地方"),
        )
    in_area_code = models.PositiveIntegerField(u"入場地域コード", choices=AREA_CODE)
    out_area_code = models.PositiveIntegerField(u"出場地域コード", choices=AREA_CODE)
    
    def __unicode__(self):
        return u"UsageHistory(%s)" % self.card.name
"""
class EnterHistory(models.Model):
    card = models.ForeignKey(u"Card")
    
    def __unicode__(self):
        return u"EnterHistory()"

class SFEnterHistory(models.Model):
    card = models.ForeignKey(u"Card")
    
    def __unicode__(self):
        return u"SFEnterHistory()"

class TicketHistory(models.Model):
    card = models.ForeignKey(u"Card")

    def __unicode__(self):
        return u"TicketHistory()"
"""
