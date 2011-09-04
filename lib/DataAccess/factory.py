import numpy as np
from ..DataCleaning import cleaning, interpolation, utils
import logging

class DataFactory(object):
  """object for generating datasets of the appropriate ndarray type for consumption data"""
  def __init__(self, src):
    self.dtype = np.dtype([('date', np.float), ('consumption', np.float), ('temperature', np.float)])
    self.src = src()#config(src.__name__, config_path))

  def temperature(self, meter_id, sd_limit=None, resolution=None):
    try:
      date, integ, movement = self.temp_date, self.temp_integ, self.temp_movement
      logging.debug('Loaded stored temperature data [%s]' % meter_id)
    except AttributeError, e:
      logging.debug('Loading temperature data [%s]' % meter_id)
      self.temp_date, self.temp_integ, self.temp_movement = self.src.temperature(meter_id)
      date, integ, movement = self.temp_date, self.temp_integ, self.temp_movement
      logging.debug('Preparing')
    if sd_limit != None: date, integ, movement = cleaning.clean_temp(date, integ, movement, sd_limit)
    if resolution !=None: date, integ, movement = interpolation.interpolate(date, integ, movement, resolution)
    return date, integ, movement

  def consumption(self, meter_id, sd_limit=None, resolution=None):
    logging.debug('Loading consumption data %s' % meter_id)
    date, integ, movement = self.src.consumption(meter_id)
    logging.debug('Preparing')
    if sd_limit != None: date, integ, movement = cleaning.clean(date, integ, movement, sd_limit)
    if resolution !=None: date, integ, movement = interpolation.interpolate(date, integ, movement, resolution)
    return date, integ, movement
    
  def dataset(self, cons_id, temp_id, sd_limit=30, temp_sd_limit=6, resolution=60*60*24):
    temp_date, temp_integ, temp_movement = self.temperature(temp_id, temp_sd_limit, resolution)
    date, integ, movement = self.consumption(cons_id, sd_limit, resolution)
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

  def locations(self):
    return self.src.locations()

  def metersForLocation(self, id):
    return self.src.metersForLocation(id)

  def meters(self):
    return self.src.meters()

if __name__ == "__main__":
  from classic import Classic
  df = DataFactory(Classic)
  d1 = df.dataset(1)
  d2 = df.dataset(2)
  
