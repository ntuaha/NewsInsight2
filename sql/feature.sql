drop table feature;
create table feature(
data_dt timestamp not NULL,
currency varchar not NULL,
score int default 0,
PRIMARY KEY(data_dt,currency)
);
