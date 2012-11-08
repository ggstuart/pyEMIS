import logging
from numpy import argmin, array, nan
from base import ModellingError, SubModel

class AnyModelError(ModellingError): pass

class Factory(object):
    def __init__(self, models, criterion='aic'):
        self.criterion = criterion
        self.models = models
        self.logger = logging.getLogger('models.AnyFactory')

    def __call__(self, data):
        if len(data) < 1:
            raise AnyModelError("Cannot fit model without any data")

        models = []
        for m in self.models:
            try:
                models.append(m(data))
            except ModellingError, e:
                self.logger.warning("Failed to fit model [%s]" % m)
                self.logger.warning(e)
                raise
                

        if len(models) == 0:
            return NanModel(data)
        if len(models) == 1:
            return models[0]

        return models[argmin([m.stats(self.criterion) for m in models])]

class NanModel(SubModel):
    """A placeholder for a model that just spits out np.nan values as a prediction"""

    n_parameters = 0
  
    def fit(self, training_data):
        pass
        
    def prediction(self, independent_data):
        if 'values' in independent_data.dtype.names:
            return independent_data['values']
        return array([nan] * len(independent_data))
