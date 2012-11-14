import os.path
from ConfigParser import SafeConfigParser, NoSectionError, NoOptionError, Error

class ConfigurationFileError(Error):
    def __init__(self, message, filename):
        Error.__init__(self, message)
        self.filename = filename

#class Config_old(object):
#    """
#	The configuration object for a link to a database.
#    """
#    def __init__(self, database, config_file=os.path.expanduser('~/.EMIS/pyEMIS.ini')):
#        parser = SafeConfigParser()
#        parser.read(config_file)
#        if not parser.has_section(database):
#            raise KeyError, 'Section [%s] not found in config file [%s]' % (database, config_file)
#        self.host = parser.get(database, 'host')
#        self.user = parser.get(database, 'user')
#        self.password = parser.get(database, 'password')
#        self.db = parser.get(database, 'db')

class Config(object):
    """
	The configuration object for a link to a database.
    """
    def __init__(self, section=None, config_file=None):
        self.parser = SafeConfigParser()#allow_no_value=True)

        default_file = os.path.expanduser('~/.EMIS/pyEMIS.ini')
        if not config_file:
            config_file = default_file
        self.config_file = config_file

        if not section:
            section = 'DEFAULT'
        self.section = section

        read_files = self.parser.read(self.config_file)

        if not read_files:
            self.parser.add_section(self.section)
            with open(default_file, 'wb') as configfile:
                self.parser.write(configfile)

        if not self.parser.has_section(self.section):
            raise ConfigurationFileError('Section [%s] not found in configuration file (sections = %s).' % (self.section, self.parser.sections()), self.config_file)

    def __getattr__(self, name):
        try:
            return self.parser.get(self.section, name)
        except NoSectionError, e:
            raise ConfigurationFileError('Section [%s] not found in configuration file (sections = %s).' % (self.section, self.parser.sections()), self.config_file)
        except NoOptionError, e:
            raise ConfigurationFileError('Option "%s = ..." not in section [%s] of configuration file (options = %s).' % (name, self.section, self.parser.options(self.section)), self.config_file)

if __name__ == "__main__":
    config_dmu = Config(section='Dynamat_DMU')
    print config_dmu.adapter
    print config_dmu.host
    print config_dmu.db
    print config_dmu.user
    print '*' * len(config_dmu.password)

    config_none = Config('does_not_exist')
    try:
        print config_none.adapter
    except ConfigurationFileError, e:
        print e
        print e.filename


    config_phd = Config('Graeme_PhD')
    print config_phd.adapter
    try:
        print config_phd.poop
    except ConfigurationFileError, e:
        print e
        print e.filename

