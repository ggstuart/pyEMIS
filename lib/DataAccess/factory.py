import numpy as np
from ..DataCleaning import cleaning, interpolation

class DataFactory(object):
  """object for generating datasets of the appropriate ndarray type for consumption data"""
  def __init__(self, src):
    self.dt = np.dtype([('date', np.float), ('consumption', np.float), ('temperature', np.float)])
    self.src = src()#config(src.__name__, config_path))

  def temperature(self, meter_id, sd_limit=None, resolution=None):
    try:
      date, temp = self.temp_date, self.temp
#      print 'Loaded stored temperature data...'
    except AttributeError, e:
#      print 'Loading temperature data...'
      self.temp_date, self.temp = self.src.temperature(meter_id)
      date, temp = self.temp_date, self.temp
#    print 'Preparing...'
    if sd_limit != None: date, temp = cleaning.clean_temp(date, temp, sd_limit)
    if resolution !=None: date, temp = interpolation.interpolate(date, temp, resolution)
    return date, temp

  def consumption(self, meter_id, sd_limit=None, resolution=None):
#    print 'Loading consumption data %s...' % meter_id  
    date, integ, movement = self.src.consumption(meter_id)
#    print 'Preparing...'
    if sd_limit != None: date, integ = cleaning.clean(date, integ, sd_limit)
    if resolution !=None: date, integ = interpolation.interpolate(date, integ, resolution)
    return date, integ
    
  def dataset(self, cons_id, temp_id, sd_limit=30, temp_sd_limit=6, resolution=60*60*24):
    temp_date, temp_movement = self.temperature(temp_id, temp_sd_limit, resolution)
    date, integ = self.consumption(cons_id, sd_limit, resolution)
#    print 'Processing...'
    _from = max(min(date), min(temp_date))
    _to = min(max(date), max(temp_date))
    cons_a = (date >= _from) & (date <= _to)
    temp_a = (temp_date >= _from) & (temp_date <= _to)
    date = date[cons_a]
    integ = integ[cons_a]
    temp_date = temp_date[temp_a]
    temp_movement = temp_movement[temp_a]    
    cons = cleaning.movement_from_integ(integ)
    temp = temp_movement
    size = len(cons)
    result = np.array([(date[i+1], cons[i+1], temp[i+1]) for i in range(size-1)], dtype = self.dt)
#    print 'Done'
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
  
