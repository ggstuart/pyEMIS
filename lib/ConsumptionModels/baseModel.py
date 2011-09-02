class baseModel(object):

  """Common functions required by all models"""

  n_parameters = -1
  
  def residuals(self, independent_data):
    pred = self.prediction(independent_data)
    return independent_data['consumption'] - pred

  #implement this for many reasons
  def gof_stats(self, independent_data):
    return gofStats(independent_data['consumption'], self.prediction(independent_data), self.n_parameters)

import numpy as np

class gofStats(object):

  """Calculate a few useful goodness of fit statistics"""

  def __init__(self, actual, prediction, n_parameters):
    self.n_parameters = n_parameters
    self.residuals = actual - prediction
    self.n = len(self.residuals)
    self.mu = np.mean(actual)
    self.sse = np.sum(self.residuals**2)
    self.rmse = np.sqrt(self.sse/(self.n-1))
    self.cv_rmse = self.rmse/self.mu
    k = self.n_parameters + 1
    self.bic = self.n * np.log(self.sse) + np.log(self.n) * self.n_parameters
    self.aic = (self.n * np.log(self.sse/self.n)) +  (2 * k) + (2 * (k + 1) / (self.n - k - 1))
    
  def aic(self): return self.aic
  def bic(self): return self.bic