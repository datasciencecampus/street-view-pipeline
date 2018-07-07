import logging
import sys
import copy
sys.path.append('../api')
from api import API
import idw


class Interpolator():

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api = API()

    def interpolate_way(self, way):
        def diff(s1, s2, tol=10**-8):
            return abs(s1['value'] - s2['value']) > tol
        x = copy.deepcopy(way) 
        idw.interpolate_road(way)
        up = [w for i, w in enumerate(way) if diff(x[i], w)]
        # <-- todo: idw.interpolate() should just return list of updated items. 
        return up

    def interpolate_city(self, city):
        self.logger.info("interpolate {}".format(city))
        ok, samples = self.api.samples(city)
        if not ok:
            self.logger.error("error fetching city samples")
        else:
            up = []
            self.logger.info("process left")
            for way in samples['left'].values():
                up.extend(self.interpolate_way(way))
            self.logger.info("process right")
            for way in samples['right'].values():
                up.extend(self.interpolate_way(way))
            self.api.update_samples(up)

    def interpolate(self):
        ok, summaries = self.api.summary()
        if not ok:
            self.logger.error("error fetching city summaries")
        else:    
            for s in summaries:
                self.interpolate_city(s['city']) 


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    interpolator = Interpolator()
    if len(sys.argv) > 1:
        city = sys.argv[1]
        interpolator.interpolate_city(city)
    else:
        interpolator.interpolate()
