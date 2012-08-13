#Python Energy Management Information System Library

Includes tools for:

##Accessing data from a variety of sources

Currently supports

1. Energy Metering Technology's DynamatPlus database
2. Graeme Stuart's Classic PhD thesis database format (not very useful for anyone but me - GS)
3. A fake data source which generates random data

##Data cleaning and interpolation

Raw datasets can be scanned for extreme values which can then be removed.
Cleaned data are interpolated to a user-specified resolution.
Any missing data are identified and flagged with contiguous periods of missing data identified.
If large gaps are found at the beginning or end of the dataset they are removed.

##Constructing datasets from multiple time series

If two datasets need to be compared, 
they can be pulled from the data source, 
cleaned and interpolated to the same resolution 
and then mapped together so that each data value is correctly aligned.

##Consumption Modelling

Once prepared, data can be used to fit energy consumption models.
Models can be used to produce profiles
or to generate predicted energy consumption.

Advanced, experimental features include event detection. Use with care.

##TODO
Implement energy savings calculations when provided with **before** and **after** datasets.