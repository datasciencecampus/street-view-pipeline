import logging
from pystalkd.Beanstalkd import Connection
from pprint import pprint
from pathlib import Path
import json
import requests

import sys
sys.path.append('../generic')
from consumer import Consumer


class Downloader(Consumer):

    def __init__(self, beanstalk_host, beanstalk_port, url, key, dim, fov, dst_queue, dst_store):
        super().__init__(beanstalk_host, beanstalk_port)
        self.logger = logging.getLogger(__name__)
        self.url = url
        self.key = key
        self.dim = dim
        self.fov = fov
        self.api = "{}?key={}&size={}&fov={}".format(url, key, dim, fov)
        self.meta_api = "{}/metadata?key={}".format(url, key)

        self.dst_queue = dst_queue
        self.dst_store = dst_store       

        self.http_session = requests.Session()  
        # outgoing jobs
        self.beanstalk.use(dst_queue)
        self.logger.info("now using {}".format(self.beanstalk.using()))


    def snatch_image(self, lat, lng, bearing, pitch, dst):
        """get image."""
        url = "{}&location={},{}&pitch={}&heading={}".format(self.api, lat, lng, pitch, bearing)
        self.logger.info("< {}".format(url))
        res = self.http_session.get(url)
        if res.status_code == 200:
            with open(dst, 'wb') as f:
                f.write(res.content)

            return True
        elif res.status_code == 403:
            self.logger.warning("quota exceeded.")
            sys.exit(0)
        elif res.status_code == 500:
            # this can happen if sample point too far away from nearest sv
            # image - will usually snap to nearest sv image.
            # since expected behavior, just return True. image processing module
            # shuold then deal with case of missing downloaded image.
            self.logger.warn("remote returned 500")
            return True
        else:
            self.logger.error("oops: {}".format(res.status_code))
            return False


    def snatch_meta_data(self, lat, lng, dst):
        """get meta data associated with image."""
        url = "{}&location={},{}".format(self.meta_api, lat, lng)
        self.logger.info("< {}".format(url))
        res = self.http_session.get(url)
        if res.status_code == 200:
            json_res = res.json()
            with open(dst, 'w') as f:
                f.write(json.dumps(json_res, indent=2))
        
            return True
        
        return False


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
        return (bearing, 0)


    def download(self, json_job, dst_store):
        """download and stash image from gsv api."""
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
        dst_meta_file = dst_meta_dir + "/" + dst_file + ".json"
    
        status = {'image': None, 'meta': None}
        # download the image
        if Path(dst_img_file).is_file():
            self.logger.warning("already have {}".format(dst_img_file))
            status['image'] = 'exists'
        else:
            cam_dir, pitch = self.cam_dir_deg(job_dict['bearing'], job_dict['cam_dir'])
            res = self.snatch_image(job_dict['latitude'], job_dict['longitude'], cam_dir, pitch, dst_img_file)
            if res is True:
                status['image'] = 'ok'
            else:
                status['image'] = 'nok'
                
        # download the meta data
        if Path(dst_meta_file).is_file():
            self.logger.warning("alread have {}".format(dst_meta_file))
            status['meta'] = 'exists'
        else:
            res = self.snatch_meta_data(job_dict['latitude'], job_dict['longitude'], dst_meta_file)
            if res is True:
                status['meta'] = 'ok'
            else:
                status['meta'] = 'nok'
       
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

    # gsv api conf.
    url = 'https://maps.googleapis.com/maps/api/streetview'
    key = sys.argv[5] 
    dim = '640x640'
    fov = '90' # default is 90, max = 120

    downloader = Downloader("localhost", 11300, url, key, dim, fov, dst_queue, dst_store)
    downloader.consume(max_jobs, src_queue)

