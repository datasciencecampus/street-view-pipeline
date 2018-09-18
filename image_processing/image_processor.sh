#!/bin/bash

WORKER_NAME="ip_proc"

# -1 = Block on queue forever, processing jobs when they arrive.
#  0 = Drain the queue until it is empty. 
#  N = Do N many jobs as long as there exists work in the queue.
SCHEME=0

SRC_QUEUE="image_processing_jobs"
SRC_STORE="../downloaded_images"

# vegetation calculation plugin
PLUGIN="Green"

python3 ./image_processor.py $WORKER_NAME $SCHEME $SRC_QUEUE $SRC_STORE $PLUGIN
