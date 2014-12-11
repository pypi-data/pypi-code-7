import glob
import logging
import os

_ETC_PATHS = [ '/etc/' ]
_MAIN_CONFIG_FILE = "app.cfg"
_CONFIG_VAR_INCLUDE = ""
_CONFIG_FILTER = "*.cfg"

def set_paths(etc_paths = [ "/etc/" ]):
    global _ETC_PATHS
    _ETC_PATHS = []
    for p in etc_paths:
        _ETC_PATHS.append(os.path.expanduser(p))
    
def set_main_config_file(c_file):
    global _MAIN_CONFIG_FILE
    _MAIN_CONFIG_FILE = c_file
    
def set_config_filter(config_var_include = "CONFIG_DIR", filter_ = "*.cfg"):
    global _CONFIG_VAR_INCLUDE, _CONFIG_FILTER
    _CONFIG_VAR_INCLUDE = config_var_include
    _CONFIG_FILTER = filter_

_LOGGER = logging.getLogger("[CONFIG]")

def config_filename(filename):
    global _ETC_PATHS
    if filename.startswith('/'):
        _LOGGER.info("using absolute path for filename \"%s\"" % filename)
        return filename

    import os.path
    for fpath in _ETC_PATHS:
        current_path = "%s/%s" % (fpath, filename)
        if os.path.isfile(current_path):
            current_path = os.path.realpath(current_path)
            _LOGGER.info("using path \"%s\" for filename \"%s\"" % (current_path, filename))
            return current_path

    _LOGGER.info("using path \"%s\" for filename \"%s\"" % (filename, filename))
    return filename

def read_config(section, variables, sink, filename = None):
    global _ETC_PATHS
    import ConfigParser
    config = ConfigParser.ConfigParser()
    
    if filename is None:
        config_files = existing_config_files()
    else:
        config_files = []
        for fpath in _ETC_PATHS:
            config_files.append("%s/%s" % (fpath, filename))
    
    config.read(config_files)

    options = {}
    if section in config.sections():
        options = config.options(section)

    for varname, value in variables.items():
        varname = varname.lower()
        if varname in options:
            if isinstance(value, bool):
                value = config.getboolean(section, varname)
            elif isinstance(value, int):
                value = config.getint(section, varname)
            else:
                value = config.get(section, varname)
                if len(value) > 0:
                    value = value.split("#")[0].strip()
                
        varname = varname.upper()
        sink.__dict__[varname] = value
        _LOGGER.debug("%s=%s" % (varname, str(value)))

class Configuration():
    def __init__(self, section, variables, filename = None):
        read_config(section, variables, self, filename)

def existing_config_files():
    global _ETC_PATHS
    global _MAIN_CONFIG_FILE
    global _CONFIG_VAR_INCLUDE
    global _CONFIG_FILTER

    config_files = []
    for possible in _ETC_PATHS:
        config_files = config_files + glob.glob("%s%s" % (possible, _MAIN_CONFIG_FILE))
    
    if _CONFIG_VAR_INCLUDE != "":
        main_config = Configuration("general", {
            _CONFIG_VAR_INCLUDE:""
        }, _MAIN_CONFIG_FILE)

        if main_config.CONFIG_DIR != "":
            for possible in _ETC_PATHS:
                config_files = config_files + glob.glob("%s%s/%s" % (possible, main_config.CONFIG_DIR, _CONFIG_FILTER))
            
    return config_files