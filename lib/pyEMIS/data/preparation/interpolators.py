import logging
import math
import numpy as np

from .. import utils

"""
DataCleaning must handle consumption data and temperature data
These data sources should be treated differently as consumption should be totalled whilst temperature should be averaged
"""

class Interpolator(object):
    def __init__(self):
        self.logger = logging.getLogger('pyEMIS:data:preparation:{0}'.format(self.__class__.__name__))

    def interpolate(self, data, resolution, do_integ):
        first = data['timestamp'].min()
        last = data['timestamp'].max()

        average_seconds_per_reading = (last - first) / len(data)
        if average_seconds_per_reading > (resolution * 2):
            self.logger.warning('Interpolating data with [%i] average seconds per reading to [%i] resolution' % (int(average_seconds_per_reading), int(resolution)))

        first = math.ceil(first / resolution) * resolution
        last = math.floor(last / resolution) * resolution
        ts = np.arange(first, last + 1, resolution)    #make sure the last one is included and no more

        original_val = data['value']

        #ignore nans?
        masked_val = np.ma.masked_array(original_val, np.isnan(original_val))
        masked_ts = np.ma.masked_array(data['timestamp'], np.isnan(original_val))

        if do_integ:
            masked_val = utils.integ_from_movement(masked_val)

#        val = np.interp(ts, data['timestamp'], original_val)
        val = np.interp(ts, masked_ts, masked_val)


        if do_integ:
            val = utils.movement_from_integ(val)

        limit = resolution * 2
        mymissing = np.zeros(len(val), dtype=np.bool)
        mygaps = self.gaps(data['timestamp'], limit)
        for g in mygaps:
            mymissing[(ts >= g['from']) & (ts <= g['to'])] = True

        dtype = np.dtype([('timestamp', np.float), ('value', np.float), ('missing', np.bool)])
        result = np.zeros(len(ts), dtype=dtype)
        result['timestamp'] = ts
        result['value'] = val
        result['missing'] = mymissing
        return result

#    def missing(self, data, limit):
#        return np.append(np.nan, np.diff(data['timestamp']) > limit)

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

class Interpolator_old(object):

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
        print(min_ts, max_ts)

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
