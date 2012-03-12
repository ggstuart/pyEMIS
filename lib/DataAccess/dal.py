import logging
import time
import datetime
import numpy as np
from ..DataCleaning import Interpolator, ConsumptionCleaner, TemperatureCleaner, utils


class DALError(Exception): pass
class UnknownColumnType(DALError): pass

class DataAccessLayer(object):
    """
    Simple facade for all the complexities of data access
    >>> from pyEMIS.DataAccess import adapters, DataAccessLayer as DAL
    >>> dal = DAL(adapters.Test)
    >>> dal #doctest: +ELLIPSIS
    <pyEMIS.DataAccess.dal.DataAccessLayer object at 0x...>
    >>> dal.adapter #doctest: +ELLIPSIS
    <pyEMIS.DataAccess.adapters.test.Test object at 0x...>
    >>> 
    """
    def __init__(self, adapter):
        self.logger = logging.getLogger('DataAccessLayer')
        self.adapter = adapter()

    def column(self, col_id, sd_limit=None, resolution=None, as_timestamp=False):
        """
        Returns a 'sanitised' column of data plus a few items of meta-data
        The data are optionally cleaned and interpolated
        'integ' data are converted to 'movement'
        >>> from pyEMIS.DataAccess import adapters, DataAccessLayer as DAL
        >>> dal = DAL(adapters.Test)
        >>> daily_col = dal.column('valid', resolution=60*60*24)
        >>> len(daily_col['value'])
        364
        >>> clean_col = dal.column('valid', sd_limit=30, resolution=60*60*24)
        >>> import numpy as np
        >>> np.testing.assert_array_equal(clean_col['timestamp'], daily_col['timestamp'])
        """
        data = self.adapter.timeseries(col_id)
        if sd_limit is not None:
            if data['type'] in ['consumption', 'integ']:
                cleaner = ConsumptionCleaner()
            elif data['type'] in ['temperature', 'movement']:
                cleaner = TemperatureCleaner()
            else:
                raise UnknownColumnType, "I don't know what to do with a '{0}' data type.".format(data['type'])
            data = cleaner.clean(data, sd_limit)
        if resolution is not None:
            interpolator = Interpolator(data)
            data = interpolator.interpolate(resolution, missing=True)
        if data['type'] == 'integ':
            data['value'] = utils.movement_from_integ(data['value'])
            data['type'] = 'movement'
        return data

    def dataset(self, columns, resolution):
        self.logger.debug('constructing dataset')
        #pick up the raw data and bring it together
        raw = {}
        for c in columns:
            col = self.column(c['id'], sd_limit=c['sd_limit'], resolution=resolution, as_timestamp=True)
            raw[c['label']] = {
                'data': col,
                'min_date': min(col['timestamp']),
                'max_date': max(col['timestamp'])
            }
        #determine the range
        _from = max([raw[label]['min_date'] for label in raw.keys()])
        _to = min([raw[label]['max_date'] for label in raw.keys()])
        #construct the result
        result = {}
        for c in columns:
            label = c['label']
            a = (raw[label]['data']['timestamp'] >= _from) & (raw[label]['data']['timestamp'] <= _to)
            if not result.has_key('timestamp'):
                result['timestamp'] = raw[label]['data']['timestamp'][a]
            result[label] = raw[label]['data']['value'][a]
        #convert to output
        dt = np.dtype([(lbl, np.float) for lbl in result.keys()])
        size = len(result['timestamp'])
        result = np.array([tuple([result[lbl][i+1] for lbl in result.keys()]) for i in xrange(size-1)], dtype = dt)
        return result

    def meter(self, meter_id):
        return self.adapter.meter(meter_id)

    def meters(self):
        return self.adapter.meters()

