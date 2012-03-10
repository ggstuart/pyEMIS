import pymssql, logging
from .. import config

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
    def __init__(self, config_file, database='DynamatPlus'):
        self._logger = logging.getLogger('DynamatPlus')
        conf = config(config_file, database)
        try:
            self.conn = pymssql.connect(host=conf.host(), user=conf.user(), password=conf.password(), database=conf.db(), as_dict=True)
            self.cur = self.conn.cursor()
        except pymssql.InterfaceError, e:
            self._logger.error(e)
            self.conn = None
            self.cur = None
            raise

        except Exception, e:
            self._logger.error(e)
            raise


    #Prevent SQL injection by passing args directly to execute function rather than using string formatting stuff
    def _query(self, sql, *args):
        """
        The _query method is pretty straight forward.
        >>> import os.path, pyEMIS.DataAccess as DA, logging
        >>> config_path = os.path.expanduser('~/.EMIS/config.cfg')
        >>> src = DA.sources.DynamatPlus(config_path, "DynamatPlus")
        >>> src._query("SELECT Meter_ID, Description, meter_type FROM Meter WHERE Meter_ID = '%s'", 111)
        [{0: 111, 1: 'LEC/KIMB/EM01                 ', 2: 1, 'Description': 'LEC/KIMB/EM01                 ', 'meter_type': 1, 'Meter_ID': 111}]
        >>> 
        """
        self._logger.debug(sql % (args))
        self.cur.execute(sql, (args))
        return self.cur.fetchall()

    def meter(self, meter_id):
        """
        The meter method uses _query.
        >>> import os.path, pyEMIS.DataAccess as DA, logging
        >>> config_path = os.path.expanduser('~/.EMIS/config.cfg')
        >>> src = DA.sources.DynamatPlus(config_path, "DynamatPlus")
        >>> src.meter(111)
        [{0: 111, 1: 'LEC/KIMB/EM01                 ', 2: 1, 'Description': 'LEC/KIMB/EM01                 ', 'meter_type': 1, 'Meter_ID': 111}]
        >>> 
        """
        return self._query("SELECT Meter_ID as id, Description as description, meter_type as type FROM Meter WHERE meter_id = %s;", meter_id)[0]

    def meter_with_units(self, meter_id):
        """
        The meter method uses _query.
        >>> import os.path, pyEMIS.DataAccess as DA, logging
        >>> config_path = os.path.expanduser('~/.EMIS/config.cfg')
        >>> src = DA.sources.DynamatPlus(config_path, "DynamatPlus")
        >>> src.meter_with_units(111)
        [{0: 111, 1: 'LEC/KIMB/EM01                 ', 2: 1, 'Description': 'LEC/KIMB/EM01                 ', 'meter_type': 1, 'Meter_ID': 111}]
        >>> 
        """
        return self._query("SELECT m.Meter_ID as id, m.Description as description, m.meter_type as type, u.unit_description, u.unit_type, u.units_per_gj, u.units_per_cubic_metre, u.abbreviation FROM Meter m LEFT JOIN Units u ON m.measured_unit_id = u.unit_id WHERE meter_id = %s;", meter_id)[0]

#    def meterList(self):
#        return self._query("SELECT Meter_ID, Description FROM Meter;")

#    def readingsList(self, meter_id):
#        return self._query("SELECT Reading_DateTime, Reading_Or_Total/Units_Per_GJ/0.0036 as Reading_Or_Total, Delivered_Or_Movement/Units_Per_GJ/0.0036 as Delivered_Or_Movement FROM Meter_Reading, Meter, Units WHERE Meter.Meter_ID = Meter_Reading.Meter_ID AND Units.Unit_ID=Meter.Measured_Unit_ID AND Meter.Meter_ID = '%s'", meter_id)

#    def temperatureList(self, meter_id):
#        return self._query("SELECT Reading_DateTime, Reading_Or_Total, Delivered_Or_Movement FROM Meter_Reading, Meter WHERE Meter.Meter_ID = Meter_Reading.Meter_ID AND Meter.Meter_ID = '%s'", meter_id)

    def integColumn(self, meter_id):
        """No unit correction, just the raw integ data"""
        return self._query("SELECT Reading_DateTime as datetime, Reading_Or_Total as value FROM Meter_Reading WHERE Meter_ID = '%s'", meter_id)

    def movementColumn(self, meter_id):
        """No unit correction, just the raw movement data"""
        return self._query("SELECT Reading_DateTime as datetime, Delivered_Or_Movement as value FROM Meter_Reading WHERE Meter_ID = '%s'", meter_id)

    def energyColumn(self, meter_id):
        """Convert units to kWh"""
        return self._query("SELECT Reading_DateTime as datetime, Reading_Or_Total/Units_Per_GJ/0.0036 as value FROM Meter_Reading, Meter, Units WHERE Meter.Meter_ID = Meter_Reading.Meter_ID AND Units.Unit_ID=Meter.Measured_Unit_ID AND Meter.Meter_ID = '%s'", meter_id)

    def waterColumn(self, meter_id):
        """Convert units to m3"""
        return self._query("SELECT Reading_DateTime as datetime, Reading_Or_Total/Units_Per_Cubic_Metre as value FROM Meter_Reading, Meter, Units WHERE Meter.Meter_ID = Meter_Reading.Meter_ID AND Units.Unit_ID=Meter.Measured_Unit_ID AND Meter.Meter_ID = '%s'", meter_id)

    def childMeters(self, meter_id):
        """
        Returns a list of child meters for a given meter id
        This is used to pull meter_ids for a virtual meter and should only be called if the parent meter_type = 6
        """
        sql = """
            SELECT cNode.Virtual_Meter_Factor, cMeter.Meter_ID, cMeter.Description, cMeter.meter_type
            FROM METER pMeter
            INNER JOIN TREE pNode ON pMETER.METER_ID = pNODE.OBJECT_ID AND pNODE.Object_Type = 32
            INNER JOIN TREE cNode ON pNODE.NODE_ID = cNODE.PARENT_NODE_ID
            INNER JOIN METER cMETER ON cNODE.OBJECT_ID = cMETER.METER_ID AND cNODE.Object_Type = 32
            WHERE
            pMETER.METER_ID = %s
        """
        return self._query(sql, meter_id)

#    def virtualMetersForSite(self, Site_ID):
#        return self._query("SELECT Meter.Meter_ID, Meter.Description FROM Meter LEFT JOIN Tree parent ON Meter.Meter_ID = parent.Object_ID INNER JOIN Tree child ON parent.node_id = child.parent_node_id WHERE parent.object_id = 75 AND parent.object_type = 16 AND child.object_subtype = 6", str(Site_ID))

    def __del__(self):
        if self.conn:
            self.conn.close

if __name__ == "__main__":
    import doctest
    doctest.testmod()
