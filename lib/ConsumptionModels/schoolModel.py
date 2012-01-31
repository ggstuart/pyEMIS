from baseModel import baseModel, ModellingError as me
import logging
import numpy as np

class ModellingError(me): pass

class SchoolModelFactory(object):
    def __init__(self, factory, field='term'):
        """Configure the factory with all elements specific to the schools model"""
        self._field = field
        self._factory = factory

    def __call__(self, data):
        """
        Mimicking the baseModel __init__ function, i.e. fit the model
        The data are split into subsets (term time and holidays)
        The object itself is returned - does this cause problems if this is called more than once?
        """
        model = SchoolModel(self._factory, self._field)
        model(data)
        return model


class SchoolModel(baseModel):
    """
    Split data into term-time and holiday time based on a 'term' field in the input data
    """
    def __init__(self, factory, field='term'):
        """Configure the 'schools' elements of the model"""
        self.logger = logging.getLogger('pyEMIS.Models.School')
        self.field = field
        self._factory = factory

    def __call__(self, data):
        """
        Mimicking the baseModel __init__ function, i.e. fit the model
        The data are split into subsets (term time and holidays)
        """
        if not self.field in data.dtype.names:
            raise ModellingError, "Field [%s] not found in input data." % self.field
#        self.logger.info("term: %s" % sum(self.term(data)))
#        self.logger.info("holiday: %s" % sum(self.holiday(data)))
        self.termModel = self._factory(data[self.term(data)])
        self.holidayModel = self._factory(data[self.holiday(data)])
        self.n_parameters = sum([self.termModel.n_parameters, self.holidayModel.n_parameters])
        
    def term(self, data):
        return (data[self.field] == True)

    def holiday(self, data):
        return (data[self.field] != True)

    def prediction(self, independent_data):
        term_pred = self.termModel.prediction(independent_data)
        hol_pred = self.holidayModel.prediction(independent_data)
        hols = self.holiday(independent_data)
        term_pred[hols] = hol_pred[hols]
        return term_pred

    def percentiles(self, independent_data, percentiles):
        dt = np.dtype([(str(p), np.float64) for p in percentiles])
        result = np.zeros(independent_data.shape, dtype=dt)
        iterm = self.term(independent_data)
        ihols = self.holiday(independent_data)
        termP = self.termModel.percentiles(independent_data[iterm], percentiles)    #dict
        holsP = self.holidayModel.percentiles(independent_data[ihols], percentiles) #dict
        for p in termP.keys():
            result[p][iterm] = termP[p]
            result[p][ihols] = holsP[p]
        result2 = {}
        for key in result.dtype.names:
            result2[key] = result[key].tolist()
        return result2

    def parameters(self):
        return {'term': self.termModel.parameters(), 'holidays': self.holidayModel.parameters()}
