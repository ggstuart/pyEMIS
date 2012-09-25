from ..sources import Classic as ClassicSource
#from ...DataCleaning import utils
import numpy as np
import calendar, os.path, logging

class ClassicError(Exception): pass


class Classic(object):
    def __init__(self, config_path=os.path.expanduser('~/.EMIS/config.cfg')):
        """
        >>> import pyEMIS.DataAccess as DA
        >>> ad = DA.adapters.Classic()
        >>> ad #doctest: +ELLIPSIS
        <pyEMIS.DataAccess.adapters.classic.Classic object at ...>
        >>>
        """
        self.logger = logging.getLogger('DataAccess:adapters:Classic')
        self.source = ClassicSource(config_path, "Classic")

    def timeseries(self, meter_id):
        """
        Retrieve readings for a given meter_id
        >>> from pyEMIS.DataAccess.adapters import Classic
        >>> classic = Classic()
        >>> jm = classic.timeseries(180)
        >>> sorted(jm.keys())
        ['commodity', 'datetime', 'description', 'integ', 'timestamp', 'units', 'value']
        >>> jm['commodity']
        'consumption'
        >>> jm['integ']
        True
        >>> jm['units']['name']
        'kiloWatt-hours'
        >>> jm['units']['abbreviation']
        'kWh'
        >>> len(jm['value'])
        101450
        """


        self.logger.debug('Getting meter %05i from Classic' % meter_id)
        m = self.source.meter_with_units(meter_id)
        self.logger.debug(m)
        self.logger.debug('meter type: %s' % m['type'])
        units = {'name': m['unit'].strip(), 'abbreviation': m['suffix'].strip()}

        if units['name'] == 'kilowatt hours':
            units['name'] = 'kiloWatt-hours'

        commodity = 'unknown'
        if m['type'] == 'Energy':
            integ = True
            self.logger.debug('Energy data')
            commodity = 'consumption'
            data = self.source.integ_units(meter_id)   #includes multiplier so units are correct
        elif m['type'] == 'Temperature':
            integ = False
            self.logger.debug('Temperature data')
            commodity = 'temperature'
            data = self.source.integ_units(meter_id)   #includes multiplier so units are correct            
        else:
            raise ClassicError, "Unknown meter type [%s]" % m['type']

        return {
            'description': m['name'],
            'integ': integ,
            'commodity': commodity,
            'datetime': [d['datetime'] for d in data],
            'timestamp': self._convert_to_date([d['datetime'] for d in data]),
            'value': np.array([d['value'] for d in data], dtype=float),
            'units': units
        }

    def meter(self, meter_id):
        return self.source.meter_with_units(meter_id)

    def meters(self):
        return self.source.meters()

    #convert sql date to numpy ndarray float
    def _convert_to_date(self, data):
        result = [calendar.timegm(t.timetuple()) for t in data]
        result = np.array(result, dtype=float)
        return result

if __name__ == "__main__":
    import doctest
    doctest.testmod()
