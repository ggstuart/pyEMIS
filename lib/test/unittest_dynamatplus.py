import unittest
from pyEMIS.data.config import Config
from pyEMIS.data.adapters import dynamat_plus as dp
from pyEMIS.data.unit import kWh, GJ

class testDynamatPlusAdapter(unittest.TestCase):
    """A test class for the DynamatPlus data adapter"""

    def setUp(self):
        conf = Config('Dynamat_DMU')
        self.adapter = dp.Adapter(conf)

    def test_datasource(self):
        qb = self.adapter.datasource(213)
        self.assertEqual(qb.label, 'LEC/QUEN/ACD/ES01')
        self.assertEqual(qb.commodity, 'electricity')

    def test_unit(self):
        unit = self.adapter.datasource(213).unit
        base = unit.base_unit
        self.assertEqual(base, GJ)

#    def testBasicData(self):
#        qb_elec = self.adapter.dataset("213")
#        self.assertGreater(len(qb_elec.data()), 10000)
#        self.assertEqual(qb_elec.unit.name, 'GigaJoules')
#        self.assertEqual(qb_elec.unit.suffix, 'GJ')
#        self.assertEqual(qb_elec.unit.coefficient, 1.0)


if __name__ == "__main__":
    unittest.main()
