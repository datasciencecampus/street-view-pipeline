# Fair scheduler
# ==============
#
# Select total number of jobs N to process such that the number of jobs 
# selected from each city is proportionate to the size of the city.
#
# Objective is to fairly distribute the processing progress amongst all
# cities regardless of size such that at any given point in time, all cities
# will be x% complete.
#
# This will form a basis for fair city comparison later on.
import logging
from pystalkd.Beanstalkd import Connection
from pprint import pprint
from math import ceil 
from random import shuffle


class Shovel():
    
    def __init__(self, beanstalk_host, beanstalk_port):
        self.logger = logging.getLogger(__name__)
        self.beanstalk = Connection(host=beanstalk_host, port=beanstalk_port)
        self.logger.info("host: {} {}".format(beanstalk_host, beanstalk_port))

    def watch_single_tube(self, tube):
        """watch a single tube."""
        # todo: is this necessary?
        self.beanstalk.watch(tube)
        watching = [x for x in self.beanstalk.watching() if x != tube]
        for x in watching:
            self.beanstalk.ignore(x)
        self.logger.info("now watching {}".format(self.beanstalk.watching()))

    def move_jobs(self, src_tube, dst_tube, n=0):
        """move n jobs from one tube to another."""
        self.watch_single_tube(src_tube)
        self.beanstalk.watch(src_tube)
        self.beanstalk.use(dst_tube)
        # BATCH DRAIN INTO THIS (note that this bit is not persistent!)
        lifo = []
        while(n > 0):
            job = self.beanstalk.reserve(timeout=60)
            if job is None:
                print("timed out. nothing to do?!")
                return
            lifo.append(job)
            n -= 1

        stack_len = len(lifo)

        # dump stack into destination work queue.
        while(len(lifo) > 0):
            job = lifo.pop()
            self.beanstalk.put(job.body)
            job.delete()

        self.logger.info("drained {} jobs".format(stack_len))

    def drain(self, total_shovel, target_queue, queue_prefix="backlog"):
        self.logger.info("total_shovel: [{}] target_queue: [{}] queue_prefix: [{}]".format(total_shovel, target_queue, queue_prefix))
        backlog = [self.beanstalk.stats_tube(x) for x in self.beanstalk.tubes() if x.startswith(queue_prefix + "_")]
        # shuffle cities.
        # we do this because there is a chance that some of the jobs in the last
        # city to be processed may be left on backlog if number of jobs shoveled
        # so far exceeds maximum processing limit. this happens due to 
        # accumulation of rounding error.
        shuffle(backlog)

        total_jobs = sum(city['current-jobs-ready'] for city in backlog)
        total_shovel = min(total_jobs, total_shovel)

        self.logger.info("jobs remaining: [{}] jobs to shovel: [{}]".format(total_jobs, total_shovel))

        done = 0
        for city in backlog:
            name, jobs = city['name'], city['current-jobs-ready']
            weight = jobs / total_jobs
            shovel = ceil(weight * total_shovel)
            done += shovel 
    
            if done > total_shovel:
                excess = done - total_shovel
                shovel = max(0, shovel - excess)
      
            self.logger.info("tube: {} jobs: {} weight: {:0.1f}%, shovel: {}".format(name, jobs, 100*weight, shovel))
    
            self.move_jobs(name, target_queue, shovel) 

        self.beanstalk.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO) 
    import sys
    total_shovel = int(sys.argv[1])
    target_queue = sys.argv[2]
    queue_prefix = sys.argv[3]
    host = "localhost"
    port = 11300  
    shovel = Shovel(host, port)
    shovel.drain(total_shovel, target_queue, queue_prefix)
