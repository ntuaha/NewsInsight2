# -*- coding: utf-8 -*-


import sys
import os
import psycopg2
import cookielib, urllib2,urllib
from lxml import html,etree
import StringIO
import datetime
import json
#處理掉unicode 和 str 在ascii上的問題
reload(sys)
sys.setdefaultencoding('utf8')

from pymongo import ASCENDING, DESCENDING
#aha's library
sys.path.append('/home/aha/Project/NewsInsight/src/lab2/rawdata/')
from WEB import WEB
from RAW_DB import RAW_DB



class CNYES_DB(RAW_DB):
  def __init__(self,path):
    RAW_DB.__init__(self,path,"news")
    self.table = self.db["cnyes"]

  def isExistNews(self,record):
    if self.table.find({'Title':record['Title'],'NewsTime':record['NewsTime']}).count()>0:
      return True
    else:
      return False

  def bulkInsertNews(self,news,crawler):
    insert_data = []
    i = 0
    rows_cnt = len(news)
    for n in news:
      #重複就不加入
      #計數器
      i = i+1
      print "\r[%d/%d] (%.2f%%)"%(i,rows_cnt,float(i)/rows_cnt*100.0),
      if self.isExistNews(n) ==False:
        try:
      #    print n['Link']
          d = crawler.fetchContent(n['Link'])
          n['Content'],n["Info"] = d["content"],d["info"]
        except:
          print "Error at getContent"
        insert_data.append(n)
        #print n
      else:
        #print "%s,%s"% (n["Title"],n["NewsTime"])
        pass
    count = len(insert_data)
    if count >0:
      self.table.insert(insert_data)
      #Build index
      self.table.create_index([("NewsTime", DESCENDING), ("Title", ASCENDING)])
    self.db["log"].insert({"crawler_dt":datetime.datetime.now(),"modified_record":count,"source":"cnyes"})
    return count


class CNYES:
  link_url = 'http://news.cnyes.com/Ajax.aspx?Module=GetRollNews'
  def __init__(self):
    self.web = WEB()


  def fetchListDOM(self,datum):
    the_page = self.web.getRawData(self.link_url,datum)
    # 將網頁轉成結構化資料
    parser = etree.XMLParser()
    root = etree.parse(StringIO.StringIO(the_page),parser)
    # 抓指定位置的連結
    return root.xpath('.//Table1')

  def fetchContent(self,url):
      the_page = self.web.getRawData(url)
      parser = etree.HTMLParser()
      root = etree.parse(StringIO.StringIO(the_page),parser)
      contents =  root.xpath('//*[@id="newsText"]//text()')
      content = []
      for c in contents:
        part = c.strip()
        if part != "":
          content.append(part)
      info = root.xpath("//*[contains(@class, 'info')]")[0].text.strip()
      return {"content":content,"info":info}


  def fetchNews(self,data,target_dt,limit=0):
    rows = self.fetchListDOM(data)
    rows_cnt = len(rows)
    i = 0
    news = []
    for row in rows:
      try:
        datum ={}
        datum['Title'] = row.xpath('.//NEWSTITLE')[0].text.strip()
        datum['Link'] = 'http://news.cnyes.com'+row.xpath('.//SNewsSavePath')[0].text.strip()
        datum['ClassCN'] = row.xpath('.//ClassCName')[0].text.strip()
        datum['ClassEN'] = row.xpath('.//CLASSENAME')[0].text.strip()
        #datum['NewsTime'] = t.strftime("%Y-%m-%d ")+row.xpath('.//NewsTime')[0].text.strip()
        datum['NewsTime'] = datetime.datetime.strptime(target_dt.strftime("%Y-%m-%d ")+row.xpath('.//NewsTime')[0].text.strip(),"%Y-%m-%d %H:%M:%S")
        #datum['CreateDate'] = row.xpath('.//CreateDate')[0].text.strip().replace("T"," ").replace("+08:00","")
        datum['CreateDate'] = datetime.datetime.strptime(row.xpath('.//CreateDate')[0].text.strip().replace("T"," ").replace("+08:00",""),"%Y-%m-%d %H:%M:%S")
        news.append(datum)
      except AttributeError:
        print 'there exists a None object '

      if limit>0 and i >=limit:
        break
    return news





if __name__ =="__main__":
  cnyes = CNYES()
  print os.path.dirname(__file__)+"/../mongodb.inf"
  db = CNYES_DB(os.path.dirname(__file__)+"/../mongodb.inf")
  if len(sys.argv)<2:
    raise "Too Few Parameters"
  else:
    start_dt = datetime.datetime.strptime(sys.argv[1],'%Y%m%d')
    end_dt = datetime.datetime.strptime(sys.argv[2],'%Y%m%d')
    while start_dt <= end_dt:
      d = {'date' : start_dt.strftime("%Y%m%d")}
      print d['date']
      news = cnyes.fetchNews(d,start_dt,0)
      #Append News
      print db.bulkInsertNews(news,cnyes)
      start_dt = start_dt + datetime.timedelta(days=1)

