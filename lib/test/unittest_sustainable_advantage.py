import unittest
from pyEMIS.data.adapters import sustainable_advantage as sa
import os.path

here = os.path.dirname(__file__)
filename = os.path.abspath(os.path.join(here, 'sustainable_advantage.xls'))

class testSustainableAdvantageSource(unittest.TestCase):
    """A test class for the sustainable_advantage data source"""
    
    def setUp(self):
        self.file = sa.File(filename)

    def testBasicData(self):
        ds = self.file.dataset('1200010086239')
        data = """01/10/2010 00:30	17.02
01/10/2010 01:00	15.58
01/10/2010 01:30	13.22
01/10/2010 02:00	13.33
01/10/2010 02:30	12.41
01/10/2010 03:00	12.81
01/10/2010 03:30	12.59
01/10/2010 04:00	12.02
01/10/2010 04:30	12.3
01/10/2010 05:00	12.11
01/10/2010 05:30	12.05
01/10/2010 06:00	20.34
01/10/2010 06:30	23.19
01/10/2010 07:00	24.15
01/10/2010 07:30	22.69
01/10/2010 08:00	22.44
01/10/2010 08:30	26.28
01/10/2010 09:00	27.04
01/10/2010 09:30	27.7
01/10/2010 10:00	28.39
01/10/2010 10:30	26.44
01/10/2010 11:00	27.19
01/10/2010 11:30	27.99
01/10/2010 12:00	25.79""".split("\n")
        for dt, val in ds.readings():
            dt2, val2 = data.pop(0).split("\t")
            self.assertEqual(dt.strftime("%d/%m/%Y %H:%M"), dt2)
            self.assertEqual(val, float(val2))
            if len(data)==0:
                break

class testSustainableAdvantageAdapter(unittest.TestCase):
    """A test class for the Sustainable Advantage data adapter"""

    def setUp(self):
        self.adapter = sa.Adapter(filename)


    def testBasicData(self):
        dataset = self.adapter.dataset('1200010086239')
        data = dataset.data()
        self.assertEqual(len(data), 19538)
        self.assertAlmostEqual(sum(data['value']), 400253.9)
        self.assertEqual(dataset.unit.name, 'kiloWatt hour')
        self.assertEqual(dataset.unit.suffix, 'kWh')
        self.assertEqual(dataset.unit.coefficient, 1.0)


if __name__ == "__main__":
    unittest.main()
