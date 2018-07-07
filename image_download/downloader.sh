#!/bin/bash

# -1 = Block on queue forever, processing jobs when they arrive.
#  0 = Drain the queue until it is empty. 
#  N = Do N many jobs as long as there exists work in the queue.
SCHEME=0

# The incoming image download job queue.
SRC_QUEUE="image_download_jobs"

# The outgoing image processing job queue.
DST_QUEUE="image_processing_jobs"

# The destination directory/image store location.
DST_STORE="../downloaded_images"

python3 ./downloader.py $SCHEME $SRC_QUEUE $DST_QUEUE $DST_STORE $1
