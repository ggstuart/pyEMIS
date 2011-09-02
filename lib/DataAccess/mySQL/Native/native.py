from .. import MySQLSource
#from classic import MySQLSource
#import MySQLdb
#import sys
import time

class Native(MySQLSource):
  """
  Implements a save() function to store cleaned data from other sources
  Provides clean, interpolated data designed as a simple, fast solution for daily analysis and clean data sharing
  """
  def __init__(self, resolution=60*60*24):
    MySQLSource.__init__(self)
    if resolution==60*60*24: suffix = 'daily'
    elif resolution==60*30: suffix = 'hh'
    elif resolution==60*60*24*7: suffix = 'weekly'
    else:
      print "I don't understand a resolution of %s" % resolution
      sys.exit(1)
    self.cons_table = '%s' % suffix
    self.temp_table = 'temp_%s' % suffix
     
  def consumption(self, meter_id):
#    try:
      #missing data should be idenified in database
      sql = "SELECT date, value FROM %s LEFT JOIN datasets ON %s.datasets_id = datasets.id WHERE channel_id = %s" % (self.cons_table, self.cons_table, str(meter_id))
      return self._convert(self.query(sql))
#      self.cursor.execute (sql)
#      return self._convert(self.cursor.fetchall())
#    except MySQLdb.Error, e:
#      print "Error: %d: %s" % (e.args[0], e.args[1])
#      sys.exit(1)

  def temperature(self, meter_id):
    try:
      #, missing
      sql = "SELECT date, value FROM %s LEFT JOIN datasets ON %s.datasets_id = datasets.id WHERE channel_id = %s" % (self.temp_table, self.temp_table, str(meter_id))
      self.cursor.execute (sql)
      return self._convert(self.cursor.fetchall())
    except MySQLdb.Error, e:
      print "Error: %d: %s" % (e.args[0], e.args[1])
      sys.exit(1)

  def readings(self, meter_id, temperature=False):
    if temperature: return self.temperature(meter_id)
    return self.consumption(meter_id)
    
  def meter(self, dataset_id):
    try:
      sql = """SELECT 
      datasets.id as dataset_id, 
      datasets.name as name, 
      dataset_types.id as dataset_type_id, 
      dataset_types.name as dataset_type
      FROM datasets 
      LEFT JOIN dataset_types ON datasets.type_id = dataset_types.id
      WHERE datasets.id =  '%s'""" % str(dataset_id)
      self.cursor.execute (sql)
      return self.cursor.fetchone ()
    except MySQLdb.Error, e:
      print "Error: %d: %s" % (e.args[0], e.args[1])
      sys.exit(1)

  def meters(self):
    try:
      sql = """SELECT 
      datasets.id, 
      datasets.channel_id as source_id,
      datasets.name as name, 
      dataset_types.name as dataset_type
      FROM datasets 
      LEFT JOIN dataset_types ON datasets.dataset_types_id = dataset_types.id"""
      self.cursor.execute (sql)
      return self.cursor.fetchall ()
    except MySQLdb.Error, e:
      print "Error: %d: %s" % (e.args[0], e.args[1])
      sys.exit(1)

  def save_consumption(self, date, integ, meter_id):
#    d = [(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(date[i])), integ[i], meter_id) for i in range(len(date))]
    d = [(time.strftime('%Y-%m-%d', time.gmtime(date[i])), integ[i], meter_id) for i in range(len(date))]
    sql = """INSERT INTO %s""" % self.cons_table
    sql = sql + """(date, value, datasets_id) VALUES (%s, %s, %s)"""
    try:
      self.cursor.executemany(sql, d)
      self.conn.commit()
    except MySQLdb.Error, e:
      print "Error: %d: %s" % (e.args[0], e.args[1])
      sys.exit(1)

  def save_temperature(self, date, integ, meter_id):
    d = [(time.strftime('%Y-%m-%d', time.gmtime(date[i])), integ[i], meter_id) for i in range(len(date))]
    sql = """INSERT INTO %s""" % self.temp_table
    sql = sql + """(date, value, datasets_id) VALUES (%s, %s, %s)"""
    try:
      self.cursor.executemany(sql, d)
      self.conn.commit()
    except MySQLdb.Error, e:
      print "Error: %d: %s" % (e.args[0], e.args[1])
      sys.exit(1)


  def save_meter(self, meter):
    try:
      channel_type_id = self.save_channel_type(meter['channel_type'])
      sql = """INSERT INTO datasets(`channel_id`, `name`, `dataset_types_id`) VALUES(%s, '%s', %s)""" % (meter['channel_id'], meter['channel_name'], channel_type_id)
      self.cursor.execute(sql)
      print sql
      self.conn.commit()
      return self.cursor.lastrowid
    except MySQLdb.Error, e:
      if e.args[0] == 1062:
        sql = """SELECT `id` FROM `datasets` WHERE `channel_id` = '%s'""" % meter['channel_id']
        self.cursor.execute(sql)
        return int(self.cursor.fetchone()['id'])
      else: raise e
      
  def save_channel_type(self, channel_type):
    try:
      sql = """INSERT INTO dataset_types(`name`) VALUES('%s')""" % channel_type
      self.cursor.execute(sql)
      print sql
      self.conn.commit()
      return self.cursor.lastrowid
    except MySQLdb.Error, e:
      if e.args[0] == 1062:
        sql = """SELECT `id` FROM `dataset_types` WHERE `name` = '%s'""" % channel_type
        self.cursor.execute(sql)
        return int(self.cursor.fetchone()['id'])
      else: raise e
      
  #convert sql output to numpy ndarrays
  def _convert(self, result, data_col='value'):
      date = self._convert_to_date([r['date'] for r in result])
      value = self._convert_to_float([r[data_col] for r in result])
      return date, value


#load HH data from classic database and push it into a new cleanDaily one
def test_data():
  from factory import DataFactory
  from classic import Classic
  try:
    print '-'*100
    clean = CleanData()
    df = DataFactory(Classic)
    meters = df.meters()
    for m in meters:
      if m['channel_type'] == 'Energy':
        pass
#        meter_id = clean.save_meter(m)
#        date, integ = df.consumption(m['channel_id'], sd_limit=30, resolution=60*60*24)
#        clean.save_consumption(date, integ, meter_id)
      elif m['channel_type'] == 'Temperature':
        meter_id = clean.save_meter(m)
        date, temp = df.temperature(m['channel_id'], sd_limit=10, resolution=60*60*24)
        clean.save_temperature(date, temp, meter_id)
#      else: print m['channel_type']
  finally:
    print '-'*100


if __name__ == "__main__":
  test_data()
