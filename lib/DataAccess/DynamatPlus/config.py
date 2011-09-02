from ConfigParser import ConfigParser

class config(ConfigParser):
    """
	The configuration object for a link to a Dynamat database.
    Each section is a database.
    DEFAULT values can be provided in the [DEFAULT] section.
    """
    def __init__(self, file, database='Sample'):
        ConfigParser.__init__(self)
        self.read(file)
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
    #using the following line I should be able to write a default config for a given machine
    #User may want to change so this could just be the predefined option in GUI wizard or something
    #from socket import gethostname; print gethostname()    
    from os.path import split, join
    test = config(join(split(__file__)[0], 'example.ini'))
    print 'DEFAULT'
    print test.host()
    print test.db()
    dbs = test.getDatabases()
    db = dbs[1]
    test.setDatabase(db)
    print db
    print test.host()
    print test.db()
