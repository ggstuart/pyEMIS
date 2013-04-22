import logging
from scipy.stats import scoreatpercentile, percentileofscore
import numpy as np


class ModellingError(Exception): pass

class Base(object):
    """Base model inherited by all real models"""

    def __init__(self, training_data):
        self.fit(training_data)
        self.training_residuals = self.residuals(training_data)
        self._stats = {'mu': np.mean(training_data['value'])}

    def parameters(self):
        raise NotImplementedError

    def prediction(self, independent_data):
        raise NotImplementedError

    def residuals(self, independent_data):
        p = self.prediction(independent_data)
        return independent_data['value'] - p

    def scoreatpercentile(self, independent_data, percentiles):
        raise NotImplementedError

    def percentileofscore(self, independent_data):
        raise NotImplementedError

    def fit(self):
        raise NotImplementedError

    def calculate_goodness_of_fit(self):
        if 'done' in self._stats.keys():
            return
        res = self.training_residuals
        n = len(res)
        sse = np.sum(res ** 2)
        rmse = np.sqrt(sse / (n - 1))
        cv_rmse = rmse/self._stats['mu']
        bic = n * np.log(sse) + np.log(n) * self.n_parameters
        k = self.n_parameters + 1 # because variance is also estimated (?)
        basic_aic = (n * np.log(sse / n)) +  (2 * k)
        aic_correction = (2 * k * (k + 1)) / (n - k - 1)
        aic = basic_aic + aic_correction

#        print aic
#        #slated for removal
#        aic = (n * np.log(sse / n)) +  (2 * k) + (2 * (k + 1) / (n - k - 1))
#        print aic

        for key, value in zip(['n', 'sse', 'rmse', 'bic', 'aic', 'cv_rmse'], [n, sse, rmse, bic, aic, cv_rmse]):
            self._stats[key] = value
        self._stats['done'] = True

#    def cv_rmse(self, mu):
#        while True:
#            try:
#                return self._stats['rmse'] / mu
#            except KeyError:
#                self.calculate_goodness_of_fit()

    def stats(self, key):
        while True:
            try:
                return self._stats[key]
            except KeyError:
                self.calculate_goodness_of_fit()

                
class SubModel(Base):
    """A low-level model with simple percentiles calculated from training residuals"""    

    def residualatpercentile(self, percentile):
        """
        return the residual value equivalent to the provided percentile
        e.g. given 50, will return the median of the training_residuals
        """
        return scoreatpercentile(self.training_residuals, percentile)


    def scoreatpercentile(self, independent_data, percentile):
        """
        return the value equivalent to the provided percentile
        e.g. given 50, will return the predicted value plus the median of the model residuals
        """
        return self.prediction(independent_data) + self.residualatpercentile(percentile)


    def percentileofscore(self, independent_data):
        """
        return the percentile equivalent to the provided values
        the data provided are used to generate a prediction and residuals
        the residuals are then compared to the training residuals to generate percentile values
        e.g. given consumption which differs from the model by precisely the median value of the training residuals, 50 will be returned
        """
        res = self.residuals(independent_data)
        return np.array([percentileofscore(self.training_residuals, r) for r in res])


class GroupedModel(Base):
    """A model that splits data into subsets and fits models separately to each subset"""

    def __init__(self, training_data, factory, grouping_function):
        """Fit the model
        The data are split into subsets by the grouping function
        A model is fitted to each subset and stored against the provided key
        """
        self._factory = factory
        self.grouping_function = grouping_function
        super(GroupedModel, self).__init__(training_data)

    def fit(self, training_data):
        """
        use the grouping function to generate a value for each datum
        fit a model to each unique value
        store the values and models as key/value pairs in a dict
        """
        _groups = self.grouping_function(training_data)
        _keys = np.unique(_groups)
        self._models = dict([(key, self._factory(training_data[_groups==key])) for key in _keys])
        self.n_parameters = sum([self._models[key].n_parameters for key in self._models.keys()])

    def prediction(self, independent_data):
        """
        The provided data are split into subsets based on the grouping function
        The model for each subset is used to generate a bit of the prediction
        """
        _groups = self.grouping_function(independent_data)
        result = np.empty(independent_data.shape) * np.nan
        for key in self._models.keys():
            indices = _groups==key
            result[indices] = self._models[key].prediction(independent_data[indices])
        return result

    def scoreatpercentile(self, independent_data, percentile):
        """
        The provided data are split into subsets based on the grouping function
        The model for each subset is used to generate a bit of the result
        """
        _groups = self.grouping_function(independent_data)
        result = np.empty(independent_data.shape) * np.nan
        for key in self._models.keys():
            indices = _groups==key
            result[indices] = self._models[key].scoreatpercentile(independent_data[indices], percentile)
        return result

    def percentileofscore(self, independent_data):
        _groups = self.grouping_function(independent_data)
        result = np.empty(independent_data.shape) * np.nan
        for key in self._models.keys():
            indices = _groups==key
            result[indices] = self._models[key].percentileofscore(independent_data[indices])
        return result
        
    def groups(self):
        return self._models.keys()
        
    def model_for_group(self, group):
        return self._models[group]

    def data_for_group(self, group, independent_data):
        _groups = self.grouping_function(independent_data)
        return independent_data[_groups==group]

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
