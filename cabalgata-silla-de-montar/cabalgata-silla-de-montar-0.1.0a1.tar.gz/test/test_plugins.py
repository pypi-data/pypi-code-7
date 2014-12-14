#
# Copyright 2014 the original author or authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import pkg_resources

import mock

from cabalgata.silla import plugins
from cabalgata.silla.util import disk


def plugin_entry_points():
    return (
        pkg_resources.EntryPoint.parse('a=data.plugins:FactoryA'),
    )


@mock.patch('pkg_resources.iter_entry_points')
def test_load_plugins(mock_pkg_resources):
    mock_pkg_resources.return_value = plugin_entry_points()

    plugin = plugins.load_plugins('a')

    assert plugin.versions
    assert plugin.definitions

    try:
        plugins.load_plugins('does_not_exist')

        assert False, 'Should have raised an KeyError'
    except KeyError:
        pass


@mock.patch('pkg_resources.iter_entry_points')
def test_install(mock_pkg_resources):
    mock_pkg_resources.return_value = plugin_entry_points()

    plugin = plugins.load_plugins('a')

    with disk.temp_directory() as temp_directory:
        plugin.install('1.2.3', temp_directory)

        p = plugin.load(temp_directory)

        assert p.version == '1.2.3'

        plugin.uninstall(temp_directory)


@mock.patch('pkg_resources.iter_entry_points')
def test_start(mock_pkg_resources):
    mock_pkg_resources.return_value = plugin_entry_points()

    plugin = plugins.load_plugins('a')

    with disk.temp_directory() as temp_directory:
        plugin.install('1.2.3', temp_directory)

        p = plugin.load(temp_directory)
        assert not p.running

        p.start()
        assert p.running
        p.stop()
        assert not p.running

        p.start()
        assert p.running
        p.kill()
        assert not p.running

        plugin.uninstall(temp_directory)
