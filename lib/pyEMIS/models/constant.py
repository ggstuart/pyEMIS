import numpy as np

from .base import SubModel, ModellingError

class ConstantModelError(ModellingError): pass

class Factory(object):

    def __call__(self, data):
        return Constant(data)

class Constant(SubModel):
    """
    A constant consumption model: consumption is estimated as the average of all input data
    Input_data must have a column named 'value' which is assumed to be consumption data
    """
    n_parameters = 1

    def fit(self, training_data):
        val = training_data['value'] #we're only working with the value column here
        masked = np.ma.masked_array(val, np.isnan(val))
        if len(masked.compressed()) <= 0:
            raise ConstantModelError("No input data %s" % masked)
        elif len(masked.compressed()) <= 2:
            raise ConstantModelError("Not enough input data %s" % masked)
        self.mean = np.ma.mean(masked)
        self.std = np.ma.std(masked)

    def prediction(self, independent_data):
        return np.array([self.mean] * len(independent_data))

    def parameters(self):
        return {'mean': self.mean, 'std': self.std}
