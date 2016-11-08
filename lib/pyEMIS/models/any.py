import logging
from numpy import argmin, array, nan

from .base import ModellingError, SubModel

class AnyModelError(ModellingError): pass

class Factory(object):
    def __init__(self, models, criterion='aic'):
        self.criterion = criterion
        self.models = models
        self.logger = logging.getLogger('pyEMIS.models.AnyFactory')

    def __call__(self, data):
        if len(data) < 1:
            raise AnyModelError("Cannot fit model without any data")

        models = []
        for m in self.models:
            try:
                models.append(m(data))
            except ModellingError as e:
                self.logger.warning("Failed to fit model [%s]" % m)
                self.logger.warning(e)
                raise
            except TypeError as e:
                self.logger.error("Problem with model type [%s]" % type(m))
                raise


        if len(models) == 0:
            return NanModel(data)
        if len(models) == 1:
            return models[0]

        selected = argmin([m.stats(self.criterion) for m in models])
        self.logger.debug('model [%s] selected' % models[selected].__class__.__name__)
        return models[selected]

class NanModel(SubModel):
    """A placeholder for a model that just spits out np.nan values as a prediction"""

    n_parameters = 0

    def fit(self, training_data):
        pass

    def prediction(self, independent_data):
        if 'values' in independent_data.dtype.names:
            return independent_data['values']
        return array([nan] * len(independent_data))
