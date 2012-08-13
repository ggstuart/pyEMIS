from datetime import datetime
import numpy as np

from pyEMIS.data.unit import BaseUnit, Unit
from pyEMIS.data.dataset import Dataset

class Fake(object):
    def __init__(self, meters):
        self.meters = meters
        
    def dataset(self, meter_id):
        meter = self.meters[meter_id]
        values = np.random.normal(meter['mu'], meter['sigma'], meter['n'])
        dt1 = datetime.today()
        datetimes = [dt1 - (meter['n'] - i) * meter['res'] for i in xrange(meter['n'])]
        return Dataset(datetimes, values, meter['unit'])

