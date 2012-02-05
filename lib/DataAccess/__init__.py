__version__ = '0.1'
__all__ = ['DataFactory', 'sources', 'adapters']#, 'Classic', 'CleanData', 'Fake', 'DynamatPlus']

from config import config
from dal import DataAccessLayer
import sources
import adapters

