import logging
import numpy as np
import pyEMIS
from pyEMIS.DataCleaning import utils


class Test():
    """
    Test data
    """
    def __init__(self):
        self.logger = logging.getLogger('sources:test')

    def basic_dates(self):
        ts = (np.arange(48*365, dtype=float) + 1) * 30 * 60
        return utils.datetime_from_timestamp(ts)

    def late_dates(self):
        ts = (np.arange(48*365, dtype=float) + 100) * 30 * 60
        return utils.datetime_from_timestamp(ts)        

    def trim_front_dates(self):
        ts = (np.arange(48*365, dtype=float) + 1) * 30 * 60
        ts = ts + (26 * pyEMIS.WEEKLY)
        ts[0] = ts[0] - (pyEMIS.WEEKLY * 2)
        return utils.datetime_from_timestamp(ts)

    def trim_front_dates2(self):
        ts = (np.arange(48*365, dtype=float) + 1) * 30 * 60
        ts = ts + (26 * pyEMIS.WEEKLY)
        ts[0] = ts[0] - (pyEMIS.WEEKLY * 4)
        ts[1] = ts[1] - (pyEMIS.WEEKLY * 2)
        return utils.datetime_from_timestamp(ts)

    def trim_end_dates(self):
        ts = (np.arange(48*365, dtype=float) + 1) * 30 * 60
        ts = ts + (26 * pyEMIS.WEEKLY)
        ts[-1] = ts[-1] + (pyEMIS.WEEKLY * 2)
        return utils.datetime_from_timestamp(ts)

    def trim_end_dates2(self):
        ts = (np.arange(48*365, dtype=float) + 1) * 30 * 60
        ts = ts + (26 * pyEMIS.WEEKLY)
        ts[-1] = ts[-1] + (pyEMIS.WEEKLY * 4)
        ts[-2] = ts[-2] + (pyEMIS.WEEKLY * 2)
        return utils.datetime_from_timestamp(ts)

    def trim_both_dates(self):
        ts = (np.arange(48*365, dtype=float) + 1) * 30 * 60
        ts = ts + (26 * pyEMIS.WEEKLY)
        ts[0] = ts[0] - (pyEMIS.WEEKLY * 2)
        ts[-1] = ts[-1] + (pyEMIS.WEEKLY * 2)
        return utils.datetime_from_timestamp(ts)

    def basic_movement(self):
        result = np.random.normal(0, 1, 48)
        result[0] = 50
        return np.tile(np.cumsum(result), 365)

    def one_to_nine(self):
        return np.arange(9, dtype=float) + 1

    def one_to_nine_dates(self):
        ts = (np.arange(9, dtype=float) + 1) * 30 * 60
        return utils.datetime_from_timestamp(ts)

    def basic_integ(self, n_steps=0, n_spikes=0):
        result = utils.integ_from_movement(self.movement(n_steps))   #integ = np.cumsum(movement)
        for i in range(n_spikes):
            result[np.random.randint(self.n)] += (self.sigma * 100 * np.random.randn())
        return result

