# Street view image processing

This module consumes from the **image\_processing\_jobs** queue.

Each consumed job is an image processing task. Upon receiving a new job, the 
consumer will obtain the correspdonding image from the image store (local dir)
of the form:

```
downloaded_images/city/road/osm_way_id/{left,right}/sequence_lat_lon.jpg
```

The image is processed (for example object detection applied) resulting in a 
json encoded result. The result may contain for example scene labels, bounding
boxes, green index..)

At this stage the result is appended to a csv. Although later will be inserted
into a database.

## Dependencies

```bash
sudo pip3 install beanstalk
sudo pip3 install pystalkd
sudo pip3 install opencv-python
```

