drop database if exists streetview;

create database streetview;
use streetview;

create table sample_points(
  id bigint(20) not null auto_increment,
  city varchar(255) not null,
  road_name varchar(255) not null,
  osm_way_id bigint(20) not null,
  sequence int(11) not null,
  bearing double not null,
  geom Point not null,
  sample_order int(11) not null,
  sample_priority int(11) not null,
  ts timestamp not null,
  cam_dir enum('left', 'right') not null,
  predicted boolean default true,
  value double default 0,
  primary key(id),
  spatial index(geom)
) charset=utf8, engine=MyISAM;
