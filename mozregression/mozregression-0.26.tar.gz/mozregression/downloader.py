#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import mozinfo
import sys
import datetime
from utils import download_url, urlLinks
import re

class NightlyDownloader(object):

    @staticmethod
    def _getBuildRegex(bits):
        if mozinfo.os == "win":
            if bits == 64:
                # XXX this should actually throw an error to be consumed by the caller
                print "No builds available for 64 bit Windows"
                sys.exit()
            return ".*win32.zip"
        elif mozinfo.os == "linux":
            if bits == 64:
                return ".*linux-x86_64.tar.bz2"
            else:
                return ".*linux-i686.tar.bz2"
        elif mozinfo.os == "mac":
            return ".*mac.*\.dmg"

    def __init__(self, repo_name=None, bits=mozinfo.bits, cacheDir=None):
        self.buildRegex = self._getBuildRegex(bits)
        self.cacheDir = cacheDir
        self.repo_name = repo_name

    def getBuildUrl(self, datestamp):
        url = "http://ftp.mozilla.org/pub/mozilla.org/" + self.appName + "/nightly/"
        year = str(datestamp.year)
        month = "%02d" % datestamp.month
        day = "%02d" % datestamp.day
        repo_name = self.repo_name or self.getRepoName(datestamp)
        url += year + "/" + month + "/"

        linkRegex = '^' + year + '-' + month + '-' + day + '-' + '[\d-]+' + repo_name + '/$'
        cachekey = year + '-' + month
        if cachekey in self._monthlinks:
            monthlinks = self._monthlinks[cachekey]
        else:
            monthlinks = urlLinks(url)
            self._monthlinks[cachekey] = monthlinks

        # first parse monthly list to get correct directory
        for dirlink in monthlinks:
            dirhref = dirlink.get("href")
            if re.match(linkRegex, dirhref):
                # now parse the page for the correct build url
                for link in urlLinks(url + dirhref):
                    href = link.get("href")
                    if re.match(self.buildRegex, href):
                        return url + dirhref + href

    def download(self, date=datetime.date.today(), dest=None):
        url = self.getBuildUrl(date)
        if url:
            if not dest:
                dest = self.get_destination(url, date)
            if not self.persist:
                self.remove_lastdest()

            self.dest = self.lastdest = dest
            download_url(url, dest)
            return True
        else:
            return False
