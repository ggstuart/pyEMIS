import logging
import time
import numpy as np
import utils
"""
DataCleaning must handle consumption data and temperature data
These data sources should be treated differently as consumption should be cleaned based on the rate of consumption whilst temperature should be cleaned on absolute values
Also, consumption is currently expected to be provided as cumulative totals - this may change or may be specified with input data (i.e. 'type' information)
"""

class CleanerBase(object):
    def __init__(self):
        self.logger = logging.getLogger('DataCleaning:{}'.format(self.__class__.__name__))

    def clean(self, data, sd_limit):
        """
        >>> from pyEMIS.DataAccess import adapters as ad
        >>> from pyEMIS.DataCleaning import cleaners as cl, utils
        >>> a = ad.Test()
        >>> c = cl.ConsumptionCleaner()
        >>> c #doctest: +ELLIPSIS
        <pyEMIS.DataCleaning.cleaners.ConsumptionCleaner object at 0x...>
        >>> valid = a.timeseries('valid')
        >>> len(valid['datetime'])
        17520
        >>> clean = c.clean(valid, 30)
        >>> len(clean['datetime'])
        17520
        >>> clean['datetime'] == valid['datetime']
        True
        """
        self.logger.debug('cleaning process started')
        clean = data.copy()
        ts = utils.timestamp_from_datetime(clean['datetime'])
        if ts.size == 0:
            raise NoDataError("Can't clean an empty dataset")
        value = clean['value']

        while self._has_invalid_dates(ts):
            self.logger.debug('corrupt dates')
            ok = self._valid_dates(ts)
            ts = ts[ok]
            value = value[ok]

        ts, value = self._trimmed_ends(ts, value)

        if clean['type'] == 'movement':
            self.logger.debug('converting to integ')
            value = utils.integ_from_movement(value)

        ts, value = self._remove_extremes(ts, value, sd_limit)

        if clean['type'] == 'movement':
            self.logger.debug('converting back to movement')
            value = utils.movement_from_integ(value)

        clean['timestamp'] = ts
        clean['datetime'] = utils.datetime_from_timestamp(ts)
        clean['value'] = value
        clean['cleaned'] = {'sd_limit': sd_limit}            
        return clean

    @staticmethod
    def _trimmed_ends(timestamps, values, big_gap = 60*60*24*7):
        """
        Uses timestamps array to identify and trim big gaps.
        The values array is trimmed to match.
        >>> from pyEMIS.DataAccess import adapters as ad
        >>> from pyEMIS.DataCleaning import cleaners as cl, utils
        >>> a = ad.Test()
        >>> c = cl.ConsumptionCleaner()
        >>> valid = a.timeseries('valid')
        >>> ts, val = utils.timestamp_from_datetime(valid['datetime']), valid['value']
        >>> trimmed_ts, trimmed_val = c._trimmed_ends(ts, val)
        >>> len(trimmed_ts)
        17520
        >>> trim_front = a.timeseries('trim_front')
        >>> ts, val = utils.timestamp_from_datetime(trim_front['datetime']), trim_front['value']
        >>> trimmed_ts, trimmed_val = c._trimmed_ends(ts, val)
        >>> len(trimmed_ts)
        17519
        >>> trim_end = a.timeseries('trim_end')
        >>> ts, val = utils.timestamp_from_datetime(trim_end['datetime']), trim_end['value']
        >>> trimmed_ts, trimmed_val = c._trimmed_ends(ts, val)
        >>> len(trimmed_ts)
        17519
        >>> trim_both = a.timeseries('trim_both')
        >>> ts, val = utils.timestamp_from_datetime(trim_both['datetime']), trim_both['value']
        >>> trimmed_ts, trimmed_val = c._trimmed_ends(ts, val)
        >>> len(trimmed_ts)
        17518
        """
        big_gaps = np.diff(timestamps) >= big_gap
        front_gaps = np.logical_and.accumulate(np.append(big_gaps, False))
        end_gaps = np.logical_and.accumulate(np.append(False, big_gaps)[::-1])[::-1]
        big_gaps = np.logical_or(front_gaps, end_gaps)
        n = np.sum(front_gaps), np.sum(end_gaps)
        keep = np.logical_not(big_gaps)
        if sum(n) > 0:
            logging.debug("%i points trimmed (%i from beginning, %i from end)" % (sum(n), n[0], n[1]))
        else:
            logging.debug("No points trimmed")
        return timestamps[keep], values[keep]

    @staticmethod
    def _has_invalid_dates(timestamps):
        """Check for out of order or repeated dates"""
        gap = np.diff(timestamps)
        return any(gap<=0)

    @staticmethod
    def _valid_dates(timestamps):
        """remove indices for duplicate and out of order dates"""
        gap = np.diff(timestamps)
        return np.append(True, (gap>0))


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
    """
    The ConsumptionCleaner class filters extreme data based on variations in the rate of consumption
    >>> from pyEMIS.DataCleaning import ConsumptionCleaner as CC
    >>> from pyEMIS.DataAccess import DataAccessLayer as DAL, adapters
    >>> dal = DAL(adapters.Test)
    >>> data = dal.adapter.timeseries('basic data')
    >>> cc = CC()
    >>> cc #doctest: +ELLIPSIS
    <pyEMIS.DataCleaning.cleaners.ConsumptionCleaner object at ...>
    >>>
    """
        
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
        
    def _filter(self, date, movement, sd_limit):
        lower_limit, upper_limit = self._limits(movement, sd_limit, allow_negs=True)
        keep, remove = (movement>=lower_limit) & (movement<=upper_limit), (movement<lower_limit) | (movement>upper_limit)
        filtered = any(remove)
        nremoved = len(movement[remove])
        filtered_date = date[keep]
        filtered_movement = movement[keep]
        return nremoved, filtered_date, filtered_movement

if __name__ == "__main__":
    import logging
    import doctest
    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod()
