import os.path
from ConfigParser import ConfigParser

class config(ConfigParser):
    """
	The configuration object for a link to a Dynamat database.
    Each section is a database.
    DEFAULT values can be provided in the [DEFAULT] section.
    """
    def __init__(self, config_file=os.path.expanduser('~/.EMIS/config.cfg'), database='DEFAULT'):
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

