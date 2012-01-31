import logging
import numpy as np
from ..ConsumptionModels.baseModel import baseModel
from ..DataCleaning import utils


class InvalidPeriod(Exception): pass

class EventModelFactory(object):
    def __init__(self, submodel):
        self.submodel = submodel

    def __call__(self, data):
        model = EventModel(self.submodel)
        model(data)
        return model


class Event(object):
    """Events separate periods of data"""
    def __init__(self, date):
        self.date = date

    def timestamp(self):
        return utils.timestamp_from_datetime([self.date])[0]


class Period(object):
    """A period includes a model and is part of a parent EventModel"""
    def __init__(self, parent, period_range):
        self.logger = logging.getLogger("EventModel:Period")
        self._from = period_range['from']
        self._to = period_range['to']
        self.parent = parent
        self.model = self.parent.modelFactory(self.data())  #here is the actual model instance

    def indices(self):
        from_indices = (self.parent.data['date'] > self._from)
        to_indices = (self.parent.data['date'] <= self._to)
        self.logger.debug("length: %i" % sum((from_indices & to_indices)))
        if self._from == min(self.parent.data['date']):
            return to_indices
        elif self._to == max(self.parent.data['date']):
            return from_indices
        else:
            return (from_indices & to_indices)

    def data(self):
        return self.parent.data[self.indices()]

    def __str__(self):
        i = self.parent.periods.index(self)
        n = len(self.parent.periods)
        return "Period %i of %i" % (i+1, n)

class EventModel(baseModel):
    """Fits the given data to the given model but allows for events to be added which segment the modelling"""
    def __init__(self, modelFactory):
        self.logger = logging.getLogger('pyEMIS:EventDetection:EventModel')
        self.logger.info("Hello")
        self.modelFactory = modelFactory

    def __call__(self, data):
        self.data = data
        self.events = []
        self.recalculate()
  
#    def _recalculate(self):
#        """
#        Generate a list of period instances for each subset of data
#        """
##        self.periods = [self.modelFactory(self._period_data(self.data, i)) for i in range(len(self.events) + 1)]
#        self.periods = [Period(self, self.period_range(i)) for i in range(len(self.events) + 1)]

    def recalculate(self):
        self.periods = []
        dates = [ev.timestamp() for ev in self.events]
        dates.insert(0, np.min(self.data['date']))
        dates.append(np.max(self.data['date']))
        self.periods = [Period(self, {'from': dates[i], 'to': dates[i+1]}) for i in range(len(self.events) + 1)]

    def event_dates(self):
        dates = [ev.timestamp() for ev in self.events]
        dates.insert(0, np.min(self.data['date']))
        dates.append(np.max(self.data['date']))
        return dates
            
    def add_event(self, ev):
        self.events.append(ev)
        self.events.sort(key=lambda x: x.date)
        self.logger.info('\nNew event added')
        for ev in self.events:
            self.logger.info(ev.date)
        self.recalculate()

    def set_events(self, events):
        self.events = sorted(events, key=lambda x: x.date)
        self.recalculate()

#    def prediction(self, independent_data):
#        for p in self.periods:
#            data = p.data(independent_data, i)
#            p_pred = self.periods[i].prediction(p_data)
#            if i == 0:
#                result = p_pred
#            else:
#                result = np.concatenate((result, p_pred))
#        return result

#    def prediction(self, independent_data):
#        for i in range(len(self.periods)):
#            p_data = self._period_data(independent_data, i)
#            p_pred = self.periods[i].prediction(p_data)
#            if i == 0:
#                result = p_pred
#            else:
#                result = np.concatenate((result, p_pred))
#        return result

