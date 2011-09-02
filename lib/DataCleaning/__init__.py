__version__ = '0.1'
__all__ = ['clean', 'hh', 'daily', 'weekly']

from cleaning import clean
from interpolation import interpolate, hh, daily, weekly
