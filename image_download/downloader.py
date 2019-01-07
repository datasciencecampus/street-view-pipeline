import logging
from pathlib import Path
import json

import sys
sys.path.append('../generic')
from consumer import Consumer


class Downloader(Consumer):

    def __init__(self, beanstalk_host, beanstalk_port, dst_queue, dst_store):
        super().__init__(beanstalk_host, beanstalk_port)
        self.logger = logging.getLogger(__name__)

        self.dst_queue = dst_queue
        self.dst_store = dst_store       

        # outgoing jobs
        self.beanstalk.use(dst_queue)
        self.logger.info("now using {}".format(self.beanstalk.using()))


    def cam_dir_deg(self, bearing, cam_dir):
        if cam_dir == 'left':
            return ((bearing - 90) % 360, 0)
        if cam_dir == 'leftup':
            return ((bearing - 90) % 360, 45)
        if cam_dir == 'up':
            return (bearing, 90)
        if cam_dir == 'right':
            return ((bearing + 90) % 360, 0)
        if cam_dir == 'rightup':
            return ((bearing + 90) % 360, 45)

        # default is straight on.
        return bearing

    def download_image(self, lat, lon, cam_direction_degrees):
        """download an image from a remote endpoint."""
        return False


    def download(self, json_job, dst_store):
        """download image from a remote location."""
        def exists(f):
            p = Path(f)
            return p.is_file() and p.stat().st_size > 0

        job_dict = json.loads(json_job)
        self.logger.info("*** processing ***")
        self.logger.info(job_dict)
        dst_img_dir = "{}/{city}/{road_name}/{osm_way_id}/{cam_dir}".format(dst_store, **job_dict)
        dst_meta_dir = "{}/{city}/{road_name}/{osm_way_id}/meta".format(dst_store, **job_dict)
   
        # mkdir -p
        Path(dst_img_dir).mkdir(parents=True, exist_ok=True)
        Path(dst_meta_dir).mkdir(parents=True, exist_ok=True)
     
        dst_file = "{sequence}_{latitude}_{longitude}_{id}".format(**job_dict)
        dst_img_file = dst_img_dir + "/" + dst_file + ".jpg"

        status = {'image': None}

        # download the image
        if exists(dst_img_file):

            self.logger.warning("already have {}".format(dst_img_file))
            status['image'] = 'exists'

        else:

            cam_dir = self.cam_dir_deg(job_dict['bearing'], job_dict['cam_dir'])

            if self.download_image(job_dict['latitude'], job_dict['longitude'], cam_dir):
                status['image'] = 'ok'
            else:
                status['image'] = 'nok'

        return status


    def push_image_processing_job(self, job):
        """after downloading image, tell workers further up the pipeline that
        an image is available for image processing.
        """
        self.beanstalk.put(job)

        # todo: outgoing push status
        return True 


    def process_job(self, json_job):

        # download the image and associated meta data. 
        res = self.download(json_job, dst_store)
        if res['image'] == 'ok' or res['image'] == 'exists':

            # got new image.
            # push a new job onto the image *processing* queue.
            if self.push_image_processing_job(json_job):
                return True 
            else:
                return False 
        else:
            return False 


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO) 
    import sys
    max_jobs = int(sys.argv[1])
    src_queue = sys.argv[2]
    dst_queue = sys.argv[3]
    dst_store = sys.argv[4]

    downloader = Downloader("localhost", 11300, dst_queue, dst_store)
    downloader.consume(max_jobs, src_queue)