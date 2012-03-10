import numpy as np
from baseModel import baseModel
from datetime import date
#from constantModel import ConstantModel
from anyModel import AnyModelFactory as AnyModel

def uniq(alist):
  myset = {}
  return [myset.setdefault(e,e) for e in alist if e not in myset]

class DowModel(baseModel):
  """
  A 'days of the week' consumption model: consumption is modelled independently for different days of the week
  Input_data must respond to the method call 'consumption' 
  """
  def __init__(self, input_data, submodel=AnyModel, dow=[0,1,2,3,4,5,6]):
    weekdays = np.array([date.fromtimestamp(d).weekday() for d in input_data['date']])
    self.dow = np.array(dow)
    model_ids = uniq(self.dow)
    self.submodels = []
    for i in model_ids: #[0,1,2] for [0,1,1,1,1,1,2]
      wds = np.array(range(7))[(self.dow == i)]  #which weekdays are covered by this model_id
      indices = np.array([], int)
      for wd in wds:
        chunk = np.where(weekdays == wd)
        indices = np.sort(np.concatenate((indices, chunk[0])))
      self.submodels.append(submodel(input_data[indices]))
    self.n_parameters = 0
    for submodel in self.submodels: self.n_parameters += submodel.n_parameters
      
  def prediction(self, independent_data):
    weekdays = [date.fromtimestamp(d).weekday() for d in independent_data['date']]
    model_ids = uniq(self.dow)
    result = np.zeros(len(independent_data))
    for i in model_ids: #[0,1,2]
      wds = np.array(range(7))[(self.dow == i)]  #which weekdays are covered by this model_id
      indices = np.array([], int)
      for wd in wds:
        chunk = np.where(weekdays == wd)
        indices = np.sort(np.concatenate((indices, chunk[0])))
      result[indices] = self.submodels[i].prediction(independent_data[indices])
    return result

  def simulation(self, independent_data):
    pass
	  #return self.std * np.random.randn(independent_data.size) + self.mean

  def parameters(self):
    pass
    #return {'mean': self.mean, 'std': self.std}

  def types(self):
    return [model.__class__.__name__ for model in self.submodels]
    
if __name__ == "__main__":
  import matplotlib.pylab as plt
  from pyEMIS.DataAccess import DataFactory, Fake, Classic
  f = DataFactory(Classic)
  d = f.dataset(48, 88)
  plt.plot(d['date'], d['consumption'])

  dow = DowModel(d)
  pred = dow.prediction(d)
  plt.plot(d['date'], pred)
  
  plt.show()
