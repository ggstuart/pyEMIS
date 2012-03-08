import logging
import datetime
import time
from itertools import izip
import numpy as np


def movement_from_integ(integ):
    return np.append(np.nan, np.diff(integ))

def integ_from_movement(movement):
    return np.append(0.0, np.cumsum(movement[1:]))

def timestamp_from_datetime(dt):
    return np.array([time.mktime(d.timetuple()) for d in dt])

def datetime_from_timestamp(ts):
    return [datetime.datetime.fromtimestamp(s) for s in ts]

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
