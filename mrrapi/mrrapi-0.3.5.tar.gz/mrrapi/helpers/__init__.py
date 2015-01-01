# -*- coding: utf-8 -*-
""" This module will interface with the MiningRigRentals.com API in an attempt to give you easy access to their api.
"""

import hmac
import hashlib
import time
import urllib
import urllib2
import json
import sys
import ConfigParser
import os
from optparse import OptionParser
from inspect import currentframe

debug = False
__author__ = 'jcwoltz'
__version__ = '0.3.5a1'

def getmrrconfig():
    mkey = None
    msecret = None

    config = ConfigParser.ConfigParser()
    for loc in os.curdir, os.path.expanduser("~"), os.path.expanduser("~/.mrrapi"), os.path.expanduser("~/mrrapi"):
        try:
            with open(os.path.join(loc,"mrrapi.cfg")) as source:
                config.readfp(source)
                if debug:
                    print "DEBUG: Using %s for config file" % (str(source.name))
        except IOError:
            pass

    mkey = config.get('MRRAPIKeys','key')
    msecret = config.get('MRRAPIKeys','secret')

    if mkey is not None and msecret is not None:
        return mkey, msecret
    else:
        print "ERROR: Could not find mrrapi.cfg"
        sys.exit(10)
        return str(0), str(0)

def getTerminalSize():
    import os
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))

        ### Use get(key[, default]) instead of a try/catch
        #try:
        #    cr = (env['LINES'], env['COLUMNS'])
        #except:
        #    cr = (25, 80)
    return int(cr[1]), int(cr[0])

#helper function to format floats
def ff(f):
    return format(f, '.8f')

#helper function to format floats
def ff12(f):
    return format(f, '.12f')

def getBTCValue():
    # https://www.bitstamp.net/api/  BTC -> USD
    bitstampurl = "https://www.bitstamp.net/api/ticker/"
    try:
        bsjson = urllib2.urlopen(bitstampurl).read()
        dbstamp_params = json.loads(bsjson)
        btc_usd = float(dbstamp_params['last'])
    except:
        print "Unable to retrieve BTC Value"
        btc_usd = float(1.1)
    return btc_usd

def parsemyrigs(rigs,list_disabled=False):
    """
    :param rigs: pass the raw api return from mrrapi.myrigs()
    :param list_disabled: Boolean to list the disabled rigs
    :return: returns dict by algorithm
    """
    mrrrigs = {}
    # I am not a python programmer, do you know a better way to do this?
    # first loop to create algo keys
    # second loop populates rigs in algo
    for x in rigs['data']['records']:
        mrrrigs.update({str(x['type']): {}})
    for x in rigs['data']['records']:
        if debug:
            print x
        if (list_disabled or str(x['status']) != 'disabled') and not (str(x['name']).__contains__('retired') or str(x['name']).__contains__('test')):
            mrrrigs[str(x['type'])][int(x['id'])] = str(x['name'])
    if debug:
        print mrrrigs
    return mrrrigs
