#!/bin/bash
GSV_LIMIT=25000
TARGET_QUEUE="image_download_jobs"
TUBE_PREFIX="backlog"
python3 ./fair_scheduler.py $GSV_LIMIT $TARGET_QUEUE $TUBE_PREFIX
