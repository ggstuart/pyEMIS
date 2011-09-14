import numpy as np, datetime, time

def movement_from_integ(integ):
    return np.append(np.nan, np.diff(integ))

def integ_from_movement(movement):
    return np.append(0.0, np.cumsum(movement[1:]))

def timestamp_from_datetime(dt):
    return np.array([time.mktime(d.timetuple()) for d in dt])

def datetime_from_timestamp(ts):
    return [datetime.datetime.fromtimestamp(s) for s in ts]

