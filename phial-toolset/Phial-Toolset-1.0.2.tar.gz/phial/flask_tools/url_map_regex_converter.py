# -*- coding: utf-8 -*-
from werkzeug.routing import BaseConverter


class   FlaskURLMapRegexConverter(BaseConverter):
    '''
    FlaskURLMapRegexConverter

    Add regular expressions on Flask URL mapping system.

    How to use:
      ('/url-path/<regex("[a-zA-Z]{4,10}"):var_name>', view_funct, ['GET, POST']),
    '''

    def __init__(self, url_map, *items):
        super(FlaskURLMapRegexConverter, self).__init__(url_map)
        self.regex = items[0]
