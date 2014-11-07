"""Common test tools."""
import os
import shutil
import stat
import unittest
import yaml
from .mocks import patch_container, unpatch
from containerctl.version import Version, latest as latest_version
from tempfile import mkdtemp


class TempPathTestCase(unittest.TestCase):
    """Create a temporary directory for the test case to use as a sandbox."""
    def setUp(self, prefix=None):
        self.path = mkdtemp(prefix='containerctl_')

    def tearDown(self):
        shutil.rmtree(self.path)


class TestContainer(unittest.TestCase):
    """Handle monkey patching of the container class. Provide methods for creating basic containers
    in /tmp."""
    def setUp(self, best_version=None, all_versions=None):
        if best_version and not all_versions:
            all_versions = [best_version]
        self.containers = []
        patch_container(best_version, all_versions)

    def tearDown(self):
        unpatch()
        for container in self.containers:
            shutil.rmtree(container)

    def create_container(self, name, config=None, dockerfile=None):
        """Create a container in a temp directory. The the name and additional configuration are
        written into the container config. If ``dockerfile`` is not ``False`` a simple Dockerfile
        will also be written. Return the path to the container."""
        if not config:
            config = {}
        path = mkdtemp(prefix='containerctl_{}_'.format(name))
        self.containers.append(path)
        config['name'] = name
        out = yaml.dump(config)
        with open(os.path.join(path, 'container.yml'), 'w') as f:
            f.write(out)
        if dockerfile is None or dockerfile:
            with open(os.path.join(path, 'Dockerfile'), 'w') as f:
                f.write("FROM debian:wheezy\n")
                f.write("MAINTAINER WiFast Engineering <engineering@wifast.com>\n")
        return path

    def remove_container(self, path):
        self.container.remove(path)
        shutil.rmtree(path)

    def create_prebuild(self, path, filename=None, fail=None):
        """Create a prebuild script that touches a file at path/prebuilt. If ``fail`` is ``True``
        it will instead return a 1 for exit code. Return the path to the script."""
        if not filename:
            filename = 'prebuild'
        filepath = os.path.join(path, filename)
        with open(filepath, 'w') as f:
            f.write('#!/bin/sh\n')
            if fail:
                f.write('exit 1\n')
            else:
                f.write('touch "$(dirname "$0")/prebuilt"\n')
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        return filepath

    def remove_prebuild(self, path, filename=None):
        """Remove a prebuild script."""
        for filename in ((filename or 'prebuild'), 'prebuilt'):
            filepath = os.path.join(path, filename)
            try:
                os.unlink(filepath)
            except OSError as e:
                print("failed to unlink {}: {}".format(filepath, e))

    def check_prebuild(self, path):
        """Return ``True`` if the prebuild was run."""
        return os.path.isfile(os.path.join(path, 'prebuilt'))


class TestSimpleContainer(TestContainer):
    """Container.push"""
    def get_tag(self, version):
        return '{}:{}'.format(self.name, version.value)

    def get_tags(self, versions, latest=None):
        tags = [self.get_tag(v) for v in versions]
        if latest:
            tags.append(self.get_tag(self.latest))
        return tags

    def setUp(self):
        self.name = 'test'

        self.verified_versions = [Version('v1', True)]
        self.unverified_versions = [Version('r1234567', False)]

        self.version = self.verified_versions[0]
        self.versions = self.verified_versions + self.unverified_versions
        self.latest = latest_version
        super(TestSimpleContainer, self).setUp(self.version, self.versions)
