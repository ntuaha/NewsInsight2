#encoding=utf-8
import jieba
import jieba.analyse
import psycopg2
import sys

reload(sys)
sys.setdefaultencoding('utf8')



def getDB():

  f = open('../../link.info','r')
  database = f.readline()[:-1]
  user = f.readline()[:-1]
  password = f.readline()[:-1]
  host = f.readline()[:-1]
  port =f.readline()[:-1]
  f.close()
  conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
  cur = conn.cursor()
  return [conn,cur]



def extractTag(s,k):
  #print "Input：", s
  tags = jieba.analyse.extract_tags(s, k)
  print "Output："
  print ",".join(tags)
  return tags


if __name__=="__main__":
  jieba.set_dictionary('./dict/dict.txt.big')
  jieba.load_userdict("./dict/user_dict.txt")
  jieba.analyse.set_stop_words("./dict/user_stop_words.txt")
  jieba.analyse.set_idf_path("./dict/idf.txt.big")

  [conn,cur] = getDB()
  sql ="SELECT datetime, type, title, content FROM cnyes WHERE date_trunc('day',datetime)='2015-01-06' and type similar to '%(財經部會|台灣總經|銀行|新台幣)%'"
  cur.execute(sql)
  rows = cur.fetchall()
  content = []
  for row in rows:
    content.append(row[3])
  #print content
  s = "|".join(content)
  tags = extractTag(s,20)
  f = open('./result.txt','w+')
  for tag in tags:
    f.write(tag+"\n")
  f.close()
  set_tags = set(tags)

  f = open('./result_news.txt','w+')
  for row in rows:
    row_tags = extractTag(row[3],20)
    se = set(row_tags)&set_tags
    num = len(se)
    if num>0:
      s = "%d, %s, %s, [%s]"%(num,row[0].strftime('%Y-%m-%d %H:%M:%S'),row[2],",".join(list(se)))
      print s
      f.write(s+"\n")
  f.close()




  conn.close()

