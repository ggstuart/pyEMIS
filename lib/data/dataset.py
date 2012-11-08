import numpy as np
import math

from utils import timestamp_from_datetime, datetime_from_timestamp, movement_from_integ, integ_from_movement
from unit import BaseUnit
from preparation import cleaners, interpolators

doesnt_need_integ = ['temperature']

class Dataset(object):
    """Core Dataset class stores timeseries as numpy array and holds meta-data"""
    def __init__(self, datetimes, values, datasource, unit=None):
        """
        takes datetimes and values with unit
        converts datetimes into a numpy array with timestamps
        converts values into base_units and stores base_units
        """
        assert(len(datetimes) == len(values))
        self.datasource = datasource
        self.datasource.dataset = self
        dtype = np.dtype([('timestamp', np.float), ('value', np.float)])
        data = np.zeros(len(datetimes), dtype=dtype)
        data['timestamp'] = timestamp_from_datetime(datetimes)
        data['value'] = values

        #convert to specified unit or to the source data base unit
        if unit:
            self.unit = unit
        else:
            self.unit = self.datasource.unit.base_unit

        data['value'] = self.datasource.unit.to_unit(data['value'], self.unit)

        self._processed = {}
        self._processed[(None, None)] = data

    def data(self, sd_limit=None, resolution=None, start=None, length=None):
        """Provide access to data, optionally cleaned, optionally interpolated, optionally converted to another unit"""
            
        while True:
            try:
                data = self._processed[(sd_limit, resolution)]
                break
            except KeyError:
                try:
                    clean = self._processed[(sd_limit, None)]
                    interpolator = interpolators.Interpolator()
                    #TODO: the cleaning logic should be in the cleaners module - pass in the datasource?
                    do_integ = self.datasource.commodity not in doesnt_need_integ
                    self._processed[(sd_limit, resolution)] = interpolator.interpolate(clean, resolution, do_integ)
                except KeyError:
                    cleaner = cleaners.cleaner(self.datasource.commodity)
                    self._processed[(sd_limit, None)] = cleaner.clean(self._processed[(None, None)], sd_limit)

        if not start:
            ts_start = min(data['timestamp'])
            start = datetime_from_timestamp(ts_start)
        else:
            ts_start = timestamp_from_datetime(start)

        if not length:
            ts_end = max(data['timestamp']) + 0.01
        else:
            end = start + length
            ts_end = timestamp_from_datetime(end)

        indices = np.where((data['timestamp'] < ts_end) & (data['timestamp'] >= ts_start))
        return data[indices]
