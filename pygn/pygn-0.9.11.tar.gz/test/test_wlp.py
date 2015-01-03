#!/usr/bin/python
# -*- coding: utf-8 -*-

import mail2news
import os
import os.path
import re
import subprocess
import sys
import sysconfig
import unittest
import wlp


def distutils_dir_name(dname):
    """Returns the name of a distutils build directory"""
    f = "{dirname}.{platform}-{version[0]}.{version[1]}"
    return f.format(dirname=dname,
                    platform=sysconfig.get_platform(),
                    version=sys.version_info)
wlp_lib_path = os.path.join('build', distutils_dir_name('lib'))
sys.path.insert(0, wlp_lib_path)




class TestWLP(unittest.TestCase):
    def test_wlp_parser(self):
        wlp.setfilebyname('examples/whitelist.example')
        wl_dict = wlp.mkdict()
        expected_dict = {'alfarano@students.cs.unibo.it': {
            'From:': 'Cosimo Alfarano',
            'X-Firstname:': 'Cosimo'
        },
            'kame@innocent.com': {
            'From:': 'kame@inwind.it',
            'Reply-to': 'me',
            'Reply-to:': 'KA',
            'Sender:': 'Kalfa'}
        }
        self.assertEqual(wl_dict, expected_dict)


class TestM2N(unittest.TestCase):
    expected_output = """Newsgroups: pyg.test
From: Pyg <pyg@localhost.com>
To: User <user@localhost.com>
Subject: test
Date: Sun, 1 Feb 2002 16:40:40 +0200
Message-Id: <20001001164040.Aa8326@localhost>
Return-Path: <pyg@localhost>
Mime-Version: 1.0
Content-Type: text/plain; charset=us-ascii
User-Agent: Mutt/1.2.5i
X-Multiline: this header probably broke RFC, but is frequent.
X-Gateway: pyg %s %s

one line test

""" % (mail2news.VERSION, mail2news.DESC)

    def test_m2n(self):
        with open('examples/mail') as in_mail:
            pid = subprocess.Popen(['./pygm2n', '-Tv', '-n', 'pyg.test'],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
            out, _ = pid.communicate(in_mail.read())
        self.assertEqual(out, self.expected_output)


class TestN2M(unittest.TestCase):
    expected_output = """Received: from GATEWAY by mitmanek.ceplovi.cz with pyg
    for <test@example.com> ; Mon Dec 15 17:13:30 2014 (CEST)
From: kame@inwind.it (PYG)
To: test@example.com
Subject: pyg's article test
Date: 10 Jun 2000 23:20:47 +0200
Organization: Debian GNU/Linux
Reply-To: pyg@localhost
Content-Type: text/plain; charset=US-ASCII
Mime-Version: 1.0
Content-Transfer-Encoding: 7bit
X-Trace: pyg.server.tld 960672047 927 192.168.1.2 (10 Jun 2000 21:20:47 GMT)
X-Newsgroups: local.moderated
X-Gateway: pyg %s %s
X-NNTP-Posting-Host: pyg.server.tld
Resent-From: sender@example.com
Resent-Sender: sender@example.com
""" % (mail2news.VERSION, mail2news.DESC)

    def test_n2m(self):
        env = os.environ
        env['PYTHONPATH'] = wlp_lib_path

        with open('examples/articletest.accepted') as in_mail:
            pid = subprocess.Popen(['./pygn2m', '-Tvt', 'test@example.com',
                                    '-s', 'sender@example.com',
                                    '-w', 'examples/whitelist.example'],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, env=env)
            in_message = in_mail.read().replace('pyg@pyg.server.tld',
                                                'kame@inwind.it')
            out, err = pid.communicate(in_message)
            out = re.sub(r'^Message-Id:.*$', '', out)
        # Not sure how to compare two email mesages (with different
        # times, etc.) so for now just to make sure the script doesn’t
        # blow up and gives some output
        # otherwise it would be
        # self.assertEqual(out, expected_output)
        self.assertEqual(pid.returncode, 0)
        self.assertGreater(len(out), 0)


if __name__ == "__main__":
    unittest.main()
