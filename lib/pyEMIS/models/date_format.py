from numpy import array, unique, zeros, zeros_like, dtype, float64

from ..data import utils
from ..models.base import Base, GroupedModel

class Factory(object):
    def __init__(self, factory, format):
        self.factory = factory
        self.format = format

    def __call__(self, training_data):

        def grouping_function(data):
            datetimes = utils.datetime_from_timestamp(data['timestamp'])
            return array([dt.strftime(self.format) for dt in datetimes])
        return GroupedModel(training_data, self.factory, grouping_function)
