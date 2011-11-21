import numpy as np
from ..DataCleaning import cleaning, interpolation, utils
import logging, time, datetime

class FactoryError(Exception): pass
class InvalidRequest(FactoryError): pass
class UnknownColumnType(InvalidRequest): pass

class DataFactory(object):
    """object for generating datasets of the appropriate ndarray type for consumption data"""
    def __init__(self, src):
        self.dtype = np.dtype([('date', np.float), ('consumption', np.float), ('temperature', np.float)])
        self.src = src()

    def column(self, col_id, col_type, sd_limit=None, resolution=None, as_timestamp=False):
        if col_type == 'integ':
            return self.integ_column(col_id, sd_limit=sd_limit, resolution=resolution, as_timestamp=as_timestamp)
        elif col_type == 'movement':
            return self.movement_column(col_id, sd_limit=sd_limit, resolution=resolution, as_timestamp=as_timestamp)
        else:
            raise UnknownColumnType, "col_type argument must be either 'integ' or 'movement'. [%s] was passed." % col_type

    def integ_column(self, col_id, sd_limit=None, resolution=None, as_timestamp=False):
        dt, integ = self.src.timeseries(col_id)
        movement = utils.movement_from_integ(integ)
        ts = utils.timestamp_from_datetime(dt)
        if sd_limit != None:
            dt, integ, movement = cleaning.clean(dt, integ, movement, sd_limit)
        if resolution !=None:
            date, integ = interpolation.interpolate2(date, integ, resolution)
            movement = utils.movement_from_integ(integ)
        if not as_timestamp: date = utils.datetime_from_timestamp(date)
        return date, integ

    def movement_column(self, col_id, sd_limit=None, resolution=None, as_timestamp=False):
        dt, movement = self.src.timeseries(col_id)
        integ = utils.integ_from_movement(movement)
        ts = utils.timestamp_from_datetime(dt)
        if sd_limit != None:
            dt, integ, movement = cleaning.clean(dt, integ, movement, sd_limit)
        if resolution !=None:
            date, movement = interpolation.interpolate2(date, movement, resolution)
            integ = utils.integ_from_movement(movement)
        if not as_timestamp: date = utils.datetime_from_timestamp(date)
        return date, movement
        
    def temperature(self, meter_id, sd_limit=None, resolution=None, as_timestamp=False, missing=False, limit=None):
        logging.warning('Using deprecated interface')
        date, integ, movement = self.src.temperature(meter_id)
        date = utils.timestamp_from_datetime(date)
        if sd_limit != None:
            logging.debug('Cleaning [%s]' % meter_id)
            date, integ, movement = cleaning.clean_temp(date, integ, movement, sd_limit)
        if resolution !=None:
            logging.debug('Interpolating [%s]' % meter_id)
            date, movement = interpolation.interpolate2(date, movement, resolution, missing=missing, limit=limit)
            integ = utils.integ_from_movement(movement)
        if not as_timestamp: date = utils.datetime_from_timestamp(date)
        return date, integ, movement

    def consumption(self, meter_id, sd_limit=None, resolution=None, as_timestamp=False, missing=False):
        logging.warning('Using deprecated interface')
        logging.debug('Loading consumption data %s' % meter_id)
        date, integ, movement = self.src.consumption(meter_id)
        date = utils.timestamp_from_datetime(date)
        if sd_limit != None:
            logging.debug('Cleaning [%s]' % meter_id)
            date, integ, movement = cleaning.clean(date, integ, movement, sd_limit)
        if resolution !=None:
            logging.debug('Interpolating [%s]' % meter_id)
            date, integ = interpolation.interpolate2(date, integ, resolution)
            movement = utils.movement_from_integ(integ)
        if not as_timestamp: date = utils.datetime_from_timestamp(date)
        return date, integ, movement

    def dataset(self, cons_id, temp_id, sd_limit=30, temp_sd_limit=6, resolution=60*60*24):
        logging.warning('Using deprecated interface for generating dataset')
        temp_date, temp_integ, temp_movement = self.temperature(temp_id, temp_sd_limit, resolution, as_timestamp=True)
        date, integ, movement = self.consumption(cons_id, sd_limit, resolution, as_timestamp=True)
        _from = max(min(date), min(temp_date))
        _to = min(max(date), max(temp_date))
        cons_a = (date >= _from) & (date <= _to)
        temp_a = (temp_date >= _from) & (temp_date <= _to)
        date = date[cons_a]
        integ = integ[cons_a]
        temp_date = temp_date[temp_a]
        temp_movement = temp_movement[temp_a]    
        cons = utils.movement_from_integ(integ)
        temp = temp_movement
        size = len(cons)
        result = np.array([(date[i+1], cons[i+1], temp[i+1]) for i in range(size-1)], dtype = self.dtype)
        return result
    
  #{'id': 1, 'label': 'consumption', 'sd_limit': None, 'type': ['integ'|'movement']}
    def dataset2(self, columns, resolution, missing=False):
        logging.debug('constructing dataset')

        #pick up the raw data
        data = {}
        for col in columns:
            row = {'column': col}
            if col['type'] == 'movement': 
                row['date'], row['integ'], row['movement'] = self.temperature(col['id'], col['sd_limit'], resolution, as_timestamp=True, missing=missing)
            elif col['type'] == 'integ': 
                row['date'], row['integ'], row['movement'] = self.consumption(col['id'], col['sd_limit'], resolution, as_timestamp=True, missing=missing)
            row['min_date'], row['max_date'] = min(row['date']), max(row['date'])
            data[col['label']] = row

        #determine the range
        _from = max([data[label]['min_date'] for label in data.keys()])
        _to = min([data[label]['max_date'] for label in data.keys()])

        #construct the result
        result = {}
        for col in columns:
            label = col['label']
            a = (data[label]['date'] >= _from) & (data[label]['date'] <= _to)
            if not result.has_key('date'): result['date'] = data[label]['date'][a]
            if col['type'] == 'movement': result[label] = data[label]['movement'][a]
            elif col['type'] == 'integ': result[label] = utils.movement_from_integ(data[label]['integ'][a])

        #convert to output
        dt = np.dtype([(lbl, np.float) for lbl in result.keys()])
        size = len(result['date'])
        result = np.array([tuple([result[lbl][i+1] for lbl in result.keys()]) for i in xrange(size-1)], dtype = dt)
        return result

    def dataset3(self, columns, resolution):
        logging.debug('constructing dataset')

        #pick up the raw data
        data = {}
        for c in columns:
            row = {'column': c}
            row['date'], row['value'] = self.column(c['id'], c['type'], sd_limit=c['sd_limit'], resolution=c['resolution'], as_timestamp=True)
            row['min_date'], row['max_date'] = min(row['date']), max(row['date'])
            data[c['label']] = row

        #determine the range
        _from = max([data[label]['min_date'] for label in data.keys()])
        _to = min([data[label]['max_date'] for label in data.keys()])

        #construct the result
        result = {}
        for c in columns:
            label = c['label']
            a = (data[label]['date'] >= _from) & (data[label]['date'] <= _to)
            if not result.has_key('date'): result['date'] = data[label]['date'][a]
            value = data[label]['value'][a]
            if c['type'] == 'integ': value = utils.movement_from_integ(value)
            result[label] = value

        #convert to output
        dt = np.dtype([(lbl, np.float) for lbl in result.keys()])
        size = len(result['date'])
        result = np.array([tuple([result[lbl][i+1] for lbl in result.keys()]) for i in xrange(size-1)], dtype = dt)
        return result


    def locations(self):
        return self.src.locations()

    def metersForLocation(self, id):
        return self.src.metersForLocation(id)

    def meters(self):
        return self.src.meters()
        
    def meter(self, meter_id):
        return self.src.meter(meter_id)

if __name__ == "__main__":
    from DynamatPlus.dplusAdapter import DynamatPlus
    df = DataFactory(DynamatPlus)
    cons = {'id': 213, 'label': 'consumption', 'type': 'integ', 'sd_limit': 30}
    temp = {'id': 840, 'label': 'temperature', 'type': 'movement', 'sd_limit': 6}
    columns = [cons, temp]
    resolution=60*60*24

    d1 = df.dataset(213, 840, resolution=resolution)
    d2 = df.dataset2([columns], resolution=resolution)

    print d1-d2
    
