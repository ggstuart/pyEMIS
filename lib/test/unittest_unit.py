import unittest
from pyEMIS.data.unit import Unit, BaseUnit

class testUnit(unittest.TestCase):
    """A test class for the Unit module"""
    
    def setUp(self):
        self.joule = BaseUnit('Joule', 'J')
        self.m3 = BaseUnit('Cubic Metre', 'm3')        
        self.kWh = Unit(self.joule, 3600000.0, 'kiloWatt hour', 'kWh')
        self.BTU = Unit(self.joule, 1055, 'British thermal unit', 'BTU')
        self.litre = Unit(self.m3, 0.001, 'litre', 'l')
        self.kilojoule = Unit(self.joule, 1000.0, 'KiloJoule', 'kJ')

    def testBasicAttributes(self):
        self.assertEqual(self.joule.name, 'Joule')
        self.assertEqual(self.joule.suffix, 'J')
        self.assertEqual(self.kilojoule.base_unit, self.joule)

    def testUnitConversion(self):
        self.assertEqual(self.kilojoule.to_base(1.0), 1000.0)
        self.assertEqual(self.kWh.to_unit(1.0, self.kilojoule), 3600.0)
        self.assertEqual(self.kWh.to_base(1.0), 3600000.0)
        
    def testInvalidConversion(self):
        self.assertRaises(TypeError, self.litre.to_unit, (1.0, self.kilojoule))
        self.assertRaises(TypeError, self.kilojoule.to_unit, (1.0, self.litre))
        
        
if __name__ == "__main__":
    unittest.main()
