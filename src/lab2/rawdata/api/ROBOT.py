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



class PGSQL_AHA():
  def __init__(self):
    f = open('/home/aha/Project/NewsInsight/src/lab/link.info','r')
    database = f.readline()[:-1]
    user = f.readline()[:-1]
    password = f.readline()[:-1]
    host = f.readline()[:-1]
    port =f.readline()[:-1]
    f.close()
    self.conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    self.cur = self.conn.cursor()

  def close(self):
    self.conn.close()



class MONGO_AHA(RAW_DB):
  def __init__(self,path):
    RAW_DB.__init__(self,path,"robot")
    self.table = self.db["fb_log"]

  def addLog(self,data):
    self.table.insert({"post_dt":datetime.datetime.now(),"data":data})


class ROBOT:

  target_dt = datetime.datetime.now()-datetime.timedelta(days=1)
  message = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime("%Y-%m-%d")+'重點新聞\n'
  api = '688430041191592'
  api_secret = '6bb097ca9fe10f1bca0c1c320232eba2'
  callback_website = 'http://104.46.234.139/news/index.html'
  picture_url_tick = 'http://media-cache-ec0.pinimg.com/originals/6a/97/aa/6a97aaca218e0606730e1fa1e0acd55e.jpg'
  caption='la la'
  facebook_id = '100000185149998'

  def __init__(self):
    self.pgsql = PGSQL_AHA()


  def pickNews(self):
    sql = "SELECT update_dt,tags FROM day_tags where date_dt= '%s' order by update_dt desc limit 1"%self.target_dt.strftime("%Y-%m-%d")
    self.pgsql.cur.execute(sql)
    results = self.pgsql.cur.fetchall()
    t = results[0][0]
    sql = "SELECT A.news_id,rank,title,classCN as type ,newstime,content,tags from news_tags as A left join cnyes as B on A.news_id = B.news_id where A.update_dt = '%s' order by rank desc"%t

    self.pgsql.cur.execute(sql)
    results = self.pgsql.cur.fetchall()
    i=0
    for result in results:
      i=i+1
      self.message = self.message+"%d: %s\n"%(i,result[2])
    self.caption='一共挑出%d則'%len(results)
    print self.message
    return self

  def sendFB(self):

    opener = urllib2.build_opener()
    #opener.addheaders.append(('Cookie', 'over18=1'))
#    opener.addheaders.append(('grant_type', 'client_credentials'))
#    opener.addheaders.append(('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.99 Safari/537.36'))
    #opener.addheaders.append(('Referer', 'http://gis.mohw.gov.tw/'))
#    opener.addheaders.append(('client_id', self.api))
    #opener.addheaders.append(('client_secret', self.api_secret))
    urllib2.install_opener(opener)
    ff={}
    ff['client_id']=self.api
    ff['client_secret']=self.api_secret
    ff['grant_type']='client_credentials'
    param = urllib.urlencode(ff)
    print 'https://graph.facebook.com/oauth/access_token?%s'%(param)
    response = opener.open('https://graph.facebook.com/oauth/access_token?%s'%(param))

    data = response.read()
    response.close()
    self.access_token = data.split('=')[1]
    print self.access_token

    f = {}
    f['access_token'] = self.access_token
    f['message'] = self.message
    #f['picture'] = self.picture_url_tick
    #f['caption'] = self.caption
    #f['link'] = self.callback_website
    #param = urllib.urlencode(f)
    for k,v in f.iteritems():
      f[k] = urllib.quote(v)
      print f[k]
    #url = 'https://graph.facebook.com/%s/feed?%s&'%(self.facebook_id,data)+param
    url = 'https://graph.facebook.com/%s'%self.facebook_id
    print url


    work = "/usr/bin/curl -F 'access_token=%s' -F 'message=%s' -F 'name=%s' -F 'icon=%s' -F 'caption=%s' -F 'link=%s'  -k https://graph.facebook.com/%s/feed"%(self.access_token,self.message,self.target_dt.strftime("%Y-%m-%d")+"重點財經新聞",self.picture_url_tick,self.caption,self.callback_website,self.facebook_id)
    #print work
    cmd = os.popen(work)
    #opener = urllib2.build_opener()
    #reponse = opener.open(url,urllib.urlencode(f))
    #reponse = opener.open(url)
    #data = response.read()
    #reponse.close()
    print data

    return self
#https://graph.facebook.com/100000185149998/feed?access_token=688430041191592%7C1apOpKzaTmbqC6AIjvSSlJF-4Jo&message=%E6%9C%AC%E6%97%A5%E9%87%8D%E9%BB%9E%E6%96%B0%E8%81%9E%0A
#/usr/local/bin/curl -F grant_type=client_credentials -F client_id=688430041191592 -F client_secret=6bb097ca9fe10f1bca0c1c320232eba2 -k https://graph.facebook.com/oauth/access_token


  def close(self):
    self.pgsql.close()
    return self






if __name__ =="__main__":

  mongo = MONGO_AHA(os.path.dirname(__file__)+"/../mongodb.inf")
  robot = ROBOT().pickNews().sendFB().close()
  #print robot.pickNews()
  #robot.close()


