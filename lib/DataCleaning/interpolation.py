import numpy as np
import math, utils

def interpolate(date, integ, movement, resolution):
  first, last = math.ceil(min(date)/resolution)*resolution, math.floor(max(date)/resolution)*resolution
  new_date = np.arange(first, last, resolution)
  new_integ = np.interp(new_date, date, integ)
  new_movement = utils.movement_from_integ(new_integ)
  return new_date, new_integ, new_movement

def hh(date, integ, movement):
  return interpolate(date, integ, movement, resolution=60*30)

def daily(date, integ, movement):
  return interpolate(date, integ, movement, resolution=60*60*24)

def weekly(date, integ, movement):
  return interpolate(date, integ, movement, resolution=60*60*24*7)

