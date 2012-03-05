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

def gaps_from_flags(flags, ts):
    logger = logging.getLogger('gaps_from_flags')
    """given missing flags and timestamps produces a list of contiguous gaps"""
    _gap = {'from': None, 'to': None}
    result = []
    for i in xrange(len(flags)):
        if not flags[i]:
            logger.debug(flags[i])
            if _gap['from'] is not None:
                result.append(_gap)
                logger.debug('Gap saved [%s -> %s]' % (_gap['from'], _gap['to']))
                _gap = {'from': None, 'to': None}
        else:
            if _gap['from'] is None:
                logger.debug('%s: New gap initialised at %s' % (flags[i], ts[i]))
                _gap['from'] = ts[i]
            logger.debug('%s: Gap extended to %s' % (flags[i], ts[i]))
            _gap['to'] = ts[i]
    if _gap['from'] is not None:
        result.append(_gap)
        logger.debug('Gap saved [%s -> %s]' % (_gap['from'], _gap['to']))
    return result
                
def flags_from_gaps(gaps, ts):
    """given gaps and timestamps produces an array of boolean values indicating whether data are missing at each timestamp"""
    flags = np.array([False]*len(ts), dtype=bool)
    for g in gaps:
        a = (ts >= g['from']) & (ts <=g['to'])
        flags[a] = True
    return flags

def add_field(a, descr):
    """Return a new array that is like "a", but has additional fields.

    Arguments:
      a     -- a structured numpy array
      descr -- a numpy type description of the new fields

    The contents of "a" are copied over to the appropriate fields in
    the new array, whereas the new fields are uninitialized.  The
    arguments are not modified.

    >>> sa = numpy.array([(1, 'Foo'), (2, 'Bar')], \
                         dtype=[('id', int), ('name', 'S3')])
    >>> sa.dtype.descr == numpy.dtype([('id', int), ('name', 'S3')])
    True
    >>> sb = add_field(sa, [('score', float)])
    >>> sb.dtype.descr == numpy.dtype([('id', int), ('name', 'S3'), \
                                       ('score', float)])
    True
    >>> numpy.all(sa['id'] == sb['id'])
    True
    >>> numpy.all(sa['name'] == sb['name'])
    True
    """
    if a.dtype.fields is None:
        raise ValueError, "'A' must be a structured numpy array"
    b = np.empty(a.shape, dtype=a.dtype.descr + descr)
    for name in a.dtype.names:
        b[name] = a[name]
    return b
