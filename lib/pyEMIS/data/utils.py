import logging
import datetime
import time

from dateutil.tz import tzutc
import numpy as np

utc = tzutc()
#class tzuk(datetime.tzinfo):
#    def utcoffset(self, dt):
#        return self.dst(dt)
#
#    def dst(self, dt):
#        return datetime.timedelta(hours=0)
#        if dt.month in [4,5,6,7,8,9]:
#            return datetime.timedelta(hours=-1)
#        elif dt.month in [1,2,11,12]:
#            return datetime.timedelta(hours=0)
#        elif dt.month == 3:
#            if (dt + datetime.timedelta(days=7)).month != 4:
#                return datetime.timedelta(hours=0)
#            else:
#                #we are within a week of April
#        elif dt.month == 10:
#            if (dt + datetime.timedelta(days=7)).month != 11:
#                return datetime.timedelta(hours=-1)
#            else:
#                #we are within a week of November
#
#tz = tzuk()

def movement_from_integ(integ):
#    return np.append(np.nan, np.ma.diff(integ))
#    return np.ma.concatenate([[np.nan], np.ma.diff(integ)])
    return np.ma.concatenate([[np.nan], np.ma.ediff1d(integ)])

def integ_from_movement(movement):
    #the first integ value is always zero
    #We always lose the first movement value anyway
    movement[0] = 0
    result = np.ma.cumsum(movement)
    return result
#    #handle lists, np.arrays and np.ma.masked_arrays
#    has_mask = hasattr(movement, 'mask')
#    if not has_mask or (has_mask and not movement.mask[0]):
#        result -= movement[0]
##    elif has_mask:
##        result -= movement.data[0]
#    return result
##    return np.append(0.0, np.cumsum(movement[1:]))

def timestamp_from_datetime(dt):
    try:
        return [time.mktime(d.timetuple()) for d in dt]
    except TypeError:
        return time.mktime(dt.timetuple())

def datetime_from_timestamp(ts):
    try:
        return [datetime.datetime.fromtimestamp(s, utc) for s in ts]
    except TypeError:
        return datetime.datetime.fromtimestamp(ts, utc)

def gaps_from_flags(flags, timestamps):
    logger = logging.getLogger('gaps_from_flags')
    res = []
    for k, g in itertools.groupby(zip(flags, timestamps), lambda x: x[0]):
        time_stamps = list(g)
        res.append({'from': time_stamps[0], 'to': time_stamps[-1]})

def flags_from_gaps(gaps, ts):
    """given gaps and timestamps produces an array of boolean values indicating whether data are missing at each timestamp"""
#    flags = np.array([False]*len(ts), dtype=bool)
    flags = np.zeros(len(ts), dtype=bool)
    for g in gaps:
        a = (ts >= g['from']) & (ts <=g['to'])
        flags[a] = True
    return flags

#def add_field(a, descr):
#    """Return a new array that is like "a", but has additional fields.

#    Arguments:
#      a     -- a structured numpy array
#      descr -- a numpy type description of the new fields

#    The contents of "a" are copied over to the appropriate fields in
#    the new array, whereas the new fields are uninitialized.  The
#    arguments are not modified.

#    >>> sa = numpy.array([(1, 'Foo'), (2, 'Bar')], \
#                         dtype=[('id', int), ('name', 'S3')])
#    >>> sa.dtype.descr == numpy.dtype([('id', int), ('name', 'S3')])
#    True
#    >>> sb = add_field(sa, [('score', float)])
#    >>> sb.dtype.descr == numpy.dtype([('id', int), ('name', 'S3'), \
#                                       ('score', float)])
#    True
#    >>> numpy.all(sa['id'] == sb['id'])
#    True
#    >>> numpy.all(sa['name'] == sb['name'])
#    True
#    """
#    if a.dtype.fields is None:
#        raise ValueError, "'A' must be a structured numpy array"
#    b = np.empty(a.shape, dtype=a.dtype.descr + descr)
#    for name in a.dtype.names:
#        b[name] = a[name]
#    return b
