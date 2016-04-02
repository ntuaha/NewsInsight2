drop table cnyes;
create table cnyes(
news_id bigserial,
title varchar,
link varchar,
classCN varchar,
classEN varchar,
NewsTime timestamp with time zone,
CreateDate timestamp with time zone,
Content varchar,
primary key (title,NewsTime)
);


drop table news_tags;
create table news_tags(
news_id bigint,
tags varchar,
update_dt timestamp with time zone default now(),
rank integer
);


drop table day_tags;
create table day_tags(
  date_dt timestamp with time zone,
  update_dt timestamp with time zone default now(),
  tags varchar
);
