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

    def __init__(self, n=5000, mu=100, sigma=1, date_mu=30*60, date_sigma=60):
        #number of points
        self.n = n
        #date is every 30 minutes plus noise with sdev of 60 seconds
        self.date_mu = date_mu
        self.date_sigma = date_sigma   # 60 seconds
        self.mu = mu
        self.sigma = sigma

    def dates(self):
        date = ((np.arange(self.n, dtype = float) + 1) * self.date_mu) + np.round(np.random.normal(0, self.date_sigma, self.n))        
        return utils.datetime_from_timestamp(date)

    def movement(self, n_steps=0):
        result = abs(np.random.normal(self.mu, self.sigma, self.n))        
        for i in range(n_steps):
            result[np.random.randint(self.n)] += (self.sigma * 100 * np.random.randn())
        return result

    def integ(self, n_steps=0, n_spikes=0):
        result = utils.integ_from_movement(self.movement(n_steps))   #integ = np.cumsum(movement)
        for i in range(n_spikes):
            result[np.random.randint(self.n)] += (self.sigma * 100 * np.random.randn())
        return result

    def meters(self):
        return [{'id': i+1, 'name': 'meter_%04i' % (i+1), 'type': 'fake'} for i in xrange(10)]#np.arange(10, dtype = int) + 1

    def meter(self, meter_id):
        return {'id': int(meter_id), 'name': 'meter_%04i' % (int(meter_id)), 'type': 'fake'}
