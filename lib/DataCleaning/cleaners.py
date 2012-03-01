import logging, time
import numpy as np
import utils
"""
DataCleaning must handle consumption data and temperature data
These data sources should be treated differently as consumption should be cleaned based on the rate of consumption whilst temperature should be cleaned on absolute values
Also, consumption is currently expected to be provided as cumulative totals - this may change or may be specified with input data (i.e. 'type' information)
"""

class CleanerBase(object):

    def clean(self, sd_limit):
        self.logger.debug('cleaning process started')
        clean = self.raw.copy()
        ts = self.raw['timestamp']
        value = self.raw['value']
        while self._has_invalid_dates(ts):
            ok = self._valid_dates(ts)
            ts = ts[ok]
            value = value[ok]
        ts, value = self._trim_ends(ts, value)
        ts, value = self._remove_extremes(ts, value, sd_limit)
        clean['timestamp'] = ts
        clean['datetime'] = utils.datetime_from_timestamp(ts)
        clean['value'] = value
        clean['cleaned'] = {'sd_limit': sd_limit}
            
        return clean


    def _has_invalid_dates(self, dates):
        gap = np.diff(dates)
        return any(gap<=0)

    def _valid_dates(self, dates):
        """remove duplicate dates and oddness"""
        self.logger.debug('preparing data for cleaning')
        gap = np.diff(dates)
        ok = np.append(True, (gap>0))
        return ok


    def _trim_ends(self, date, value):
        """
        Uses date array to identify big gaps.
        Value field is trimmed to match.
        """
        if len(date) == 0: raise NoDataError("Can't trim ends from an empty dataset")
        n = 0
        big_gap = 60*60*24*7
        for i in range(0, len(date)-1):
            gap = date[i+1] - date[i]
            if gap < big_gap: break
            else:
                n += 1
                logging.debug("gap->: %s [hr]" % (gap / (60*60)))
        start = i
        for j in range(len(date)-1):
            i = len(date)-1 - j
            gap = date[i] - date[i-1]
            if gap < big_gap:
                break
            else:
                n += 1
                logging.debug("<-gap: %s [hr]" % (gap / (60*60)))
        end = i+1
        if n > 0:
            logging.debug("%s points removed from ends ( so [0:%s] became [%s:%s])" % (n, len(date)-1, start, end))
        else:
            logging.debug("No points removed from ends")
        return date[start:end], value[start:end]

    def _remove_extremes(self, date, integ, sd_limit):
        self.logger.debug('removing extremes')
        nremoved, new_date, new_integ = self._filter(date, integ, sd_limit)
        total_removed = nremoved
        self.logger.debug('-->%i readings removed' % nremoved)
        while nremoved > 0:
            nremoved, new_date, new_integ = self._filter(new_date, new_integ, sd_limit)
            self.logger.debug('-->%i readings removed' % nremoved)
            total_removed += nremoved
        if total_removed > 0:
            self.logger.debug("%s extreme record(s) removed in total" % total_removed)
        else: self.logger.debug("No extreme records removed")
        return new_date, new_integ

    def _limits(self, data, sd_limit, allow_negs = False):
        mean = np.mean(data)
        std = np.std(data)
        limit = std * sd_limit
        result = [mean - limit, mean + limit]
        if not allow_negs: result[0] = max(0, result[0])
        return result

class ConsumptionCleaner(CleanerBase):
    def __init__(self, data):
        self.raw = data
#        self.type = data['type']
#        self.raw_ts = data['timestamp']
#        self.raw_values = data['value']
        self.logger = logging.getLogger("DataCleaning:ConsumptionCleaner")
        
    def _filter(self, date, integ, sd_limit):
        r = self._rate(date, integ)
        lower_limit, upper_limit = self._limits(r, sd_limit)
        keep, remove = (r>=lower_limit) & (r<=upper_limit), (r<lower_limit) | (r>upper_limit)
        filtered = any(remove)
        nremoved = len(r[remove])
        keep, remove = np.append(True, keep), np.append(True, remove)    #add one element to the beginning to keep the first integ and date values intact
        filtered_date = date[keep]
        movement = utils.movement_from_integ(integ)
        filtered_integ = utils.integ_from_movement(movement[keep])
        return nremoved, filtered_date, filtered_integ

    def _rate(self, date, integ):
        gap = np.diff(date)
        if any(gap<0): raise negativeGapError
        if any(gap==0): 
            a = (gap==0)
            raise zeroGapError, "Cannot determine rate for a zero length gap %s" % [time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(d)) for d in date[a]]
        movement = np.diff(integ)
        return movement/gap

class TemperatureCleaner(CleanerBase):
    def __init__(self, data):
        self.raw = data
#        self.type = data['type']
#        self.raw_ts = data['timestamp']
#        self.raw_values = data['value']
        self.logger = logging.getLogger("DataCleaning:TemperatureCleaner")
        
    def _filter(self, date, movement, sd_limit):
        lower_limit, upper_limit = self._limits(movement, sd_limit, allow_negs=True)
        keep, remove = (movement>=lower_limit) & (movement<=upper_limit), (movement<lower_limit) | (movement>upper_limit)
        filtered = any(remove)
        nremoved = len(movement[remove])
        filtered_date = date[keep]
        filtered_movement = movement[keep]
        return nremoved, filtered_date, filtered_movement
        




