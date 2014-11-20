from __future__ import print_function
from __future__ import unicode_literals

import errno
import glob
import logging
import os
import re
import shutil
import stat
import subprocess
import zc.buildout

import six.moves.urllib as urllib
from six import text_type as str

import hexagonit.recipe.download

strip = lambda x:x.strip()  # noqa


class Recipe(object):
    """zc.buildout recipe for compiling and installing software"""

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name
        self.log = logging.getLogger(name)

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
        )

        if 'gems' not in options:
            self.log.error("Missing 'gems' option.")
            raise zc.buildout.UserError('Configuration error')

        self.gems = options['gems'].split()
        self.version = options.get('version')
        self.url = options.get('url')
        # Allow to define specific ruby executable. If not, take just 'ruby'
        self.ruby_executable = options.get('ruby-executable', 'ruby')

    def run(self, cmd, environ=None):
        """Run the given ``cmd`` in a child process."""
        env = os.environ.copy()
        if environ:
            env.update(environ)

        try:
            subprocess.check_output(cmd, env=env)
        except OSError as e:
            self.log.error('Command failed: %s: %s' % (e, cmd))
            raise zc.buildout.UserError('System error')
        except subprocess.CalledProcessError as e:
            self.log.error(e.output)
            if e.returncode < 0:
                self.log.error('Command received signal %s: %s' % (
                    -e.returncode, e.cmd
                ))
                raise zc.buildout.UserError('System error')
            elif e.returncode > 0:
                self.log.error('Command failed with exit code %s: %s' % (
                    e.returncode, e.cmd
                ))
                raise zc.buildout.UserError('System error')

    def update(self):
        pass

    def _join_paths(self, *paths):
        return ':'.join(filter(None, paths))

    def _get_env_override(self, env):
        env = filter(None, map(strip, env.splitlines()))
        try:
            env = list([(key, val) for key, val in [
                map(strip, line.split('=', 1)) for line in env
            ]])
        except ValueError:  # Unpacking impossible
            self.log.error("Every environment line should contain a '=' sign")
            raise zc.buildout.UserError('Configuration error')
        return env

    def _get_env(self):
        s = {
            'PATH': os.environ.get('PATH', ''),
            'PREFIX': self.options['location'],
            'RUBYLIB': os.environ.get('RUBYLIB', ''),
        }
        env = {
            'GEM_HOME': '%(PREFIX)s/lib/ruby/gems/1.8' % s,
            'RUBYLIB': self._join_paths(
                '%(RUBYLIB)s',
                '%(PREFIX)s/lib',
                '%(PREFIX)s/lib/ruby',
                '%(PREFIX)s/lib/site_ruby/1.8',
            ) % s,
            'PATH': self._join_paths(
                '%(PATH)s',
                '%(PREFIX)s/bin',
            ) % s,
        }
        env_override = self.options.get('environment', '')
        env_override = self._get_env_override(env_override)
        env.update({k: (v % env) for k, v in env_override})
        return env

    def _get_latest_rubygems(self):
        if self.url:
            version = self.version
            if not version:
                version = (
                    re.search(r'rubygems-([0-9.]+).zip$', self.url).group(1)
                )
            return (self.url, version)

        if self.version:
            return ('http://production.cf.rubygems.org/rubygems/'
                    'rubygems-%s.zip' % self.version, self.version)

        f = urllib.request.urlopen('http://rubygems.org/pages/download')
        s = f.read()
        s = str(s)
        f.close()
        r = re.search(r'http://production.cf.rubygems.org/rubygems/'
                      r'rubygems-([0-9.]+).zip', s)
        if r:
            url = r.group(0)
            version = r.group(1)
            return (url, version)
        else:
            self.log.error("Can't find latest rubygems version.")
            raise zc.buildout.UserError('Configuration error')

    def _install_rubygems(self):
        url, version = self._get_latest_rubygems()

        options = {
            'url': url,
            'destination': self.buildout['buildout']['parts-directory'],
        }
        HexagonitDownload = hexagonit.recipe.download.Recipe
        recipe = HexagonitDownload(self.buildout, self.name, options)
        recipe.install()

        current_dir = os.getcwd()
        try:
            os.mkdir(self.options['location'])
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                self.log.error((
                    "IO error while creating '%s' directory."
                ) % self.options['location'])
                raise zc.buildout.UserError('Configuration error')

        srcdir = os.path.join(self.buildout['buildout']['parts-directory'],
                              'rubygems-%s' % version)
        os.chdir(srcdir)

        env = self._get_env()
        env['PREFIX'] = self.options['location']

        cmd = [
            self.ruby_executable,
            'setup.rb',
            'all',
            '--prefix=%s' % self.options['location'],
            '--no-rdoc',
            '--no-ri',
        ]

        try:
            self.run(cmd, env)
        finally:
            shutil.rmtree(srcdir)
            os.chdir(current_dir)

    def _install_executable(self, path):
        content = ['#!/bin/sh']
        for key, val in self._get_env().items():
            content.append("export %s='%s'" % (key, val))
        content.append('%s "$@"' % path)
        name = os.path.basename(path)
        bindir = self.buildout['buildout']['bin-directory']
        executable = os.path.join(bindir, name)
        f = open(executable, 'w')
        f.write('\n'.join(content) + '\n\n')
        f.close()
        os.chmod(executable, (
            # rwx rw- rw-
            stat.S_IRWXU |
            stat.S_IRGRP | stat.S_IWGRP |
            stat.S_IROTH | stat.S_IWOTH
        ))

        return executable

    def _install_gem(self, gemname, gem_executable, bindir):
        cmd = [
            gem_executable,
            'install',
            '--no-rdoc',
            '--no-ri',
            '--bindir=%s' % bindir,
        ]

        if '==' in gemname:
            gemname, version = map(strip, gemname.split('==', 1))
            cmd.append(gemname)
            cmd.append('--version=%s' % version)
        else:
            cmd.append(gemname)

        extra = self.options.get('gem-options', '')
        extra = filter(None, map(strip, extra.splitlines()))

        cmd.append('--')
        cmd.extend(extra)

        self.run(cmd, self._get_env())

    def get_gem_executable(self, bindir):
        gem_executable = os.path.join(bindir, 'gem')
        gem_executable = glob.glob(gem_executable + '*')

        if gem_executable:
            return gem_executable[0]

    def install(self):
        parts = [self.options['location']]

        bindir = os.path.join(self.options['location'], 'bin')
        gem_executable = self.get_gem_executable(bindir)

        if not gem_executable:
            self._install_rubygems()
            gem_executable = self.get_gem_executable(bindir)

        for gemname in self.gems:
            self.log.info('installing ruby gem "%s"' % gemname)
            self._install_gem(gemname, gem_executable, bindir)

        for executable in os.listdir(bindir):
            installed_path = self._install_executable(
                os.path.join(bindir, executable)
            )
            parts.append(installed_path)

        return parts
