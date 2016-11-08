from . import DataError

COMMODITIES = [
    'electricity',
    'electricity (reactive)',
    'gas',
    'temperature',
    'unknown',
    'water',
]

class DataSourceError(DataError): pass

class DataSource(object):
    """Stores meta-data about the sensor, meter or simulation that generated a dataset"""
    def __init__(self, label, commodity, unit):
        """
        Label should be a string that describes the data source
        """
        if commodity.lower() not in COMMODITIES:
            raise DataSourceError("Unknown commodity: %s (must be one of %s)" % (commodity.lower(), COMMODITIES))
        self.commodity = commodity.lower()
        self.label = label
        self.unit = unit
