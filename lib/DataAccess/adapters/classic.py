from ..sources import Classic as ClassicSource
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
        """
        self.logger.debug('Getting meter %05i from Classic' % meter_id)

        m = self.source.meter_with_units(meter_id)
        self.logger.debug(m)
        self.logger.debug('meter type: %s' % m['type'])

        units = {'name': m['unit'].strip(), 'abbreviation': m['suffix'].strip()}

        value_type = 'unknown'

        if m['type'] == 'Energy':
            data_type = 'integ'
            self.logger.debug('Energy data')
            value_type = 'Consumption'
            data = self.source.integ_units(meter_id)   #includes multiplier so units are correct
#            units = {'name': 'kiloWatt-hours', 'abbreviation': 'kWh'}
        else:
            raise ClassicError, "Unknown meter type [%s]" % m['type']

        return {
            'description': m['name'],
            'type': data_type,
            'value_type': value_type,
            'datetime': [d['datetime'] for d in data],
            'timestamp': self._convert_to_date([d['datetime'] for d in data]),
            'value': np.array([d['value'] for d in data], dtype=float),
            'units': units
        }

    def meterInfo(self, meter_id):
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
