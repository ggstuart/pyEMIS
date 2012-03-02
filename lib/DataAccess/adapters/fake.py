import calendar, numpy as np
from ..sources import Fake as FakeSource
from ...DataCleaning import utils

class Fake(object):
    """Provides raw datasets for analysis"""
    def __init__(self):
        self.src = FakeSource()

    def consumption(self, meter_id):
        dates = self.src.dates()
        integ = self.src.integ()
        return {
            'description': 'Fake consumption %s' % meter_id,
            'type': 'integ',
            'value_type': 'Consumption',
            'datetime': dates,
            'timestamp': self._convert_to_date(dates),
            'value': integ,
            'units': {'name': 'kiloWatt-hours', 'abbreviation': 'kWh'}
        }

    def temperature(self, meter_id):
        dates = self.src.dates()
        movement = self.src.movement()
        return {
            'description': 'Fake temperature %s' % meter_id,
            'type': 'movement',
            'value_type': 'Temperature',
            'datetime': dates,
            'timestamp': self._convert_to_date(dates),
            'value': movement,
            'units': {'name': 'Celsius', 'abbreviation': 'C'}
        }

    def timeseries(self, meter_id):
        return self.consumption(meter_id)

    def meters(self):
        return self.src.meters()

    def meter(self, meter_id):
        return self.src.meter(meter_id)
        
    #convert sql date to numpy ndarray float
    def _convert_to_date(self, data):
        result = [calendar.timegm(t.timetuple()) for t in data]
        result = np.array(result, dtype=float)
        return result

