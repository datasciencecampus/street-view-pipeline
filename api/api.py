# http api client wrapper
import logging
import requests


class API():

    def __init__(self):
        """persistent http connection."""
        self.logger = logging.getLogger(__name__)
        self.s = requests.Session()
        
    def jobs(self, city, sample_order):
        """get jobs for this sample order from api."""
        if sample_order is not None:
            url = 'http://localhost:5000/api/jobs/{:s}/{:d}'.format(city, int(sample_order))
        else:
            url = 'http://localhost:5000/api/jobs/{:s}'.format(city)
        res = self.s.get(url)
        if res and res.status_code == 200:
            return True, res.json() 
        else:
            self.logger.error(res.status_code)
            return False, None

    def all_jobs(self, limit=25000):
        """get next batch of jobs prioritised by sampling order and evenly 
        distributed among cities.
        """
        url = 'http://localhost:5000/api/all_jobs/{:d}'.format(limit)
        res = self.s.get(url)
        if res and res.status_code == 200:
            return True, res.json()
        else:
            self.logger.error(res.status_code)
            return False, None 

    def sample(self, sample_id, value):
        """add a new sample."""
        url = 'http://localhost:5000/api/sample/{:d}'.format(int(sample_id))
        payload = {'value': value}
        res = self.s.post(url, data=payload)
        if res and res.status_code == 200 and res.text == "ok":
            return True
        else:
            self.logger.error(res.status_code)
            return False

    def samples(self, city):
        """get all non-predicted samples for a city."""
        url = 'http://localhost:5000/api/samples/{:s}'.format(city)
        self.logger.info("request: {}".format(url))
        res = self.s.get(url)
        if res and res.status_code == 200:
            self.logger.info("got samples.")
            return True, res.json()
        else:
            self.logger.error(res.status_code)
            return False, None
    
    def update_samples(self, samples):
        """update samples with new interpolated values."""
        if len(samples) == 0:
            return
        url = 'http://localhost:5000/api/interpolate'
        res = self.s.post(url, json=samples)
        if res and res.status_code == 200 and res.text == "ok":
            self.logger.info("updated {:d} samples".format(len(samples)))
            return True
        else:
            self.logger.error(res.status_code)
            return False
        
    def summary(self):
        """get sample summary stats."""
        url = 'http://localhost:5000/api/summary'
        res = self.s.get(url)
        if res and res.status_code == 200:
            return True, res.json()
        else:
            self.logger.error(res.status_code)
            return False, None

    def export(self, city):
        """get samples as geogson for a city."""
        url = 'http://localhost:5000/api/geojson/{}'.format(city)
        res = self.s.get(url)
        if res and res.status_code == 200:
            return True, res.json()
        else:
            self.logger.error(res.status_code)
            return False, None


if __name__ == '__main__':
    import json
    import sys
    logging.basicConfig(level=logging.INFO)
    api = API()
    #_, j = api.export(sys.argv[1])
    _, j = api.all_jobs(int(sys.argv[1]))
    print(json.dumps(j, indent=2))
