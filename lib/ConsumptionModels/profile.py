import numpy as np
from scipy import stats
from datetime import datetime
from . import ThreeParameterModel

#TODO
#Make this general - it currently assumes half hourly data and a weekly grid
class ConsumptionProfile(object):
    """start_wday should be set based on 0=Monday, 1=Tuesday... 6=Sunday"""
    def __init__(self, data, width=48*7, start_wday=6, start_hour=0, start_min=0):
        self.width = width
        self.start_wday = start_wday
        self.start_hour = start_hour
        self.start_min = start_min
        self.data = grid(data, self.width, self.start_wday, self.start_hour, self.start_min)
        self.len = self.data.shape[0]
        
        #self.models = [ThreeParameterModel(self.data[:, i]) for i in range(self.width)]

    def simple_profile(self, lbl='consumption'):
        upper = stats.scoreatpercentile(self.data[lbl], 90)
        median = stats.scoreatpercentile(self.data[lbl], 50)
        lower = stats.scoreatpercentile(self.data[lbl], 10)
        time = self.data['date']
        return lower, median, upper

    def temp_profile(self):
        return [model.parameters() for model in self.models]

    def simple_prediction(self, lbl='consumption'):
        return stats.scoreatpercentile(self.data[lbl].transpose(), 50)

        
def grid(data, width, start_wday, start_hour, start_min):
    """reshape the data so one 'row' contains a full period (i.e. a week)"""
    result = np.resize(data, (int(len(data)/width), width))
    time = datetime.fromtimestamp(result[0, 0]['date']) #time of the first value
    #calculate the shift needed to roll to Monday 00:00
    shift1 = time.weekday() * 48 + time.hour * 2 + time.minute/30
    shift2 = (start_wday * 48 + start_hour * 2 + start_min/30) * -1
    shift = shift1 + shift2
    result = np.roll(result, shift, axis=1)
    return result
    
    
#def date_to_index(date):
    