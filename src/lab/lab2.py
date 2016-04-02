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
jieba.set_dictionary('./dict/dict.txt.big')
jieba.load_userdict("./dict/user_dict.txt")
jieba.analyse.set_stop_words("./dict/user_stop_words.txt")
jieba.analyse.set_idf_path("./dict/idf.txt.big")




def getDB():
  database = 'news'
  user = os.environ.get('AHA_PG_USER')
  password = os.environ.get('AHA_PG_PWD')
  host = os.environ.get('AHA_PG_IP')
  port = os.environ.get('AHA_PG_PORT')
  conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
  cur = conn.cursor()
  return [conn,cur]



def extractTag(s,k):
  #print "Input：", s
  tags = jieba.analyse.extract_tags(s, k)
  print "Output："
  print ",".join(tags)
  return tags


def getTags(cur):
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
  return fx_tags

def getScore(content,fx_tags):
  words = jieba.cut(content, cut_all=False)
  #print words
  w  = [x.encode('utf-8') for x in words]
  ## split
  str_content = set(w)
  ## 找有交集的文字
  score = str_content & fx_tags
  print "score:%d"%len(score)
  return len(score)



if __name__=="__main__":
  #讀入資料

  #讀入postgresql
  [conn,cur] = getDB()
  #sql ="SELECT datetime, type, title, content FROM cnyes WHERE date_trunc('day',datetime)='2015-01-06' and type similar to '%(財經部會|台灣總經|銀行|新台幣)%'"
  fx_tags = getTags(cur)

  sql = "select newstime,classcn,title,content from cnyes where content like '%人民幣%' order by newstime limit 1"
  cur.execute(sql)
  rows = cur.fetchall()
  for row in rows:
    #print content
    content = row[3]
    print content
    s = getScore(content,fx_tags)





  '''
  sql = 'select datetime,type,title,content from cnyes order by datetime limit 1'
  cur.execute(sql)
  rows = cur.fetchall()
  content = []
  for row in rows:
    content.append(row[3])
  #print content
  s = "|".join(content)
  tags = extractTag(s,20)
  with open('./result.txt','w+') as f:
    for tag in tags:
      f.write(tag+"\n")
  set_tags = set(tags)

  with open('./result_news.txt','w+') as f:
    for row in rows:
      row_tags = extractTag(row[3],20)
      se = set(row_tags)&set_tags
      num = len(se)
      if num>0:
        s = "%d, %s, %s, [%s]"%(num,row[0].strftime('%Y-%m-%d %H:%M:%S'),row[2],",".join(list(se)))
        print s
        f.write(s+"\n")
  '''
  conn.close()

