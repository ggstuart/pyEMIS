import os.path
from ConfigParser import SafeConfigParser

class Config(object):
    """
	The configuration object for a link to a database.
    """
    def __init__(self, database, config_file=os.path.expanduser('~/.EMIS/pyEMIS.ini')):
        parser = SafeConfigParser()
        parser.read(config_file)
        if not parser.has_section(database):
            raise KeyError, 'Section [%s] not found in config file [%s]' % (database, config_file)
        self.host = parser.get(database, 'host')
        self.user = parser.get(database, 'user')
        self.password = parser.get(database, 'password')
        self.db = parser.get(database, 'db')

if __name__ == "__main__":
    config_dmu = Config('Dynamat_DMU')
    print config_dmu.host
    print config_dmu.db
    print config_dmu.user
    print '*' * len(config_dmu.password)
    config_phd = Config('Graeme_PhD')
    try:
        config_none = Config('does_not_exist')
    except KeyError, e:
        print e
   
