from pkg_resources import load_entry_point, iter_entry_points, DistributionNotFound

from ..config import ConfigurationFileError
from ..config import Config
from .. import DataError

group = 'pyEMIS.data'

class AdapterError(DataError): pass

def adapter_instance_from_config(config):
    try:
        adapter_name = config.adapter

    except ConfigurationFileError as e:
        raise AdapterError("The file [%s] must include an option like 'adapter = ...' under the section %s" % (e.filename, config.section))

    try:
        adapter = load_entry_point(adapter_name, group, 'adapter')

    except DistributionNotFound:
        adapters = [str(ep) for ep in iter_entry_points(group=group)]
        if adapters:
            raise AdapterError("Adapter '%s' (from [%s]) is not installed. \n\nTry one of these %s." % (adapter_name, config.config_file, adapters))
        else:
            raise AdapterError("Adapter '%s' not found, no plugins are installed." % adapter_name)

    return adapter(config)

def get_adapter(section):
    config = Config(section)
    return adapter_instance_from_config(config)

def installed_adapters():
    return [str(ep) for ep in iter_entry_points(group=group)]
