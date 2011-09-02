__version__ = '0.1'
__all__ = ['DataFactory', 'Classic', 'CleanData', 'Fake', 'DynamatPlus']

#The data factory provides nice, formatted datasets from a given source ready to analyse
from factory import DataFactory

#Data sources - use these to get data in a basic format native to the source
from mySQL import Classic, Native
from DynamatPlus import DynamatPlus
from Fake import Fake






#===================================================================================================================

#Adapters may also be needed to transform the interface and format of data sources which are out of my control

#the duall library could be provided by someone else (but would probably just be imported in the duallAdapter file rather than here as it is not supported directly for users)
#import duall as libDuall?

#Ultimately, the interface allows for a simple reference to DataAccess.Duall and the config file will set it up under [Duall]
#from duallAdapter import DuallAdapter as Duall

#===================================================================================================================
