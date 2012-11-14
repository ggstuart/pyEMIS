import logging
from scipy.stats import scoreatpercentile, percentileofscore
import numpy as np


class ModellingError(Exception): pass

class Base(object):
    """Base model inherited by all real models"""

    def parameters(self):
        raise NotImplementedError

    def prediction(self, independent_data):
        raise NotImplementedError

    def residuals(self, independent_data):
        p = self.prediction(independent_data)
        return independent_data['value'] - p

    def percentiles(self, percentiles):
        raise NotImplementedError


class SubModel(Base):
    """A low-level model that actually implements a fitting method - not to be used for aggregate models"""

    def __init__(self, training_data):
        self.fit(training_data)
        self.training_residuals = self.residuals(training_data)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._stats = {}

    def fit(self):
        raise NotImplementedError

    def percentile(self, percentile):
        """DEPRECATED"""
        return self.scoreatpercentile(percentile)

    def scoreatpercentile(self, percentile):
        return scoreatpercentile(self.training_residuals, percentile)

    def percentileofscore(self, independent_data):
        res = self.residuals(independent_data)
        return np.array([percentileofscore(self.training_residuals, r) for r in res])

    def calculate_goodness_of_fit(self):
        if 'done' in self._stats.keys():
            return
        res = self.training_residuals
        n = len(res)
        sse = np.sum(res ** 2)
        rmse = np.sqrt(sse / (n - 1))
        bic = n * np.log(sse) + np.log(n) * self.n_parameters
        k = self.n_parameters + 1 # because variance is also estimated (?)
        basic_aic = (n * np.log(sse / n)) +  (2 * k)
        aic_correction = (2 * k * (k + 1)) / (n - k - 1)
        aic = basic_aic + aic_correction
#        print aic

        #slated for removal
#        aic = (n * np.log(sse / n)) +  (2 * k) + (2 * (k + 1) / (n - k - 1))
#        print aic

        for key, value in zip(['n', 'sse', 'rmse', 'bic', 'aic'], [n, sse, rmse, bic, aic]):
            self._stats[key] = value
        self._stats['done'] = True

    def cv_rmse(self, mu):
        while True:
            try:
                return self._stats['rmse'] / mu
            except KeyError:
                self.calculate_goodness_of_fit()

    def stats(self, key):
        while True:
            try:
                return self._stats[key]
            except KeyError:
                self.calculate_goodness_of_fit()

#
#class gofStats(object):
#    """Calculate a few useful goodness of fit statistics"""
#
#    def __init__(self, actual, prediction, n_parameters):
#        logging.debug("Calculating stats: actual length=%s, prediction length=%s" % (len(actual), len(prediction)))
#        self.n_parameters = n_parameters
#        self.residuals = actual - prediction
#        self.n = len(self.residuals)
#        self.mu = np.mean(actual)
#        self.sse = np.sum(self.residuals**2)
#        self.rmse = np.sqrt(self.sse/(self.n-1))
#        self.cv_rmse = self.rmse/self.mu
#        k = self.n_parameters + 1
#        self.bic = self.n * np.log(self.sse) + np.log(self.n) * self.n_parameters
#        try:
#            self.aic = (self.n * np.log(self.sse/self.n)) +  (2 * k) + (2 * (k + 1) / (self.n - k - 1))
#            self.aic = (self.n * np.log(self.sse/self.n)) +  (2 * self.n_parameters) + (2 * (self.n_parameters + 1) / (self.n - self.n_parameters - 1))
#        except ZeroDivisionError, e:
#            raise ModellingError("%s data points in a %s-parameter model" % (self.n, self.n_parameters))
#
#    def aic(self): return self.aic
#    def bic(self): return self.bic
