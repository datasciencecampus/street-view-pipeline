#!/bin/bash
## todo: should do this in lang. just fire up a bunch of processes for now.
##
## this starts a load of image processing processes.

# number of processes
# cat /proc/cpuinfo |grep proc |wc -l .. but might be on mac. probably diff 
# there...
PROCS=8

# -1 = Block on queue forever, processing jobs when they arrive.
#  0 = Drain the queue until it is empty. 
#  N = Do N many jobs as long as there exists work in the queue.
SCHEME=0

SRC_QUEUE="image_processing_jobs"
SRC_STORE="../downloaded_images"

for((i=1; i <= $PROCS; i++)) ;do
  worker_name=$(printf "%04d" $i)_r_proc 
  echo $worker_name
  python3 ./image_processor.py $worker_name $SCHEME $SRC_QUEUE $SRC_STORE &  
done
