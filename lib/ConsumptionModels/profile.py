import numpy as np
from scipy import stats
from datetime import datetime
from . import ThreeParameterModel
import logging

#TODO
#Make this general - it currently assumes half hourly data and a weekly grid
class ConsumptionProfile(object):
    """start_wday should be set based on 0=Monday, 1=Tuesday... 6=Sunday"""
    def __init__(self, data, res=30*60, width=48*7, start_wday=6, start_hour=0, start_min=0):
        self.width = width
        self.start_wday = start_wday
        self.start_hour = start_hour
        self.start_min = start_min
        self.data = grid(data, res, self.width, self.start_wday, self.start_hour, self.start_min)
        self.len = self.data.shape[0]
        
        #self.models = [ThreeParameterModel(self.data[:, i]) for i in range(self.width)]

    def simple_profile(self, percentiles=[10, 90, 50], lbl='consumption'):
        result = {}
        for percentile in percentiles:
            result[percentile] = stats.scoreatpercentile(self.data[lbl], percentile)
#        upper = stats.scoreatpercentile(self.data[lbl], 90)
#        median = stats.scoreatpercentile(self.data[lbl], 50)
#        lower = stats.scoreatpercentile(self.data[lbl], 10)
        time = self.data['date'][0,:]
#        return time, lower, median, upper
        return time, result

    def temp_profile(self):
        return [model.parameters() for model in self.models]

    def simple_prediction(self, lbl='consumption'):
        return stats.scoreatpercentile(self.data[lbl].transpose(), 50)

#TODO
#This is using 48 and 30 because it assumes half hourly data
#If it were possible to geenralise, here is where to start

#resolution is needed, e.g. if res = 30*60 then 
#day shift  = 24*60*60 / res = 48, 
#hour shift = 60*60 / res = 2
#minute shift = 60 / res = 1/30

def grid(data, res, width, start_wday, start_hour, start_min):
    """reshape the data so one 'row' contains a full period (e.g. 336 = a half-hourly week)"""
    logging.debug("Reshaping data to %sx%s" % (int(len(data)/width), width))
    result = np.resize(data, (int(len(data)/width), width))
    time = datetime.fromtimestamp(result[0, 0]['date']) #time of the first value
    #calculate the shift needed to roll to Monday 00:00
#    shift1 = time.weekday() * 48 + time.hour * 2 + time.minute/30
    #calculate the shift to given start day, hour and minute
#    shift2 = (start_wday * 48 + start_hour * 2 + start_min/30) * -1

    shift1 = (time.weekday() * 24*60 + time.hour * 60 + time.minute) * 60
    shift2 = ((start_wday*24*60 + start_hour*60 + start_min) * -1) * 60
    shift = (shift1 + shift2) / res

    result = np.roll(result, shift, axis=1)
    return result
    
#def date_to_index(date):
    
