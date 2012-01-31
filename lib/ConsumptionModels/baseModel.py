import logging
from scipy.stats import scoreatpercentile
import numpy as np
#from ..DataCleaning import utils

class ModellingError(Exception): pass

class baseModel(object):
    """Common functions required by all models"""

    n_parameters = -1
  
    def residuals(self, independent_data):
        pred = self.prediction(independent_data)
        result = independent_data['consumption'] - pred
        if 'missing' in independent_data.dtype.names:
            result[independent_data['missing']] = 0
        return result

    def gof_stats(self, independent_data):
        return gofStats(independent_data['consumption'], self.prediction(independent_data), self.n_parameters)

    def percentiles(self, independent_data, percentiles, expand=True):
        res = self.residuals(independent_data)
        result = {}
        if expand:
            for p in percentiles:
                result[str(p)] = [scoreatpercentile(res, p)] * len(res)
        else:
            for p in percentiles:
                result[str(p)] = scoreatpercentile(res, p)
        return result


class gofStats(object):
    """Calculate a few useful goodness of fit statistics"""

    def __init__(self, actual, prediction, n_parameters):
        logging.debug("Calculating stats: actual length=%s, prediction length=%s" % (len(actual), len(prediction)))
        self.n_parameters = n_parameters
        self.residuals = actual - prediction
        self.n = len(self.residuals)
        self.mu = np.mean(actual)
        self.sse = np.sum(self.residuals**2)
        self.rmse = np.sqrt(self.sse/(self.n-1))
        self.cv_rmse = self.rmse/self.mu
#        k = self.n_parameters + 1
        self.bic = self.n * np.log(self.sse) + np.log(self.n) * self.n_parameters
        try:
#            self.aic = (self.n * np.log(self.sse/self.n)) +  (2 * k) + (2 * (k + 1) / (self.n - k - 1))
            self.aic = (self.n * np.log(self.sse/self.n)) +  (2 * self.n_parameters) + (2 * (self.n_parameters + 1) / (self.n - self.n_parameters - 1))
        except ZeroDivisionError, e:
            raise ModellingError("%s data points in a %s-parameter model" % (self.n, self.n_parameters))

    def aic(self): return self.aic
    def bic(self): return self.bic
