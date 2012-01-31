from baseModel import baseModel, ModellingError as me
from nanModel import NanModel
from constantModel import ConstantModel
from twoParameterModel import TwoParameterModel
from threeParameterModel import ThreeParameterModel
from numpy import argmin
import logging

class ModellingError(me): pass

class AnyModelFactory(object):
    def __init__(self, criterion='aic', models = [ConstantModel, TwoParameterModel, ThreeParameterModel], ignore_missing=True):
        self.criterion = criterion
        self.models = models
        self.ignore_missing = ignore_missing
        self.logger = logging.getLogger('pyEMIS:models:AnyModel')

    def __call__(self, data):
        if self.ignore_missing:
            if 'missing' in data.dtype.names:
                data = data[~data['missing']]

        models = []
        for m in self.models:
            try:
                model = m(data)
                models.append(model)
            except me, e:
                pass
        if len(models) == 0:
            return NanModel(data)
        if len(models) == 1:
            return models[0]
        stats = [m.gof_stats(data) for m in models]
        best = argmin([getattr(s, self.criterion) for s in stats])
        return models[best]

    def __getattr__(self, name):
        """Get a specific model easily too"""
        names = [t.__name__ for t in self.models]
        if name in names:
            return self.models[names.index(name)]
        else: raise ModellingError, "No model named '%s' exists" % name

#def AnyModel(input_data, criterion='aic', types = [ConstantModel, TwoParameterModel, ThreeParameterModel]):    
#    if 'missing' in input_data.dtype.names:
#        input_data = input_data[~input_data['missing']]
#    models = [m(input_data) for m in types]
#    stats = [m.gof_stats(input_data) for m in models]
#    best = argmin([getattr(s, criterion) for s in stats])
#    return models[best]
