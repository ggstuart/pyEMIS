#import MySQLdb
from MySQLdb import connect, cursors, Error
import numpy as np
import os.path, calendar, sys

class MySQLSource(object):
  """Parent object for all mySQL datasources"""
  def __init__(self, config_path=os.path.expanduser('~/.EMIS/config.cfg')):
    conf = config(self.__class__.__name__, config_path)
    try:
      self.conn = connect(host = conf['host'], user = conf['user'], passwd = conf['passwd'], db = conf['db'])
      self.cursor = self.conn.cursor (cursors.DictCursor)
    except Error, e:
      if e.args[0] == 1045:
        print 'Invalid configuration for [%s] at %s' % (self.__class__.__name__, config_path)
        sys.exit(1)
      else: raise
#      import traceback
#      traceback.print_exc()
#      print "Error: %d: %s" % (e.args[0], e.args[1])
#      print 'MySQLSource.__init__()'

  def query(self, sql):
    try:
      self.cursor.execute (sql)
      return self.cursor.fetchall ()
    except Error, e:
      if e.args[0] == 1054:
        print "invalid sql"
        print e.args[1]
        print sql
        sys.exit(1)
      else:
#        print "Error: %d: %s" % (e.args[0], e.args[1])
        raise
#        sys.exit(1)

  def __del__(self):
    try:
      self.cursor.close ()
      self.conn.close ()
    except AttributeError, e:
      pass

  #convert sql date to numpy ndarray
  def _convert_to_date(self, data):
      result = [calendar.timegm(t.timetuple()) for t in data]
      result = np.array(result, dtype=float)
      return result

  #convert sql data to numpy ndarray float
  def _convert_to_float(self, data):
      return np.array(data, dtype=float)

def config(section, path):
  if not os.path.exists(path):
    print 'No configuration file at %s' % path
    exit(1)
  from ConfigParser import SafeConfigParser, NoSectionError
  cfg = SafeConfigParser()
  cfg.read(path)
  if not cfg.has_section(section):
    print 'No configuration for "%s" in %s' % (section, path)
    exit(1)
  return dict(cfg.items(section))

