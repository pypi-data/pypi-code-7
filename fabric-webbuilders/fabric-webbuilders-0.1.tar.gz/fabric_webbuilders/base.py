# -*- coding: utf-8 -*-
#
# This file is part of fabric-webbuilders (https://github.com/mathiasertl/fabric-webbuilders).
#
# fabric-webbuilders is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# fabric-webbuilders is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with fabric-webbuilders.
# If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import os

from distutils.version import LooseVersion

from git import Repo

from fabric.colors import green
from fabric.context_managers import lcd
from fabric.state import env
from fabric.tasks import Task


class BuildTask(Task):
    def __init__(self, origin=None, version=None, build_dir=None, dest_dir=None):
        self.origin = origin
        self.version = version
        self.build_dir = build_dir
        self.dest_dir = dest_dir

    def run(self, origin=None, version=None, build_dir=None, dest_dir=None):
        # get options that may be overwritten by the command-line
        if build_dir is not None:
            self.build_dir = build_dir
        elif self.build_dir is None:
            default_build_dir = os.path.abspath(self.prefix)
            if os.environ.get('VIRTUAL_ENV'):
                default_build_dir = os.path.join(os.environ.get('VIRTUAL_ENV'), 'build', self.prefix)

            global_build_dir = os.path.join(env.get('build_dir', ''), default_build_dir)
            local_build_dir = env.get('%s_build_dir' % self.prefix, global_build_dir)
            self.build_dir = os.path.abspath(local_build_dir)

        if origin is not None:
            self.origin = origin
        elif self.origin is None:
            # env['origin'] doesn't make much sense, but here for consistency non-the-less
            default_origin = env.get('origin', self.default_origin)
            self.origin = env.get('%s_origin' % self.prefix, default_origin)

        if version is not None:
            self.version = version
        elif self.version is None:
            # env['version'] doesn't make much sense, but here for consistency non-the-less
            self.version = env.get('%s_version' % self.version)

        if dest_dir is not None:
            self.dest_dir = dest_dir
        elif self.dest_dir is None:
            self.dest_dir = env.get('%s_dest_dir' % self.prefix, env.get('dest_dir'))
        if self.dest_dir is not None:
            self.dest_dir = os.path.abspath(self.dest_dir)

        self.download()
        with lcd(self.build_dir):
            self.build()


class VCSMixin(object):
    def download(self):
        repo = self.clone()
        self.checkout(repo)


class GitMixin(VCSMixin):
    def clone(self):
        if not os.path.exists(self.build_dir):
            print(green('Cloning %s into %s' % (self.origin, self.build_dir)))
            repo = Repo.init(self.build_dir)
            repo.create_remote('origin', self.origin)
        else:
            print(green('Fetch updates for %s' % self.build_dir))
            repo = Repo(self.build_dir)
            if repo.remotes.origin.url != self.origin:  # update remote if desired
                repo.delete_remote(repo.remotes.origin)
                repo.create_remote('origin', self.origin)
            repo.git.checkout('master', f=True)

        repo.remotes.origin.fetch(tags=True)
        repo.remotes.origin.pull('master')
        return repo

    def is_version_tag(self, tag, match):
        if not match or not match.get('version'):
            return False
        return True

    def tag_sortkey(self, tag, match):
        obj = tag.object
        if hasattr(tag.object, 'object'):
            obj = obj.object

        return LooseVersion(match['version']), obj.authored_date

    def get_tags(self, repo):
        tags = [(t, self.tag_re.match(t.name).groupdict()) for t in repo.tags]
        tags = filter(lambda t: self.is_version_tag(*t), tags)
        return sorted(tags, key=lambda t: self.tag_sortkey(*t), reverse=True)

    def checkout(self, repo):
        if self.version == 'HEAD':
            print(green('Building %s-%s' % (self.prefix, self.version)))
            repo.git.checkout('master')
        elif self.version and self.version.startswith('~'):
            tags = self.get_tags(repo)
            tag = filter(lambda t: t[1]['version'].startswith(self.version[1:]), tags)[0][0]

            print(green('Building %s-%s' % (self.prefix, tag)))
            repo.git.checkout(tag)
        elif self.version:
            print(green('Building %s-%s' % (self.prefix, self.version)))
            repo.git.checkout(self.version)
        else:
            tag = self.get_tags(repo)[0][0]
            print(green('Building %s-%s' % (self.prefix, tag)))
            repo.git.checkout(tag)
