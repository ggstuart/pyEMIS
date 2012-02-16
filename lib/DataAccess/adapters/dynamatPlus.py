from ..sources import DynamatPlus as DplusSource
import numpy as np
import calendar, os.path, logging

class DynamatPlusError(Exception): pass
   

class DynamatPlus(object):
    def __init__(self, config_path=os.path.expanduser('~/.EMIS/config.cfg')):
        """
        >>> import pyEMIS.DataAccess as DA
        >>> ad = DA.adapters.DynamatPlus()
        >>> ad #doctest: +ELLIPSIS
        <pyEMIS.DataAccess.adapters.dynamatPlus.DynamatPlus object at ...>
        >>>
        """
        self.logger = logging.getLogger('DataAccess:adapters:DynamatPlus')
        self.src = DplusSource(config_path, "DynamatPlus")

    def timeseries(self, meter_id):
        """
        Retrieve readings for a given meter_id
        """
        self.logger.debug('Getting meter %05i from DynamatPlus' % meter_id)
        m = self.src.meter_with_units(meter_id)
        self.logger.debug('meter type: %i' % m['type'])
        self.logger.debug('unit type: %i' % m['unit_type'])
        units = {'name': m['unit_description'].strip(), 'abbreviation': m['abbreviation'].strip()}
        value_type = 'unknown'
        if units['abbreviation'][0] == chr(0xb0):
            #replace degree symbol - boo!
            units['abbreviation'] = 'Degrees ' + units['abbreviation'][1:]
            value_type = 'Temperature'
            
        if m['type'] == 1:
            data_type = 'integ'
            if m['unit_type'] == 0:
                self.logger.debug('Energy data')
                value_type = 'Consumption'
                data = self.src.energyColumn(meter_id)
                units = {'name': 'kiloWatt-hours', 'abbreviation': 'kWh'}
            elif m['unit_type'] == 1:
                self.logger.debug('Water data')
                value_type = 'Consumption'
                data = self.src.waterColumn(meter_id)
                units = {'name': 'Cubic meters', 'abbreviation': 'm3'}
            elif m['unit_type'] == 2:
                self.logger.debug('%s data' % m['unit_description'])
                data = self.src.integColumn(meter_id)
            else:
                raise DynamatPlusError, "Unknown unit type for integ meter (type 1) [%s]" % m['unit_type']

        elif m['type'] == 4:
            data_type = 'movement'
            if m['unit_type'] == 2:
                self.logger.debug('%s data' % m['unit_description'])
                data = self.src.movementColumn(meter_id)
            else:
                raise DynamatPlusError, "Unknown unit type for movement meter (type 4) [%s]" % m['unit_type']

        elif m['type'] == 6:
            raise DynamatPlusError, "Virtual meter!"
        else:
            raise DynamatPlusError, "Unknown meter type [%s]" % m['type']

        result = {
            'description': m['description'],
            'type': data_type,
            'value_type': value_type,
            'datetime': [d['datetime'] for d in data],
            'timestamp': self._convert_to_date([d['datetime'] for d in data]),
            'value': np.array([d['value'] for d in data], dtype=float),
            'units': units
        }
        return result

    def meterInfo(self, meter_id):
        return sself.src.meter_with_units(meter_id)

    #convert sql date to numpy ndarray float
    def _convert_to_date(self, data):
        result = [calendar.timegm(t.timetuple()) for t in data]
        result = np.array(result, dtype=float)
        return result

if __name__ == "__main__":
    import doctest
    doctest.testmod()
