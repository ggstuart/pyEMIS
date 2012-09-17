from pyEMIS.data.unit import BaseUnit
from pyEMIS.data.dataset import Dataset
from pyEMIS.data.config import ConfigurationFileError
from source import File

class BritishGasError(Exception): pass

class Adapter(object):

    def __init__(self, config):
        try:
            filename = config.filename
        except ConfigurationFileError, e:
            raise BritishGasError, "Specify the filename for British Gas data, add the option 'filename = ...' under the section [%s] in config file [%s]" % (config.section, e.filename)
        self.file = File(filename)

    def dataset(self, dataset_id):
        ds = self.file.dataset(dataset_id)
        return convert_dataset(ds)

    def dataset_ids(self):
        for n in self.file.datasets.keys():
            yield n

def convert_dataset(dataset):
    """Convert a British Gas dataset into a pyEMIS dataset"""
    kWh = BaseUnit('kiloWatt hour', 'kWh')
    dts = []
    vals = []
    label = "British Gas [%03i]" % dataset.dataset_id
    return Dataset(dataset.data['datetimes'], dataset.data['values'], label, kWh, 'energy')
