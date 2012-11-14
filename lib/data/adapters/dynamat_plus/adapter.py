import logging
from pytz import timezone, AmbiguousTimeError, NonExistentTimeError

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#from pyEMIS.data.adapters.dynamat_plus import Source
from pyEMIS.data.config import ConfigurationFileError
from pyEMIS.data.unit import BaseUnit, Unit, GJ, M3, C
from pyEMIS.data.dataset import Dataset
from pyEMIS.data.datasource import DataSource
from pyEMIS.data.utils import movement_from_integ
from pyEMIS.data.adapters import AdapterError

from source import Meter

#utc = timezone('UTC')
london = timezone('Europe/London')
logger = logging.getLogger('DynamatPlus adapter')

class DynamatPlusError(AdapterError): pass


#class Source(object):
#
#    def meters(self):
#        return self.session.query(Meter).all()
#
#    def meter(self, Meter_ID):
#        return self.session.query(Meter).get(Meter_ID)
#
#    def root(self):
#        return self.session.query(Tree).filter(Tree.Parent_Node_ID==0).one()
#
#    def siteSearch(self, term):
#        return self.session.query(Site).filter(Site.Name.contains(unicode(term))).all()
#
#    def meterSearch(self, term):
#        return self.session.query(Meter).filter(Meter.Description.contains(unicode(term))).all()
#
#    def unit(self, Unit_ID):
#        return self.session.query(Units).get(Unit_ID)
#
#    def service_type(self, Service_ID):
#        return self.session.query(Service_Type).get(Service_ID)


class Adapter(object):

    def __init__(self, config):
        try:
            self.timezone = timezone(config.timezone)
        except ConfigurationFileError:
            self.timezone = timezone('Europe/London')
        connection_string = "mssql+%s://%s:%s@%s/%s" % (config.driver, config.user, config.password, config.host, config.db)
        engine = create_engine(connection_string, echo=False)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def dataset(self, meter_id, unit=None):
        m = self.session.query(Meter).get(meter_id)
        if m:
            return convert_dataset(m, self.timezone, unit=unit)

    def datasource(self, meter_id):
        m = self.session.query(Meter).get(meter_id)
        if m:
            return convert_datasource(m)
        
    def dataset_ids(self):
        return self.session.query(Meter.Meter_ID).all()

#    def datasets_like(self, meter_name):
#        meters = self.session.query(Meter).filter(Meter.Description get(meter_id)
#        if m:
#            return convert_dataset(m, unit=unit)

#    #TODO - create a pyEMIS.MeterPoint and merge it with dataset somehow
#    #This should allow for a meterpoint to be pulled from the database and then the dataset pulled from the meterpoint
#    #The meterpoint holds all the metadata about the system underlying the dataset, the dataset holds information about the data (units, commodity etc.)
#    def meter_points(self):
#        for meter in self.src.meters():
#            yield meter

commodity_map = {
    'Electricity MD': 'electricity',
    'Electricity block': 'electricity',
    'Elec Active': 'electricity',
    'Elec Reactive': 'electricity (reactive)',
    'Firm Gas': 'gas',
    'Mains water': 'water',
}


#TODO: What about temperature?
def convert_unit(unit):
    """Convert a dynamatplus unit record into a pyEMIS unit"""
    desc = unit.Unit_Description.strip()
    suffix = unit.Abbreviation.strip()

    if unit.Unit_Type == 0:   # Energy unit
        coefficient = 1.0 / float(unit.Units_Per_GJ)
        return Unit(GJ, coefficient, desc, suffix)

    elif unit.Unit_Type == 1: # Water unit
        coefficient = 1.0 / float(unit.Units_Per_Cubic_Metre)
        return Unit(M3, coefficient, desc, suffix)

    # Not sure what this means
    # it includes kVAh, kVArh, Degrees C, hours run, pulses, meals, miles etc.
    elif unit.Unit_Type == 2:
        
        #This is a fudge to catch temperature data
        if desc == 'Degrees C':
            return Unit(C, 1.0, desc, suffix)

        #TODO: possible check for unit.Units_Per_Cubic_Metre and unit.Units_Per_GJ
        #This would identify quantified energy and volume units

        return BaseUnit(desc, suffix)
    else:
        raise DynamatPlusError, 'Unknown Unit_Type [%s] for unit [%s].' % (unit.Unit_Type, desc)


def convert_datasource(meter):
    """Convert a dynamatplus meter record into a pyEMIS datasource"""
    label = meter.Description.strip()
    unit = convert_unit(meter.Measured_Unit)
    if meter.Service_Type:
        commodity = commodity_map[meter.Service_Type.Service_Description.strip()]
    else:
        if unit.base_unit == C:
            commodity = 'temperature'
        else:
            raise DynamatPlusError, 'cannot infer service type'
    return DataSource(label, commodity, unit)

    
def convert_dataset(meter, tz, unit=None):
    """Convert a dynamatplus meter record into a pyEMIS dataset"""
    dsrc = convert_datasource(meter)
    datetimes = []
    count = 0
    for r in meter.Readings:
        naive_dt = r.Reading_DateTime
        try:
            dt = tz.localize(naive_dt, is_dst=None)
        except NonExistentTimeError:
            dt = tz.localize(naive_dt, is_dst=True)
        except AmbiguousTimeError:
            count += 1
            is_dst = count in [1, 2]
            if count == 4:
                count = 0
            dt = tz.localize(naive_dt, is_dst=is_dst)
        datetimes.append(dt)

    if meter.Readings_Or_Deliveries:
        integ = [float(r.Reading_Or_Total) for r in meter.Readings]
        values = movement_from_integ(integ)
    else:
        values = [float(r.Delivered_Or_Movement) for r in meter.Readings]
    return Dataset(datetimes, values, dsrc, unit=unit)
    
