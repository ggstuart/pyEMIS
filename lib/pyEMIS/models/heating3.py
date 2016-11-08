import numpy as np
import logging

from .base import SubModel, ModellingError

logger = logging.getLogger('3PH model')

class Factory(object):

    def __init__(self, temp_key='temperature'):
        self.temp_key = temp_key

    def __call__(self, data):
        return Heating3(data, self.temp_key)

class Heating3(SubModel):
    """
    A three parameter heating model:
    consumption is estimated as a piece-wise linear regression
    between consumption and outside air emperature below a change-point
    training_data must have the following columns
    'value' is assumed to be consumption data
    'temperature' is assumed to be temperature data
    """

    n_parameters = 3

    def __init__(self, training_data, temp_key):
        self.temp_key = temp_key
        super(Heating3, self).__init__(training_data)


    def fit(self, training_data):

        val = training_data['value']
        temp = training_data[self.temp_key]
        masked_val = np.ma.masked_array(val, np.isnan(val))
        masked_temp = np.ma.masked_array(temp, np.isnan(temp))

        if len(masked_val.compressed()) <= 1:
            raise ModellingError("Not enough consumption data %s" % masked_val)

        if len(masked_temp.compressed()) <= 1:
            raise ModellingError("Not enough temperature data %s" % masked_temp)

        def _grid_search(min_temp, max_temp, steps):

            def _fit(change_point):
                x = np.ma.vstack([change_point - masked_temp, np.zeros(len(masked_temp))])
                x = np.ma.amax(x, axis=0)
                y = masked_val
                A = np.vstack([x, np.ones(len(x))]).T
                etc = np.linalg.lstsq(A, y)
                return change_point, etc[0][0], etc[0][1]

            def _rmse(prediction):
                diff = masked_val - prediction
                diff_squared = diff**2
                return np.ma.sqrt(np.ma.mean(diff_squared))

            temp_range = max_temp - min_temp
            temp_step = temp_range / (steps - 1)
            best_temp = np.float64(15.5)
            self.cp, self.m, self.c = _fit(best_temp)
            pred = self.prediction(training_data)
            best_rmse = _rmse(pred)
            logger.debug("\nStarting base temperature: %6.4f -> %6.4f" % (best_temp, best_rmse))
            for step in range(steps):
                test_temp = min_temp + step * temp_step
                self.cp, self.m, self.c = _fit(test_temp)
                test_rmse = _rmse(self.prediction(training_data))
                if test_rmse < best_rmse:
                    logger.debug("New base temperature %6.4f -> %6.4f" % (test_temp, test_rmse))
                    best_rmse = test_rmse
                    best_temp = test_temp

            self.cp, self.m, self.c = _fit(best_temp)
            return best_temp - temp_step, best_temp + temp_step

        min_temp, max_temp = np.ma.min(masked_temp), np.ma.max(masked_temp)
        min_temp, max_temp = _grid_search(min_temp, max_temp, 20)
        min_temp, max_temp = _grid_search(min_temp, max_temp, 20)


    def prediction(self, independent_data):
        temp = independent_data[self.temp_key]
        masked_temp = np.ma.masked_array(temp, np.isnan(temp))
        dd = np.ma.vstack([self.cp - masked_temp, np.zeros(len(masked_temp))])
        dd = np.ma.amax(dd, axis=0)
        return dd * self.m + self.c
