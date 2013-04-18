import unittest
from pyEMIS.data.unit import Unit, BaseUnit, kWh, M3

class testUnit(unittest.TestCase):
    """A test class for the Unit module"""
    
    def setUp(self):
        self.GJ = BaseUnit('GigaJoules', 'GJ')
        self.m3 = BaseUnit('Cubic Metres', 'm3')        
        self.kWh = Unit(self.GJ, 0.0036, 'kiloWatt hours', 'kWh')
        self.BTU = Unit(self.GJ, 0.000001055, 'British thermal units', 'BTU')
        self.litre = Unit(self.m3, 0.001, 'litres', 'l')
        self.kilojoule = Unit(self.GJ, 0.000001, 'KiloJoules', 'kJ')

    def testBasicAttributes(self):
        self.assertEqual(self.GJ.name, 'GigaJoules')
        self.assertEqual(self.GJ.suffix, 'GJ')
        self.assertEqual(self.kilojoule.base_unit, self.GJ)

    def testUnitConversion(self):
        self.assertEqual(self.kilojoule.to_base(1000.0), 0.001)
        self.assertEqual(self.kWh.to_unit(1.0, self.kilojoule), 3600.0)
        self.assertEqual(self.kWh.to_base(1000.0), 3.6)
        
    def testInvalidConversion(self):
        self.assertRaises(TypeError, self.litre.to_unit, (1.0, self.kilojoule))
        self.assertRaises(TypeError, self.kilojoule.to_unit, (1.0, self.litre))

    def testEquivalence(self):
        self.assertEqual(self.kWh, kWh)
        self.assertEqual(self.m3, M3)
        
if __name__ == "__main__":
    unittest.main()
