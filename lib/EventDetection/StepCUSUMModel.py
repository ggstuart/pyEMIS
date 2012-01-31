#!/usr/bin/env python
#-*- coding:utf-8 -*-

import logging
import numpy as np
from ..ConsumptionModels.baseModel import baseModel
from ..EventDetection import EventModel, Event
from ..DataCleaning import utils
import event_model

class unknownCriticalValue(Exception): pass

class DuplicateEventError(Exception):
    def __init__(self, msg, cusum):
        self.msg = msg
        self.cusum = cusum

    def __str__(self):
        return repr(self.msg)

class StepCUSUMModelFactory(object):
    def __init__(self, submodel, alpha=0.0001):
        self.submodel = submodel
        self.alpha = alpha

    def __call__(self, data):
        model = StepCUSUMModel(self.submodel, self.alpha)
        model(data)
        return model


class StepCUSUMModel(EventModel):
    """An event model that auto-generates events using the CUSUM algorithm
       The model offers an add_event method that either auto-detects or returns false
    """
    def __init__(self, modelFactory, alpha):
        self.logger = logging.getLogger('pyEMIS:EventDetection:StepCUSUMModel')
        self.modelFactory = modelFactory
        self.alpha = alpha
        
    def __call__(self, data):
        self.data = data
        self.events = []
        self.recalculate()

    def add_event(self):
        candidates = []
        for p in self.periods:
            cusum = self.period_CUSUM(p)
            if cusum.has_event():
                if cusum.event.date in [e.date for e in self.events]:
                    raise DuplicateEventError, ('Duplicate event!', cusum)
                candidates.append(cusum.event)
        self.logger.debug("%i candidate events" % len(candidates))
        if len(candidates) == 0:
            return False
        winner = sorted(candidates, key=lambda x: x.significance)[0]
        self.logger.info("Event found: %s" % winner.date.strftime("%d/%m/%Y"))
        #could I use super() here to actually add the event?
        self.events.append(winner)
        self.events.sort(key=lambda x: x.date)
        self.recalculate()
        return True

    def process_events(self, max_count=25):
        count = 0
        self.logger.debug("Processing events")
        while not self.confirm_events:
            self.logger.info("Events are bad")
            new_events = []
            for i in range(len(self.events)):
                cusum = self.event_CUSUM(i)
                if cusum.has_event():
                    new_events.append(cusum.event)
            new_events.sort(key=lambda x: x.date)
            self.events = new_events
            self.recalculate()
            count += 1
            self.logger.info("Count: %i" % count)
            if count >= max_count: break
        self.logger.debug("Events are sorted")
            
    def confirm_events(self):
        for i in range(len(self.events)):
            if not self.confirm_event(i):
                return False
        return True

    def confirm_event(self, event_index):
        event = self.events[event_index]
        cusum = self.event_CUSUM(event_index)
        if not cusum.has_event():
            return False
        else:
            return cusum.event.date == event.date

    def old_period_CUSUM(self, period_index):
        self.logger.debug("Period: %i" % period_index)
        data = self._period_data(self.data, period_index)
        res = self.periods[period_index].residuals(data)
        return OLS_CUSUM(data['date'], res, self.alpha)

    def period_CUSUM(self, period):
        data = period.data()
        return OLS_CUSUM(data['date'], period.model.residuals(data), self.alpha)
        
    def event_CUSUM(self, event_index):
        self.logger.debug("Event: %i" % event_index)
        _from = self._period_range(event_index)['from']
        _to = self._period_range(event_index+1)['to']
        from_indices = (self.data['date'] > _from)
        to_indices = (self.data['date'] <= _to)
        data = self.data[(from_indices & to_indices)]
        model = self.modelFactory(data)
        res = model.residuals(data)
        return OLS_CUSUM(data['date'], res, self.alpha)


class OLS_CUSUM(object):
    def __init__(self, timestamps, residuals, alpha):
        self.logger = logging.getLogger('StepCUSUMModel:OLS_CUSUM')
        self.dt = utils.datetime_from_timestamp(timestamps)
        self.residuals = residuals
        self.alpha = alpha
        n = len(self.residuals)
        std = np.std(residuals)
        result = np.cumsum(residuals) * (1.0 / (std * np.sqrt(n)))  #n
        self.ols_cusum = np.insert(result, 0, 0)    #n + 1, starts and ends with zero
        t = np.linspace(0, 1, num=n + 1)            #n + 1
        self.shape = np.sqrt(t * (1 - t))           #n + 1, starts and ends with zero
        self.clambda = np.append(np.insert(self.ols_cusum[1:-1] / self.shape[1:-1], 0, 0), 0)   #replace ends with zeros, n + 1
        index = np.abs(self.clambda).argmax()
        self.event = Event(self.dt[index])
        self.event.significance = self.clambda[index]

    def has_event(self):
        return np.abs(self.event.significance) > self.critical_value()

    def boundary(self):
        return self.shape * self.critical_value()

    def critical_value(self):
        if self.alpha == 0.0001: return 10.0
        elif self.alpha == 0.001: return 4.5
        elif self.alpha == 0.005: return 4.0
        elif self.alpha == 0.01: return 3.833
        elif self.alpha == 0.05: return 3.375
        elif self.alpha == 0.1: return 3.133
        else: raise unknownAlphaValue("The alpha value [%s] has no known equivalent critical value" % self.alpha)

