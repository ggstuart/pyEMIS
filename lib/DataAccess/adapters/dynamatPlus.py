from ..sources import DynamatPlus as DplusSource
import numpy as np
import calendar, os.path, logging

class DynamatPlus(object):
    def __init__(self, config_path=os.path.expanduser('~/.EMIS/config.cfg')):
        self.src = DplusSource(config_path, "DynamatPlus")

    def consumption(self, meter_id):
        logging.debug('Getting meter_%04i from DynamatPlus' % meter_id)
        data = self.src.readingsList(meter_id)
        date = [d['Reading_DateTime'] for d in data]
        integ =  [d['Reading_Or_Total'] for d in data]
        movement =  [d['Delivered_Or_Movement'] for d in data]
#        return self._convert_to_date(date), self._convert_to_float(integ), self._convert_to_float(movement)
        return date, self._convert_to_float(integ), self._convert_to_float(movement)

    def temperature(self, meter_id):
        logging.debug('Getting temperature_%04i from DynamatPlus' % meter_id)
        data = self.src.temperatureList(meter_id)
        date = [d['Reading_DateTime'] for d in data]
        integ =  [d['Reading_Or_Total'] for d in data]
        movement =  [d['Delivered_Or_Movement'] for d in data]
        return date, self._convert_to_float(integ), self._convert_to_float(movement)
        
    def timeseries(self, meter_id):
        "Retrieve data for a given timeseries"
        m = self.src.meter(meter_id)
        if m['Meter_Type'] == 4:
            return self.temperature(meter_id)
        else:
            return self.consumption(meter_id)

    def meterInfo(self, meter_id):
        return src.meterSummary(meter_id)

    #convert sql date to numpy ndarray float
    def _convert_to_date(self, data):
        result = [calendar.timegm(t.timetuple()) for t in data]
        result = np.array(result, dtype=float)
        return result

    #convert sql data to numpy ndarray float
    def _convert_to_float(self, data):
        return np.array(data, dtype=float)

    def __getattr__(self, attr):
        """Everything else is delegated to src"""
        return getattr(self.src, attr)
        
if __name__ == "__main__":
    db = DynamatPlus("./dynamat.ini", "DMU")
    
