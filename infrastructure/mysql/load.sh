#!/bin/bash
## load left and right samples from csv into schema.

if [ $# != 1 ] ;then
  cat << EOF
./load.sh <src csv directory>
EOF
  exit 0
fi

mysql -u root < create.sql

src_dir=$1

for i in $(ls $src_dir"/"*.csv |sed 's/ /;/g') ;do
  f=$(echo $i |sed 's/;/ /g')
  echo "processing" $f
  python3 ./add_priority.py "$f" _tmp.csv
  echo "use streetview;" >_tmp.sql
  cat _tmp.csv \
      |tr -d '\r' \
      |sed 's/way\///' \
      |awk -F ',' '{printf "insert into sample_points values(null, \"%s\", \"%s\", %d, %d, %.2f, ST_GeomFromText(\"POINT(%.6f %.6f)\"), %d, %d, null, \"left\", true,-1);\n", $11, $2, $1, $10, $14, $13, $12, $15, $16}' >>_tmp.sql
  cat _tmp.csv \
      |tr -d '\r' \
      |sed 's/way\///' \
      |awk -F ',' '{printf "insert into sample_points values(null, \"%s\", \"%s\", %d, %d, %.2f, ST_GeomFromText(\"POINT(%.6f %.6f)\"), %d, %d, null, \"right\", true,-1);\n", $11, $2, $1, $10, $14, $13, $12, $15, $16}' >>_tmp.sql 
  mysql -u root < _tmp.sql
  rm -f _tmp.csv _tmp.sql
done

# clean up: remove points with no road name and points not within a city.
mysql -u root -e 'use streetview; delete from sample_points where road_name = ""'
mysql -u root -e 'use streetview; delete from sample_points where city = ""'
