import logging

from pystalkd.Beanstalkd import Connection

import sys
import subprocess
import json

sys.path.append('../generic')
sys.path.append('../api')
from consumer import Consumer
from api import API 
from green import Green


class Processor(Consumer):

    def __init__(self, worker_name, beanstalk_host, beanstalk_port, src_store):
        super().__init__(beanstalk_host, beanstalk_port)
        self.logger = logging.getLogger(__name__)
        self.worker_name = worker_name
        self.beanstalk = Connection(host=beanstalk_host, port=beanstalk_port)
        self.src_store = src_store 
        self.sample_api = API()
        self.green = Green()       
 
    def process_job(self, json_job):
        job_dict = json.loads(json_job)
        filename = '{}/{city}/{road_name}/{osm_way_id}/{cam_dir}/{sequence}_{latitude}_{longitude}_{id}.jpg'.format(src_store, **job_dict) 
        sample_id = job_dict['id']
        v = self.green.green_from_file(filename)
        self.logger.info("green: {:.4f}".format(v))
        return self.sample_api.sample(sample_id, v)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    worker_name = sys.argv[1]
    max_jobs = int(sys.argv[2])
    src_queue = sys.argv[3]
    src_store = sys.argv[4] 

    processor = Processor(worker_name, 'localhost', 11300, src_store)
    processor.consume(max_jobs, src_queue)
