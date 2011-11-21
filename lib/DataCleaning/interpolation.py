import numpy as np
import math, utils, logging

def interpolate(date, integ, movement, resolution):
    first, last = math.ceil(min(date)/resolution)*resolution, math.floor(max(date)/resolution)*resolution
    new_date = np.arange(first, last, resolution)
    new_integ = np.interp(new_date, date, integ)
    new_movement = utils.movement_from_integ(new_integ)
    return new_date, new_integ, new_movement

def interpolate2(ts, value, resolution, missing=False, limit=None):
    first, last = math.ceil(min(ts)/resolution)*resolution, math.floor(max(ts)/resolution)*resolution
    new_ts = np.arange(first, last, resolution)
    new_value = np.interp(new_ts, ts, value)
    if missing:
        if limit == None: limit = resolution*2
        mymissing = np.array([False]*len(new_ts), dtype=bool)
        mygaps = gaps(ts, limit)
        for g in mygaps:
            logging.info(g)
            a = (new_ts >= g['from']) & (new_ts <=g['to'])
            mymissing[a] = True
        return new_ts, new_value, mymissing, mygaps
    return new_ts, new_value

def hh(date, integ, movement):
    return interpolate(date, integ, movement, resolution=60*30)

def daily(date, integ, movement):
    return interpolate(date, integ, movement, resolution=60*60*24)

def weekly(date, integ, movement):
    return interpolate(date, integ, movement, resolution=60*60*24*7)


def gaps(ts, limit):
    """
    For a given array of timestamps and a given size limit
    returns a list of gaps between timestamps which are greater than the limit
    Contiguous gaps are merged
    """
    seconds = np.diff(ts)   #   n - 1
    logging.debug(seconds)
    over_limit = seconds > limit
    _gap = {'from': None, 'to': None}
    result = []
    for i in xrange(len(seconds)):
        if not over_limit[i]:   #No gap, close off the current gap if it exists
            if _gap['to'] != None:   #If a current gap exists
                logging.debug('Saving the current gap and resetting')
                result.append(_gap)
                _gap = {'from': None, 'to': None}
        else:   #We have a gap, either append it to current or start a new one
            if _gap['to'] != None:   #If a current gap exists
                if _gap['to'] == ts[i]:  #if the 'current' gap can be appended directly
                    logging.debug("Extend the current gap")
                    _gap['to'] = ts[i+1] #then extend the 'current' gap
                    logging.debug(_gap)
                else: #if not then something is going wrong
                    logging.warning("New gap doesn't append to 'current' gap")
                    result.append(_gap)
                    _gap = {'from': None, 'to': None}
            else:   #if no 'current' gap exists then start one
                logging.debug("starting a new gap")
                _gap['from'] = ts[i] #just get the next data
                _gap['to'] = ts[i+1] #and loop round to next i
                logging.debug(_gap)
    if _gap['to'] != None:   #If a current gap exists at the end it needs to be saved
        logging.debug('Saving the current gap and resetting')
        result.append(_gap)
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
