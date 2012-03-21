import numpy as np
from datetime import datetime, timedelta
from baseModel import baseModel, ModellingError as me
from nanModel import NanModel
from ..DataCleaning import utils
import logging

class ModellingError(me): pass

class WeeklyModelFactory(object):
    def __init__(self, factory, resolution, format="%a %H:%M"):
        if timedelta(weeks=1).total_seconds() % resolution.total_seconds() != 0:
            raise ModellingError, "Invalid resolution (%s) for weekly model" % resolution
        self.format = format
        self.resolution = resolution
        self.factory = factory

    def __call__(self, data):
        model = WeeklyModel(self.factory, self.resolution, self.format)
        model(data)
        return model

class WeeklyModel(baseModel):
    def __init__(self, factory, resolution, format):
        """Configure the weekly elements of the model
        """
        self.logger = logging.getLogger('pyEMIS:Models:Weekly')
        self.resolution = resolution
        self.width = int(timedelta(weeks=1).total_seconds()/self.resolution.total_seconds())
        self.logger.debug("Width=%i" % self.width)
        self._format = format
        self._factory = factory

    def __call__(self, data):
        """
        Mimicking the baseModel __init__ function, i.e. fit the model
        The data are split into subsets (the number of subsets is dependent on the resolution)
        """
        datetimes = utils.datetime_from_timestamp(data['timestamp'])                                            #datetimes for each record
        _keys = np.array([(datetimes[0] + self.resolution * i).strftime(self._format) for i in xrange(self.width)])  #A list of unique keys for the model
        formats = np.array([dt.strftime(self._format) for dt in datetimes])                                      #Keys mapped to the datetimes
        self._models = dict([(key, self._factory(data[formats==key])) for key in _keys])                        #dictionary of models with formats as keys
        self.n_parameters = sum([self._models[key].n_parameters for key in self._models.keys()])                #add up all the parameters

    def parameters(self):
        return [self._models[key].parameters() for key in self._models.keys()]

    def prediction(self, independent_data):
        self.logger.debug('Calculating prediction')
        datetimes = utils.datetime_from_timestamp(independent_data['timestamp'])
        formats = np.array([dt.strftime(self._format) for dt in datetimes])
        result = np.zeros(independent_data.shape)
        for key in self._models.keys():
            indices = formats==key
            result[indices] = self._models[key].prediction(independent_data[indices])
        return result

    def percentiles(self, independent_data, percentiles, expand=True):
        self.logger.debug('Calculating percentiles')
        result = np.zeros(independent_data.shape, dtype=np.dtype([(str(p), np.float64) for p in percentiles]))
        datetimes = utils.datetime_from_timestamp(independent_data['timestamp'])
        formats = np.array([dt.strftime(self._format) for dt in datetimes])
        for key in self._models.keys():
            indices = formats==key
            chunk = self._models[key].percentiles(independent_data[indices], percentiles)
            for p in chunk.keys():
                result[p][indices] = chunk[p]
        return result
