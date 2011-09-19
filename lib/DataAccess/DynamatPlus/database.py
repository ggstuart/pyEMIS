import pymssql, logging
from config import config

class DynamatPlus():
    """
    The dynamat database uses a dynamat config object so it needs a config file.
    """
    def __init__(self, file, database='Sample'):
        self.conf = config(file, database)
        self.conn = pymssql.connect(host=self.conf.host(),user=self.conf.user(),password=self.conf.password(),database=self.conf.db(), as_dict=True)
        self.cur = self.conn.cursor()

    def query(self, sql):
        logging.debug(sql)
        self.cur.execute(sql)
        return self.cur.fetchall()

    def rootNode(self): return self.query("SELECT * FROM Tree WHERE Parent_Node_ID=0")[0]
    def node(self, Node_ID): return self.query("SELECT * FROM Tree WHERE Node_ID=%s" % str(Node_ID))[0]
    def nodeList(self): return self.query("SELECT Node_ID, Parent_Node_ID, Object_ID, Object_Description FROM Tree;")
    def nodeForNode(self, Node_ID): return self.query("SELECT Node_ID, Object_ID, Object_Type, Object_Description FROM Tree WHERE Parent_Node_ID = %s;" % str(Node_ID))

    def site(self, id): return self.query("SELECT * FROM Site WHERE Site_ID=%s" % id)[0]
    def siteList(self): return self.query("SELECT Site_ID, Name FROM Site;")
    def sitesForSite(self, Site_ID): return self.query("SELECT Site.Site_ID, Site.Name FROM Site LEFT JOIN Tree AS Child ON Site.Site_ID = Child.Object_ID AND Child.Object_Type = 16 LEFT JOIN Tree AS Parent ON Parent.Node_ID = Child.Parent_Node_ID AND Parent.Object_Type = 16 WHERE Parent.Object_ID = %s;" % str(Site_ID))
    def sitesForNode(self, Node_ID): return self.query("SELECT Site.Site_ID, Site.Name FROM Site LEFT JOIN Tree ON Site.Site_ID = Tree.Object_ID WHERE Tree.Object_Type = 16 AND Tree.Node_ID = %s;" % str(Node_ID))

    def meterList(self): return self.query("SELECT Meter_ID, Description FROM Meter;")

    def metersForNode(self, Node_ID): return self.query("SELECT Meter.Meter_ID, Meter.Description FROM Meter LEFT JOIN Tree ON Meter.Meter_ID = Tree.Object_ID WHERE Tree.Object_Type = 32 AND Tree.Node_ID = %s;" % str(Node_ID))
    
    def metersForSite(self, Site_ID): return self.query("SELECT Meter.Meter_ID, Meter.Description FROM Meter LEFT JOIN Tree AS MeterNodes ON Meter.Meter_ID = MeterNodes.Object_ID AND MeterNodes.Object_Type = 32 LEFT JOIN Tree AS SiteNodes ON MeterNodes.Parent_Node_ID = SiteNodes.Node_ID AND SiteNodes.Object_Type = 16 WHERE SiteNodes.Object_ID = %s" % str(Site_ID))
 
    def metersSummary(self, Site_ID): return self.query("SELECT Meter.Meter_ID, Meter.Description, COUNT(Reading_DateTime) as count, MIN(Reading_DateTime) as first, MAX(Reading_DateTime) as last FROM Meter LEFT JOIN Tree AS MeterNodes ON Meter.Meter_ID = MeterNodes.Object_ID AND MeterNodes.Object_Type = 32 LEFT JOIN Tree AS SiteNodes ON MeterNodes.Parent_Node_ID = SiteNodes.Node_ID AND SiteNodes.Object_Type = 16 LEFT JOIN Meter_Reading ON Meter.Meter_ID = Meter_Reading.Meter_ID WHERE SiteNodes.Object_ID = %s GROUP BY Meter.Meter_ID, Meter.Description ORDER BY MIN(Reading_DateTime) ASC;" % str(Site_ID))

#    def readingsList(self, meter_id) : return self.query("SELECT Reading_DateTime, Reading_Or_Total, Delivered_Or_Movement FROM Meter_Reading WHERE Meter_ID = %s;" % meter_id)
    def readingsList(self, meter_id) : return self.query("SELECT Reading_DateTime, Reading_Or_Total/Units_Per_GJ/0.0036 as Reading_Or_Total, Delivered_Or_Movement/Units_Per_GJ/0.0036 as Delivered_Or_Movement FROM Meter_Reading, Meter, Units WHERE Meter.Meter_ID = Meter_Reading.Meter_ID AND Units.Unit_ID=Meter.Measured_Unit_ID AND Meter.Meter_ID = '%s'" % meter_id)
    def temperatureList(self, meter_id) : return self.query("SELECT Reading_DateTime, Reading_Or_Total, Delivered_Or_Movement FROM Meter_Reading, Meter WHERE Meter.Meter_ID = Meter_Reading.Meter_ID AND Meter.Meter_ID = '%s'" % meter_id)

    def readingsSummary(self, meter_id): return self.query("SELECT COUNT(Reading_DateTime) as count, MIN(Reading_DateTime) as first, MAX(Reading_DateTime) as last FROM Meter_Reading WHERE Meter_ID = %s;" % meter_id)

    def nodesForNode(self, parent_node_id, child_object_type=None, child_object_subtype=None):
        sql = "SELECT t2.* FROM Tree t1 INNER JOIN Tree t2 ON t1.node_id = t2.parent_node_id WHERE t1.node_id = %s" % str(parent_node_id)
        if object_type: sql += " AND t2.object_type = %s" % str(child_object_type)
        if object_subtype: sql += " AND t2.object_subtype = %s" % str(child_object_subtype)
        return self.query(sql)

    def virtualMetersForSite(self, Site_ID): return self.query("SELECT Meter.Meter_ID, Meter.Description FROM Meter LEFT JOIN Tree t1 ON Meter.Meter_ID = t1.Object_ID INNER JOIN Tree t2 ON t1.node_id = t2.parent_node_id WHERE t1.object_id = 75 AND t1.object_type = 16 AND t2.object_subtype = 6" % str(Site_ID))

    def __del__(self):
        self.conn.close

if __name__ == "__main__":
    from os.path import split, join
    dynamat = DynamatPlus(join(split(__file__)[0], 'test.ini'), 'AIM4SMES')
    print dynamat.siteList()[0]['Name']
    print dynamat.site(32)['Name']
    
