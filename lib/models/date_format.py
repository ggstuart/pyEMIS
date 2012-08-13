from numpy import array, unique, zeros, zeros_like, dtype, float64

from pyEMIS.data import utils
from pyEMIS.models.base import Base

class DateFormat(Base):
    def __init__(self, factory, format):
        """Configure the weekly elements of the model
        """
        self.format = format
        self._factory = factory

    def __call__(self, training_data):
        """Fit the model
        The data are split into subsets based on the date format
        A model is fitted to each subset and stored against its date format
        """
        _formats = array([dt.strftime(self.format) for dt in utils.datetime_from_timestamp(training_data['timestamp'])])
        _keys = unique(_formats)
        self._models = dict([(key, self._factory(training_data[_formats==key])) for key in _keys])
        self.n_parameters = sum([self._models[key].n_parameters for key in self._models.keys()])


    def prediction(self, independent_data):
        """Unpack the model
        The provided data are split into subsets based on the date format
        The model for each subset is used to generate a bit of the prediction
        """
        _formats = array([dt.strftime(self.format) for dt in utils.datetime_from_timestamp(independent_data['timestamp'])])
        result = zeros(independent_data.shape)
        for key in self._models.keys():
            indices = _formats==key
            result[indices] = self._models[key].prediction(independent_data[indices])
        return result

    def percentile(self, percentile):
        return dict([(k, self._models[k].percentile(percentile)) for k in self._models.keys()])

    def percentile_in_place(self, percentile, independent_data):
        result = zeros_like(independent_data['timestamp'])
        _formats = array([dt.strftime(self.format) for dt in utils.datetime_from_timestamp(independent_data['timestamp'])])
        p = self.percentile(percentile)
        for fmt, score in p.iteritems():
            result[_formats==fmt] = score
        return result

    def percentiles(self, independent_data, percentiles):
        """Unpack the model
        The provided data are split into subsets based on the date format
        The model for each subset is used to generate a bit of the percentiles
        The percentiles are then agregated into a final result
        """
        _formats = array([dt.strftime(self.format) for dt in utils.datetime_from_timestamp(independent_data['timestamp'])])
        result = dict([(p, array([0.0] * len(independent_data))) for p in percentiles])
        for key in self._models.keys():
            indices = _formats==key
            chunk = self._models[key].percentiles(independent_data[indices], percentiles)
            for p in chunk.keys():
                result[p][indices] = chunk[p]
        return result

    def profile(self, independent_data, percentiles):
        _formats = array([dt.strftime(self.format) for dt in utils.datetime_from_timestamp(independent_data['timestamp'])])
        _keys = self.model.keys()
        
