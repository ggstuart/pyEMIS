import numpy as np
import math

def interpolate(date, integ, resolution):
  first, last = math.ceil(min(date)/resolution)*resolution, math.floor(max(date)/resolution)*resolution
  new_date = np.arange(first, last, resolution)
  new_integ = np.interp(new_date, date, integ)
  return new_date, new_integ

def hh(date, integ):
  return interpolate(date, integ, resolution=60*30)

def daily(date, integ):
  return interpolate(date, integ, resolution=60*60*24)

def weekly(date, integ):
  return interpolate(date, integ, resolution=60*60*24*7)

