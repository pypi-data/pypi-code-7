# coding=utf-8
import logging
from crayola import initialize, ColorStreamHandler

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'

FG_COLOR_LOG_LEVELS = dict(
    BLACK=1001,
    RED=1002,
    GREEN=1003,
    YELLOW=1004,
    BLUE=1005,
    MAGENTA=1006,
    CYAN=1007,
    WHITE=1008
)

BG_COLOR_LOG_LEVELS = dict(
    BLACK=100,
    RED=200,
    GREEN=300,
    YELLOW=400,
    BLUE=500,
    MAGENTA=600,
    CYAN=700,
    WHITE=800
)


class CustomLogger(logging.getLoggerClass()):
    pass


class DemoHandler(ColorStreamHandler):
    def __init__(self):
        super(DemoHandler, self).__init__()
        demo_level_map = {}
        for fg, fg_value in FG_COLOR_LOG_LEVELS.iteritems():
            for bg, bg_value in BG_COLOR_LOG_LEVELS.iteritems():
                demo_level_map[fg_value + bg_value] = (bg, fg, False)
                demo_level_map[fg_value + bg_value + 10] = (bg, fg, True)
        self.level_map.update(demo_level_map)


def main():
    initialize()

    # logging.setLoggerClass(CustomLogger)
    dicts = (FG_COLOR_LOG_LEVELS, BG_COLOR_LOG_LEVELS)

    for the_dict in dicts:
        for lvl, value in the_dict.iteritems():
            logging.addLevelName(value, lvl)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(DemoHandler())

    logging.info("COLORS\n======")

    for fg, fg_value in FG_COLOR_LOG_LEVELS.iteritems():
        logging.info("Foreground color: %s" % fg)
        for bg, bg_value in BG_COLOR_LOG_LEVELS.iteritems():
            if fg != bg:
                logging.log(fg_value + bg_value, "  %s on %s  " % (fg, bg))
                logging.log(fg_value + bg_value + 10, "  BRIGHT %s on %s  " % (fg, bg))

    # logging.debug('DEBUG')
    # logging.info('INFO')
    # logging.warning('WARNING')
    # logging.error('ERROR')
    # logging.critical('CRITICAL')


if __name__ == '__main__':
    main()
