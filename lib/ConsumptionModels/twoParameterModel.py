import numpy as np
from baseModel import baseModel, ModellingError as me

class ModellingError(me): pass

class TwoParameterModel(baseModel):
    """
    A two-parameter consumption model where consumption is estimated as a linear regression between consumption and outside air emperature
    Input_data must respond to the method calls 'consumption'  and 'temperature'
    """
  
    n_parameters = 2
  
    def __init__(self, data):
        if len(data) <= (self.n_parameters + 2):
            raise ModellingError, "Not enough input data"
        x = data['temperature']
        self.xrange = [min(x), max(x)]
        y = data['consumption']
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
