import numpy as np

class AnalysisBase(object):
    def __init__(self, dataset, drivers=None):
        self.dataset = dataset
        if not drivers:
            drivers = []
        self.drivers = drivers
        
    def data(self, resolution, sd_limit=None):
        original_data = {}
        for dataset in self.drivers + [self.dataset]:
            mydata = dataset.data(resolution=resolution, sd_limit=sd_limit)
            original_data[dataset.label] = {
                'data': mydata,
                'min_date': min(mydata['timestamp']),
                'max_date': max(mydata['timestamp'])
            }
        #determine the range
        _from = max([original_data[label]['min_date'] for label in original_data.keys()])
        _to = min([original_data[label]['max_date'] for label in original_data.keys()])

        #construct the result
        result = {}
        for label in original_data.keys():
            #get indices for overlapping data
            a = (original_data[label]['data']['timestamp'] >= _from) & (original_data[label]['data']['timestamp'] <= _to)
            if not result.has_key('timestamp'):
                result['timestamp'] = original_data[label]['data']['timestamp'][a]
            result[label] = original_data[label]['data']['value'][a]
            if 'missing' in original_data[label]['data'].dtype.names:
                try:
                    missing = missing | original_data[label]['data']['missing'][a]
                except NameError:
                    missing = original_data[label]['data']['missing'][a]

        #convert to output
        dtype = [(str(lbl), np.float) for lbl in result.keys()] + [('missing', np.bool)]
        dt = np.dtype(dtype)
        size = len(result['timestamp'])
        result = np.ma.array([tuple([result[lbl][i+1] for lbl in result.keys()] + [missing[i+1]]) for i in xrange(size-1)], dtype = dt)
        return result
