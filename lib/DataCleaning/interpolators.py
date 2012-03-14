import logging
import math
import numpy as np
import utils

"""
DataCleaning must handle consumption data and temperature data
These data sources should be treated differently as consumption should be totalled whilst temperature should be averaged
"""

class Interpolator(object):

    def __init__(self, data):
        self.raw = data
        self.logger = logging.getLogger('DataCleaning:Interpolator')

    def interpolate(self, resolution, missing=False, limit=None):
        self.logger.debug('Interpolating some data')
        result = self.raw.copy()
        first, last = math.ceil(min(self.raw['timestamp'])/resolution)*resolution, math.floor(max(self.raw['timestamp'])/resolution)*resolution
        self.logger.debug("from %s to %s" % tuple(utils.datetime_from_timestamp([first, last])))
        result['timestamp'] = np.arange(first, last, resolution)
        result['value'] = np.interp(result['timestamp'], self.raw['timestamp'], self.raw['value'])
        result['datetime'] = utils.datetime_from_timestamp(result['timestamp'])
        if missing:
            if limit == None: limit = resolution*2
            mymissing = np.array([False]*len(result['timestamp']), dtype=bool)
            mygaps = self.gaps(self.raw['timestamp'], limit)
            for g in mygaps:
                self.logger.debug("Flagging gap %s as missing" % g)
                a = (result['timestamp'] >= g['from']) & (result['timestamp'] <= g['to'])
                mymissing[a] = True
            result['missing'] = mymissing
            result['gaps'] = mygaps
        result['interpolated'] = {'resolution': resolution, 'missing': missing, 'limit': limit}
        return result

    def gaps(self, ts, limit):
        """
        For a given array of timestamps and a given size limit
        returns a list of gaps between timestamps which are greater than the limit
        Contiguous gaps are merged
        """
        seconds = np.diff(ts)   #   n - 1
        over_limit = seconds > limit
        _gap = {'from': None, 'to': None}
        result = []
        for i in xrange(len(seconds)):
            if not over_limit[i]:   #No gap, close off the current gap if it exists
                if _gap['to'] != None:   #If a current gap exists
                    self.logger.debug('Saving the current gap and resetting')
                    result.append(_gap)
                    _gap = {'from': None, 'to': None}
            else:   #We have a gap, either append it to current or start a new one
                if _gap['to'] != None:   #If a current gap exists
                    if _gap['to'] == ts[i]:  #if the 'current' gap can be appended directly
                        self.logger.debug("Extend the current gap")
                        _gap['to'] = ts[i+1] #then extend the 'current' gap
                        self.logger.debug(_gap)
                    else: #if not then something is going wrong
                        self.logger.warning("New gap doesn't append to 'current' gap")
                        result.append(_gap)
                        _gap = {'from': None, 'to': None}
                else:   #if no 'current' gap exists then start one
                    self.logger.debug("starting a new gap")
                    _gap['from'] = ts[i] #just get the next data
                    _gap['to'] = ts[i+1] #and loop round to next i
                    self.logger.debug(_gap)
        if _gap['to'] != None:   #If a current gap exists at the end it needs to be saved
            self.logger.debug('Saving the current gap and resetting')
            result.append(_gap)
        return result

    def merge_gaps(gaps1, gaps2):
        """Given two lists of gaps, generates a single list with no overlaps."""
        min_ts = min([g['from'] for g in gaps1.extend(gaps2)])
        max_ts = max([g['to'] for g in gaps1.extend(gaps2)])
        print min_ts, max_ts   

    def trim_gaps(gaps, _from, _to):
        """Trim the list of gaps so it only refers to the period between _from and _to"""
        result = []
        for gap in gaps:
            if (gap['from'] >= _from) & (gap['to'] <= _to): result.append(gap)
            elif gap['from'] < _from: result.append({'from': _from, 'to': gap['to']})
            elif gap['to'] > _to: result.append({'from': _from, 'to': gap['to']})
            elif (gap['to'] > _to) & (gap['from'] < _from): result.append({'from': _from, 'to': _to})
            else: self.logger.error("This shouldn't happen")
        return result        
