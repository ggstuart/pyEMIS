import numpy as np
from baseModel import baseModel

class TwoParameterModel(baseModel):
  """
  A two-parameter consumption model where consumption is estimated as a linear regression between consumption and outside air emperature
  Input_data must respond to the method calls 'consumption'  and 'temperature'
  """
  
  n_parameters = 2
  
  def __init__(self, input_data):
    if len(input_data) == 0: raise ValueError('Data are of zero length')
    x = input_data['temperature']
    y = input_data['consumption']
    A = np.vstack([x, np.ones(len(x))]).T
    self.m, self.c = np.linalg.lstsq(A, y)[0]

  def prediction(self, independent_data):
    return independent_data['temperature'] * self.m + self.c

  def simulation(self, independent_data):
    return np.random.randn(independent_data.size)
    
  def parameters(self):
    return {'m': self.m, 'c': self.c}
	
if __name__ == "__main__":
  import matplotlib.pylab as plt
  from DataAccess.myData import RandomDataFactory
  f = RandomDataFactory()
  d = f.randomData(50)
  m = TwoParameterModel(d)
  pred = m.prediction(d)
  plt.plot(d['date'], d['consumption'])
  plt.plot(d['date'], pred)
  plt.show()

