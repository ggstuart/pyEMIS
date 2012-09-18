'''
Created on 17 September 2012

@author: gstuart

This is a data source module for accessing data
It handles files in the format first provided by Jimmy Dean from British Gas
'''
import logging
import os.path
import csv
from datetime import datetime, timedelta
#from pytz import timezone, AmbiguousTimeError

#london = timezone('Europe/London')

class BritishGasError(Exception): pass

class Dataset(object):
    def __init__(self, dataset_id, data):
        self.logger = logging.getLogger("Dataset(%s)" % dataset_id)
        self.data = data
        self.dataset_id = dataset_id
        self.logger.info('Ready')

class File(object):
    """Represents a data file"""
    def __init__(self, path):#, tz=london):
        self.path = path
        self.logger = logging.getLogger("File(%s)" % os.path.basename(path))
        self.logger.info('Opening')
        self.datasets = {}
        prev = None
        with open(self.path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dataset_id = row['Ref']
                if not dataset_id in self.datasets.keys():
                    self.datasets[dataset_id] = None

    def dataset(self, dataset_id):
        if dataset_id not in self.datasets.keys():
            raise BritishGasError, "Dataset [%s] not recognised" % dataset_id
        dts = []
        values = []
        with open(self.path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Ref'] != dataset_id:
                    continue
                date = datetime.strptime(row['ReadingDate'], "%d/%m/%Y")
                dt = [date + timedelta(minutes=30*i) for i in range(1, 49)] #the last column is headed midnight, wierdly
                dts.extend(dt)
                values.extend([float(row[d.strftime("KWh%H%M")]) for d in dt])
        return Dataset(dataset_id, {'values': values, 'datetimes': dts})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info('Started')
    import os.path
    from matplotlib import pyplot as plt
    
    def plot(dataset):
        logging.info(dataset.dataset_id)
        dt = dataset.data['datetimes']
        v = dataset.data['values']
        plt.figure()
        plt.suptitle(dataset.dataset_id)
        plt.plot(dt, v)
        plt.show()

    fname = "E:\Work\Projects\pyEMIS\scripts\data\British_Gas.csv"
    f = File(fname)
    ds = f.dataset(f.datasets.keys()[0])
    plot(ds)
    logging.info('Finished')
