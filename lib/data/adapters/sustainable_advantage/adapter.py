from pyEMIS.data.adapters.sustainable_advantage import File
from pyEMIS.data.unit import BaseUnit
from pyEMIS.data.dataset import Dataset

class Adapter(object):

    #TODO this constructor breaks the requirement for a common API, 
    #consider a set_file method or similar for all adapters
    def __init__(self, filename):
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
    for dt, val in dataset.readings():
        dts.append(dt)
        vals.append(val)
    return Dataset(dts, vals, kWh, 'energy')
