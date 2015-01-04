# -*- coding: utf-8 -*-

# $Id$


import optparse # required for 2.6 compatibility

_parser = optparse.OptionParser()
_parser.add_option("-c", "--config-file",
                   dest="config_file",
                   default="autotest.cfg",
                   help=u"Specify alternative config file",
                   metavar="FILE")

def parse():
    options, args = _parser.parse_args()
    return options
