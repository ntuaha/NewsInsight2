\copy (select * from cnyes where date_trunc('month',newstime)='2015-07-01') to '/home/aha/Project/NewsInsight/data/backup/201507.csv' WITH CSV HEADER;
\copy (select * from cnyes where date_trunc('month',newstime)='2015-08-01') to '/home/aha/Project/NewsInsight/data/backup/201508.csv' WITH CSV HEADER;
\copy (select * from cnyes where date_trunc('month',newstime)='2015-09-01') to '/home/aha/Project/NewsInsight/data/backup/201509.csv' WITH CSV HEADER;
\copy (select * from cnyes where date_trunc('month',newstime)='2015-10-01') to '/home/aha/Project/NewsInsight/data/backup/201510.csv' WITH CSV HEADER;
\copy (select * from cnyes where date_trunc('month',newstime)='2015-11-01') to '/home/aha/Project/NewsInsight/data/backup/201511.csv' WITH CSV HEADER;
\copy (select * from cnyes where date_trunc('month',newstime)='2015-12-01') to '/home/aha/Project/NewsInsight/data/backup/201512.csv' WITH CSV HEADER;
