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
import ConfigParser
import os
import sys

from requests.exceptions import HTTPError

from pdsapi.pds import Pds


class ConfigCmdProcessor(object):
    
    def __init__(self, session, login_processor):
        self.session = session
        self.config = self.load_config()
        self.login_processor = login_processor
        
    def configure_parser(self, driver, subparsers):
        # Create parser for the configuration commands themselves, then a sub-parser under that
        parser = subparsers.add_parser('config', help='Configure PDS command line client.', 
                                       add_help = False)
        subparsers = driver.create_sub_parser(parser, 'Configuration command help.')
        
        parser = subparsers.add_parser('show', help='Show the current configuration values.')
        parser.set_defaults(func=self.show)

        parser = subparsers.add_parser('set', help='Set the named configuration value.')
        parser.add_argument('name', help='Name of the configuration value to set.')
        parser.add_argument('value', help='Value to set.')
        parser.set_defaults(func=self.set)

    def load_config(self):
        config_file= self._get_config_file()
        config_dir = os.path.dirname(config_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, mode=0755)
            config = self._default_config()
            self._update_config(config_file, config)
            return config
        
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        return config
    
    def _get_config_file(self):
        config_dir = os.path.expanduser('~/.youtech')
        return os.path.join(config_dir, 'config')

    def _default_config(self):
        config = ConfigParser.ConfigParser()
        config.add_section('Server')
        config.set('Server', 'host', 'pds.you.tc')
        return config
    
    def show(self, args):
        # Display local settings
        self.config.write(sys.stdout)
        
        # Display PDS specific settings
        sys.stdout.write('\n[PDS]\n')
        try:
            pds = Pds(self.session)
            our_pds = pds.get_current()
            if our_pds is None:
                namespace = 'no value set'
            else:
                namespace = our_pds['assignedNamespace']
            sys.stdout.write('namespace = %s\n' % namespace)
        except HTTPError:
            sys.stdout.write('Unable to retrieve settings from your PDS.\n')
    
    def set(self, args):
        # Namespace is a PDS setting
        # TODO -- clean this up a bit
        if args.name == 'namespace':
            self.login_processor.login(self.session.host)
            self._assign_namespace(args.value)
            return
        
        # Update local server configuration
        config = self.config
        config.set('Server', args.name, args.value)
        self._update_config(self._get_config_file(), config)
        
    def _assign_namespace(self, namespace):
        pds = Pds(self.session)
        pds.assign_namespace(namespace)
    
    def _update_config(self, config_file, config):
        with open(config_file, 'w') as fp:
            config.write(fp)