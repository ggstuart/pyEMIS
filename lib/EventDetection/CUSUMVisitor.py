import logging
import numpy as np
from ..DataCleaning import utils
from . import Event

class CUSUMVisitor(object):
    def __init__(self, alpha):
        self.alpha = alpha
        self.logger = logging.getLogger('EventDetection:CUSUMVisitor')
        self.logger.info("Hello")
        
    def detect(self, model, *args, **kwargs):
        meth = None
        for cls in model.__class__.__mro__:
            meth_name = 'detect_'+cls.__name__
            meth = getattr(self, meth_name, None)
            if meth:
                break

        if not meth:
            meth = self.generic_visit
        return meth(model, *args, **kwargs)

    def generic_detect(self, model, *args, **kwargs):
        print 'generic_detect '+node.__class__.__name__

    def detect_EventModel(self, model, *args, **kwargs):
        while self.add_event(model):
            self.logger.info("Added event %i" % len(model.events))
        self.logger.info("Processing events")
        self.process_events(model)

    def add_event(self, model):
        """See if an event can be detected in the model. If so, add it."""
        candidates = []
        for p in model.periods:
            cusum = self.period_CUSUM(p)
            if cusum.has_event():
                candidates.append(cusum.event)
        self.logger.info("%i candidate events" % len(candidates))
        if len(candidates) == 0:
            return False
        winner = sorted(candidates, key=lambda x: x.significance)[0]
        self.logger.info("winner: %s" % winner.date.strftime("%d/%m/%Y"))
        model.add_event(winner)
        return True


    def process_events(self, model, max_count=25):
        count = 0
        self.logger.info("Processing events")
        while not self.confirm_events(model):
            self.logger.info("Events are bad")
            new_events = []
            for i in range(len(model.events)):
                cusum = self.event_CUSUM(model, i)
                if cusum.has_event():
                    new_events.append(cusum.event)
            new_events.sort(key=lambda x: x.date)
            model.events = new_events
            model.recalculate()
            count += 1
            self.logger.info("Count: %i" % count)
            if count >= max_count: break
        self.logger.info("Events are sorted")
            
    def confirm_events(self, model):
        for i in range(len(model.events)):
            if not self.confirm_event(model, i):
                return False
        return True

    def confirm_event(self, model, event_index):
        self.logger.debug("Confirming event %03i" % event_index)
        cusum = self.event_CUSUM(model, event_index)
        if not cusum.has_event():
            return False
        else:
            event = model.events[event_index]
            return cusum.event.date == event.date

    def period_CUSUM(self, period):
        self.logger.debug(str(period))
        data = period.data()
        return OLS_CUSUM(data['date'], period.model.residuals(data), self.alpha)

#    def period_CUSUM(self, model, period_index):
#        self.logger.debug("Period: %i" % period_index)
#        data = model._period_data(model.data, period_index)
#        res = model.periods[period_index].residuals(data)
#        return OLS_CUSUM(data['date'], res, self.alpha)

    def event_CUSUM(self, model, event_index):
        """Return an OLS_CUSUM covering the periods before and after an event"""
        dates = model.event_dates() #includes min_date and max_date -> 0... n_events + 2
        from_indices = (model.data['date'] > dates[event_index])
        to_indices = (model.data['date'] <= dates[event_index + 2])
        data = model.data[(from_indices & to_indices)]
        submodel = model.modelFactory(data)
        res = submodel.residuals(data)
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

