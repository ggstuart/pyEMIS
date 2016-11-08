import numpy as np

from .utils import timestamp_from_datetime, datetime_from_timestamp, movement_from_integ, integ_from_movement
from .unit import BaseUnit
from .preparation import cleaners, interpolators

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
        self.drivers = {}
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

    def add_driver(self, other_dataset, label, sd_limit=30):
        """
        Adds a driver dataset to this dataset
        """
        self.drivers[label] = (other_dataset, sd_limit)


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

    def data_with_drivers(self, resolution=None, sd_limit=None, start=None, length=None):

        labels = self.drivers.keys() + ['value']
        datasets = [self.drivers[driver_key][0] for driver_key in self.drivers.keys()] + [self]
        sd_limits = [self.drivers[driver_key][1] for driver_key in self.drivers.keys()] + [sd_limit]

        original_data = {}
        for label, sd_lim, dataset in zip(labels, sd_limits, datasets):
            mydata = dataset.data(sd_limit=sd_lim, resolution=resolution, start=start, length=length)
            original_data[label] = {
                'data': mydata,
                'min_date': min(mydata['timestamp']),
                'max_date': max(mydata['timestamp'])
            }

        #determine the range
        _from = max([original_data[label]['min_date'] for label in original_data.keys()])
        _to = min([original_data[label]['max_date'] for label in original_data.keys()])

        #construct the result
        result = {}
        for label in original_data.keys():
            #get indices for overlapping data
            a = (original_data[label]['data']['timestamp'] >= _from) & (original_data[label]['data']['timestamp'] <= _to)
            if not result.has_key('timestamp'):
                result['timestamp'] = original_data[label]['data']['timestamp'][a]
            result[label] = original_data[label]['data']['value'][a]
            if 'missing' in original_data[label]['data'].dtype.names:
                try:
                    missing = missing | original_data[label]['data']['missing'][a]
                except NameError:
                    missing = original_data[label]['data']['missing'][a]
        try:
            missing = missing
        except NameError:
            missing = np.zeros_like(result[result.keys()[0]])


        #convert to output
        dtype = [(str(lbl), np.float) for lbl in result.keys()] + [('missing', np.bool)]
        dt = np.dtype(dtype)
        size = len(result['timestamp'])
#        loses one value
#        result = np.ma.array([tuple([result[lbl][i+1] for lbl in result.keys()] + [missing[i+1]]) for i in xrange(size-1)], dtype = dt)
        result = np.ma.array(zip(*[result[lbl] for lbl in result.keys()] + [missing]), dtype = dt)
        return result
