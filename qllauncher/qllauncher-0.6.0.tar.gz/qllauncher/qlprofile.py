"""
QuakeLive Launcher
Copyright (C) 2014  Victor Polevoy (vityatheboss@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = 'Victor Polevoy'


import requests


class QLProfile():
    PROFILE_PAGE_PATTERN = 'http://www.quakelive.com/profile/%s/%s'

    def __init__(self, nick, profile_request_type, parse_immediate=False):
        self._nick = nick
        self._profile_request_type = profile_request_type

        if parse_immediate:
            self._parse_profile()

    def _parse_profile(self):
        page = QLProfile.get_profile_page(self._nick, self._profile_request_type)
        print('page got: %s' % str(page))

    @staticmethod
    def get_profile_page(nick, profile_request_type):
        return requests.get(QLProfile.PROFILE_PAGE_PATTERN % (profile_request_type, nick))


class QLProfileRequestType():
    SUMMARY = 'summary'


class QLProfileParser():
    def parse_html(self, page):
        raise NotImplementedError('ERROR: Method not implemented')

    @staticmethod
    def create_parser(profile_request_type):
        if profile_request_type == QLProfileRequestType.SUMMARY:
            return QLProfileSummaryParser()


class QLProfileSummaryParser(QLProfileParser):
    def __init__(self):
        QLProfileParser.__init__(self)

    def parse_html(self, page):
        pass