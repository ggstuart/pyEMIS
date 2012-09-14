from pyEMIS.data.adapters.sustainable_advantage import File
from pyEMIS.data.unit import BaseUnit
from pyEMIS.data.dataset import Dataset
from pyEMIS.data.config import ConfigurationFileError

class SustainableAdvantageError(Exception): pass

class Adapter(object):

    #TODO this constructor breaks the requirement for a common API, 
    #consider a set_file method or similar for all adapters
    def __init__(self, config):
        try:
            filename = config.filename
        except ConfigurationFileError, e:
            raise SustainableAdvantageError, "Specify the filename for sustainable advantage data, add the option 'filename = ...' under the section [%s] in config file [%s]" % (config.section, e.filename)
        self.file = File(filename)

    def dataset(self, sheet_name):
        ds = self.file.dataset(sheet_name)
        return convert_dataset(ds)

    def dataset_ids(self):
        for n in self.file.dataset_names():
            yield n

def convert_dataset(dataset):
    """Convert a Sustainable Advantage dataset into a pyEMIS dataset"""
    kWh = BaseUnit('kiloWatt hour', 'kWh')
    dts = []
    vals = []
    label = dataset.name
    for dt, val in dataset.readings():
        dts.append(dt)
        vals.append(val)
    return Dataset(dts, vals, label, kWh, 'energy')
