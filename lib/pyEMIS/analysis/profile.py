from datetime import datetime, timedelta

from numpy import where

from .base import AnalysisBase
from ..data import utils

class SimpleProfile(AnalysisBase):
    """This class will create profile data for any dataset
    """
    def __init__(self, dataset, model_factory, resolution, sd_limit=None):
        super(SimpleProfile, self).__init__(dataset) #No drivers with the simple models
        self.model_factory = model_factory
        self._data = self.data(resolution, sd_limit)

    def set_baseline(self, start, length):
        """
        start is a datetime
        length is a timedelta
        """
        end = start + length
        ts_start, ts_end = utils.timestamp_from_datetime([start, end])
        self.baseline_indices = where((self._data['timestamp'] < ts_end) & (self._data['timestamp'] >= ts_start))
        self.baseline_model = self.model_factory(self._data[self.baseline_indices])

    def percentiles(self, start, percentiles = [10, 25, 75, 90]):
        end = start + timedelta(days=7)
        ts_start, ts_end = utils.timestamp_from_datetime([start, end])
        this_week_indices = where((self._data['timestamp'] < ts_end) & (self._data['timestamp'] >= ts_start))
        this_week = self._data[this_week_indices]
        result = {}
        pred = self.baseline_model.prediction(this_week)
        for p in percentiles:
            result[p] = pred + self.baseline_model.percentile_in_place(this_week, p)
        return result


def plot_profile(axes, dt, percentiles, **kwargs):
    #A visualisation where the central peak is highlighted
    levels = [int(key) for key in percentiles.keys()]
    while len(levels) > 1:
        levels = sorted(levels)
        upper_level = levels.pop()
        levels.reverse()
        lower_level = levels.pop()
        axes.fill_between(dt, percentiles[lower_level], percentiles[upper_level], **kwargs)
    if len(levels) == 1:
        axes.plot(dt, percentiles[levels[0]], **kwargs)


def plot_profile2(axes, dt, percentiles, labels=None, colors=None, **kwargs):
    from matplotlib import pyplot as plt
    #A visualisation where layers are given specific colors and labels
    levels = sorted([int(key) for key in percentiles.keys()])
    result = []
    for upper, lower, color, label in zip([None] + levels, levels + [None], [None] + colors, [None] + labels):
        if upper and lower:
            axes.fill_between(dt, percentiles[lower], percentiles[upper], color=color, label=label, **kwargs)
            result.append(plt.Rectangle((0, 0), 1, 1, fc=color, **kwargs))
    return result
