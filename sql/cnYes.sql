drop table cnyes;
create table cnyes(
newsid bigserial,
link varchar,
type varchar,
title varchar,
info varchar,
source varchar,
content text,
author varchar,
datetime timestamp
);
CREATE UNIQUE INDEX cnyes_news ON cnyes (title,link);
CREATE INDEX cnyes_time ON cnyes (datetime);
