from mySQLSource import MySQLSource
#from MySQLdb import Error as SQLError
#from mySQLSource import MySQLSource

class Classic(MySQLSource):
  """Provides raw data from the 'classic format' mySQL database designed by Graeme Stuart for his PhD"""

  def consumption(self, meter_id):
    return self.readings(meter_id)

  def temperature(self, meter_id):
    date, integ, movement = self.readings(88)#, temperature=True)
    return date, integ, movement

  def readings(self, meter_id):#, temperature=False):#, convert=True):
    sql = "SELECT DISTINCT date_sql, integ, movement FROM tbl_meter_data WHERE channel_id = %s AND date_sql > 0 ORDER BY date_sql" % str(meter_id)
    return self._convert(self.query(sql))

  #convert sql output to numpy ndarrays
  def _convert(self, result, movement=False):
    date = self._convert_to_date([r['date_sql'] for r in result])
    integ = self._convert_to_float([r['integ'] for r in result])
    move = self._convert_to_float([r['movement'] for r in result])
    return date, integ, move

  def meter(self, meter_id):
    try:
      sql = """
SELECT tbl_channels.id as channel_id, tbl_channels.name as channel_name, tbl_sites.id as site_id, tbl_sites.Site as site_name,
measured_units.id as measured_unit_id, measured_units.name as measured_unit_name, measured_units.suffix as measured_unit_suffix,
tbl_channel_units.multiplier, tbl_channel_types.id as channel_type_id, tbl_channel_types.channel_type, base_units.id as base_unit_id, 
base_units.name as base_unit_name, base_units.suffix as base_unit_suffix, tbl_unit_conversions.coefficient
FROM tbl_channels Left Join tbl_sites ON tbl_channels.site_id = tbl_sites.id
Left Join tbl_channel_units ON tbl_channels.channel_unit_id = tbl_channel_units.id
Left Join tbl_units AS measured_units ON tbl_channel_units.unit_id = measured_units.id
Left Join tbl_channel_types ON tbl_channels.channel_type_id = tbl_channel_types.id
Left Join tbl_units AS base_units ON base_units.id = tbl_channel_types.unit_id
Left Join tbl_unit_conversions ON tbl_unit_conversions.from_unit_id = measured_units.id AND tbl_unit_conversions.to_unit_id = base_units.id
WHERE tbl_channels.id = '%s'""" % str(meter_id)
      self.cursor.execute (sql)
      return self.cursor.fetchone ()
    except SQLError, e:
      print "Error: %d: %s" % (e.args[0], e.args[1])
      sys.exit(1)

  def locations(self):
    sql = """
    SELECT id, site as name
    FROM tbl_sites
    """
    return self.query(sql)

  def metersForLocation(self, id):
    sql = """
    SELECT ch.id, ch.name, t.channel_type as type
    FROM tbl_channels AS ch
    LEFT JOIN tbl_channel_types as t ON ch.channel_type_id = t.id
    WHERE ch.site_id = %i
    """ % id
    return self.query(sql)

  def meters(self):
#    try:
#      sql = """
#SELECT tbl_channels.id as channel_id, tbl_channels.name as channel_name, tbl_sites.id as site_id, tbl_sites.Site as site_name,
#measured_units.id as measured_unit_id, measured_units.name as measured_unit_name, measured_units.suffix as measured_unit_suffix,
#tbl_channel_units.multiplier, tbl_channel_types.id as channel_type_id, tbl_channel_types.channel_type, base_units.id as base_unit_id, 
#base_units.name as base_unit_name, base_units.suffix as base_unit_suffix, tbl_unit_conversions.coefficient
#FROM tbl_channels Left Join tbl_sites ON tbl_channels.site_id = tbl_sites.id
#Left Join tbl_channel_units ON tbl_channels.channel_unit_id = tbl_channel_units.id
#Left Join tbl_units AS measured_units ON tbl_channel_units.unit_id = measured_units.id
#Left Join tbl_channel_types ON tbl_channels.channel_type_id = tbl_channel_types.id
#Left Join tbl_units AS base_units ON base_units.id = tbl_channel_types.unit_id
#Left Join tbl_unit_conversions ON tbl_unit_conversions.from_unit_id = measured_units.id AND tbl_unit_conversions.to_unit_id = base_units.id"""
    sql = """
    SELECT ch.id, ch.name, t.channel_type as type
    FROM tbl_channels AS ch
    LEFT JOIN tbl_channel_types as t ON ch.channel_type_id = t.id
    """
    return self.query(sql)
#      self.cursor.execute (sql)
#      return self.cursor.fetchall ()
#    except SQLError, e:
#      print "Error: %d: %s" % (e.args[0], e.args[1])
#      sys.exit(1)



if __name__ == "__main__":
  import matplotlib.pyplot as plt
  df = DataFactory(config())
  d = df.data(180)
  plt.scatter(d['temperature'], d['consumption'])
  plt.show()
