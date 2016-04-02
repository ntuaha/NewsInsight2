#encoding=utf-8
import os
import datetime
import psycopg2
import sys
sys.path.append('/home/aha/Other_Project/jieba/')
reload(sys)
sys.setdefaultencoding('utf8')

import jieba
import jieba.analyse




class DB:

  def __init__(self):
    user = os.environ.get('AHA_PG_USER')
    password = os.environ.get('AHA_PG_PWD')
    host = os.environ.get('AHA_PG_IP')
    port = os.environ.get('AHA_PG_PORT')
    self.conn = psycopg2.connect(database='news', user=user, password=password, host=host, port=port)
    self.cur = self.conn.cursor()

  def close(self):
    self.conn.close()

  def getNews(self,na,t,types):
    #types = "|".join(types)
    #sql ="SELECT NewsTime, classCN, title, content,news_id FROM cnyes WHERE date_trunc('day',NewsTime)='%s' and classCN similar to '%%(%s)%%'"%(t,types)
    sql ="SELECT NewsTime, classCN, title, content,news_id FROM cnyes WHERE date_trunc('day',NewsTime)='%s' "%(t)
    self.cur.execute(sql)
    rows = self.cur.fetchall()
    result= []
    for row in rows:
      content = row[3]
      print content
      s = na.getScore(content)
      if len(s)>0:
        r = list(row)
        r.append(s)
        result.append(r)
    return result


  def insertNewsTag(self,news_id,tags,update_dt,rank,fx_tags):
    sql ="INSERT INTO news_tags_fx (news_id,tags,update_dt,rank,fx_tags,fx_rank) VALUES (%d,'%s','%s',%d,'%s',%d)"%(news_id,",".join(tags),update_dt,rank,",".join(fx_tags),len(fx_tags))
    self.cur.execute(sql)
    self.conn.commit()

  def insertDayTag(self,date_dt,update_dt,tags,fx_tags):
    sql ="INSERT INTO day_tags_fx (date_dt,update_dt,tags,fx_tags,fx_rank) VALUES ('%s','%s','%s','%s',%d)"%(date_dt,update_dt,",".join(tags),",".join(fx_tags),len(fx_tags))
    self.cur.execute(sql)
    self.conn.commit()


class NEWS_ANALYSE:
  TAG_SIZE = 20
  def __init__(self):
    jieba.set_dictionary('/home/aha/Project/NewsInsight/src/lab/dict/dict.txt.big')
    jieba.load_userdict("/home/aha/Project/NewsInsight/src/lab/dict/user_dict.txt")
    jieba.analyse.set_stop_words("/home/aha/Project/NewsInsight/src/lab/dict/user_stop_words.txt")
    jieba.analyse.set_idf_path("/home/aha/Project/NewsInsight/src/lab/dict/idf.txt.big")

  def extractTag(self,s):
    #print "Input：", s
    tags = jieba.analyse.extract_tags(s, self.TAG_SIZE)
    print "Output："
    print ",".join(tags)
    return tags

  def getTags(self,cur):
    sql = "select keyword from keywords where product='外匯'"
    cur.execute(sql)
    rows = cur.fetchall()
    tags = []
    for row in rows:
      tags.append(row[0])
    #  print row[0]
      fx_tags = set(tags)
    #print fx_tags
    #print len(fx_tags)
    self.fx_tags = fx_tags
    return fx_tags

  def getScore(self,content):
    words = jieba.cut(content, cut_all=False)
    #print words
    w  = [x.encode('utf-8') for x in words]
    ## split
    str_content = set(w)
    ## 找有交集的文字
    score = str_content & self.fx_tags
    print "score:%d"%len(score)
    return score

if __name__=="__main__":
  #try:
    #[year,month,day] = map(int,sys.argv[1:4])
  #except e:
  # raise '請輸入正確數值'
  now = datetime.datetime.now()
  [year,month,day] = [now.year,now.month,now.day]
  get_time = datetime.datetime(year,month,day)
  #get_time = datetime.datetime.now().strftime('%Y-%m-%d')
  current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  db = DB()
  na = NEWS_ANALYSE()
  #get keyword for foreign exchange
  fx_tags = na.getTags(db.cur)
  #types = ['財經部會','台灣總經','銀行']

  records = db.getNews(na,get_time,fx_tags)


  #get Tags from all news
  total_words = [record[3] for record in records]

  total_words ="|".join(total_words)
  day_tags = na.extractTag(total_words)
  rank_set = list(set([d.encode('utf-8') for d in day_tags])&fx_tags)
  db.insertDayTag(get_time, current_time,day_tags,rank_set)
  set_day_tags = set(day_tags)

  # get Tags of each news
  for record in records:
    content = record[3]
    event_id = int(record[4])
    news_tags = na.extractTag(content)
    rank = len(set(news_tags)&set_day_tags)
    db.insertNewsTag(event_id,news_tags,current_time,rank,list(record[-1]))



  db.close()
