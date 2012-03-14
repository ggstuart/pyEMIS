import logging
import numpy as np
import pyEMIS
from pyEMIS.DataCleaning import utils


class Test():
    """
    Test data
    """
    class MeterNotFoundError(Exception): pass

    def __init__(self):
        self.logger = logging.getLogger('adapters:test')
        self.datasets = [
        {
            'meter': {'id': 'valid', 'description': 'Test consumption data'}, 
            'ts_func': self.basic_dates, 
            'val_func': self.basic_movement
        },
        {
            'meter': {'id': 'trim_front', 'description': 'Data with a spurious first timestamp'}, 
            'ts_func': self.trim_front_dates, 
            'val_func': self.basic_movement
        },
        {
            'meter': {'id': 'trim_end', 'description': 'Data with a spurious last timestamp'}, 
            'ts_func': self.trim_end_dates, 
            'val_func': self.basic_movement
        },
        {
            'meter': {'id': 'trim_front2', 'description': 'Data with two spurious timestamps at the beginning'}, 
            'ts_func': self.trim_front_dates2,
            'val_func': self.basic_movement
        },
        {
            'meter': {'id': 'trim_end2', 'description': 'Data with two spurious timestamps at the end'}, 
            'ts_func': self.trim_end_dates2,
            'val_func': self.basic_movement
        },
        {
            'meter': {'id': 'trim_both', 'description': 'Data with a spurious first and last timestamp'}, 
            'ts_func': self.trim_both_dates, 
            'val_func': self.basic_movement
        },
        {
            'meter': {'id': '123456789', 'description': 'Integers from one to nine'}, 
            'ts_func': self.one_to_nine_dates, 
            'val_func': self.one_to_nine
        },
    ]

    def timeseries(self, meter_id):
        """
        >>> from pyEMIS.DataAccess import sources
        >>> test = sources.Test()
        >>> valid = test.timeseries('valid')
        >>> valid['commodity']
        'consumption'
        >>> valid['integ']
        False
        >>> valid['units']['name']
        'kiloWatt-hours'
        >>> valid['units']['abbreviation']
        'kWh'
        """
        self.logger.debug("Getting test dataset '%s'" % meter_id)
        for d in self.datasets:
            if d['meter']['id'] == meter_id:
                result = d['meter']
                result['integ'] = False
                result['commodity'] = 'consumption'
                result['units'] = {'name': 'kiloWatt-hours', 'abbreviation': 'kWh'}
                result['datetime'] = d['ts_func']()
                result['value'] = d['val_func']()
                result['timestamp'] = utils.timestamp_from_datetime(result['datetime'])
                return result
        raise MeterNotFoundError, 'Unknown meter [%s]' % meter_id

    def basic_dates(self):
        ts = (np.arange(48*365, dtype=float) + 1) * 30 * 60
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

    def meters(self):
        return [d['meter'] for d in self.datasets]

    def meter(self, meter_id):
        for m in self.meters():
            if m['id'] == meter_id:
                return m
        raise MeterNotFoundError, 'Unknown meter [%s]' % meter_id
