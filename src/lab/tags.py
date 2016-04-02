#encoding=utf-8

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

  def getNews(self,t,types):
    types = "|".join(types)
    sql ="SELECT NewsTime, classCN, title, content,news_id FROM cnyes WHERE date_trunc('day',NewsTime)='%s' and classCN similar to '%%(%s)%%'"%(t,types)
    self.cur.execute(sql)
    return self.cur.fetchall()

  def insertNewsTag(self,news_id,tags,update_dt,rank):
    sql ="INSERT INTO news_tags (news_id,tags,update_dt,rank) VALUES (%d,'%s','%s',%d)"%(news_id,",".join(tags),update_dt,rank)
    self.cur.execute(sql)
    self.conn.commit()

  def insertDayTag(self,date_dt,update_dt,tags):
    sql ="INSERT INTO day_tags (date_dt,update_dt,tags) VALUES ('%s','%s','%s')"%(date_dt,update_dt,",".join(tags))
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
  types = ['財經部會','台灣總經','銀行']
  records = db.getNews(get_time,types)
  total_words = []
#get Tags from all news
  for record in records:
    total_words.append(record[3])
  total_words ="|".join(total_words)
  day_tags = na.extractTag(total_words)
  db.insertDayTag(get_time, current_time,day_tags)
  set_day_tags = set(day_tags)

# get Tags of each news
  for record in records:
    content = record[3]
    event_id = int(record[4])
    news_tags = na.extractTag(content)
    rank = len(set(news_tags)&set_day_tags)
    db.insertNewsTag(event_id,news_tags,current_time,rank)



  db.close()
