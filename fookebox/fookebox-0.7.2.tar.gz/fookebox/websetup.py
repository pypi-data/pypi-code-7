"""Setup the fookebox application"""
import logging

import pylons.test

from fookebox.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
	"""Place any commands to setup fookebox here"""
	# Don't reload the app if it was loaded under the testing environment
	if not pylons.test.pylonsapp:
		load_environment(conf.global_conf, conf.local_conf)

	log.info("Successfully setup")
