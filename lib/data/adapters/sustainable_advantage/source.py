'''
Created on 23 May 2012

@author: gstuart

This is a data source module for accessing data
It handles files in the format first provided by Neil Bland on 22/05/2012
'''
import logging
import os.path
from xlrd import open_workbook, xldate_as_tuple
from datetime import datetime
from pytz import timezone, AmbiguousTimeError

#utc = timezone('UTC')
london = timezone('Europe/London')

class SustainableAdvantageError(Exception): pass

class Dataset(object):
    def __init__(self, sheet, tz):
        self.tz = tz
        self.sheet = sheet
        self.id = sheet.name
        self.name = self.sheet.cell(1,0).value
        self.logger = logging.getLogger("Dataset('%s')" % self.id)
        self.logger.info('Created')

    def readings(self):
        previous = None
        count = 0
        for row in range(1, self.sheet.nrows):
            if self.sheet.cell(row, 0).value != self.name:
                raise SustainableAdvantageError, 'Unexpected value [%s instead of %s] in site name column [row %s]' % (self.sheet.cell(row, 0).value, self.site_name, row)
            date_value = xldate_as_tuple(self.sheet.cell(row, 1).value, self.sheet.book.datemode)
            naive_dt = datetime(*date_value)
            try:
                dt = self.tz.localize(naive_dt, is_dst=None)
            except AmbiguousTimeError:
                count += 1
                is_dst = count in [1, 2]
                if count == 4:
                    count = 0
                dt = self.tz.localize(naive_dt, is_dst=is_dst)
                
                
            if previous:
                if dt < previous:
                    raise SustainableAdvantageError, 'Cannot process file. Records are not in proper date order [row %i].' % row
                elif dt == previous:
                    raise SustainableAdvantageError, 'Cannot process file. Repeated date [row %i: %s].' % (row, dt.strftime('%d/%m/%Y %H:%M:%S'))
            val = self.sheet.cell(row, 2).value
            if dt:
#                yield dt.astimezone(utc), val
                if val:
                    yield dt, val
                else:
                    yield dt, None
                previous = dt


class File(object):
    def __init__(self, path, tz=london):
        self.logger = logging.getLogger("File(%s)" % os.path.basename(path))
        self.logger.info('Opening')
        self.tz = tz
        self.book = open_workbook(path)

    def dataset_names(self):
        for s in self.book.sheets():
            yield s.name

    def datasets(self):
        for s in self.book.sheets():
            yield Dataset(s)
            
    def dataset(self, sheet_name):
        return Dataset(self.book.sheet_by_name(sheet_name), self.tz)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info('Started')
    import os.path
    from matplotlib import pyplot as plt
    
    def plot(dataset, root):
        lbl = "%s (%s)" % (dataset.name, dataset.id)
        logging.info(lbl)
        data = list(dataset.readings())
        dt = [rec['datetime'] for rec in data]
        v = [rec['value'] for rec in data]
        plt.Figure()
        plt.suptitle(lbl)
        plt.plot(dt, v)
        outfile = os.path.join(root, "output", "%03i.png" % i)
        plt.savefig(outfile)
        plt.close()


    root = "E:\Work\Projects\SustainableAdvantage"
#    fname = os.path.join(root, "first files", "Site 5.xls")
    fname = os.path.join(root, "data", "first files", "HH data oct10_nov11.xls")
    f = File(fname)
    for i, d in enumerate(f.datasets()):
        logging.info("dataset %i" % i)
        plot(d, root)
    logging.info('Finished')
