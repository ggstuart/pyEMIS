from pyEMIS.DataCleaning import utils
import numpy as np

class Fake():
    """Randomly generated data.
    Default values
    n = 5000
    mean period between readings = 30*60 seconds
    'noise' in the timestamp = 60 seconds
    """
    class MeterNotFoundError(Exception): pass
    
    def __init__(self, n=5000, date_mu=30*60, date_sigma=60):
      #number of points
      self.n = n
      #date is every 30 minutes plus noise with sdev of 60 seconds
      self.date_mu = date_mu
      self.date_sigma = date_sigma   # 60 seconds
      self.mu = 100  #mean
      self.sigma = 1 #sdev
      self.n_spikes = 0  #spikes in consumption are steps in the integ
      self.n_steps = 0   #steps in consumption are double opposite spikes in the integ

    def consumption(self, meter_id):
      date = ((np.arange(self.n, dtype = float) + 1) * self.date_mu) + np.round(np.random.normal(0, self.date_sigma, self.n))
      movement = abs(np.random.normal(self.mu, self.sigma, self.n))
      for i in range(self.n_steps):
        movement[np.random.randint(self.n)] += (self.sigma * 100 * np.random.randn())
      integ = utils.integ_from_movement(movement)   #integ = np.cumsum(movement)
      for i in range(self.n_spikes):
        integ[np.random.randint(self.n)] += (self.sigma * 100 * np.random.randn())
      return utils.datetime_from_timestamp(date), integ, movement

    def temperature(self, meter_id):
      date = ((np.arange(self.n, dtype = float) + 1) * self.date_mu) + np.round(np.random.normal(0, self.date_sigma, self.n))
      movement = abs(np.random.normal(self.mu, self.sigma, self.n))
      for i in range(self.n_steps):
        movement[np.random.randint(self.n)] += (self.sigma * 100 * np.random.randn())
      integ = utils.integ_from_movement(movement)
      return utils.datetime_from_timestamp(date), integ, movement

      

    """Provides raw datasets for analysis"""
    def readings(self, meter_id):
      #maybe add todays date or determine starting point somehow
      date = ((np.arange(self.n, dtype = float) + 1) * self.date_mu) + np.round(np.random.normal(0, self.date_sigma, self.n))
      movement = abs(np.random.normal(self.mu, self.sigma, self.n))
      for i in range(self.n_steps):
        movement[np.random.randint(self.n)] += (self.sigma * 100 * np.random.randn())
      integ = np.cumsum(movement)
      for i in range(self.n_spikes):
        integ[np.random.randint(self.n)] += (self.sigma * 100 * np.random.randn())
      return date, integ
       
    def meters(self):
      return [{'id': i+1, 'name': 'meter_%04i' % (i+1), 'type': 'fake'} for i in xrange(10)]#np.arange(10, dtype = int) + 1
        
    def meter(self, meter_id):
#      if meter_id != 1: raise MeterNotFoundError(meter_id)
      return {'id': int(meter_id), 'name': 'meter_%04i' % (int(meter_id)), 'type': 'fake'}# {'channel_id': 1, 'multiplier': 1, 'coefficient': 1}
