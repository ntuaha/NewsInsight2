# -*- coding: utf-8 -*-

#處理掉unicode 和 str 在ascii上的問題
import sys
import os
import psycopg2
import cookielib, urllib2,urllib
from lxml import html,etree
import StringIO
import datetime
import json

reload(sys)
sys.setdefaultencoding('utf8')


def getRawData(url,d=None):
  #url = 'http://news.cnyes.com/Ajax.aspx?Module=GetRollNews'
  if d is not None:
    value = urllib.urlencode( {'date' : d.strftime("%Y%m%d")})
    response = urllib2.build_opener().open(url,value)
  else:
    response = urllib2.build_opener().open(url)
  the_page = response.read()
  response.close()
  return the_page


def getListDOM(url,d):
  try:
    the_page = getRawData(url,d)
    # 將網頁轉成結構化資料
    parser = etree.XMLParser()
    root = etree.parse(StringIO.StringIO(the_page),parser)
  except lxml.etree.XMLSyntaxError:
    with open('./error.log','w+') as f:
      f.write(StringIO.StringIO(the_page))
    raise 'Error :lxml.etree.XMLSyntaxError'

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



class DB:

  def __init__(self):

    database = 'news'
    user = os.environ.get('AHA_PG_USER')
    password = os.environ.get('AHA_PG_PWD')
    host = os.environ.get('AHA_PG_IP')
    port = os.environ.get('AHA_PG_PORT')
    self.conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    self.cur = self.conn.cursor()
  def close(self):
    self.conn.close()

  def isExistRow(self,newstime,title):
    sql = "SELECT * FROM cnyes WHERE title='%s' and newstime='%s'"%(title,newstime)
    self.cur.execute(sql)
    return len(self.cur.fetchall())>0

  def addNews(self,datum):
    sql_cond = []
    sql_cond.append(['title',"'%s'"%datum['title']])
    sql_cond.append(['link',"'%s'"%datum['link']])
    sql_cond.append(['classCN',"'%s'"%datum['classCN']])
    sql_cond.append(['classEN',"'%s'"%datum['classEN']])
    sql_cond.append(['NewsTime',"'%s'"%datum['NewsTime']])
    sql_cond.append(['CreateDate',"'%s'"%datum['CreateDate']])
    sql_cond.append(['Content',"'%s'"%(datum['Content'].replace("'","''"))])
    cols = ",".join([x[0] for x in sql_cond])
    values = ",".join([x[1] for x in sql_cond])
    sql = "INSERT INTO cnyes (%s) VALUES (%s)"%(cols,values)
#    print sql
    self.cur.execute(sql)
    self.conn.commit()


def parseArgv(values):
  if len(values[1])<8 or len(values[2])<8:
    raise Exception("argc are invalid.")
  a = datetime.datetime(int(values[1][0:4]),int(values[1][4:6]),int(values[1][6:8]))
  b = datetime.datetime(int(values[2][0:4]),int(values[2][4:6]),int(values[2][6:8]))
  print "Start:%s End:%s"%(a.strftime("%Y-%m-%d"),b.strftime("%Y-%m-%d"))
  return (a,b)


if __name__ == "__main__":
  if len(sys.argv)<2:
    raise ('Too few arguments to execute')

  (start_dt,end_dt) = parseArgv(sys.argv)
  itr = start_dt
  db = DB()
  while itr <= end_dt:
    now = itr
    t = datetime.datetime(now.year,now.month,now.day)
    print t
    print "開始處理... "
    # 抓指定位置的連結
    # 抓網頁下來

    rows =  getListDOM('http://news.cnyes.com/Ajax.aspx?Module=GetRollNews',t)
    #data  = []
    total_num = len(rows)
    i = 0
    for row in rows:
      i = i+1
      print "\r[%d/%d] (%.2f%%)"%(i,total_num,float(i)/total_num*100.0),
      datum ={}
      try:
        datum['title'] = row.xpath('.//NEWSTITLE')[0].text.strip()
        datum['link'] = 'http://news.cnyes.com'+row.xpath('.//SNewsSavePath')[0].text.strip()
        datum['classCN'] = row.xpath('.//ClassCName')[0].text.strip()
        datum['classEN'] = row.xpath('.//CLASSENAME')[0].text.strip()
        datum['NewsTime'] = t.strftime("%Y-%m-%d ")+row.xpath('.//NewsTime')[0].text.strip()
        datum['CreateDate'] = row.xpath('.//CreateDate')[0].text.strip().replace("T"," ").replace("+08:00","")
        if db.isExistRow(datum['NewsTime'],datum['title'])==False:
          try:
            datum['Content'] = getContent(datum['link']).strip()
            db.addNews(datum)
          except:
            print "Error via getContent"
      except AttributeError:
        with open('./error.log','w+') as f:
          etree.tostring(row, pretty_print=True)

    itr = itr + datetime.timedelta(days=1)
#      print "加一條"
#    else:
#      print "重複"

  db.close()

