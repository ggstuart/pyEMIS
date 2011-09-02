from baseModel import baseModel
from constantModel import ConstantModel
from twoParameterModel import TwoParameterModel
from threeParameterModel import ThreeParameterModel
from numpy import argmin

class AnyModel_old(baseModel):
  """
  A 'best fit' consumption model: consumption is modelled using several alternatives
  The best fitting model based on BIC or AIC is selected and returned
  """
  
  types = [ConstantModel, TwoParameterModel, ThreeParameterModel]
  
  def __init__(self, input_data, criterion='bic'):
    models = [m(input_data) for m in self.types]
    stats = [m.gof_stats(input_data) for m in models]
    best = argmin([getattr(s, criterion) for s in stats])
    self.model = models[best]
    self.n_parameters = self.model.n_parameters
    
  def __getattr__(self, attr):
    """Everything else is delegated to the model"""
    return getattr(self.model, attr)
    
    
def AnyModel(input_data, criterion='aic'):
    types = [ConstantModel, TwoParameterModel, ThreeParameterModel]
    models = [m(input_data) for m in types]
    stats = [m.gof_stats(input_data) for m in models]
    best = argmin([getattr(s, criterion) for s in stats])
    return models[best]