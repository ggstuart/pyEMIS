import logging
import numpy as np
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
            'meter': {
                'id': 'basic data',
                'description': 'Test consumption data', 
                'type': 'movement', 
                'value_type': 'Consumption', 
                'units': {
                    'name': 'kiloWatt-hours',
                    'abbreviation': 'kWh'
                }
            }, 
            'ts_func': self.basic_dates, 
            'val_func': self.basic_movement
        }
    ]


    def timeseries(self, meter_id):
        for d in self.datasets:
            if d['meter']['id'] == meter_id:
                self.logger.info('Found dataset [%s]' % meter_id)
                result = d['meter']
                result['datetime'] = d['ts_func']()
                result['value'] = d['val_func']()
                return result

    def basic_dates(self, resolution=30*60):
        date = (np.arange(1000, dtype=float) + 1) * resolution
        return utils.datetime_from_timestamp(date)

    def basic_movement(self, resolution=30*60):
        result = np.random.normal(0, 1, 1000)
        result[0] = 1000
        return np.cumsum(result)

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
