import unittest
from pyEMIS.models.constant import Constant
from pyEMIS.models.base import ModellingError
import os.path
import numpy as np

here = os.path.dirname(__file__)
filename = os.path.abspath(os.path.join(here, '..', 'sustainable_advantage.xls'))

class testConstantModel(unittest.TestCase):
    """A test class for the constant model"""

    def testGoodData(self):
        dtype = np.dtype([('timestamp', np.float), ('value', np.float)])
        data = np.zeros(5, dtype=dtype)
        data['timestamp'] = [(i + 1) * 3600 for i in range(5)]
        data['value'] = [1,2,3,4,5]
        model = Constant(data)
        self.assertEqual(model.mean, 3.0)
        self.assertAlmostEqual(model.std, 1.414, places=3)

    def testShortData(self):
        dtype = np.dtype([('timestamp', np.float), ('value', np.float)])
        data = np.zeros(1, dtype=dtype)
        data['timestamp'] = [1.0]
        data['value'] = [1.0]
        self.assertRaises(ModellingError, Constant, data)

    def testMissingData(self):
        dtype = np.dtype([('timestamp', np.float), ('value', np.float)])
        data = np.zeros(6, dtype=dtype)
        data['timestamp'] = [np.nan, np.nan, 1.0, np.nan, np.nan, np.nan]
        data['value'] = [np.nan, np.nan, 1.0, np.nan, np.nan, np.nan]
        self.assertRaises(ModellingError, Constant, data)
        data['timestamp'] = [np.nan, np.nan, 1.0, np.nan, 3.0, np.nan]
        data['value'] = [np.nan, np.nan, 1.0, np.nan, 3.0, np.nan]
        self.assertRaises(ModellingError, Constant, data)
        data['timestamp'] = [np.nan, np.nan, 1.0, 2.0, 3.0, np.nan]
        data['value'] = [np.nan, np.nan, 1.0, 2.0, 3.0, np.nan]
        model = Constant(data)
        self.assertEqual(model.mean, 2.0)


if __name__ == "__main__":
    unittest.main()
