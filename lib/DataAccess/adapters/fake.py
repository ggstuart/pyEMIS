from ..sources import Fake as FakeSource
from ...DataCleaning import utils

class Fake(object):
    """Provides raw datasets for analysis"""
    def __init__(self):
        self.src = FakeSource()

    def consumption(self, meter_id):
        dates = self.src.dates()
        integ = self.src.integ()
        movement = utils.movement_from_integ(integ)
        return dates, integ, movement

    def temperature(self, meter_id):
        dates = self.src.dates()
        movement = self.src.movement()
        integ = utils.integ_from_movement(movement)
        return dates, integ, movement

