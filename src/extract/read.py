# -*- coding: utf-8 -*-



import re

#處理掉unicode 和 str 在ascii上的問題
import sys
import os
import psycopg2
import datetime
import cookielib, urllib2,urllib
from lxml import html,etree
import StringIO

#自己的libaray
from DB_NOW import DB_NOW
from READSITE import READSITE

reload(sys)
sys.setdefaultencoding('utf8')




def runCrawler(year,month,day,signal):
	if ahaDB.isRawNewsExist(year,month,day) == True:
		print "%s 已完成 在%s"%(ahaDB.date_s,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		return False

	ahaDB.insertStartInfo(year,month,day)

	d = datetime.datetime(year,month,day)
	d_s = d.strftime("%Y%m%d")
	worker = READSITE(ahaDB)
	worker.getFullNewsList(d)


	if ahaDB.insertEndInfo() == True:
		print " ====> %s 完成 在%s"%(ahaDB.date_s,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		if signal==True:
			ahaDB.sendtoFB(year,month)

	return True


def parseArgv(values):
	if len(values[1])<8 or len(values[2])<8:
		raise Exception("argc are invalid.")
	a = datetime.datetime(int(values[1][0:4]),int(values[1][4:6]),int(values[1][6:8]))
	b = datetime.datetime(int(values[2][0:4]),int(values[2][4:6]),int(values[2][6:8]))
	print "Start:%s End:%s"%(a.strftime("%Y-%m-%d"),b.strftime("%Y-%m-%d"))
	return (a,b)

if __name__ == '__main__':
#Global variable
	rebuildTable = False

# 確認時間

	ahaDB = DB_NOW(os.path.dirname(__file__)+'/../../link.info')
	ahaDB.setTable("cnyes")
	#20141001 20141031
	(start_dt,end_dt) = parseArgv(sys.argv)

	init = start_dt
	sendFinalSignal = False
	while init<=end_dt:

		if init==end_dt:
			sendFinalSignal=True


		year = int(init.strftime("%Y"))
		month = int(init.strftime("%m"))
		day = int(init.strftime("%d"))
		runCrawler(year,month,day,sendFinalSignal)
		init = init + datetime.timedelta(days=1)
	ahaDB.endDB()

