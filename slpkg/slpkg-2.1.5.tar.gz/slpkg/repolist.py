#!/usr/bin/python
# -*- coding: utf-8 -*-

# repolist.py file is part of slpkg.

# Copyright 2014 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# Slpkg is a user-friendly package manager for Slackware installations

# https://github.com/dslackw/slpkg

# Slpkg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import sys

from repositories import Repo
from messages import template
from __metadata__ import (
    repositories,
    color
)


class RepoList(object):

    def __init__(self):
        self.all_repos = {
            'slack': Repo().slack(),
            'sbo': Repo().sbo(),
            'rlw': Repo().rlw(),
            'alien': Repo().alien(),
            'slacky': Repo().slacky(),
            'studio': Repo().studioware(),
            'slackr': Repo().slackers(),
            'slonly': Repo().slackonly(),
            'ktown': Repo().ktown(),
            'multi': Repo().multi(),
            'slacke': Repo().slacke(),
            'salix': Repo().salix(),
            'slackl': Repo().slackel()
        }

    def repos(self):
        '''
        View or enabled or disabled repositories
        '''
        print('')
        template(78)
        print('{0}{1}{2}{3}{4}'.format(
            '| Repo id', ' ' * 10,
            'Repo name', ' ' * 45,
            'Status'))
        template(78)
        for repo_id, repo_name in sorted(self.all_repos.iteritems()):
            status, COLOR = 'disabled', color['RED']
            if repo_id in repositories:
                status, COLOR = 'enabled', color['GREEN']
            print('  {0}{1}{2}{3}{4}{5:>15}{6}'.format(
                repo_id, ' ' * (17 - len(repo_id)),
                repo_name, ' ' * (45 - len(repo_name)),
                COLOR, status, color['ENDC']))
        print("\nFor enable or disable repositories edit "
              "'/etc/slpkg/slpkg.conf' file\n")
        sys.exit(0)
