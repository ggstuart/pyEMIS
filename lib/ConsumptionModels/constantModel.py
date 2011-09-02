#This is a class because it stores its model parameters and has a 'prediction' function which returns predictions for input data
import numpy as np
from baseModel import baseModel

class ConstantModel(baseModel):
  """
  A constant consumption model: consumption is estimated as the average of all input data
  Input_data must respond to the method call 'consumption' 
  """
  
  n_parameters = 1
  
  def __init__(self, input_data):
    self.mean = np.mean(input_data['consumption'])
    self.std = np.std(input_data['consumption'])

  def prediction(self, independent_data):
    return independent_data['consumption'] * 0 + self.mean

  def simulation(self, independent_data):
	  return self.std * np.random.randn(independent_data.size) + self.mean

  def parameters(self):
    return {'mean': self.mean, 'std': self.std}