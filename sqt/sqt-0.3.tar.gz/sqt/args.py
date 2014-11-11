from optparse import OptionParser as OptionParser

try:
	from argparse import ArgumentParser as ArgumentParser, RawDescriptionHelpFormatter
except ImportError:
	# use our local copy
	from .argparse import ArgumentParser, RawDescriptionHelpFormatter
import sys


class HelpfulOptionParser(OptionParser):
	"""An OptionParser that prints full help on errors."""
	def error(self, msg):
		self.print_help(sys.stderr)
		self.exit(2, "\n%s: error: %s\n" % (self.get_prog_name(), msg))


class HelpfulArgumentParser(ArgumentParser):
	"""An ArgumentParser that prints full help on errors."""

	def __init__(self, *args, **kwargs):
		if 'formatter_class' not in kwargs:
			kwargs['formatter_class'] = RawDescriptionHelpFormatter
		super().__init__(*args, **kwargs)

	def error(self, message):
		self.print_help(sys.stderr)
		args = {'prog': self.prog, 'message': message}
		self.exit(2, '%(prog)s: error: %(message)s\n' % args)
