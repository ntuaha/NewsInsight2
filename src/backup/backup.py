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


if __name__ =="__main__":
	backup_path = '/home/aha/Project/NewsInsight/data/backup'
	sql_file = '/home/aha/Project/NewsInsight/sql/backup.sql'
	f = open(sql_file,'w+')
	for year in range(2015,2016):
		for month in range(1,13):
			#line = "\copy (select * from cnyes where date_trunc('month',datetime)='%04d-%02d-01') to '%s/%04d%02d.csv' WITH CSV HEADER;"%(year,month,backup_path,year,month)
			line = "\copy (select * from cnyes where date_trunc('month',newstime)='%04d-%02d-01') to '%s/%04d%02d.csv' WITH CSV HEADER;\n"%(year,month,backup_path,year,month)
			f.write(line)
	f.close()
	#Copy (Select * From foo) To '/tmp/test.csv' With CSV;
	os.system("psql  -d news  -f %s"%sql_file)
	for year in range(2015,2016):
		for month in range(1,13):
			line = "zip -j %s/%04d%02d.zip %s/%04d%02d.csv;rm %s/%04d%02d.csv"%(backup_path,year,month,backup_path,year,month,backup_path,year,month)
			os.system(line)


