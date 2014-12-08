# Copyright 2014 You Technology, Inc. or its affiliates. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
# 
#     http://www.apache.org/licenses/LICENSE-2.0.html
# 
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
'''
Created on Oct 30, 2014

@author: sfitts
'''
import getpass
from netrc import netrc
import os
import platform

from requests.exceptions import HTTPError

from pdsapi.oauth import OAuthClient
from pdsapi.users import Users
from pdsapi.utils import AuthenticationError, AuthorizationError
from pdscli.commands.exceptions import CommandFailure
from pdscli.commands.utils import DEV_CLIENT_ID, DEV_CLIENT_SECRET, DEV_SCOPE


class LoginCmdProcessor(object):
    
    def __init__(self, session):
        self.session = session
        self.oauth = None
    
    def __call__(self, args):
        self.oauth = OAuthClient(self.session)
        if args.revoke:
            self.revoke_token(self.session.host)
        elif args.expire:
            self.expire_token(self.session.host)
        else:
            self.login(self.session.host, create_user=True)
    
    def configure_parser(self, subparsers):
        parser = subparsers.add_parser('login', help='Authorize user with PDS.')
        # TODO -- need a separate "auth" command
        parser.add_argument('--revoke', action='store_true', default=False,
                            help='Revoke any existing login token.')
        parser.add_argument('--expire', action='store_true', default=False,
                            help='Expire any existing login token.')
        parser.set_defaults(func=self)
        
    def login(self, host, create_user=False):
        # Create an OAuth client if we need one
        if self.oauth is None:
            self.oauth = OAuthClient(self.session)
        
        # Get authentication info from the netrc file    
        netrc_file, netrc_info = self._load_netrc()
        auth_info = netrc_info.authenticators(host)
        if auth_info is None:
            # Check to see if should permit user creation
            if not create_user:
                raise CommandFailure("No user credentials found.  Use 'login' to establish identity.")
            
            # Get credentials from user and register
            username = raw_input('Email: ')
            password = getpass.getpass()

            # Authorize the user
            try: 
                token_info = self.oauth.password_grant(username, password, DEV_CLIENT_ID, 
                                                       DEV_CLIENT_SECRET, DEV_SCOPE)
            except HTTPError:
                # The likely cause here is that login failed, try creating the user
                try:
                    self.register_user(username, password)
                except HTTPError as e:
                    if e.response.status_code == 409:
                        # User exists, password is bad
                        raise CommandFailure('Failed to authenticate user credentials.')
                    raise e
                
                # New user created, get token
                token_info = self.oauth.password_grant(username, password, DEV_CLIENT_ID, 
                                                       DEV_CLIENT_SECRET, DEV_SCOPE)
            
            # Grab tokens from the response and update host entry
            token = token_info['access_token']
            refresh = token_info['refresh_token']
            auth_info = (username, refresh, token)
            netrc_info.hosts[host] = auth_info

            # Update .netrc file so login is automatic from here on out
            with open(netrc_file, 'w') as fp:
                self._write_netrc(netrc_info, fp)
        else:
            # Attempt to fetch user (to prove creds are good)
            try:
                self.session.set_token(auth_info[2], auth_info[1])
                username = auth_info[0]
                users = Users(self.session)
                users.find_by_name(username)
            except (AuthenticationError, AuthorizationError):
                try:
                    auth_info = self._refresh_token(auth_info, host)
                except HTTPError:
                    raise CommandFailure('Existing credentials were invalid and have been removed.  Repeat command to reestablish identity.')

        # Set session to use updated token data
        self.session.set_token(auth_info[2], auth_info[1])
        return auth_info
    
    def _refresh_token(self, auth_info, host):
        # Refresh the token, get the new info and update the .netrc file
        netrc_file, netrc_info = self._load_netrc()
        token_info = None
        try:
            token_info = self.oauth.refresh_token(auth_info[1], DEV_CLIENT_ID, DEV_CLIENT_SECRET)
        except HTTPError as e:
            # Remove bogus token info and re-raise
            netrc_info.hosts.pop(host, None)
            with open(netrc_file, 'w') as fp:
                self._write_netrc(netrc_info, fp)
            raise e
         
        # Extract updated token info and update .netrc file
        token = token_info['access_token']
        refresh = token_info['refresh_token']
        auth_info = (auth_info[0], refresh, token)
        netrc_info.hosts[host] = auth_info
        with open(netrc_file, 'w') as fp:
            self._write_netrc(netrc_info, fp)
        return auth_info          


    def register_user(self, username, password):
        oauth_admin = self.oauth.client_grant('registration', 'bootstrap')
        self.session.set_token(oauth_admin['access_token'])
        users = Users(self.session)
        return users.create({'userName': username, 'password': password, 'email': username})
    
    def revoke_token(self, host):
        netrc_file, netrc_info = self._load_netrc()
        auth_info = netrc_info.authenticators(host)
        if not auth_info is None:
            # Revoke token as requested
            try:
                self.oauth.revoke_token(auth_info[2], DEV_CLIENT_ID, DEV_CLIENT_SECRET)
            except HTTPError as e:
                # Not found is OK since we're trying to nuke the token anyway
                if e.response.status_code != 404:
                    raise
                
            # Remove host information and rewrite netrc file
            netrc_info.hosts.pop(host, None)
            with open(netrc_file, 'w') as fp:
                self._write_netrc(netrc_info, fp)
    
    def expire_token(self, host):
        netrc_file, netrc_info = self._load_netrc()
        auth_info = netrc_info.authenticators(host)
        if not auth_info is None:
            # Expire token as requested
            try:
                self.oauth.expire_token(auth_info[2], DEV_CLIENT_ID, DEV_CLIENT_SECRET)
            except HTTPError as e:
                # Should we take this seriously?
                if e.response.status_code != 404:
                    raise
                else:
                    # Token is bad, so just remove
                    netrc_info.hosts.pop(host, None)
                    with open(netrc_file, 'w') as fp:
                        self._write_netrc(netrc_info, fp)
    
    def _load_netrc(self):
        netrc_name = '~/.netrc'
        if platform.system() == 'Windows':
            netrc_name = '~/_netrc'
        netrc_file = os.path.expanduser(netrc_name)
        if not os.path.exists(netrc_file):
            open(netrc_file, 'w').close()
        netrc_info = netrc(netrc_file)
        return (netrc_file, netrc_info)
    
    def _write_netrc(self, netrc_info, fp):
        for host in netrc_info.hosts.keys():
            attrs = netrc_info.hosts[host]
            fp.write("machine %s\n" % host)
            fp.write("    login %s\n" % attrs[0])
            if attrs[1]:
                fp.write("    account %s\n" % attrs[1])
            fp.write("    password %s\n" % attrs[2])