import unittest
from pyEMIS.data.config import Config
from pyEMIS.data.adapters import dynamat_plus as dp

class testDynamatPlusSource(unittest.TestCase):
    """A test class for the DynamatPlus data source"""
    
    def setUp(self):
        conf = Config('Dynamat_DMU')
        self.src = dp.Source(conf)

    def testRootNode(self):
        root = self.src.root()
        self.assertEqual(root.Object_Description.strip(), 'Dynamat World')
        top_level = root.children
        for node in top_level:
            self.assertEqual(node.parent, root)

    def testSearch(self):
        term = 'queens'
        sites = self.src.siteSearch(term)
        for site in sites:
            self.assertIn(term.lower(), site.Name.strip().lower())
        meters = self.src.meterSearch(term)
        for meter in meters:
            self.assertIn(term.lower(), meter.Description.strip().lower())

    def testMeter(self):
        meters = self.src.meterSearch('queens')
        for m in meters[0:10]:
            meter = self.src.meter(m.Meter_ID)
            self.assertEqual(meter, m)

    def testUnit(self):
        unit = self.src.unit(1)
        self.assertEqual(unit.Unit_Description.strip(), 'Cubic feet gas')
        self.assertEqual(unit.Abbreviation.strip(), 'cu.ft')
        self.assertEqual(float(unit.Units_Per_GJ), 928.31)

    def testServiceType(self):
        meters = self.src.meterSearch('queens')
        for m in meters:
            if m.Service_ID:
                stype = self.src.service_type(m.Service_ID)
                self.assertEqual(m.Service_Type, stype)

class testDynamatPlusAdapter(unittest.TestCase):
    """A test class for the DynamatPlus data adapter"""

    def setUp(self):
        conf = Config('Dynamat_DMU')
        self.adapter = dp.Adapter(conf)


    def testBasicData(self):
        qb_elec = self.adapter.dataset("213")
        self.assertGreater(len(qb_elec.data()), 10000)
        self.assertEqual(qb_elec.unit.name, 'GigaJoules')
        self.assertEqual(qb_elec.unit.suffix, 'GJ')
        self.assertEqual(qb_elec.unit.coefficient, 1.0)


if __name__ == "__main__":
    unittest.main()
