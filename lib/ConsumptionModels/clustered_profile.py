import numpy as np
from scipy import stats
from datetime import datetime
from baseModel import baseModel
from ..DataCleaning import utils
import logging

#TODO
#Make this general - it currently assumes half hourly data and a weekly grid
class ClusteredProfile(baseModel):
    """start_wday should be set based on 0=Monday, 1=Tuesday... 6=Sunday"""
    def __init__(self, data, res=30*60, width=48*7, start_wday=None, start_hour=None, start_min=None):
        self.logger = logging.getLogger('pyEMIS.Models.ClusteredProfile')
        self.width = width
        self.res = res
        default_start_datetime = utils.datetime_from_timestamp([data[0]['date']])[0]
        if start_wday == None:
            self.start_wday = default_start_datetime.isoweekday()
        else:
            self.start_wday = start_wday
        if start_hour == None:
            self.start_hour = default_start_datetime.hour
        else:
            self.start_hour = start_hour
        if start_min == None:
            self.start_min = default_start_datetime.minute
        else:
            self.start_min = start_min
        self.data = grid(data, self.res, self.width, self.start_wday, self.start_hour, self.start_min)
        self.len = self.data.shape[0]

    def simple_profile(self, percentiles=[10, 90, 50], lbl='consumption'):
        result = {}
        for percentile in percentiles:
            result[percentile] = stats.scoreatpercentile(self.data[lbl], percentile)
        time = utils.datetime_from_timestamp(self.data['date'][0,:])
        return time, result

    def calculate_models(self, Model):
        all_models = [Model(self.data[:, i]) for i in range(self.width)]
        
        self.n_parameters = sum([m.n_parameters for m in self.models])

    def model_parameters(self):
        return [m.parameters() for m in self.models]

    def prediction(self, independent_data):
        pred, data = self.prediction2(independent_data)
        return pred
        
    def prediction2(self, independent_data):
        self.logger.debug('Calculating prediction')
        self.logger.debug('input data shape: %s' % ' x '.join([str(s) for s in independent_data.shape]))
        independent_data = grid(independent_data, self.res, self.width, self.start_wday, self.start_hour, self.start_min)
        self.logger.debug('Reshaped to %sx%s' % (independent_data.shape))
        pred = np.zeros(independent_data.shape)
        self.logger.debug('Result initialised to zeros %sx%s' % (pred.shape))
        for i in range(self.width):
            pred[:, i] = self.models[i].prediction(independent_data[:, i])
        pred = np.reshape(pred, (-1, 1))
        independent_data = np.reshape(independent_data, (-1, 1))
        self.logger.debug('Result reshaped to %sx%s' % (pred.shape))
        return pred, independent_data
    
    def simple_prediction(self, lbl='consumption'):
        return stats.scoreatpercentile(self.data[lbl].transpose(), 50)

#resolution is needed, e.g. if res = 30*60 then 
#day shift  = 24*60*60 / res = 48, 
#hour shift = 60*60 / res = 2
#minute shift = 60 / res = 1/30
def grid(data, res, width, start_wday, start_hour, start_min):
    logger = logging.getLogger('pyEMIS.Models.Profile.grid')
    """reshape the data so one 'row' contains a full period (e.g. 336 = a half-hourly week)"""
    time = datetime.fromtimestamp(data[0]['date']) #time of the first value
    logger.debug("Data start at %s" % time.strftime("%a (%w) %H:%M"))
    goal = "%i %02i:%02i" % (start_wday, start_hour, start_min)
    logger.debug("Data need to start at %s" % goal)
    while True:
        candidate = datetime.fromtimestamp(data[0]['date']).strftime("%w %H:%M")
        logger.debug("Checking %s" % datetime.fromtimestamp(data[0]['date']).strftime("%a (%w) %H:%M"))
        if (candidate == goal):
            logger.debug('Match found!')
            break
        data = data[1:]
    logger.debug("Reshaping data to %sx%s" % (int(len(data)/width), width))
    result = np.resize(data, (int(len(data)/width), width))
    return result
