import numpy as np
import math, utils, logging

class dataCleaningError(Exception): pass
class zeroGapError(dataCleaningError): pass
class negativeGapError(dataCleaningError): pass
class NoDataError(dataCleaningError): pass

def clean(date, integ, movement, sd_limit):
  logging.debug('cleaning process started')
  while invalid_dates(date): date, integ, movement = prepare(date, integ, movement)
  new_date, new_integ = trim_ends(date, integ)
  clean_date, clean_integ = remove_extremes(new_date, new_integ, sd_limit)
  clean_movement = utils.movement_from_integ(clean_integ)
  return clean_date, clean_integ, clean_movement

def invalid_dates(dates):
  gap = np.diff(dates)
  return any(gap<=0)

def prepare(date, integ, movement):
  logging.debug('preparing data for cleaning')
  gap = np.diff(date)
  ok = np.append(True, (gap>0))
  date = date[ok]
  integ = integ[ok]
  movement = utils.movement_from_integ(integ)
  return date, integ, movement    

def remove_extremes(date, integ, sd_limit):
  logging.debug('removing extremes')
  nremoved, new_date, new_integ = rate_filter(date, integ, sd_limit)
  total_removed = nremoved
  logging.debug('-->%i readings removed' % nremoved)
  while nremoved > 0:
    nremoved, new_date, new_integ = rate_filter(new_date, new_integ, sd_limit)
    logging.debug('-->%i readings removed' % nremoved)
    total_removed += nremoved
  if total_removed > 0:
    logging.debug("%s extreme record(s) removed in total" % total_removed)
  else: logging.debug("No extreme records removed")
  return new_date, new_integ

def rate_filter(date, integ, sd_limit):
  r = rate(date, integ)
  lower_limit, upper_limit = limits(r, sd_limit)
  keep, remove = (r>=lower_limit) & (r<=upper_limit), (r<lower_limit) | (r>upper_limit)
  filtered = any(remove)
  nremoved = len(r[remove])
  keep, remove = np.append(True, keep), np.append(True, remove)    #add one element to the beginning to keep the first integ and date values intact
  filtered_date = date[keep]
  movement = utils.movement_from_integ(integ)
  filtered_integ = utils.integ_from_movement(movement[keep])
  return nremoved, filtered_date, filtered_integ


def clean_temp(date, integ, movement, sd_limit):
  new_date, new_movement = trim_ends(date, movement)
  clean_date, clean_movement = remove_extremes_temp(new_date, new_movement, sd_limit)
  clean_integ = utils.integ_from_movement(clean_movement)
  return clean_date, clean_integ, clean_movement

def remove_extremes_temp(date, movement, sd_limit):
  nremoved, new_date, new_movement = filter_temp(date, movement, sd_limit)
  total_removed = nremoved
  while nremoved > 0:
    nremoved, new_date, new_movement = filter_temp(new_date, new_movement, sd_limit)
    total_removed += nremoved
#  if total_removed > 0:
#    print "%s extreme record(s) removed" % total_removed
#  else: print "No extreme records removed"
  return new_date, new_movement

def filter_temp(date, movement, sd_limit):
  lower_limit, upper_limit = limits(movement, sd_limit, allow_negs=True)
  keep, remove = (movement>=lower_limit) & (movement<=upper_limit), (movement<lower_limit) | (movement>upper_limit)
  filtered = any(remove)
  nremoved = len(movement[remove])
  filtered_date = date[keep]
  filtered_movement = movement[keep]
  return nremoved, filtered_date, filtered_movement

def trim_ends(date, value):
  """
  Uses date array to identify big gaps.
  Value field is trimmed to match.
  """
  if len(date) == 0: raise NoDataError("Can't trim ends from an empty dataset")
  n = 0
  big_gap = 60*60*24*7
  for i in range(0, len(date)-1):
    gap = date[i+1] - date[i]
    if gap < big_gap: break
    else:
      n += 1
      logging.debug("gap->: %s [hr]" % (gap / (60*60)))
  start = i
  for j in range(len(date)-1):
    i = len(date)-1 - j
    gap = date[i] - date[i-1]
    if gap < big_gap:
      break
    else:
      n += 1
      logging.debug("<-gap: %s [hr]" % (gap / (60*60)))
  end = i+1
  if n > 0:
    logging.debug("%s points removed from ends ( so [0:%s] became [%s:%s])" % (n, len(date)-1, start, end))
  else:
    logging.debug("No points removed from ends")
  return date[start:end], value[start:end]

def rate(date, integ):
  import time
  gap = np.diff(date)
  if any(gap<0): raise negativeGapError
  if any(gap==0): 
    a = (gap==0)
    raise zeroGapError, "Cannot determine rate for a zero length gap %s" % [time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(d)) for d in date[a]]
  movement = np.diff(integ)
  return movement/gap

def limits(data, sd_limit, allow_negs = False):
  mean = np.mean(data)
  std = np.std(data)
  limit = std * sd_limit
  result = [mean - limit, mean + limit]
  if not allow_negs: result[0] = 0
  return result

#def movement_from_integ(integ):
#  return np.append(np.nan, np.diff(integ))
#
#def integ_from_movement(movement):
#  return np.append(0.0, np.cumsum(movement[1:]))
