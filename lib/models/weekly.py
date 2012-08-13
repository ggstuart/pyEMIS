from pyEMIS.data import utils

from date_format import DateFormat

import numpy as np

class Factory(object):
    def __init__(self, factory):
        self.factory = factory

    def __call__(self, data):
        model = DateFormat(self.factory, "%a %H:%M")
        model(data)
        return model
