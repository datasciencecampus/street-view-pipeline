# batch loader
# ------------
# get n jobs from db, dump on image_download queue.
import sys
import json
from pystalkd.Beanstalkd import Connection

sys.path.append('../api')
from api import API


def push_jobs(jobs):
    """push jobs to image_download queue."""
    dst_tube = 'image_download_jobs'
    beanstalk = Connection(host='localhost', port=11300)
    print("tubes:", beanstalk.tubes())
    print("switching to", beanstalk.use(dst_tube))
    print("now using", beanstalk.using())

    for job in jobs:
        job_json = json.dumps(job)
        beanstalk.put(job_json)        
        print("pushed {}_{}_{}_{}".format(job['city'], job['osm_way_id'], job['sequence'], job['cam_dir']))
    
    beanstalk.close()
    return len(jobs) 


def transfer_jobs(limit=25000):
    """get all jobs prioritised by sampling order,
    then push to download queue."""
    job_api = API()
    ok, jobs = job_api.all_jobs(limit)
    if not ok:
        return -1
    return push_jobs(jobs)


if __name__ == '__main__':
    limit = int(sys.argv[1])
    transfer_jobs(limit)
