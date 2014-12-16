import logging
from nose.plugins.base import Plugin
from .loghandler import LogFileHandler


class SQLCapture(Plugin):
    enabled = False
    env_opt = 'NOSE_SQLCAPTURE'
    name = 'sqlcapture'
    score = 400
    filename = '/tmp/sqlcapture.log'
    format = 'plain'

    def options(self, parser, env):
        parser.add_option(
            "--sqlcapture-filename", action="store",
            dest="sqlcapture_filename",
            type='string', default=self.filename,
            metavar="FILENAME",
            help="write captured queries to FILENAME")
        parser.add_option(
            "--sqlcapture-format", action="store",
            dest="sqlcapture_format",
            type='string', default=self.format,
            metavar="FORMAT",
            help=(
                "The format of of the result capture file. "
                "Either json or plain"
            ))
        return super(SQLCapture, self).options(parser, env)

    def configure(self, options, conf):
        self.filename = options.sqlcapture_filename
        self.format = options.sqlcapture_format
        return super(SQLCapture, self).configure(options, conf)

    def begin(self):
        self.handler = LogFileHandler(self.filename, self.format)

    def end(self):
        self.handler.close()

    def startTest(self, test):
        self.handler.current_test = str(test)
        logger = logging.getLogger('sqlalchemy.engine')
        self.current_level = logger.getEffectiveLevel()
        logger.setLevel(logging.INFO)
        logger.addHandler(self.handler)

    def stopTest(self, test):
        logger = logging.getLogger('sqlalchemy.engine')
        logger.removeHandler(self.handler)
        logger.setLevel(self.current_level)
