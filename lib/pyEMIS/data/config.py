import os.path
from configparser import SafeConfigParser, NoSectionError, NoOptionError, Error

class ConfigurationFileError(Error):
    def __init__(self, message, filename):
        Error.__init__(self, message)
        self.filename = filename

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
        except NoSectionError as e:
            raise ConfigurationFileError('Section [%s] not found in configuration file (sections = %s).' % (self.section, self.parser.sections()), self.config_file)
        except NoOptionError as e:
            raise ConfigurationFileError('Option "%s = ..." not in section [%s] of configuration file (options = %s).' % (name, self.section, self.parser.options(self.section)), self.config_file)
