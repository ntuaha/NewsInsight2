# -*- coding: utf-8 -*-

import re
import sys
import os
import datetime
import json
#處理掉unicode 和 str 在ascii上的問題
reload(sys)
sys.setdefaultencoding('utf8')

#aha's library
from PTT import PTT_DB,PTT

#Bank_Service
#ForeignEX
#LOAN
#FUND
#boy-girl
#gay
#finance
#creditcard
#Foreign_Inv/lP
#IC-Card
#Lifeismoney
#tax
#CFP
#e-coupon
#food

if __name__ =="__main__":
  board = sys.argv[1]
  ptt = PTT('https://www.ptt.cc/bbs/%s/index.html'%board)
  #db = PTT_DB(os.path.dirname(__file__)+"/mongodb.inf",board)
  #now = datetime.datetime.now()
  #t = datetime.datetime(now.year,now.month,now.day) - datetime.timedelta(days=1)
  t = datetime.datetime(2013,1,1)
  #print t
  #if len(sys.argv)>1:
  #  limit = int(sys.argv[1])
  #else:
  limit = 0
  #posts = ptt.fetchData(t,limit)
  reRun = False
  url = 'https://www.ptt.cc/bbs/%s/index.html'%board
  while 1:
    reRun,url = ptt.crawlData(t,limit,board,url)
    if reRun == False:
      break
  #Append News
  #print db.bulkInsertNews(posts)


