
# python standard library
from ConfigParser import NoSectionError
import datetime

# this package
from ape import BaseClass
from ape.infrastructure.errors import ConfigurationError
from ape.infrastructure.crash_handler import try_except, log_error
from ape.infrastructure.strings import RED, BOLD, RESET
from ape.plugins.quartermaster import QuarterMaster


RED_ERROR = "{red}{bold}{{error}}{reset}".format(red=RED,
                                                 bold=BOLD,
                                                 reset=RESET)
INFO_STRING = '{b}**** {{0}} ****{r}'.format(b=BOLD, r=RESET)


DOCUMENT_THIS = __name__ == '__builtin__'


class BaseStrategy(BaseClass):
    """
    A base for the sub-commands
    """
    def __init__(self):
        """
        BaseStrategy Constructor
        """
        super(BaseStrategy, self).__init__()
        self._logger = None
        self.error = (Exception, KeyboardInterrupt)
        self.error_message = "Oops, I Crapped My Pants"
        self.ape = None
        return

    quartermaster = QuarterMaster()

    def build_ape(self, configfiles):
        """
        Tries to build the Ape plugin
        (has a side-effect of setting self.ape so that crash-handling can get to it)

        :return: ape or None
        :postcondition: self.ape set to ape (or None on failure)

        :param: `configfiles`: a list of configuration files for the ape        
        """
        plugin = self.quartermaster.get_plugin('Ape')
        
        # The ape needs the config-filenames
        try:
            self.ape = plugin(configfiles=configfiles).product
        except ConfigurationError as error:
            self.logger.error(RED_ERROR.format(error=error))
            return
        except NoSectionError as error:
            self.logger.error(error)
            self.logger.error(RED_ERROR.format(error='missing section in {0}'.format(configfiles)))
            self.logger.error(RED_ERROR.format(error='check the name of the config file'))
            self.logger.info("Try `ape help` and `ape fetch`")
            return 
        return self.ape
    
    def clean_up(self, error):
        """
        To be called by the try-except if an exception is caught
        """
        if type(error) is KeyboardInterrupt:
            log_error(error, self.logger, 'Oh, I am slain!')
            if self.ape is not None:                
                self.ape.clean_up(error)
        else:
            log_error(error, self.logger, self.error_message)
        return
        
#
