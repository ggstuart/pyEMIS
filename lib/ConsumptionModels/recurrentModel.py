import numpy as np
from datetime import datetime
from baseModel import baseModel, ModellingError as me
from nanModel import NanModel
from ..DataCleaning import utils
import logging

class ModellingError(me): pass

class RecurrentModelFactory(object):
    def __init__(self, factory, width):
        self.width = width
        self._factory = factory

    def __call__(self, data):
        model = RecurrentModel(self._factory, self.width)
        model(data)
        return model

class RecurrentModel(baseModel):
    def __init__(self, factory, width):
        """Configure the recurrent elements of the model"""
        self.logger = logging.getLogger('pyEMIS:Models:Recurrent')
        self.width = width
        self._factory = factory

    def __call__(self, data):
        """
        Mimicking the baseModel __init__ function, i.e. fit the model
        The data are split into subsets (the number of subsets is equal to the width)
        The datetime of the first subset is recorded so it can be used to index the model array
        """
        datetimes = utils.datetime_from_timestamp(data['timestamp'])
        self._start_dt = datetimes[0]
        self._models = [self._factory(data[range(i, len(data), self.width)]) for i in range(self.width)]
#        self._models = []
#        for i in range(self.width):
#            chunk = data[range(i, len(data), self.width)]
#            try:
#                model = self._factory(chunk)
#            except me, e:
#                model = NanModel(chunk)
#            self._models.append(model)
        self.n_parameters = sum([m.n_parameters for m in self._models])

    def parameters(self):
        return [m.parameters() for m in self._models]

    def prediction(self, independent_data):
        self.logger.debug('Calculating prediction')
        start = self._find_offset(utils.datetime_from_timestamp(independent_data['timestamp']))
        result = np.zeros(independent_data.shape)
        for i in range(self.width):
            indices = range((i + start) % self.width, len(independent_data), self.width)
            result[indices] = self._models[i].prediction(independent_data[indices])
        return result

    def percentiles(self, independent_data, percentiles, expand=True):
        self.logger.debug('Calculating percentiles')
        start = self._find_offset(utils.datetime_from_timestamp(independent_data['timestamp']))
        dt = np.dtype([(str(p), np.float64) for p in percentiles])
        result = np.zeros(independent_data.shape, dtype=dt)
        for i in range(self.width):
            indices = range((i + start) % self.width, len(independent_data), self.width)
            chunk = self._models[i].percentiles(independent_data[indices], percentiles)
            for p in chunk.keys():
                result[p][indices] = chunk[p]
        return result

    def _find_offset(self, datetimes):
        for start in range(len(datetimes)):
            candidate = datetimes[start]
            if candidate.weekday() != self._start_dt.weekday(): continue            
            if candidate.hour != self._start_dt.hour: continue            
            if candidate.minute != self._start_dt.minute: continue            
            return start
