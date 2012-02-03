__version__ = '0.1'
__all__ = ['DataFactory', 'sources', 'adapters']#, 'Classic', 'CleanData', 'Fake', 'DynamatPlus']

#The data factory provides nice, formatted datasets from a given source ready to analyse
from dal import DataAccessLayer

import sources
import adapters

