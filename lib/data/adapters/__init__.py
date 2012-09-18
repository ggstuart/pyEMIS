from pyEMIS.data.config import ConfigurationFileError
from pyEMIS.data.config import Config

class AdapterError(Exception): pass

def adapter_instance_from_config(config):
    try:
        adapter_name = config.adapter
    except ConfigurationFileError, e:
        raise AdapterError, "The file [%s] must include an option like 'adapter = ...' under the section %s" % (e.filename, config.section)
    try:
        module = __import__(adapter_name, globals(), locals(), ['Adapter'], -1)
    except ImportError:
        raise AdapterError, "Adapter '%s' not found (from configuration file at [%s])." % (adapter_name, config.config_file)
    return module.Adapter(config)

def get_adapter(section):
    config = Config(section)
    return adapter_instance_from_config(config)
    
if __name__ == "__main__":
    adapter = get_adapter('Dynamat_DMU')
    print adapter

    adapter = get_adapter('british_gas')
    print adapter

