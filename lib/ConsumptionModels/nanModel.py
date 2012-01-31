import logging
import numpy as np
from baseModel import baseModel

class NanModel(baseModel):
    """A placeholder for a model that just spits out np.nan values as a prediction"""

    n_parameters = 0
  
    def __init__(self, *args, **kwargs):
        pass

    def prediction(self, independent_data):
        if 'consumption' in independent_data.dtype.names:
            return independent_data['consumption']
        return np.array([np.nan] * len(independent_data))

    def parameters(self):
        return {}
