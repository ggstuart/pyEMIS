import pymssql, logging
from ConfigParser import ConfigParser

class DynamatPlus(object):
    # doctest: +ELLIPSIS
    """
    The dynamat database uses a dynamat config object so it needs a config file.
    >>> import os.path, pyEMIS.DataAccess as DA
    >>> config_path = os.path.expanduser('~/.EMIS/config.cfg')
    >>> src = DA.sources.DynamatPlus(config_path, "DynamatPlus")
    >>> src #doctest: +ELLIPSIS
    <pyEMIS.DataAccess.sources.dynamatPlus.DynamatPlus object at ...>
    >>>
    """
    def __init__(self, config_file, database='Sample'):
        self._logger = logging.getLogger('DynamatPlus')
        conf = config(config_file, database)
        self.conn = pymssql.connect(host=conf.host(), user=conf.user(), password=conf.password(), database=conf.db(), as_dict=True)
        self.cur = self.conn.cursor()

    #Prevent SQL injection by passing args directly to execute function rather than using string formatting stuff
    def _query(self, sql, *args):
        """
        The _query method
        >>> import os.path, pyEMIS.DataAccess as DA, logging
        >>> logging.basicConfig(level=logging.INFO)
        >>> config_path = os.path.expanduser('~/.EMIS/config.cfg')
        >>> src = DA.sources.DynamatPlus(config_path, "DynamatPlus")
        >>> src._query("SELECT * FROM Meter WHERE Meter_ID = %s", 111)
        >>> 
        """
        self._logger.debug(sql % (args))
        self.cur.execute(sql, args)
        return self.cur.fetchall()

    def meter(self, meter_id):
        return self._query("SELECT Meter_ID, Description, meter_type FROM Meter WHERE meter_id = %s;", meter_id)

    def meterList(self):
        return self._query("SELECT Meter_ID, Description FROM Meter;")

    def readingsList(self, meter_id):
        return self._query("SELECT Reading_DateTime, Reading_Or_Total/Units_Per_GJ/0.0036 as Reading_Or_Total, Delivered_Or_Movement/Units_Per_GJ/0.0036 as Delivered_Or_Movement FROM Meter_Reading, Meter, Units WHERE Meter.Meter_ID = Meter_Reading.Meter_ID AND Units.Unit_ID=Meter.Measured_Unit_ID AND Meter.Meter_ID = '%s'", meter_id)

    def temperatureList(self, meter_id):
        return self._query("SELECT Reading_DateTime, Reading_Or_Total, Delivered_Or_Movement FROM Meter_Reading, Meter WHERE Meter.Meter_ID = Meter_Reading.Meter_ID AND Meter.Meter_ID = '%s'", meter_id)

    def virtualMetersForSite(self, Site_ID):
        return self._query("SELECT Meter.Meter_ID, Meter.Description FROM Meter LEFT JOIN Tree t1 ON Meter.Meter_ID = t1.Object_ID INNER JOIN Tree t2 ON t1.node_id = t2.parent_node_id WHERE t1.object_id = 75 AND t1.object_type = 16 AND t2.object_subtype = 6", str(Site_ID))

    def __del__(self):
        self.conn.close


class config(ConfigParser):
    """
	The configuration object for a link to a Dynamat database.
    Each section is a database.
    DEFAULT values can be provided in the [DEFAULT] section.
    """
    def __init__(self, config_file, database='Sample'):
        ConfigParser.__init__(self)
        self.read(config_file)
        self._section = database

    def setDatabase(self, database):
        self._section = database

    def getDatabases(self):
        return self.sections()
        
    def host(self): return self.get(self._section, 'host')
    def user(self): return self.get(self._section, 'user')
    def password(self): return self.get(self._section, 'password')
    def db(self): return self.get(self._section, 'db')

if __name__ == "__main__":
    import doctest
    doctest.testmod()
