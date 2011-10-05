import numpy as np
from ..DataCleaning import cleaning, interpolation, utils
import logging, time, datetime

class DataFactory(object):
  """object for generating datasets of the appropriate ndarray type for consumption data"""
  def __init__(self, src):
    self.dtype = np.dtype([('date', np.float), ('consumption', np.float), ('temperature', np.float)])
    self.src = src()

  def temperature(self, meter_id, sd_limit=None, resolution=None, as_timestamp=False):
    try:
      date, integ, movement = self.temp_date, self.temp_integ, self.temp_movement
      logging.debug('Loaded stored temperature data [%s]' % meter_id)
    except AttributeError, e:
      logging.debug('Loading temperature data [%s]' % meter_id)
      self.temp_date, self.temp_integ, self.temp_movement = self.src.temperature(meter_id)
      date, integ, movement = self.temp_date, self.temp_integ, self.temp_movement
    date = utils.timestamp_from_datetime(date)
    if sd_limit != None:
        logging.info('Cleaning [%s]' % meter_id)
        date, integ, movement = cleaning.clean_temp(date, integ, movement, sd_limit)
    if resolution !=None:
        logging.info('Interpolating [%s]' % meter_id)
        date, integ, movement = interpolation.interpolate(date, integ, movement, resolution)
    if not as_timestamp: date = utils.datetime_from_timestamp(date)
    return date, integ, movement

  def consumption(self, meter_id, sd_limit=None, resolution=None, as_timestamp=False):
    logging.debug('Loading consumption data %s' % meter_id)
    date, integ, movement = self.src.consumption(meter_id)
    date = utils.timestamp_from_datetime(date)
    if sd_limit != None:
        logging.info('Cleaning [%s]' % meter_id)
        date, integ, movement = cleaning.clean(date, integ, movement, sd_limit)
    if resolution !=None:
        logging.info('Interpolating [%s]' % meter_id)
        date, integ, movement = interpolation.interpolate(date, integ, movement, resolution)
    if not as_timestamp: date = utils.datetime_from_timestamp(date)
    return date, integ, movement

  #TODO Make this generic so I can ask for any number of columns and just give the appropriate dataset id's
  def dataset(self, cons_id, temp_id, sd_limit=30, temp_sd_limit=6, resolution=60*60*24):
    logging.debug('constructing dataset')
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
  def dataset2(self, columns, resolution):
    logging.debug('constructing dataset')

    #pic up the raw data
    data = {}
    for col in columns:
        row = {'column': col}
        if col['type'] == 'movement': row['date'], row['integ'], row['movement'] = self.temperature(col['id'], col['sd_limit'], resolution, as_timestamp=True)
        elif col['type'] == 'integ': row['date'], row['integ'], row['movement'] = self.consumption(col['id'], col['sd_limit'], resolution, as_timestamp=True)
        row['min_date'], row['max_date'] = min(row['date']), max(row['date'])
        data[col['label']] = row

    #determine the range
    _from = max([data[label]['min_date'] for label in data.keys()])
    _to = min([data[label]['max_date'] for label in data.keys()])

    #construct the result
    result = {}
    for col in columns:
        label = col['label']
#        result[label] = {}
        a = (data[label]['date'] >= _from) & (data[label]['date'] <= _to)
        if not result.has_key('date'): result['date'] = data[label]['date'][a]
        if col['type'] == 'movement': result[label] = data[label]['movement'][a]
        elif col['type'] == 'integ': result[label] = utils.movement_from_integ(data[label]['integ'][a])

    #convert to output
    dt = np.dtype([(lbl, np.float) for lbl in result.keys()])
    size = len(result['date'])
    result = np.array([tuple([result[lbl][i+1] for lbl in result.keys()]) for i in xrange(size-1)], dtype = dt)
#    result = np.array([(date[i+1], cons[i+1], temp[i+1]) for i in range(size-1)], dtype = self.dtype)
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
  from classic import Classic
  df = DataFactory(Classic)
  d1 = df.dataset(1)
  d2 = df.dataset(2)
  
