import numpy as np

from ..models.base import Base

class Factory(object):
    def __init__(self, factory):
        self.factory = factory

    def __call__(self, data):
        model = Discontinuous(self.factory)
        model(data)
        return model

class Discontinuous(Base):
    """Creates a model instance for each period between registered events"""
    def __init__(self, factory):
        self.factory = factory
        self.events = []

    def __call__(self, training_data):
        """Fit the model afresh to each defined period
        """
        self.data = training_data   #do I need to store the data?
        self._recalculate()

    def add_event(self, ev):
        self.events.append(ev)
        self.events.sort()
        self._recalculate()

    def remove_event(self, ev):
        self.events.remove(ev)
        self._recalculate()

    def set_events(self, events):
        self.events = sorted(events)
        self._recalculate()

    def _recalculate(self):
        """Create model instances in order with data split according to the given events"""
        _froms, _tos = list(self.events), list(self.events)
        _froms.insert(0, self.data['timestamp'][0])
        _tos.append(self.data['timestamp'][-1])
        self.periods = []
        for _from, _to in zip(_froms, _tos):
            p = Period(_from, _to)
            p.model = self.factory(p.chunk(self.data))
            self.periods.append(p)
        self.n_parameters = sum([p.model.n_parameters for p in self.periods])

    def prediction(self, independent_data):
        """Unpack the model
        Each submodel is used to generate a bit of the prediction
        """
        result = np.zeros(independent_data.shape)
        for p in self.periods:
            indices = p.indices(independent_data['timestamp'])
            result[indices] = p.model.prediction(independent_data[indices])
        return result


    def percentiles(self, independent_data, percentiles):
        """Unpack the model
        Each submodel is used to generate a bit of the percentiles
        """
        result = dict([(p, np.zeros(independent_data.shape)) for p in percentiles])
        for p in self.periods:
            indices = p.indices(independent_data['timestamp'])
            chunk = p.model.percentiles(independent_data[indices], percentiles)
            for p in chunk.keys():
                result[p][indices] = chunk[p]
        return result


class Period(object):
    def __init__(self, _from, _to):
        self._from = _from
        self._to = _to
        self.model = None

    def chunk(self, data):
        return data[self.indices(data['timestamp'])]

    def indices(self, timestamps):
        if self._from and self._to:
            from_indices = timestamps > self._from
            to_indices = timestamps <= self._to
            return from_indices & to_indices
        elif self._from:
            return timestamps > self._from
        elif self._to:
            return timestamps <= self._to
        else:
            return np.ones(timestamps.shape, dtype=np.bool)
