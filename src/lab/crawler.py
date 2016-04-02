# -*- coding: utf-8 -*-

#import re

#處理掉unicode 和 str 在ascii上的問題
import sys
#import os

import cookielib, urllib2,urllib
from lxml import html,etree
import StringIO
import datetime
import json

reload(sys)
sys.setdefaultencoding('utf8')


def getRawData(url,d=None):
  #url = 'http://news.cnyes.com/Ajax.aspx?Module=GetRollNews'

  #print url
  #print value
  if d is not None:
    value = urllib.urlencode( {'date' : d.strftime("%Y%m%d")})
    response = urllib2.build_opener().open(url,value)
  else:
    response = urllib2.build_opener().open(url)
  the_page = response.read()
  response.close()
  return the_page


def getListDOM(url,d):
  the_page = getRawData(url,d)
  # 將網頁轉成結構化資料
  parser = etree.XMLParser()
  root = etree.parse(StringIO.StringIO(the_page),parser)
  # 抓指定位置的連結
  return root.xpath('.//Table1')



def getContent(url):
  the_page = getRawData(url)
  parser = etree.HTMLParser()
  root = etree.parse(StringIO.StringIO(the_page),parser)
  contents =  root.xpath('//*[@id="newsText"]//text()')
  content = []
  for c in contents:
      content.append(c.strip())
  return "\n".join(content)

def writeData(data):
  f = open("./data_%s.json"%t.strftime("%Y-%m-%d"),"w+")
  f.write(json.dumps(data))
  f.close()
  f = open("./%s.json"%t.strftime("%Y-%m-%d"),"w+")
  f.write(json.dumps(data).decode('unicode-escape').encode('utf8'))
  f.close()





if __name__ == "__main__":
  try:
    #year = int(raw_input("請輸入年: "))
    #month = int(raw_input("請輸入月: "))
    #day = int(raw_input("請輸入日: "))
    [year,month,day] = map(int,sys.argv[1:4])
  except e:
    raise '請輸入正確數值'
  t = datetime.datetime(year,month,day)
  print "開始處理..."
  # 抓指定位置的連結
  # 抓網頁下來
  try:
    f = open("./data_%s.json"%t.strftime("%Y-%m-%d"),"r")
    data = json.loads(f.read())
    print "已讀資料 %d"%len(data)
    f.close()
  except:
    data=[]

  rows =  getListDOM('http://news.cnyes.com/Ajax.aspx?Module=GetRollNews',t)
  #data  = []

  total_num = len(rows)
  i = 0
  for row in rows:
    i = i+1
    print "\r[%d/%d] (%.2f%%)"%(i,total_num,float(i)/total_num*100.0),
    datum ={}
    datum['title'] = row.xpath('.//NEWSTITLE')[0].text.strip()
    datum['link'] = 'http://news.cnyes.com'+row.xpath('.//SNewsSavePath')[0].text.strip()
    datum['classCN'] = row.xpath('.//ClassCName')[0].text.strip()
    datum['classEN'] = row.xpath('.//CLASSENAME')[0].text.strip()
    datum['NewsTime'] = t.strftime("%Y-%m-%d ")+row.xpath('.//NewsTime')[0].text.strip()
    datum['CreateDate'] = row.xpath('.//CreateDate')[0].text.strip().replace("T"," ").replace("+08:00","")
    datum['Content'] = getContent(datum['link']).strip()
    add_flag = True
    for d in data:
      #如果重複就跳出去
      if d['title'] == datum['title'] and d['NewsTime'] == datum['NewsTime']:
        print "\r%s:重複"%datum['title']
        add_flag=False
        break
    #如果都沒有重複就加入
    if add_flag:
      data.append(datum)
  writeData(data)

