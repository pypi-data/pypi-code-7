#!/usr/bin/env python

import logging
import sys
import argparse
import md5
import time
import sys, traceback
import datetime


#pip install httplib2
import httplib2

#pip install requests
import requests

#pip install --upgrade google-api-python-client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools
#from oauth2client.tools import run_flow
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

# General Google OAuth Explanation
# --------------------------------
# https://developers.google.com/accounts/docs/OAuth2
#
# One an access token is obtained (credentials) it may be used for API access (within requested scope)
# Access token have limited lifetimes. A refresh token may be obtained and stored (credentials).
#
# WARNING: Save refresh tokens in secure long-term storage and continue to use them as long as they
# remain valid. Limits apply to the number of refresh tokens that are issued per client-user combination,
# and per user across all clients, and these limits are different. If your application requests enough
# refresh tokens to go over one of the limits, older refresh tokens stop working
#
# You should write your code to anticipate the possibility that a granted token might no longer work.
# A token might stop working for one of these reasons:
#
# - The user has revoked access.
# - The token has not been used for six months.
# - The user account has exceeded a certain number of token requests.
#
# There is currently a 25-token limit per Google user account. If a user account has 25 valid tokens,
# the next authentication request succeeds, but quietly invalidates the oldest outstanding token
# without any user-visible warning. If you need to authorize multiple programs, machines, or devices,
# one workaround is to limit the number of clients that you authorize per user account to 15 or 20.
# If you are a Google Apps admin, you can create additional admin users and use them to authorize some of the clients.
#
# Google OAuth for Python
# -----------------------
# https://developers.google.com/api-client-library/python/guide/aaa_oauth
#
# 1. Create a flow
#    from oauth2client.client import flow_from_clientsecrets (clientid, clientsecret, scope, redirecturl)
#    flow = flow_from_clientsecrets()
#
# 2. STEP1 : generate the AUTH URL and redirect the user to this url
#    auth_uri = flow.step1_get_authorize_url()
#
#    if the user has already previously granted this app, the server immediately redirects
#    to the redirecturl with a CODE param in url
#
# 3. STEP2 : obtain a CREDENTIALS object for the received CODE
#    credentials = flow.step2_exchange(code)
#
#    the credentials object holds refresh and access tokens that auth a SINGLE USER data. The
#    credentials are then applied in a http object (http=crendetials.authorize(http)) to authorize
#    access/communication with the server. credentials can be stored with storage.put(credentials).
#
# WARNING: We Need a refresh_token !!!
# This is done by adding the an "access_type" parameter with the value "offline" to the authorization url
# (the one you redirect the user to to click "I want to allow this application to get at my data").
# If you do this, you get a refresh_token back in your JSON response when you ask google for access tokens.
# Otherwise you only get the access token (which is valid for ****an hour****).
# --> The API will try to refresh the access_token (if expired) when calling an authorized http.request.


class GoogleAPI(object):
    def __init__(self, name, secretsFile, credentialsFile, scope, urlRedirect):
        #logging.basicConfig(level=logging.INFO)
        self._name=name
        self._uuid=md5.new(name).hexdigest()
        self._urlRedirect=urlRedirect
        self._secretsFile = secretsFile
        self._credentialsFile = credentialsFile
        self._scope = scope
        self._credentials = None
        self._http = None
        self._stampOAuthStep1=0
        self._stampOAuthClaimAccessToken=0

    @property
    def name(self):
        return self._name

    @property
    def uuid(self):
        return self._uuid

    @property
    def credentials(self):
        return self._credentials

    def authenticate(self, forceAuthPrompt=False):
        if self._http is not None or self.restoreCredentials():
            # refresh token when validity < 15minutes
            # the refresh works only if the refresh_token is not null
            # (token must be created with option access_type='offline')
            if (self._credentials.token_expiry - datetime.datetime.utcnow()) < datetime.timedelta(minutes=15):
                self._credentials.refresh(httplib2.Http())
                storage=self.storage()
                storage.put(self._credentials)
            if not self._credentials.invalid:
                return True

        if time.time()-self._stampOAuthClaimAccessToken>60:
            token=self.OAuth2_claimAccessToken()
            if token:
                self.OAuth2_step2_getCredentialFromCode(token)
                if self.restoreCredentials():
                    return True
            if time.time()-self._stampOAuthStep1>24*3600:
                self.OAuth2_step1_getAuthURL(forceAuthPrompt)

        return False

    def storage(self):
        return Storage(self._credentialsFile)

    def restoreCredentials(self):
        try:
            self._http = None
            storage=self.storage()
            credentials = storage.get()

            #if credentials is not None and not credentials.invalid:
            if credentials is not None:
                self._credentials=credentials
                self._http = self._credentials.authorize(httplib2.Http())
        except:
            traceback.print_exc(file=sys.stdout)
            pass
        if self._http is not None:
            return True
        return False

    # def OAuth2_runFlow(self):
    #     try:
    #         self._http = None
    #         parser = argparse.ArgumentParser(
    #             description=__doc__,
    #             formatter_class=argparse.RawDescriptionHelpFormatter,
    #             parents=[tools.argparser])

    #         # Parse the command-line flags.
    #         flags = parser.parse_args(sys.argv[1:])

    #         # Perform OAuth 2.0 authorization.
    #         flow = flow_from_clientsecrets(
    #             self._secretsFile,
    #             scope=self._scope,
    #             redirect_uri='urn:ietf:wg:oauth:2.0:oob')

    #         storage=self.storage()
    #         self._credentials = run_flow(flow, storage, flags)
    #         if self._credentials and not self._credentials.invalid:
    #             storage.put(self._credentials)
    #             self._http = self._credentials.authorize(httplib2.Http())
    #     except:
    #         traceback.print_exc(file=sys.stdout)
    #         pass

    #     return self.isAuthenticated()

    def OAuth2_step1_getAuthURL(self, forceApprovalPrompt=False):
        try:
            flow = flow_from_clientsecrets(
                self._secretsFile, scope=self._scope,
                    redirect_uri=self._urlRedirect)

            # state parameter will be passed back with the code response redirect request
            flow.params['state']=self.uuid
            flow.params['access_type']='offline'
            if forceApprovalPrompt:
                flow.params['approval_prompt']='force'

            logging.info('gapi.OAuth2_step1_getAuthURL()')
            self._stampOAuthStep1=time.time()
            url=flow.step1_get_authorize_url()

            # return the authenticate URL to be approved
            # once approved, the redirecturl (given in secretfile) is called
            # with the code as parameter for step 2 processing
            #logging.info(url)

            payload={'name':self.name, 'uuid':self.uuid, 'command':'oauth2', 'url':url}
            r=requests.get(self._urlRedirect, params=payload)

            return url
        except:
            traceback.print_exc(file=sys.stdout)
            pass

    def OAuth2_claimAccessToken(self):
        try:
            logging.info('gapi.OAuth2_claimAccessToken()')
            self._stampOAuthClaimAccessToken=time.time()
            payload={'uuid': self.uuid, 'command':'claimtoken'}
            r=requests.get(self._urlRedirect, params=payload)
            result=r.json()
            return result['token']
        except:
            pass

    def OAuth2_step2_getCredentialFromCode(self, code):
        try:
            logging.info('gapi.OAuth2_step2_getCredentialFromCode()')
            flow = flow_from_clientsecrets(
                self._secretsFile, scope=self._scope,
                    redirect_uri=self._urlRedirect)
            credentials=flow.step2_exchange(code)
            if credentials:
                storage=self.storage()
                storage.put(credentials)
        except:
            traceback.print_exc(file=sys.stdout)
            pass

    def service(self, name, version):
        return build(serviceName=name, version=version, http=self._http)


if __name__ == '__main__':
  pass

