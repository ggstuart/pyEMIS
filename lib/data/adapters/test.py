import logging
import calendar, numpy as np
from ..sources import Test as Source
from ...DataCleaning import utils



class Test(object):

    class MeterNotFoundError(Exception): pass

    """Provides datasets for testing purposes"""
    def __init__(self):
        self.logger = logging.getLogger('adapters:test')
        self.source = Source()
        self.datasets = [
        {
            'meter': {'id': 'valid', 'name': 'Test consumption data'}, 
            'ts_func': self.source.basic_dates, 
            'val_func': self.source.basic_movement
        },
        {
            'meter': {'id': 'trim_front', 'name': 'Data with a spurious first timestamp'}, 
            'ts_func': self.source.trim_front_dates, 
            'val_func': self.source.basic_movement
        },
        {
            'meter': {'id': 'trim_end', 'name': 'Data with a spurious last timestamp'}, 
            'ts_func': self.source.trim_end_dates, 
            'val_func': self.source.basic_movement
        },
        {
            'meter': {'id': 'trim_front2', 'name': 'Data with two spurious timestamps at the beginning'}, 
            'ts_func': self.source.trim_front_dates2,
            'val_func': self.source.basic_movement
        },
        {
            'meter': {'id': 'trim_end2', 'name': 'Data with two spurious timestamps at the end'}, 
            'ts_func': self.source.trim_end_dates2,
            'val_func': self.source.basic_movement
        },
        {
            'meter': {'id': 'trim_both', 'name': 'Data with a spurious first and last timestamp'}, 
            'ts_func': self.source.trim_both_dates, 
            'val_func': self.source.basic_movement
        },
        {
            'meter': {'id': '123456789', 'name': 'Integers from one to nine'}, 
            'ts_func': self.source.one_to_nine_dates, 
            'val_func': self.source.one_to_nine
        },
        {
            'meter': {'id': 'temperature', 'name': 'simple temperature data'}, 
            'ts_func': self.source.late_dates, 
            'val_func': self.source.basic_movement
        },
    ]

    def timeseries(self, meter_id):
        """
        >>> from pyEMIS.DataAccess.adapters import Test
        >>> test = Test()
        >>> valid = test.timeseries('valid')
        >>> valid['commodity']
        'consumption'
        >>> valid['integ']
        False
        >>> valid['units']['name']
        'kiloWatt-hours'
        >>> valid['units']['abbreviation']
        'kWh'
        >>> should_error = test.timeseries('unknown')
        Traceback (most recent call last):
        MeterNotFoundError: Unknown meter [unknown]
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
        raise self.MeterNotFoundError, 'Unknown meter [%s]' % meter_id

    def meters(self):
        return [d['meter'] for d in self.datasets]

    def meter(self, meter_id):
        for m in self.meters():
            if m['id'] == meter_id:
                return m
        raise MeterNotFoundError, 'Unknown meter [%s]' % meter_id
