import numpy as np
import math, utils, logging

logger = logging.getLogger('DataCleaning:interpolation')

def interpolate_old(date, integ, movement, resolution):
    logger.warning("deprecated method")
    first, last = math.ceil(min(date)/resolution)*resolution, math.floor(max(date)/resolution)*resolution
    new_date = np.arange(first, last, resolution)
    new_integ = np.interp(new_date, date, integ)
    new_movement = utils.movement_from_integ(new_integ)
    return new_date, new_integ, new_movement

def interpolate_old2(ts, value, resolution, missing=False, limit=None):
    logger.warning("deprecated method")
    first, last = math.ceil(min(ts)/resolution)*resolution, math.floor(max(ts)/resolution)*resolution
    new_ts = np.arange(first, last, resolution)
    new_value = np.interp(new_ts, ts, value)
    if missing:
        if limit == None: limit = resolution*2
        mymissing = np.array([False]*len(new_ts), dtype=bool)
        mygaps = gaps(ts, limit)
        for g in mygaps:
            logger.debug("Flagging gap %s as missing" % g)
            a = (new_ts >= g['from']) & (new_ts <=g['to'])
            mymissing[a] = True
        return new_ts, new_value, mymissing, mygaps
    return new_ts, new_value

def interpolate(ts, value, resolution, missing=False, limit=None):
    logger.info("*****Interpolating some data*****")
    first, last = math.ceil(min(ts)/resolution)*resolution, math.floor(max(ts)/resolution)*resolution
    new_ts = np.arange(first, last, resolution)
    new_value = np.interp(new_ts, ts, value)
    if missing:
        if limit == None: limit = resolution*2
        mymissing = np.array([False]*len(new_ts), dtype=bool)
        mygaps = gaps(ts, limit)
        for g in mygaps:
            logger.debug("Flagging gap %s as missing" % g)
            a = (new_ts >= g['from']) & (new_ts <=g['to'])
            mymissing[a] = True
        return new_ts, new_value, mymissing, mygaps
    return new_ts, new_value

def gaps(ts, limit):
    """
    For a given array of timestamps and a given size limit
    returns a list of gaps between timestamps which are greater than the limit
    Contiguous gaps are merged
    """
    seconds = np.diff(ts)   #   n - 1
    logger.debug(seconds)
    over_limit = seconds > limit
    _gap = {'from': None, 'to': None}
    result = []
    for i in xrange(len(seconds)):
        if not over_limit[i]:   #No gap, close off the current gap if it exists
            if _gap['to'] != None:   #If a current gap exists
                logger.debug('Saving the current gap and resetting')
                result.append(_gap)
                _gap = {'from': None, 'to': None}
        else:   #We have a gap, either append it to current or start a new one
            if _gap['to'] != None:   #If a current gap exists
                if _gap['to'] == ts[i]:  #if the 'current' gap can be appended directly
                    logger.debug("Extend the current gap")
                    _gap['to'] = ts[i+1] #then extend the 'current' gap
                    logger.debug(_gap)
                else: #if not then something is going wrong
                    logger.warning("New gap doesn't append to 'current' gap")
                    result.append(_gap)
                    _gap = {'from': None, 'to': None}
            else:   #if no 'current' gap exists then start one
                logger.debug("starting a new gap")
                _gap['from'] = ts[i] #just get the next data
                _gap['to'] = ts[i+1] #and loop round to next i
                logger.debug(_gap)
    if _gap['to'] != None:   #If a current gap exists at the end it needs to be saved
        logger.debug('Saving the current gap and resetting')
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
        else: logger.error("This shouldn't happen")
    return result        

if __name__ == '__main__':
    from matplotlib import pyplot as plt
    logging.basicConfig(level=logging.INFO)
    ts = []
    ts.extend(range(0  , 100, 10))
    ts.extend(range(101, 200, 5))
    ts.extend(range(201, 300, 2))
    ts.extend(range(301, 400, 8))
    ts.extend(range(401, 500, 5))
    v = np.cumsum(np.random.rand(len(ts)))
    ts2, v2, m, gaps = interpolate2(ts, v, 3, missing=True, limit=10)
    plt.figure()
    for g in gaps:
        plt.axvspan(g['from'], g['to'], alpha=0.25, color='black')
    plt.plot(ts, v, 'o--', color='blue', alpha = 0.5)
    plt.plot(ts2, v2, 'x-', color='red')
    plt.plot(ts2[m], v2[m], '+', color='black')
    plt.show()
