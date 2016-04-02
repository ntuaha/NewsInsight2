NewsInsight
===========

尋找新聞中間隱藏的訊息


## 資料處理流程

0. 有沒有上一天的資訊，沒有進行 step 1, 或者用直接給定的時間
1. 確認抓到哪一天     啟動時間   結束時間   總新聞數   抓取新聞數量   平均一筆新聞
2. 確認要抓哪一天
3. 清除要抓的那一天的資訊
4. 讀取那一天的頁碼數
5. 開始抓
6. 結束當天對應的當月資訊發佈在Facebook



## 執行流程


0. 建立爬蟲目標位置

	```bash
	$ psql -d library -f ./sql/links.sql
	```

1. 建立資料表，讀入新聞資訊

	```bash
	$ python ./src/extract/read.py [起頭日期8碼] [結束日期8碼]
	```
2. 建立資料表，準備做分析資料表,可已經擁有特定字詞的字串寫入

	```bash
	$ psql -d library -f ./sql/feature.sql
	$ psql -d library -f ./sql/findfeature.sql
	```	

3. 將新聞資料做備份

	```bash
	$ python ../../src/backup/backup.py 
	```



## 資料格式

請參考[Google doc](https://docs.google.com/spreadsheets/d/1crRBz8PG_0RyFh1MZCBON4ipndSpBlNzzWxc8BN9zO0/edit?usp=sharing)

## 授權

本專案試用 MIT 授權
