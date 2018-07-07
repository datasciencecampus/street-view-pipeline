from pystalkd.Beanstalkd import Connection


class Consumer():

    def __init__(self, beanstalk_host, beanstalk_port):
        self.beanstalk = Connection(host=beanstalk_host, port=beanstalk_port)


    def consume(self, max_jobs, src_queue):
        """consume from the incoming job queue."""
        # incoming jobs
        self.beanstalk.watch(src_queue)
        self.beanstalk.ignore('default')
        print("now watching", self.beanstalk.watching())

        queue_timeout = 10 if max_jobs >= 0 else None

        done = 0
        while(max_jobs <= 0 or done < max_jobs):
            job = self.beanstalk.reserve(timeout=queue_timeout)

            if job is None:
                break 
            
            try:
                res = self.process_job(job.body)
                if res is True:
                    job.delete()
                else:
                    job.bury()
            
            except Exception as e:
                print("error from process_job()", e)
                job.bury()

            finally:             
                done += 1

        self.beanstalk.close()

    
    def process_job(self, json_job):
        """default: do nothing."""
        return False
