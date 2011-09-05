from database import DynamatPlus
import numpy as np
import calendar, os.path, logging

class DplusAdapter(object):
    def __init__(self, config_path=os.path.expanduser('~/.EMIS/config.cfg')):
        self.src = DynamatPlus(config_path, "DynamatPlus")

    def consumption(self, meter_id):
        logging.debug('Getting meter_%04i from DynamatPlus' % meter_id)
        data = self.src.readingsList(meter_id)
        logging.debug(len(data))
        date = [d['Reading_DateTime'] for d in data]
        integ =  [d['Reading_Or_Total'] for d in data]
        movement =  [d['Delivered_Or_Movement'] for d in data]
        return self._convert_to_date(date), self._convert_to_float(integ), self._convert_to_float(movement)

    def temperature(self, meter_id):
        date, integ, movement = self.consumption(meter_id)
        return date, integ, movement
        

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
    
