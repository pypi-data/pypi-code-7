#!/usr/bin/env python

import logging
import sys
import argparse
import sys, traceback

#pip install httplib2
import httplib2

#pip install --upgrade google-api-python-client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools
from oauth2client.tools import run_flow
from apiclient.discovery import build

# TIPs
# First :Under "Content screen", fill the "product name" to avoid the "invalid application" error
# Note doing this first is capital (prior creating any client id).
#
# From Google Dev Console (https://console.developers.google.com/project)
# Create project, then under "APIs & Auth" --> APIs and enable wwanted APIs
# Under "Credentials", create new client ID --> "WebApplication" --> Redirect URLs "http://localhost:8080/"
# and download JSON secret file

# Warning, when authenticae through browser, use the correct Google account (may be cached by browser!)

class GoogleAPI(object):
    def __init__(self, secretsFile='secrets.json', credentialsFile='credentials.dat', scope=None):
        #logging.basicConfig(level=logging.INFO)
        self._secretsFile = secretsFile
        self._credentialsFile = credentialsFile
        self._scope = scope
        self._credentials = None
        self._http = None
        self.restoreCredentials()

    @property
    def credentials(self):
        return self._credentials

    def isAuthenticated(self):
        if self._http:
            return True

    def storage(self):
        return Storage(self._credentialsFile)

    def restoreCredentials(self):
        try:
            self._http = None
            credentials = self.storage().get()
            if credentials and not credentials.invalid:
                self._credentials=credentials
                self._http = credentials.authorize(httplib2.Http())
        except:
            pass
        return self.isAuthenticated()

    def authenticate(self):
        try:
            self._http = None
            parser = argparse.ArgumentParser(
                description=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter,
                parents=[tools.argparser])

            # Parse the command-line flags.
            flags = parser.parse_args(sys.argv[1:])

            # Perform OAuth 2.0 authorization.
            flow = flow_from_clientsecrets(
                self._secretsFile,
                scope=self._scope,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob')

            self._credentials = run_flow(flow, self.storage(), flags)
            if self._credentials and not self._credentials.invalid:
              storage=self.storage()
              storage.put(self._credentials)
            self._http = self._credentials.authorize(httplib2.Http())
        except:
            traceback.print_exc(file=sys.stdout)
            pass
        return self.isAuthenticated()

    def authenticateStep1(self):
      try:
          flow = flow_from_clientsecrets(
              self._secretsFile, scope=self._scope,
              redirect_uri='urn:ietf:wg:oauth:2.0:oob')
          url=flow.step1_get_authorize_url()
          # return the authenticate URL to be approved
          logging.info(url)
          return url
      except:
          pass

    def authenticateStep2(self, code):
      try:
          flow = flow_from_clientsecrets(
              self._secretsFile, scope=self._scope,
              redirect_uri='urn:ietf:wg:oauth:2.0:oob')
          credentials=flow.step2_exchange(code)
          if credentials:
              self._credentials=credentials
              storage=self.storage()
              storage.put(credentials)
              self._http = credentials.authorize(httplib2.Http())
      except:
          pass
      return self.isAuthenticated()

    def service(self, name, version):
        return build(serviceName=name, version=version, http=self._http)



if __name__ == '__main__':
  pass

