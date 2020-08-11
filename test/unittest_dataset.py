import unittest
from datetime import datetime, timedelta
from pyEMIS.data.dataset import Dataset
from numpy.testing import assert_array_almost_equal
from pyEMIS.data.unit import BaseUnit, Unit
import numpy as np

class testDataset(unittest.TestCase):
    """A test class for the Dataset module"""
    
    def setUp(self):
        self.kWh = BaseUnit('kiloWatt hour', 'kWh')
        self.joule = Unit(self.kWh, 1.0/3600000.0, 'Joule', 'J')
        self.length = 10778
        dt = [datetime(2000, 1, 1) + timedelta(hours=i) for i in range(self.length)]
        self.val = np.random.normal(3600000.0, 360000.0, self.length)
        self.dataset = Dataset(dt, self.val, self.joule, 'energy')

    def testBasicAttributes(self):
        self.assertEqual(self.dataset.unit, self.kWh)
        assert_array_almost_equal(self.kWh.to_unit(self.dataset.data()['value'], self.joule), self.val)
        self.assertEqual(self.dataset.commodity, 'energy')

    def testInterpolation(self):
        original = self.dataset.data()
        hourly = self.dataset.data(resolution=60*60)
        self.assertEqual(len(hourly), len(original))
        self.assertEqual(len(hourly), self.length)
        
if __name__ == "__main__":
    unittest.main()
