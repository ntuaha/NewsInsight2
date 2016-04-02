drop table day_tags_fx;
drop table news_tags_fx;
create table day_tags_fx (like day_tags including defaults);
create table news_tags_fx (like news_tags including defaults);
