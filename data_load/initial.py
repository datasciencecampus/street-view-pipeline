# initial loader.
# dump all the jobs into the first queue.
# first queues are prefixed with 'backlog_'

import sys
import json
from pystalkd.Beanstalkd import Connection

sys.path.append('../api')
from api import API


def push_city_jobs(city, sample_order):
    """get image download jobs for a city from job api then push them to image
    download queue."""
    dst_tube = 'backlog_' + city.replace(' ', '_').lower()
    beanstalk = Connection(host='localhost', port=11300)
    print("tubes:", beanstalk.tubes())
    print("switching to", beanstalk.use(dst_tube))
    print("now using", beanstalk.using())

    job_api = API()
    ok, jobs = job_api.jobs(city, sample_order)
    if not ok:
        return 0 
    
    for job in jobs:
        job_json = json.dumps(job)
        beanstalk.put(job_json)        
        print("pushed {}_{}_{}_{}".format(job['city'], job['osm_way_id'], job['sequence'], job['cam_dir']))
    
    beanstalk.close()
    return len(jobs) 


def push_all_jobs(sample_order):
    """get jobs for all cities, then push to download queue."""
    job_api = API()
    ok, summaries = job_api.summary()
    if not ok:
        return [0]
    return [push_city_jobs(s['city'], sample_order) for s in summaries]


if __name__ == '__main__':
    sample_order = int(sys.argv[1])
    if len(sys.argv) == 2:
        push_all_jobs(sample_order)
    else:
        city = sys.argv[2]
        push_city_jobs(city, sample_order if sample_order >= 0 else None)
