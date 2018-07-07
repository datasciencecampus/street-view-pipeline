#!/bin/bash
## main entry point.
## -----------------
## downloads and processes images once per day.
##
## assumes these services are running:
##
## 1) mysql
## 2) beanstalkd
## 3) image api service

echo "==== sanity check ===="
# check that we can connect to teh intern3ts.
# (no icmp)
count=1
while [ $(curl -sI http://www.google.co.uk |grep "200 OK" |wc -l) == 0 ] ;do
  count=$((count*2))
  if [ $count == 64 ] ;then
    echo "GIVING UP. NETWORK DOWN."
    exit 1
  fi
  echo "NETWORK DOWN, RETRY IN" $count "seconds..."
  sleep $count
done

echo "==== get pending jobs from image api ===="
cd data_load
python3 ./batch_loader.py 25000 
cd ..

echo "==== downloading images ===="
cd image_download
key=$(cat key.txt |head -1)
python3 ./downloader.py 0 image_download_jobs image_processing_jobs ../downloaded_images $key
cd ..

echo "==== processing images ===="
cd image_processing
python3 ./image_processor.py ip_proc 0 image_processing_jobs ../downloaded_images
cd ..

#echo "==== interpolate streets ===="
#cd interpolator
#python3 ./interpolate.py
#cd ..

echo "done."
