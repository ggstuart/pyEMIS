from source import Source
from pyEMIS.data.unit import BaseUnit, Unit
from pyEMIS.data.dataset import Dataset
from pyEMIS.data.utils import movement_from_integ

class GraemePhDError(Exception): pass

serv_desc = {
    'energy': 
}

class Adapter(object):

    def __init__(self, config):
        self.src = Source(config)

    def dataset(self, channel_id):
        m = self.src.meter(meter_id)
        return convert_dataset(m)


def convert_unit(unit):
    """Convert a database unit record into a pyEMIS unit"""
    desc = unit.name.strip()
    suffix = unit.suffix.strip()
    if unit.SERV_DESC == 0:   # Energy unit
        base = BaseUnit("GigaJoules", "GJ")
        return Unit(base, float(unit.Units_Per_GJ), desc, suffix)#suffix.split('*')[0])
    elif unit.Unit_Type == 1: # Water unit
        base = BaseUnit("Cubic metre", "m3")
        return Unit(base, float(unit.Units_Per_Cubic_Metre), desc, suffix)#suffix.split('*')[0])
    elif unit.Unit_Type == 2: # Not sure what this means - other?
        return BaseUnit(desc, suffix)
    else:
        raise GraemePhDError, 'Unknown Unit_Type [%s] for unit [%s].' % (unit.Unit_Type, desc)

def convert_dataset(meter):
    """Convert a database meter record into a pyEMIS dataset"""
    unit = convert_unit(meter.Measured_Unit)
    label = meter.Description.strip()
    if meter.Service_Type:
        commodity = meter.Service_Type.Service_Description.strip()
    else:
        commodity = 'unknown'
    datetimes = [r.Reading_DateTime for r in meter.Readings]
    if meter.Readings_Or_Deliveries:
        integ = [float(r.Reading_Or_Total) for r in meter.Readings]
        values = movement_from_integ(integ)
    else:
        values = [float(r.Delivered_Or_Movement) for r in meter.Readings]
    return Dataset(datetimes, values, label, unit, commodity)
