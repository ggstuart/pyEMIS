import numpy as np
from baseModel import baseModel, ModellingError as me
import logging

class ModellingError(me): pass

class ThreeParameterModel(baseModel):
    """
    A three-parameter heating model where consumption is estimated as a piece-wise linear regression between consumption and outside air emperature below a change-point
    Input_data must respond to the method calls 'consumption'  and 'temperature'
    """

    n_parameters = 3
  
    def __init__(self, data):
        self.logger = logging.getLogger('pyEMIS:models:3PHModel')
        if len(data) <= (self.n_parameters + 2):
            raise ModellingError, "Not enough input data"
        self.mu = np.mean(data['consumption'])
        min_temp, max_temp = np.min(data['temperature']), np.max(data['temperature'])
        self.xrange = [min_temp, max_temp]
        min_temp, max_temp = self._grid_search(data, min_temp, max_temp, 20)
        min_temp, max_temp = self._grid_search(data, min_temp, max_temp, 20)

    def _grid_search(self, data, min_temp, max_temp, steps):
        temp_range = max_temp - min_temp
        temp_step = temp_range / (steps - 1)
        best_temp = np.float64(15.5)
        self._fit(data, best_temp)
        best_rmse = self.rmse
        for step in range(steps):
            test_temp = min_temp + step * temp_step
            self._fit(data, test_temp)
            if self.rmse < best_rmse:
                best_rmse = self.rmse
                best_temp = test_temp
        self._fit(data, best_temp)
        return best_temp - temp_step, best_temp + temp_step

    def _fit(self, data, change_point):
        x = np.vstack([change_point - data['temperature'], np.zeros(len(data))])
        x = np.amax(x, axis=0)
        y = data['consumption']
        A = np.vstack([x, np.ones(len(x))]).T
        self.etc = np.linalg.lstsq(A, y)
        self.m, self.c = self.etc[0]
        self.cp = change_point
        self.diff = y - self.prediction(data)
        self.sse = np.sum(self.diff**2)
        self.rmse = np.sqrt(np.mean(self.diff**2))
    
    def prediction(self, data):
        dd = np.vstack([self.cp - data['temperature'], np.zeros(len(data))])
        dd = np.amax(dd, axis=0)
        return dd * self.m + self.c

    def simulation(self, independent_data):
        return np.random.randn(independent_data.size)
    
    def parameters(self):
        return {'m': self.m, 'c': self.c, 'cp': self.cp}
	
if __name__ == "__main__":
      import matplotlib.pyplot as plt
      from DataAccess import DataFactory, Classic
      df = DataFactory(Classic)
      d = df.dataset(265)
      m = ThreeParameterModel(d)
      plt.scatter(d['temperature'], d['consumption'])
      plt.plot(d['temperature'], m.prediction(d))
#      plt.scatter(d.temperature, c.diff, color = 'green')
      print m.diff
      print m.cv_rmse
      print m.cp
      plt.show()

