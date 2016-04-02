class READSITE:
	address = None
	content = None
	cj = None
	opener = None

	database=""
	user=""
	password=""
	host=""
	port=""
	conn = None
	table = "cnyes"
	cur = None
	EMPTYNEWS = ("","","","","","")


	def __init__(self,website,filepath):
		self.address = website
		f = open(filepath,'r')
		self.database = f.readline()[:-1]
		self.user = f.readline()[:-1]
		self.password = f.readline()[:-1]
		self.host = f.readline()[:-1]
		self.port =f.readline()[:-1]
		f.close()

	#建立更新資料庫
	def rebuildTable(self,sql):
		print '執行重建Table'
		os.system('psql -d %s -f %s'%(self.database,sql))

	def listLink(self):
		self.cj = cookielib.CookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		self.opener.addheaders = [('Host', 'news.cnyes.com')]
		self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36')]
		r = self.opener.open(self.address)
		self.content = r.read()		
		r.close()
		page = html.fromstring(self.content)
		#print self.content
		for link in page.xpath('//*[@id="listArea"]/ul[11]/ul[1]/div/*'):	
			print link.text
			print self.address[0:-5]+link.text+".htm"
			self.readLink(self.address[0:-5]+link.text+".htm")


	def getFullNews(self,d):
		#self.cj = cookielib.CookieJar()
		#self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		#self.opener.addheaders = [('Host', 'news.cnyes.com')]
		#self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36')]


		url = 'http://news.cnyes.com/Ajax.aspx?Module=GetRollNews'
		values = {'date' : d.strftime("%Y%m%d")}
		data = urllib.urlencode(values)
		req = urllib2.Request(url, data)
		response = urllib2.urlopen(req)
		the_page = response.read()
		response.close()
		print the_page

		page = html.fromstring(the_page)
		n = 0 
		for link in page.xpath('//NewDataSet/Table1'):
			n += 1
			print n
			title = link.xpath('./NEWSTITLE').







		#r = self.opener.open(self.address)

		#http://news.cnyes.com/Ajax.aspx?Module=GetRollNews


		

	def readLink(self,address):
		#self.cj = cookielib.CookieJar()
		#self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		#self.opener.addheaders = [('Host', 'news.cnyes.com')]
		#self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36')]
		print address
		r = self.opener.open(address)
		self.content = r.read()		
		r.close()
		self.parse()


	#啟用DB
	def startDB(self):
		self.conn = psycopg2.connect(database=self.database, user=self.user, password=self.password, host=self.host, port=self.port)

	#結束DB
	def endDB(self):	
		self.conn.close()

	def insertDB(self,data):

		data = (self.table,) + data
		sql = "INSERT INTO %s (link,type,title,info,content,author,datetime,source) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s');"%(data)
		#print sql
		#寫入要commit才能看見
		try:
			self.cur.execute(sql)
			self.conn.commit()
		except Exception as e:
			print e

	def parse(self):
		page = html.fromstring(self.content)

		i = 0
		self.startDB()

		self.cur = self.conn.cursor()	
		for link in page.xpath('//*[@id="container"]//*[@class="list_1 bd_dbottom"]//li/a'):	
			#try:	
			if link.text == "下一頁" or link.text =="上一頁":
				continue
			#print link.text	
			#print link.xpath('../span')
			datatime = link.xpath('../span')[0].text
			#print "type: "+link.xpath('../strong/a')[0].text
			#typ = link.xpath('../strong/a')[0].text.translate({ord(i):None for i in '[]'})
			typ = link.xpath('../strong/a')[0].text[1:-1]
			#print typ
			#print "type: %s datatime: %s"%(typ,datatime)
			i=i+1
			address = link.get("href")
			print "%d Name: %s URL: %s"%(i,link.text,address)
			#補上某些網址不齊
			if address[0:4] != 'http':				
				address = 'http://news.cnyes.com'+address
			#print "address: "+address
			l = urllib.quote(address.encode('utf-8'),safe=':/?=')		
			#print "l: "+ l
			#print "typ:" + typ
			result = self.read(l,typ)
			if result != self.EMPTYNEWS:
				(author,datetime,title,info,fulltext,source) = result
				#for i in result:
				#	print i
				self.insertDB((address,typ,title,info,fulltext,author,datetime,source))
			#except Exception as e:
			#	print e


			#break
		self.cur.close()
		self.endDB()
		print "Done! We gather %s news during this execution."% i


	def read(self,address,category):			
		#try:
		#print address
		r = self.opener.open(address)	
		page = html.fromstring(r.read().decode('utf-8'))				
		r.close()
		#處理頁面錯誤問題
		if len(page.xpath('//*[@id="form1"]//center/h2'))!=0:		
			return self.EMPTYNEWS
		
		#extract title from content
		title = page.xpath('//*[@class="newsContent bg_newsPage_Lblue"]/h1')[0].text
		#extract info from content
		info = page.xpath('//*[@class="newsContent bg_newsPage_Lblue"]/span[@class="info"]')[0].text
		#print info
		
		#extract datetime from info
		year,month,day,hour,mins = re.match(".*(\d{4})-(\d{2})-(\d{2})\W*(\d{2}):(\d{2})", info,re.U).group(1,2,3,4,5)
		datetime = "%s-%s-%s %s:%s"%(year,month,day,hour,mins)
		#print "info: "+ info

		#extract author from info
		if re.match(u"鉅亨網新聞中心",info,re.U) is not None:
			author = "新聞中心"
		elif re.match(u"鉅亨台北資料中心",info,re.U) is not None:
			author = "台北資料中心"
		elif re.match(u"鉅亨網\W+.+",info,re.U) is not None:
			author = ""
		elif re.match(u".+記者(\w+)\W+.+",info,re.U) is not None:
			author = re.match(u".+記者(\w+)\W+.+",info,re.U).group(1)
		elif re.match(u".+編譯(\w+)\W+.+",info,re.U) is not None:
			author = re.match(u".+網編譯(\w+)\W+.+",info,re.U).group(1)
		elif re.match(u"鉅亨網(\w+)\W+.+",info,re.U) is not None:
			author = re.match(u"鉅亨網(\w+)\W+.+",info,re.U).group(1)
		elif re.match(u"(\w+)\W+.+",info,re.U) is not None:			
			author = re.match(u"(\w+)\W+.+",info,re.U).group(1)
		#print "author:%s "%author

		#extract source from info 
		source = ""
		pattern = re.match(u".+\W+\(來源：(.+)\)\W+.+",info,re.U) 
		if pattern is not None:
			source = pattern.group(1)
		#print "source: "+source
		
		#extract fulltext from content
		article = page.xpath('//*[@id="newsText"]/p')
		fulltext =''
		text = []
		for a in article:
			if a.text is not None:
				text.append(a.text)
		fulltext = "\n".join(text).replace(u"'", u"''")
	#	print fulltext
		#print "title:%s\n gg:%s\n article:\n%s\n"%(title,info,fulltext)
		#print "\n\n\n"

		#return infromation in the page
		return (author,datetime,title,info,fulltext,source)
		#except Exception as e:
		#	print e
		

def mainprocess(d):
	type_list =  ["INDEX","fx_liveanal","macro"]
	d_s = d.strftime("%Y%m%d")
	for item in type_list:
		print 'http://news.cnyes.com/%s/sonews_%s%s_1.htm'%(item,d_s,d_s)
		worker = READSITE('http://news.cnyes.com/%s/sonews_%s%s_1.htm'%(item,d_s,d_s),'../../link.info')
		#worker.listLink()
		worker.getFullNews(d)



