import logging
import calendar, numpy as np
from ..sources import Test as Source
from ...DataCleaning import utils

class Test(object):
    """Provides datasets for testing purposes"""
    def __init__(self):
        self.logger = logging.getLogger('sources:test')
        self.src = Source()

    def timeseries(self, meter_id):
        return self.src.timeseries(meter_id)

    def meters(self):
        return self.src.meters()

    def meter(self, meter_id):
        return self.src.meter(meter_id)
