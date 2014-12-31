# coding=utf-8
import logging
from colorama import Style, Fore, Back, init as init_colorama

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


def initialize():
    init_colorama()


class ColorStreamHandler(logging.StreamHandler):
    default_colors = (None, 'WHITE', False)

    # levels to (background, foreground, bold/intense)
    level_map = {
        logging.DEBUG: (None, 'BLUE', True),
        logging.INFO: default_colors,
        logging.WARNING: (None, 'YELLOW', True),
        logging.ERROR: (None, 'RED', True),
        logging.CRITICAL: ('RED', 'WHITE', True)
    }

    def __init__(self, stream=None, multiline_color=True):
        super(ColorStreamHandler, self).__init__(stream)
        initialize()
        self.multiline_color = multiline_color

    # noinspection PyBroadException
    @property
    def is_tty(self):
        try:
            return getattr(self.stream, 'isatty', None)()
        except:
            return False

    def colorize(self, levelno, message=None):
        if levelno not in self.level_map:
            bg, fg, bright = self.default_colors
        else:
            bg, fg, bright = self.level_map[levelno]

        if bg is not None:
            bg = getattr(Back, bg)

        if fg is not None:
            fg = getattr(Fore, fg)

        bright = Style.BRIGHT if bright else None

        str_list = [c for c in (bg, fg, bright) if c is not None]
        return ''.join(str_list) + message + Style.RESET_ALL

    def format(self, record):
        reset = Style.RESET_ALL
        message = logging.StreamHandler.format(self, record)
        parts = message.split('\n')
        joiner = '' if len(parts) == 1 else '\n'

        if not self.multiline_color:
            parts[0] += reset

        message = joiner.join(parts)
        return self.colorize(record.levelno, message)

    # noinspection PyBroadException
    def emit(self, record):
        try:
            message = self.format(record)
            self.stream.write(message)
            self.stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def main():
    initialize()
    handler = ColorStreamHandler()

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(handler)
    logging.debug('DEBUG')
    logging.info('INFO')
    logging.warning('WARNING')
    logging.error('ERROR')
    logging.critical('CRITICAL')

if __name__ == '__main__':
    main()
