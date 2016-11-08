import logging
import time

import numpy as np

from .. import utils

"""
DataCleaning must handle consumption data and temperature data
These data sources should be treated differently as consumption should be cleaned based on the rate of consumption whilst temperature should be cleaned on absolute values
Also, consumption is currently expected to be provided as cumulative totals - this may change or may be specified with input data (i.e. 'type' information)
"""

def cleaner(commodity):
    if commodity in ['temperature']:
        return TemperatureCleaner()
    else:
        return ConsumptionCleaner()


class CleanerBase(object):
    def __init__(self):
        self.logger = logging.getLogger('DataCleaning:{0}'.format(self.__class__.__name__))

    def clean(self, data, sd_limit):
        """
        The ConsumptionCleaner class filters extreme data based on variations in the rate of consumption
        >>> from pyEMIS.DataAccess import adapters
        >>> from pyEMIS.DataCleaning import cleaners
        >>> import numpy as np
        >>> test = adapters.Test()
        >>> cleaner = cleaners.ConsumptionCleaner()
        >>> cleaner #doctest: +ELLIPSIS
        <pyEMIS.DataCleaning.cleaners.ConsumptionCleaner object at 0x...>
        >>> valid = test.timeseries('valid')
        >>> clean = cleaner.clean(valid, 30)
        >>> clean['datetime'] == valid['datetime']
        True
        >>> np.testing.assert_array_almost_equal(clean['value'][1:], valid['value'][1:])
        """
        self.logger.debug('cleaning process started')
        clean = data.copy()
        ts = clean['timestamp']
        if ts.size == 0:
            raise NoDataError("Can't clean an empty dataset")
        value = clean['value']

        ts, value = self._remove_invalid_dates(ts, value)
        ts, value = self._trimmed_ends(ts, value)
        integ = utils.integ_from_movement(value)
        ts, integ = self._remove_extremes(ts, integ, sd_limit)
        value = utils.movement_from_integ(integ)

        clean = np.empty(len(ts), dtype=clean.dtype)
        clean['timestamp'] = ts
        clean['value'] = value
        return clean

    #Is this going to do anything when the data are sorted on date?
    def _remove_invalid_dates(self, timestamps, values):
        c = 0
        while True:
            gaps = np.diff(timestamps)
            if all(gaps > 0):
                if c:
                    self.logger.debug('Algorithm iterated %i times' % c)
                return timestamps, values
            if not c: self.logger.debug('Trying to fix corrupt dates')
            #This only works if the bad date is before it should be
            ok = np.append(True, gaps > 0)
            #The alternative is this
            #ok = np.append(gaps > 0, True)
            #Some logic to work out which is best?
            #Treat each problem individually, case by case?
            c += 1
            timestamps = timestamps[ok]
            values = values[ok]

    def _trimmed_ends(self, timestamps, values, big_gap = 60*60*24*7):
        """
        Uses timestamps array to identify and trim big gaps.
        The values array is trimmed to match.
        >>> from pyEMIS.DataAccess import adapters
        >>> from pyEMIS.DataCleaning import cleaners, utils
        >>> test = adapters.Test()
        >>> cleaner = cleaners.ConsumptionCleaner()
        >>> def clean_len(name):
        ...     data = test.timeseries(name)
        ...     ts, val = utils.timestamp_from_datetime(data['datetime']), data['value']
        ...     trimmed_ts, trimmed_val = cleaner._trimmed_ends(ts, val)
        ...     return len(trimmed_ts)
        ...
        >>> clean_len('valid')
        17520
        >>> clean_len('trim_front')
        17519
        >>> clean_len('trim_end')
        17519
        >>> clean_len('trim_both')
        17518
        >>> clean_len('trim_front2')
        17518
        >>> clean_len('trim_end2')
        17518
        """
        big_gaps = np.diff(timestamps) >= big_gap
        front_gaps = np.logical_and.accumulate(np.append(big_gaps, False))
        end_gaps = np.logical_and.accumulate(np.append(False, big_gaps)[::-1])[::-1]
        big_gaps = np.logical_or(front_gaps, end_gaps)
        n = np.sum(front_gaps), np.sum(end_gaps)
        keep = np.logical_not(big_gaps)
        if sum(n) > 0:
            self.logger.debug("%i points trimmed (%i from beginning, %i from end)" % (sum(n), n[0], n[1]))
        else:
            self.logger.debug("No points trimmed")
        return timestamps[keep], values[keep]

    def _remove_extremes(self, date, integ, sd_limit):
        self.logger.debug('Checking for extreme values')
        nremoved, new_date, new_integ = self._filter(date, integ, sd_limit)
        if nremoved > 0:
            self.logger.debug('-->%i readings removed' % nremoved)
        total_removed = nremoved
        while nremoved > 0:
            nremoved, new_date, new_integ = self._filter(new_date, new_integ, sd_limit)
            if nremoved > 0:
                self.logger.debug('-->%i readings removed' % nremoved)
            total_removed += nremoved
        if total_removed > 0:
            self.logger.debug("%s extreme record(s) removed in total" % total_removed)
        else: self.logger.debug("No extreme records removed")
        return new_date, new_integ

    @staticmethod
    def _limits(data, sd_limit, allow_negs = False):
        mean = np.mean(data)
        std = np.std(data)
        limit = std * sd_limit
        result = [mean - limit, mean + limit]
        if not allow_negs: result[0] = max(0, result[0])
        return result

class ConsumptionCleaner(CleanerBase):
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

    @staticmethod
    def _rate(date, integ):
        gap = np.diff(date)
        if any(gap<0): raise negativeGapError
        if any(gap==0):
            a = (gap==0)
            raise zeroGapError("Cannot determine rate for a zero length gap %s" % [time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(d)) for d in date[a]])
        movement = np.diff(integ)
        return movement/gap

class TemperatureCleaner(CleanerBase):

    def _filter(self, date, movement, sd_limit):
        lower_limit, upper_limit = self._limits(movement, sd_limit, allow_negs=True)
        keep, remove = (movement>=lower_limit) & (movement<=upper_limit), (movement<lower_limit) | (movement>upper_limit)
        filtered = any(remove)
        nremoved = len(movement[remove])
        filtered_date = date[keep]
        filtered_movement = movement[keep]
        return nremoved, filtered_date, filtered_movement
