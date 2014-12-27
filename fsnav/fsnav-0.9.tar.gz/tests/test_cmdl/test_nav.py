"""
FS Nav unittests for utility: nav
"""


import json
import os
import subprocess
import tempfile
import unittest

import fsnav


class TestNav(unittest.TestCase):

    def setUp(self):
        self.configfile = tempfile.NamedTemporaryFile(mode='r+')
        self.default_aliases = fsnav.Aliases(fsnav.settings.DEFAULT_ALIASES)

    def tearDown(self):
        self.configfile.close()

    def test_get(self):

        # nav get ${alias}
        a = 'home'
        result = subprocess.check_output('nav -nlc get {}'.format(a), shell=True)
        self.assertEqual(self.default_aliases[a], result.decode().strip())

    def test_startup_generate(self):

        # nav startup generate
        result = subprocess.check_output('nav -nlc startup generate', shell=True)
        actual = sorted(result.decode().strip().replace('} ; ', '}__SPLIT__').split('__SPLIT__'))
        expected = sorted(fsnav.fg_tools.generate_functions(self.default_aliases))
        self.assertEqual(actual, expected)

    def test_startup_profile(self):

        # nav startup profile
        result = subprocess.check_output('nav -nlc startup profile', shell=True)
        self.assertEqual(result.decode().strip(), fsnav.fg_tools.startup_code.strip())

    def test_config_default(self):

        # nav config default
        result = subprocess.check_output('nav -nlc config default -np', shell=True)
        self.assertDictEqual(json.loads(result.decode()), self.default_aliases.default())

    def test_config_userdefined(self):

        # nav config userdefined
        ud = {'__h__': os.path.expanduser('~')}
        aliases_to_load = dict(list(ud.items()) + list(fsnav.settings.DEFAULT_ALIASES.items()))
        self.configfile.write(json.dumps({fsnav.settings.CONFIGFILE_ALIAS_SECTION: aliases_to_load}))
        self.configfile.seek(0)
        result = subprocess.check_output(
            'nav -c {configfile} config userdefined -np'.format(configfile=self.configfile.name), shell=True)
        self.assertDictEqual(ud, json.loads(result.decode().strip()))

    def test_config_addalias(self):

        # nav config addalias ${alias}=${path}
        a1 = '__h__'
        p1 = os.path.expanduser('~')
        a2 = '___h___'
        p2 = os.path.expanduser('~')

        result = subprocess.check_output(
            'nav -c {configfile} config addalias {alias1}={path1} {alias2}={path2}'.format(
                configfile=self.configfile.name, alias1=a1, path1=p1, alias2=a2, path2=p2), shell=True)
        actual = json.load(self.configfile)[fsnav.settings.CONFIGFILE_ALIAS_SECTION]
        expected = {a1: p2, a2: p2}
        self.assertDictEqual(expected, actual)

        # If specified, make sure the configfile won't be overwritten
        try:
            result = subprocess.check_output(
                'nav -c {configfile} config addalias -no {alias1}={path1} {alias2}={path2}'.format(
                    configfile=self.configfile.name, alias1=a1, path1=p1, alias2=a2, path2=p2),
                shell=True, stderr=subprocess.PIPE)
            self.fail("Above command should have returned a non-zero exit code and raised an exception")
        except subprocess.CalledProcessError:
            pass

    def test_config_path(self):

        # nav config path
        result = subprocess.check_output('nav config path', shell=True)
        self.assertEqual(result.decode().strip(), fsnav.settings.CONFIGFILE)

    def test_license(self):

        # nav --license
        result = subprocess.check_output('nav --license', shell=True)
        self.assertEqual(result.decode().strip(), fsnav.__license__.strip())

    def test_version(self):

        # nav --version
        result = subprocess.check_output('nav --version', shell=True)
        self.assertEqual(result.decode().strip(), fsnav.__version__.strip())

    def test_aliases(self):

        # nav aliases
        result = subprocess.check_output('nav -nlc aliases -np', shell=True)
        self.assertEqual(json.loads(result.decode().strip()), fsnav.settings.DEFAULT_ALIASES)

    def test_deletealias(self):

        # nav config deletealias ${alias}
        self.configfile.write(
            json.dumps({fsnav.settings.CONFIGFILE_ALIAS_SECTION: {'__h__': os.path.expanduser('~/')}}))
        self.configfile.seek(0)
        result = subprocess.check_output('nav -c {configfile} config deletealias __h__'.format(
            configfile=self.configfile.name), shell=True)
        self.assertDictEqual(
            {fsnav.settings.CONFIGFILE_ALIAS_SECTION: {}}, json.loads(self.configfile.read()))
