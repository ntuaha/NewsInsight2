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



if __name__ =="__main__":
  ptt = PTT('https://www.ptt.cc/bbs/Loan/index.html')
  db = PTT_DB(os.path.dirname(__file__)+"/mongodb.inf","loan")
  now = datetime.datetime.now()
  t = datetime.datetime(now.year,now.month,now.day) - datetime.timedelta(days=1)
  print t
  if len(sys.argv)>1:
    limit = int(sys.argv[1])
  else:
    limit = 0
  posts = ptt.fetchData(t,limit)

  #Append News
  print db.bulkInsertNews(posts)


