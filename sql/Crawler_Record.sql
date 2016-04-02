drop table Crawler_Record;

create table Crawler_Record(
source varchar,
data_dt timestamp,
start_time timestamp,
end_time timestamp,
newscount integer,
avg_speed interval,
process_time interval,
Primary key(data_dt,source)
);

