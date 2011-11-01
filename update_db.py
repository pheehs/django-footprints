#! /usr/bin/env python
#-*- coding:utf-8 -*-

#Reference
# http://www.ekidata.jp StationData
# http://www014.upp.so-net.ne.jp/SFCardFan/ StationCode

import os
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"
from django.core.management import setup_environ
import settings
setup_environ(settings)
    
from xlrd import open_workbook
from urllib import urlencode, urlretrieve
from zipfile import ZipFile
from datetime import datetime
from difflib import SequenceMatcher

from django.core.exceptions import ObjectDoesNotExist
from footprints.models import *

#from http://www.ekidata.jp/master/pref.html
PREF_CODE = {1:u"北海道", 2:u"青森県", 3:u"岩手県", 4:u"宮城県", 5:u"秋田県", 6:u"山形県", 7:u"福島県", 8:u"茨城県", 9:u"栃木県", 10:u"群馬県", 11:u"埼玉県", 12:u"千葉県", 13:u"東京都", 14:u"神奈川県", 15:u"新潟県", 16:u"富山県", 17:u"石川県", 18:u"福井県", 19:u"山梨県", 20:u"長野県", 21:u"岐阜県", 22:u"静岡県", 23:u"愛知県", 24:u"三重県", 25:u"滋賀県", 26:u"京都府", 27:u"大阪府", 28:u"兵庫県", 29:u"奈良県", 30:u"和歌山県", 31:u"鳥取県", 32:u"島根県", 33:u"岡山県", 34:u"広島県", 35:u"山口県", 36:u"徳島県", 37:u"香川県", 38:u"愛媛県", 39:u"高知県", 40:u"福岡県", 41:u"佐賀県", 42:u"長崎県", 43:u"熊本県", 44:u"大分県", 45:u"宮崎県", 46:u"鹿児島県", 47:u"沖縄県", 99:u"その他"}

class DataUpdater(object):
    def __init__(self):
        pass

    def updateMStation(self, download):
        print "[-- Update MStation --]"
        print "[*] downloading new data."
        if download:
            urlretrieve("http://www.ekidata.jp/download/dl.php", "media/m_station.zip", data=urlencode({"pv":1}))
        
        zf = ZipFile("media/m_station.zip", "r")
        csv_data = zf.read("m_station.csv").decode("euc-jp")
        zf.close()
        
        print "[*] parsing the data."
        for c in csv_data.strip().split("\n")[1:]:
            s = c.split(",")
            try:
                ms = MStation.objects.get(lon=float(s[11]), lat=float(s[12]))
            except ObjectDoesNotExist:
                ms = MStation(rr_cd=int(s[0]), line_cd=int(s[1]), station_cd=int(s[2]), line_sort=int(s[3]), station_sort=int(s[4]), station_g_cd=int(s[5]), r_type=int(s[6]), rr_name=s[7], line_name=s[8], station_name=s[9], pref_cd=int(s[10]), lon=float(s[11]), lat=float(s[12]), f_flag=bool(int(s[13])))
                print "new", "--", ms, u"(%s)" % s[9]
                ms.save()
            else:
                se = StationExtension(mstation=ms, rr_name=s[7], line_name=s[8])
                print "extension", "--", se, ms, u"(%s)" % s[9]
                se.save()
        print
        return
    
    def updateStationCode(self, download=True):
        print "[-- Update StationCode --]"
        print "[*] downloading new data."
        if download:
            urlretrieve("http://www.denno.net/SFCardFan/sendmdb.php", "media/StationCode.xls")
        wb = open_workbook("media/StationCode.xls", encoding_override="cp932")
        c = 0
        print "[*] parsing the data."
        for sheet in wb.sheets():
            if sheet.name == u"StationCode":
                for r in xrange(1, sheet.nrows):
                    c += 1
                    row = sheet.row(r)
                    sc = StationCode(AreaCode=int(row[0].value), LineCode=int(row[1].value), StationCode=int(row[2].value), CompanyName=row[3].value, LineName=row[4].value, StationName=row[5].value, Note=row[6].value)
                    print c, sc, u"(%s)" % row[5].value
                    
                    sc.save()
                break
        print
        return
        
    def update(self, auto_no_much=True, updateMStation=True, updateStationCode=True):
        
        if updateMStation:
            [m.delete() for m in MStation.objects.all()]
            self.updateMStation()
        if updateStationCode:
            [m.delete() for m in StationCode.objects.all()]
            self.updateStationCode()
        # sort out
        StationSummary.objects.all().delete()
        query = StationCode.objects.all()
        no_much = []
        undecided = []
        for c, station in enumerate(query):
            print "[--", station.StationName, "(%d/%d)--]" % (c+1, len(query))
            q = MStation.objects.filter(station_name=station.StationName).all()
            jr = MStation.objects.filter(station_name=station.StationName, rr_name="JR")
            if len(jr) > 0:
                q = jr
                
            if len(q) == 0:
                ss = StationSummary(station_name=station.StationName, area_code=station.AreaCode, line_code=station.LineCode, station_code=station.StationCode, lon=None, lat=None, m_stationcode=station, m_mstation=None)
                print ss
                ss.save()
                print "No mutch"
                no_much.append(station.StationName)
            elif len(q) == 1:
                s = q[0]
                ss = StationSummary(station_name=station.StationName, area_code=station.AreaCode, line_code=station.LineCode, station_code=station.StationCode, lon=s.lon, lat=s.lat, m_stationcode=station, m_mstation=s)
                ss.save()
                print (s.lon, s.lat)
            elif q.count() > 1:
                print u"会社名:%s 線区名:%s 備考:%s" % (station.CompanyName, station.LineName,station.Note)
                # copare ratio
                choice = []
                ratio = []
                matcher = SequenceMatcher()
                for s in q:
                    matcher.set_seqs(s.line_name, station.LineName)
                    ratio.append(matcher.ratio())
                    matcher.set_seq2(station.Note)
                    ratio[-1] += matcher.ratio()
                    matcher.set_seqs(s.rr_name, station.CompanyName)
                    ratio[-1] += matcher.ratio()
                    choice.append(s)
                    for es in StationExtension.objects.filter(mstation=s):
                        matcher.set_seqs(es.line_name, station.LineName)
                        ratio[-1] += matcher.ratio()
                        matcher.set_seq2(station.Note)
                        ratio[-1] += matcher.ratio()
                        matcher.set_seqs(es.rr_name, station.CompanyName)
                        ratio[-1] += matcher.ratio()
                
                print u"候補:"
                for i,s in enumerate(choice):
                    print i+1, u"鉄道概要名:%s 路線名:%s 都道府県:%s" % (s.rr_name, s.line_name, PREF_CODE[s.pref_cd]), (s.lon, s.lat)
                if max(ratio) != 0:
                    maxs = max_s(ratio)
                    if len(maxs) > 1:
                        print u"[*] 自動判別不能!!"
                        undecided.append((station, [choice[i] for i in maxs], c+1))
                        continue
                    else:
                        print u"[*] 自動判別完了"
                        s = choice[maxs[0]]
                        ss = StationSummary(station_name=station.StationName, area_code=station.AreaCode, line_code=station.LineCode, station_code=station.StationCode, lon=s.lon, lat=s.lat, m_stationcode=station, m_mstation=s)
                        ss.save()
                        print (s.lon, s.lat)
                else:
                    undecided.append((station, choice, c+1))
                    continue
        print
        print u"自動判別不能:\a"
        for station, choice, c in undecided:
            print "[--", station.StationName, "(%d/%d)--]" % (c, len(query))
            print u"会社名:%s 線区名:%s 備考:%s" % (station.CompanyName, station.LineName,station.Note)
            for i, s in enumerate(choice):
                print i+1, u"鉄道概要名:%s 路線名:%s 都道府県:%s" % (s.rr_name, s.line_name, PREF_CODE[s.pref_cd]), (s.lon, s.lat)
            if auto_no_much:
                ss = StationSummary(station_name=station.StationName, area_code=station.AreaCode, line_code=station.LineCode, station_code=station.StationCode, lon=None, lat=None, m_stationcode=station, m_mstation=None)
            else:
                ri = raw_input("Which?(0 to None)>")
                if int(ri) == 0:
                    ss = StationSummary(station_name=station.StationName, area_code=station.AreaCode, line_code=station.LineCode, station_code=station.StationCode, lon=None, lat=None, m_stationcode=station, m_mstation=None)
                    ss.save()
                    continue
                else:
                    s = choice[int(ri)-1]
                    ss = StationSummary(station_name=station.StationName, area_code=station.AreaCode, line_code=station.LineCode, station_code=station.StationCode, lon=s.lon, lat=s.lat, m_stationcode=station, m_mstation=s)
                    ss.save()
                    continue
        print
        print "Total:", len(query)
        print "No much:", len(no_much)
        print ",".join(no_much)
        return

def max_s(vals):
  max_val = vals[0]
  maxi = set((0,))
  for i,x in enumerate(vals):
      if x > max_val: 
          maxi.clear()
          maxi.add(i)
          max_val = x
      elif x == max_val:
          maxi.add(i)
  res = []
  while 1:
      try:
          res.append(maxi.pop())
      except KeyError:
          break
  return res

if __name__ == "__main__":
    updater = DataUpdater()
    updater.update(auto_no_much=True, updateMStation=True, updateStationCode=True)


