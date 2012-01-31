"""Events separate segements of data. A model is fitted to each segment independently"""
import numpy as np

class InvalidPeriod(Exception): pass

class event(object):
    def __init__(self, date):
        self.date = date

def period_range(min_date, max_date, events, index):
    if index > len(events): raise InvalidPeriod('Not enough events to generate period %s' % index)
    dates = []
    dates.append(min_date)
    if len(events) > 0: dates.extend([e.date for e in events])
    dates.append(max_date)  
    dates.sort()
    return {'from': dates[index], 'to': dates[index+1]}  

def period_data(data, events, i):
    min_date, max_date = np.min(data['date']), np.max(data['date'])
    p_range = period_range(min_date, max_date, events, i)
    if i == 0: from_indices = (data['date'] >= min_date)
    else: from_indices = (data['date'] >= events[i - 1].date)
    if i == len(events): to_indices = (data['date'] <= max_date)
    else: to_indices = (data['date'] < events[i].date)
    return data[from_indices & to_indices]

def periods(data, events, model):
    """Generate a list of model instances for each subset of data"""
    result = []
    for i in range(len(events)+1):
        p_data = period_data(data, events, i)
        result.append(model(p_data))
    return result


class event_model(object):
    """Fits the given data to the given model but allows for events to be added which segment the modelling"""
    def __init__(self, data):
        self.model = model
        self.data = data
        self.events = []
        self._recalculate()
  
    def _recalculate(self):
        """regenerate all internal models based on event dates and saved input data"""
#        self.periods = periods(self.data, self.events, self.model)
        self.periods = []
        for i in range(len(self.events)+1):
            p_data = period_data(self.data, self.events, i)
            self.periods.append(self.model(p_data))
    
    def add_event(self, ev):
        self.events.append(ev)
        self.events.sort(key=lambda x: x.date)
        self._recalculate()

    def prediction(self, independent_data):
        for i in range(len(self.periods)):
            p_data = period_data(independent_data, self.events, i)
            p_pred = self.periods[i].prediction(p_data)
            if i == 0:
                result = p_pred
            else:
                result = np.concatenate((result, p_pred))
        return result

    def simulation(self, independent_data):
        for i in range(len(self.periods)):
          p_data = period_data(independent_data, self.events, i)
          p_sim = self.periods[i].simulation(p_data)
          if i == 0:
              result = p_sim
          else:
              result = np.concatenate((result, p_sim))
        return result

    def residuals(self, independent_data):
        pred = self.prediction(independent_data)
        return independent_data['consumption'] - pred

    def parameters(self):
        result = []
        for p in self.periods: result.append(p.parameters())
        return result
    
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from ConsumptionModels import Constant, TwoParameterModel
    from DataAccess import RandomDataFactory
    f = RandomDataFactory()
    data = f.randomData(1000)
    em = event_model(data, Constant)
    for d in range(8):
        em.add_event(event(200000.0 * (d + 1)))  
  
    pred = em.prediction(data)
    res = em.residuals(data)
#    print em.parameters()

    plt.plot(data['date'], data['consumption'])
    plt.plot(data['date'], res)
    plt.plot(data['date'], pred)
    plt.show()

