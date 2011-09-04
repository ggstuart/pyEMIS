import numpy as np

def movement_from_integ(integ):
  return np.append(np.nan, np.diff(integ))

def integ_from_movement(movement):
  return np.append(0.0, np.cumsum(movement[1:]))
