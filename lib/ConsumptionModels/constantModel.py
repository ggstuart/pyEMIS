#This is a class because it stores its model parameters and has a 'prediction' function which returns predictions for input data
import numpy as np
from baseModel import baseModel, ModellingError as me

class ModellingError(me): pass

class ConstantModel(baseModel):
  """
  A constant consumption model: consumption is estimated as the average of all input data
  Input_data must respond to the method call 'consumption' 
  """
  
  n_parameters = 1
  
  def __init__(self, data):
    if len(data) <= 1:#(self.n_parameters + 2):
        raise ModellingError, "Not enough input data"
    if 'temperature' in data.dtype.names:
        x = data['temperature']
        self.xrange = [min(x), max(x)]
    self.mean = np.mean(data['consumption'])
    self.std = np.std(data['consumption'])

  def prediction(self, independent_data):
    return np.array([self.mean] * len(independent_data))

  def simulation(self, independent_data):
	  return self.std * np.random.randn(independent_data.size) + self.mean

  def parameters(self):
    return {'mean': self.mean, 'std': self.std}
