# batch loader
# ------------
# get n jobs from db, dump on image_download queue.
import sys
import json
from pystalkd.Beanstalkd import Connection

sys.path.append('../api')
from api import API


def connect(host, port, dst_tube):
    """connect to beanstalk, use dst_tube tube."""
    beanstalk = Connection(host, port))
    print("tubes:", beanstalk.tubes())
    print("switching to", beanstalk.use(dst_tube))
    print("now using", beanstalk.using())
    return beanstalk


def push_jobs(jobs, beanstalk):
    """push jobs to beanstalk. assume already using tube."""
    if beanstalk.using() == 'default':
        print("warning: using default tube.")

    for job in jobs:
        job_json = json.dumps(job)
        beanstalk.put(job_json)        
        print("pushed {}_{}_{}_{}".format(job['city'], job['osm_way_id'],
                                          job['sequence'], job['cam_dir']))
    
    return len(jobs) 


def existing_jobs(beanstalk, dst_tube):
    """get existing number of jobs on dst_tube."""
    stats = beanstalk.stats_tube(dst_tube)
    return stats['current-jobs-ready']


def transfer_jobs(limit, host, port, dst_tube):
    """get all jobs prioritised by sampling order, then push to download
    queue."""
    beanstalk = connect(host, port, dst_tube)

    # only take what we need.
    limit = max(0, limit - existing_jobs(beanstalk, dst_tube))

    try:
        job_api = API()
        ok, jobs = job_api.all_jobs(limit)

        if not ok:
            return -1
        return push_jobs(jobs)

     finally:
         beanstalk.close()


if __name__ == '__main__':
    limit = int(sys.argv[1])
    transfer_jobs(limit, 'localhost', 11300, 'image_download_jobs')
