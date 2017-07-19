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





class ROBOT:
  delta = 1
  target_dt = datetime.datetime.now()-datetime.timedelta(days=delta)
  message = (datetime.datetime.now()-datetime.timedelta(days=delta)).strftime("%Y-%m-%d")+'重點新聞\n'

  def __init__(self):
    self.pgsql = PGSQL_AHA()


  def pickNews(self):
    sql = "SELECT update_dt,tags FROM day_tags where date_dt= '%s' order by update_dt desc limit 1"%self.target_dt.strftime("%Y-%m-%d")
    self.pgsql.cur.execute(sql)
    results = self.pgsql.cur.fetchall()
    t = results[0][0]
    sql = "SELECT A.news_id,rank,title,classCN as type ,newstime,content,tags,link from news_tags as A left join cnyes as B on A.news_id = B.news_id where A.update_dt = '%s' order by rank desc"%t

    self.pgsql.cur.execute(sql)
    results = self.pgsql.cur.fetchall()
    self.news = [{"title":x[2],"url":x[7],"content":x[5]} for x in results]
    i=0
    for result in results:
      i=i+1
      self.message = self.message+"%d: %s\n"%(i,result[2])
    self.caption='一共挑出%d則'%len(results)
    print self.message
    return self

  
  def sendToFBMessager(self,user_id,news):
    data = {}
    data["recipient"] = {"id":user_id}
    data["message"] = {"attachment":{"type":"template","payload":{"template_type":"generic","elements":[]}}};
    img_url = "https://www.esunbank.com.tw/bank/_/media/250df4ad2eef4ae4a96bdfb4ebdda0bb.png?h=130&la=en&w=123"    
    page_token = "EAAJyH5wO1KgBAK8svgUx1LGL5Qg0MB7X2dW8l7hytGZCyTgWbtYzhv2Y3wI1IJQJypPvKDFd2BXPqHBUEnGjZANX85nnV1ArZBZBLqM1YUvdwdLA6ZA6BBH650H1cZC9CvPJZAC5p0OZCw23hlGW2hKv5k4fxQGmgd8oRBolztqIrAZDZD"
    if len(news) > 0:
      i =0
      for n in news:
        i= i + 1
        data["message"]["attachment"]["payload"]["elements"].append({"title":n["title"],"subtitle":n["content"][0:200],"image_url":img_url,"buttons":[{"type":"postback","payload":n["url"],"title":"問我觀點"},{"type":"web_url","url":n["url"],"title":"Read News"}]})
        if i>5:
          break
    else:
      data["message"]["attachment"]["payload"]["elements"].append({"title":"本日無挑選新聞","subtitle":"no news is good news","image_url":img_url,"buttons":[{"type":"postback","payload":"know it","title":"知道了"}]})
    #print json.dumps(data)
    cmd = "curl -X POST -H \"Content-Type: application/json\" -d '%s' https://graph.facebook.com/v2.6/me/messages?access_token=%s"%(json.dumps(data,encoding='utf-8',ensure_ascii=False),page_token)
    print cmd
    cmd_result = os.popen(cmd)
    return self
    
    






  def close(self):
    self.pgsql.close()
    return self






if __name__ =="__main__":

  robot = ROBOT().pickNews()
  fb_list = ['913218818787732','1075475262524149','1040636289336692']
  fb_list.append('1218909591460191')
  fb_list.append('1005514789538213')
  fb_list.append('704548156314710')
  fb_list.append('10209641738669755')
  fb_list.append('10208359871367052')
  #aha
  #jerry
  #julie
  for id in fb_list:
    robot.sendToFBMessager(id,robot.news)  
  robot.close()
  #print robot.pickNews()
  #robot.close()


