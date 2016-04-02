# -*- coding: utf-8 -*- 



import re

#處理掉unicode 和 str 在ascii上的問題
import sys 
import os
import psycopg2
import datetime
#import calendar
#import csv
#import math
#from time import mktime as mktime
import cookielib, urllib2,urllib
from lxml import html,etree
import StringIO

reload(sys) 
sys.setdefaultencoding('utf8') 

class MYDB:
	database=""
	user=""
	password=""
	host=""
	port=""
	conn = None
	cur = None
	def __init__(self,filepath):
		f = open(filepath,'r')
		self.database = f.readline()[:-1]
		self.user = f.readline()[:-1]
		self.password = f.readline()[:-1]
		self.host = f.readline()[:-1]
		self.port =f.readline()[:-1]
		f.close()
		self.startDB()
	#啟用DB
	def startDB(self):
		self.conn = psycopg2.connect(database=self.database, user=self.user, password=self.password, host=self.host, port=self.port)
		self.cur = self.conn.cursor()	


	#結束DB
	def endDB(self):	
		self.cur.close()
		self.conn.close()


	def sendtoFB(self,year,month):

		sql = "SELECT sum(newscount),sum(extract(epoch from process_time))/sum(newscount) from crawler_record where date_trunc('month',data_dt)='%04d-%02d-01' and source='%s';"%(year,month,self.table)
		self.cur.execute(sql)
		(num,speed)  = self.cur.fetchall()[0]




		Title = "完成"
		Result = "成功"
		print num
		print speed
		Detail = "%s 新聞資料獲得，得到%d筆,每筆約花%.02f秒"%("%04d年%02d月"%(year,month),num,speed)
		api = '688430041191592'; 
		api_secret = '6bb097ca9fe10f1bca0c1c320232eba2';
		callback_website = 'https://github.com/ntuaha/TWFS/';
		picture_url_tick = 'http://www.iconarchive.com/icons/pixelmixer/basic/64/tick-icon.png';
		facebook_id = '100000185149998';
		cmd = os.popen("/usr/bin/curl -F grant_type=client_credentials -F client_id=%s -F client_secret=%s -k https://graph.facebook.com/oauth/access_token"%(api,api_secret))
		k = cmd.read()
		access_token = k.split("=")[1] 
		work = "/usr/bin/curl -F 'access_token=%s' -F 'message=%s' -F 'name=%s' -F 'picture=%s' -F 'caption=%s' -k https://graph.facebook.com/%s/feed"%(access_token,Detail,Title,picture_url_tick,Result,facebook_id)
		#print work
		cmd = os.popen(work)
