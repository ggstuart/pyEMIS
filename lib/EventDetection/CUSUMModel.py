#!/usr/bin/env python
#-*- coding:utf-8 -*-

import logging
import numpy as np
from ..ConsumptionModels.baseModel import baseModel
from ..EventDetection import EventModel, Event
from ..DataCleaning import utils
import event_model

class unknownCriticalValue(Exception): pass


class CUSUMModelFactory(object):
    def __init__(self, submodel, alpha=0.0001):
        self.submodel = submodel
        self.alpha = alpha

    def __call__(self, data):
        model = CUSUMModel(self.submodel, self.alpha)
        model(data)
        return model


class CUSUMModel(EventModel):
    """An event model that auto-generates events using the CUSUM algorithm"""
    def __init__(self, modelFactory, alpha):
        self.logger = logging.getLogger('pyEMIS:EventDetection:CUSUMModel')
        self.modelFactory = modelFactory
        self.alpha = alpha
        
    def __call__(self, data):
        self.data = data
        self.logger.info("Identifying events...")
        self.events = self.binary_recursion(self.data)
        self.logger.info("Confirming events...")
        self.events = self.confirm_events()
        self.logger.info("Modelling events...")
        self._recalculate()

    def binary_recursion(self, data, period='!'):
        self.logger.info("P%s" % period)
        result=[]
        has_event, ev = self.next_event(data)
        if has_event:
            result.append(ev)
            before, after = (data['date'] < ev.timestamp()), (data['date'] >= ev.timestamp())
            b = self.binary_recursion(data[before], period+'0')
            a = self.binary_recursion(data[after], period+'1')
            result.extend(b)
            result.extend(a)
        return result

    #only works once
    def confirm_events(self):
        result = []
        for i in range(len(self.events)):
            _from = self._period_range(i)['from']
            _to = self._period_range(i+1)['to']
            from_indices = (self.data['date'] > _from)
            to_indices = (self.data['date'] <= _to)
            chunk = self.data[(from_indices & to_indices)]
            has_event, ev = self.next_event(chunk)
            self.logger.info("Has event: %s" % has_event)
            if has_event:
                self.logger.info("%s -> %s" % (self.events[i].date, ev.date))
                result.append(ev)
        return result
    
    def next_event(self, data):
        m = self.modelFactory(data)
        res = m.residuals(data)
        clambda = self.cusum_lambda(res)
        index = np.abs(clambda).argmax()
        sig = clambda[index]
        date = utils.datetime_from_timestamp([data[index]['date']])[0]
        ev = Event(date)
        ev.significance = sig
        ev.index = index
        cv = self.critical_value()
        if np.abs(sig) > cv:
            return True, ev
        else:
            return False, ev

    def cusum_lambda(self, residuals):
        """Calculates the cusum and divides by the boundary shape.
        Used to determine the most likely point for an event"""
        cusum = self.ols_cusum(residuals)
        shape = self.boundary(len(residuals)+1, 1)
        result = cusum[1:-1] / shape[1:-1]
        result = np.insert(result, 0, 0)
        result = np.append(result, 0)
        return result
  
    def ols_cusum(self, residuals):
        n = len(residuals)
        std = np.std(residuals)
        result = np.cumsum(residuals) * (1.0 / (std * np.sqrt(n)))
        return np.insert(result, 0, 0)
  
    def boundary(self, n, multiplier):
        t = np.linspace(0, 1, num = n)
        return np.sqrt(t * (1-t)) * multiplier


    def critical_value(self):
        if self.alpha == 0.0001: return 10.0
        elif self.alpha == 0.001: return 4.5
        elif self.alpha == 0.005: return 4.0
        elif self.alpha == 0.01: return 3.833
        elif self.alpha == 0.05: return 3.375
        elif self.alpha == 0.1: return 3.133
        else: raise unknownAlphaValue("The alpha value [%s] has no known equivalent critical value" % self.alpha)


#def boundary_demonstration(iterations, n, opacity = 0.1, dpi=600):
#    import matplotlib.pyplot as plt
#    fig = plt.figure()
#    for i in range(iterations):
#        data = np.random.randn(n)
#        residuals = data - np.mean(data)
#        cusum = ols_cusum(residuals)
#        plt.plot(cusum, alpha = 0.1, color = 'orange')
#    for alpha in [0.001, 0.01, 0.1]:
#        b = boundary(n+1, critical_value(alpha))
#        plt.plot(b, '--r')
#        plt.plot(b * -1, '--r')
#    fig.savefig('examples/%s Brownian bridges.png' % iterations, dpi=dpi)



#def candidate_event(residuals):
#  clambda = cusum_lambda(residuals)
#  index = np.abs(clambda).argmax()
#  return index, clambda[index]

#def simple_event_detection(data, model, alpha=0.001):
#  em = event_model.event_model(data, model)
#  cv = critical_value(alpha)
#  dates = data['date']
#  while True:
#    res = em.residuals(data)
#    index, value = candidate_event(res)
#    date = dates[index]
#    if abs(value) < cv: break
#    ev = event_model.event(date)
#    ev.value = value
#    ev.index = index
#    em.add_event(ev)
#  return em


#def next_event(data, model, alpha):
#  m = model(data)
#  res = m.residuals(data)
#  clambda = cusum_lambda(res)
#  index = np.abs(clambda).argmax()
#  sig = clambda[index]
#  date = data[index]['date']
#  ev = event_model.event(date)
#  ev.significance = sig
#  ev.index = index
#  cv = critical_value(alpha)
#  if np.abs(sig) > cv:
#    return True, ev
#  else:
#    return False, ev

#def binary_recursion(data, model, alpha=0.001, period=''):
#  result=[]
#  has_event, ev = next_event(data, model, alpha)
#  if has_event:
#    result.append(ev)
#    before, after = (data['date'] < ev.date), (data['date'] >= ev.date)
#    b = binary_recursion(data[before], model, alpha, period+'0')
#    a = binary_recursion(data[after], model, alpha, period+'1')
#    if b: result.extend(b)
#    if a: result.extend(a)
#    return result
#  else:
#    return False

#def recursive_event_detection(data, model, alpha=0.001):
#  em = event_model.event_model(data, model)
#  events = binary_recursion(data, model, alpha)
#  if events:
#    for ev in events: em.add_event(ev)
#  return em  

#if __name__ == "__main__":

#  from ConsumptionModels import ConstantModel, TwoParameterModel, ThreeParameterModel, AnyModel, DowModel
#  from DataAccess import DataFactory, Classic, CleanData
#  import os.path

#  meter_id = 180
#  alpha = 0.1
#  model = DowModel#ThreeParameterModel
#  df = DataFactory(CleanData)#Classic)
#  data = df.dataset(meter_id, 88)

#  em = event_model.event_model(data, model)
#  events = binary_recursion(data, model, alpha)
#  if events:
#    filename = os.path.expanduser('~/diagrams/debug/test')
#    for ev in events:
#      print ev.date
#      em.add_event(ev)
#  
#    pred = em.prediction(data)
#    res = em.residuals(data)
#    fig = plt.figure()
#    plt.plot(data['date'], data['consumption'], alpha = 0.5)
#    plt.plot(data['date'], res, alpha = 0.5)
#    plt.plot(data['date'], pred)
#    for ev in em.events:
#      plt.axvline(x=ev.date, ls='--', color='black')
#    fig.savefig('%s.png' % filename, dpi=600)




##  event_detection_demo2(data, model, filename, alpha)

##  filename = os.path.expanduser('~/diagrams/Event detection (2p model)')
##  event_detection_demo(500, TwoParameterModel, alpha=0.001, filename=filename)

##  boundary_demonstration(500, 500)

##  plt.plot(cusum, color = 'orange')
##  index = candidate_event(residuals)
##  plt.plot([index, index], [-3,3], '--', color = 'red')  
##  plt.show()
#  def event_detection_demo(n, model, alpha=0.001, filename='Event detection'):
#    import matplotlib.pyplot as plt
#    from DataAccess import RandomDataFactory
#    f = RandomDataFactory()
#    data = f.randomDataWithEvent(n)
#    em = simple_event_detection(data, model, alpha)
#    pred = em.prediction(data)
#    res = em.residuals(data)
#    fig = plt.figure()
#    plt.plot(data['date'], data['consumption'], alpha = 0.5)
#    plt.plot(data['date'], res, alpha = 0.5)
#    plt.plot(data['date'], pred)
#    for ev in em.events:
#      plt.axvline(x=ev.date, ls='--', color='black')
#    fig.savefig('%s.png' % filename, dpi=600)

#  def event_detection_demo2(data, model, filename, alpha=0.001):
#    em = simple_event_detection(data, model, alpha)
#    pred = em.prediction(data)
#    res = em.residuals(data)

#    fig = plt.figure()
#    plt.plot(data['date'], data['consumption'], alpha = 0.5)
#    plt.plot(data['date'], res, alpha = 0.5)
#    plt.plot(data['date'], pred)
#    for ev in em.events:
#      plt.axvline(x=ev.date, ls='--', color='black')
#    fig.savefig('%s.png' % filename, dpi=600)

#    fig = plt.figure()
#    cusum = ols_cusum(res)
#    b = boundary(len(data)+1, critical_value(alpha))
#    plt.plot(b, '--r')
#    plt.plot(b * -1, '--r')
#    plt.plot(cusum, alpha = 0.75)
#    for ev in em.events:
#      plt.axvline(x=ev.index, ls='--', color='black')
#    fig.savefig('%s - cusum.png' % filename, dpi=600)


