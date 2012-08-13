import unittest
from pyEMIS.data import utils
import numpy as np

class testIntegFromMovement(unittest.TestCase):
    """A test class for the utils module function integ_from_movement"""
    
    def testNormal(self):
        np.testing.assert_array_equal(utils.integ_from_movement([1,2,1,2,1,2]), [0,2,3,5,6,8])
        np.testing.assert_array_equal(utils.integ_from_movement([5,2,1,2,1,2]), [0,2,3,5,6,8])
        np.testing.assert_array_equal(utils.integ_from_movement([100,2,1,2,1,2]), [0,2,3,5,6,8])

    def testNumpyArray(self):   
        np.testing.assert_array_equal(utils.integ_from_movement(np.array([1,2,1,2,1,2])), [0,2,3,5,6,8])
        np.testing.assert_array_equal(utils.integ_from_movement(np.array([5,2,1,2,1,2])), [0,2,3,5,6,8])
        np.testing.assert_array_equal(utils.integ_from_movement(np.array([100,2,1,2,1,2])), [0,2,3,5,6,8])

    def testNumpyMaskedArray(self):
        datasets = [
            [1,2,1,2,1,2],
            [5,2,1,2,1,2],
            [100,2,1,2,1,2]
        ]
        for data in datasets:
            np_movement = np.array(data)
            masked_movement = np.ma.masked_array(np_movement, np_movement==1)
            integ = utils.integ_from_movement(masked_movement)
            np.testing.assert_array_equal(integ.compressed(), [0, 2, 4, 6])
            np.testing.assert_array_equal(integ, np.ma.masked_array([0,2,2000,4,2000,6], mask=[0,0,1,0,1,0]))

        
class testMovementFromInteg(unittest.TestCase):
    def testNormal(self):
        datasets = [
            [0,2,3,5,6,8],
            [10,12,13,15,16,18],
            [3,5,6,8,9,11]
        ]
        for integ in datasets:
            movement = utils.movement_from_integ(integ)
            np.testing.assert_array_equal(movement, [np.nan,2,1,2,1,2])

    def testNumpyArray(self):
        datasets = [
            [0,2,3,5,6,8],
            [10,12,13,15,16,18],
            [3,5,6,8,9,11]
        ]
        for integ in datasets:
            np_integ = np.array(integ)
            movement = utils.movement_from_integ(np_integ)
            np.testing.assert_array_equal(movement, [np.nan,2,1,2,1,2])

    def testNumpyMaskedArray(self):
        datasets = [
            [0,2,3,5,6,8],
            [10,12,13,15,16,18],
            [3,5,6,8,9,11]
        ]
        for integ in datasets:
            np_integ = np.array(integ)
            masked_integ = np.ma.masked_array(np_integ, [0,0,1,0,0,0])
            movement = utils.movement_from_integ(masked_integ)
            np.testing.assert_array_equal(movement, np.ma.masked_array([np.nan,2,1,2,1,2], mask=[0,0,1,0,0,0]))



if __name__ == "__main__":
    unittest.main()
