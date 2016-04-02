# -*- coding: utf-8 -*- 

import sys
import datetime
import MYDB 

reload(sys) 
sys.setdefaultencoding('utf8') 

class DB_NOW(MYDB.MYDB):
	date_s = None
	table = None
	check_dt = None

	def setTable(self,table):
		self.table = table
		
	def getConn(self):
		return 

	def setDate_s(self,year,month,day):
		self.check_dt = datetime.datetime(year,month,day)
		self.date_s = self.check_dt.strftime("%Y-%m-%d")

	def isRawNewsExist(self,year,month,day):
		if self.table ==None:
			raise Exception("No table")

		self.setDate_s(year,month,day)
		sql = "SELECT count(*) from crawler_record where data_dt='%s' and source='%s' and end_time is not NULL"%(self.date_s,self.table)
		self.cur.execute(sql)
		rows = self.cur.fetchall()
		if rows[0][0] >0:
			return True
		else:
			return False


	def insertStartInfo(self,year,month,day):
		if self.table ==None:
			raise Exception("No table")

		self.setDate_s(year,month,day)
		# Delete OLD record
		sql = "DELETE from crawler_record where data_dt='%s' and source='%s';"%(self.date_s,self.table)
		self.cur.execute(sql)
		self.conn.commit()
		sql = "DELETE from %s where date_trunc('day',datetime) = '%s';"%(self.table,self.date_s)
		self.cur.execute(sql)
		self.conn.commit()
		# Insert New Record
		sql  = "INSERT INTO crawler_record (source,data_dt,start_time) VALUES ('%s','%s',NOW())"%(self.table,self.date_s)
		self.cur.execute(sql)
		self.conn.commit()


	def insertEndInfo(self):
		if self.table == None or self.date_s ==None:
			raise Exception("No table or No date_")

		sql  = "SELECT count(*) from %s where date_trunc('day',datetime) = '%s';"%(self.table,self.date_s)
		self.cur.execute(sql)
		data_num  = self.cur.fetchall()[0][0]
		if data_num !=0:
			sql  = "UPDATE crawler_record SET end_time=NOW(),newscount = %d ,process_time = NOW()-start_time, avg_speed = date_trunc('sec',NOW()-start_time)/%d  where data_dt='%s' and source='%s';"%(data_num,data_num,self.date_s,self.table)
		else:
			sql = "UPDATE crawler_record SET end_time=NOW(),newscount = %d ,process_time = NOW()-start_time  where data_dt='%s' and source='%s';"%(data_num,self.date_s,self.table)
		self.cur.execute(sql)
		self.conn.commit()
		return True

	

	def insertNewsDB(self,data):

		data = (self.table,) + data
		sql = "INSERT INTO %s (link,type,title,info,content,author,datetime,source) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s');"%(data)
		self.cur.execute(sql)
		self.conn.commit()



