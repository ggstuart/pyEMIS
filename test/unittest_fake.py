import unittest
from pyEMIS.data.adapters.fake import Fake
from pyEMIS.data.unit import BaseUnit, Unit
from numpy.testing import assert_array_almost_equal

class testFake(unittest.TestCase):
    """A test class for the Fake data adapter"""
    
    def setUp(self):
        from random import randint, random
        from datetime import timedelta
        self.base = BaseUnit('kiloWatt hour', 'kWh')
        self.unit = Unit(self.base, 1.0/3600000.0, 'Joule', 'J')
        meter_ids = ["meter_%02i" % i for i in xrange(1, 11)]
        self.meters = dict([(meter_id, {'mu': random() * 100000000 + 1000000000, 'sigma': random() * 1000000 + 10000000, 'n': randint(1000, 10000), 'unit': self.unit, 'res': timedelta(hours=1)}) for meter_id in meter_ids])

    def testBasicData(self):
        src = Fake(self.meters)
        m = self.meters["meter_10"]
        d = src.dataset("meter_10")
        self.assertEqual(d.unit, m['unit'].base_unit)
        self.assertEqual(len(d.data), m['n'])
        self.assertAlmostEqual(d.data['value'].mean(), m['unit'].to_base(m['mu']), places=0)
        self.assertAlmostEqual(d.data['value'].std(), m['unit'].to_base(m['sigma']), places=0)
        

if __name__ == "__main__":
    unittest.main()
