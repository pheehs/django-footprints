#!/usr/bin/nev python
#-*- coding:utf-8 -*-

import urllib
import urllib2
import cookielib
from xlrd import open_workbook
from BeautifulSoup import BeautifulSoup as BS

#HOSTNAME = "localhost:8000"
HOSTNAME = "pythxsh.geek.jp"
LOGIN_URL = "http://%s/ontan/login/" % HOSTNAME
POSTWORD_URL = "http://%s/ontan/post_wordquestion/" % HOSTNAME
POSTFILL_URL = "http://%s/ontan/post_fillquestion/" % HOSTNAME

def init():
    cj = cookielib.MozillaCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    soup = BS(urllib2.urlopen(LOGIN_URL).read())

    logindata = {"username":"enjoy-muto", "password":"enjoying", "csrfmiddlewaretoken":soup.find("input", {"id":'csrfmiddlewaretoken'}).get("value")}
    print "http://%s/ontan/login/" % HOSTNAME, urllib.urlencode(logindata)
    urllib2.urlopen(LOGIN_URL, urllib.urlencode(logindata))
    return

def setup():
    init()
    wb = open_workbook("media/ontan.xls", )
    
    for sheet in wb.sheets():
        if sheet.name == u"一問一答":
            for r in xrange(sheet.nrows):
                row = sheet.row(r)
                soup = BS(urllib2.urlopen(POSTWORD_URL).read())
                worddata = {"number":int(row[2].value),
                            "question":row[3].value.encode("utf-8"),
                            "answer":row[4].value.encode("utf-8"),
                            "csrfmiddlewaretoken":soup.find("input", {"id":'csrfmiddlewaretoken'}).get("value")}
                print worddata
                d = urllib2.urlopen(POSTWORD_URL, urllib.urlencode(worddata))

        elif sheet.name == u"穴埋め":
            for r in xrange(sheet.nrows):
                row = sheet.row(r)
                soup = BS(urllib2.urlopen(POSTFILL_URL).read())
                filldata = {"number":int(row[2].value),
                            "question":row[3].value.encode("utf-8"),
                            "japanese":row[4].value.encode("utf-8"),
                            "answer":row[5].value.encode("utf-8"),
                            "csrfmiddlewaretoken":soup.find("input", {"id":'csrfmiddlewaretoken'}).get("value")}
                print filldata
                urllib2.urlopen(POSTFILL_URL, urllib.urlencode(filldata))

if __name__ == "__main__":
    setup()
