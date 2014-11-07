
from optparse import BadOptionError, AmbiguousOptionError
from paste.script. bool_optparse import BoolOptionParser
from pkg_resources import resource_stream
import ConfigParser, os
import urllib2
from gae_command.version import __version__


headers={
	'User-Agent': 'gae_command.py/'+ __version__
}

config_file = 'gae_command.conf'
local_config_file = os.path.expanduser('~/.'+config_file)

def urlget(url):
	request = urllib2.Request(url, headers=headers)

	return urllib2.urlopen(request)

def config_read(read_local=True):
	config = ConfigParser.SafeConfigParser()
	config.optionxform = str
	rcfp = resource_stream(__name__, os.path.join('..', config_file))
	config.readfp(rcfp)
	if read_local:
		config.read(local_config_file)
	return config

def config_save_local():
	config = config_read(read_local=False)
	local_file = open(local_config_file, 'w')
	config.write(local_file)
	local_file.close()

def get_version(url):
	"""Returns the sdk version string."""
	try:
		for line in urlget(url):
			if 'release:' in line:
				return line.split(':')[-1].strip(' \'"\r\n')
	except urllib2.URLError:
		return 'missing'

def get_remote_last_version(config=None):
	config = config or config_read()
	return get_version(config.get('globals', 'VERSION_URL'))

def get_local_version(config=None):
	config = config or config_read()
	return get_version(config.get('globals', 'VERSION_FILE'))


class PassThroughOptionParser(BoolOptionParser):
    """
    An unknown option pass-through implementation of OptionParser.

    When unknown arguments are encountered, bundle with largs and try again,
    until rargs is depleted.  

    sys.exit(status) will still be called if a known argument is passed
    incorrectly (e.g. missing arguments or bad argument types, etc.)        
    """
    def _process_args(self, largs, rargs, values):
        while rargs:
            try:
                BoolOptionParser._process_args(self, largs, rargs, values)
            except (BadOptionError, AmbiguousOptionError), e:
                largs.append(e.opt_str)
