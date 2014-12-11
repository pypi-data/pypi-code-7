#!/usr/bin/env python
'Wrappers around UPS commands'

import os
import tempfile
import tarfile
import urllib
from glob import glob
from subprocess import Popen, PIPE, check_call

import ups.products
import ups.depend
import ups.util

class UpsCommands(object):
    def __init__(self, path):
        '''Create a UPS command set.  

        The <path> argument is path of UPS product areas.
        '''
        if isinstance(path, type("")):
            path = path.split(":")
        self._products_path = path

    def ups(self, upscmdstr):
        '''
        Run a ups command string <upscmdstr> and return the full text output.  

        Eg: 

        .ups("list -aK+")
        '''
        return self.call(upscmdstr, cmd='ups')

    def call(self, cmdstr, cmd='ups', returnrc = False, usebash=True):
        '''
        Exec "cmd cmdstr" possibly with UPS set up. 

        If returnrc is True then return the return code instead stdout.
        '''
        cmdlist = list()

        for pdir in self._products_path:
            cmdlist.append(". %s/setups" % pdir)
        cmdlist.append(cmd + " " + cmdstr)
        line = ' && '.join(cmdlist)
        #print 'UPS CMD:',line
        if usebash:
            line = "/bin/bash -c '%s'" % line
        p = Popen(line, shell=True, stdout = PIPE)
        out,err = p.communicate()
        if returnrc:
            return p.returncode
        if p.returncode != 0:
            print 'STDOUT:'
            print out or ''
            print 'STDERR:'
            print err or ''
            raise RuntimeError, 'Command failed (%d): "%s"' % (p.returncode, line)
        return out

    def flavor(self):
        '''Return the output of "ups flavor"'''
        return self.ups("flavor").strip()

    def depend(self, product):
        return self.ups("depend " + ups.products.product_to_upsargs(product))

    def exists(self, product):
        return 0 == self.call("exist " + ups.products.product_to_upsargs(product), 
                              cmd='ups', returnrc = True)

    def avail(self):
        '''Return available products as list of Product objects.'''
        text = self.ups("list -aK+")
        ret = list()
        for line in text.split('\n'):
            line = line.strip()
            if not line: continue
            pd = ups.products.upslisting_to_product(line) # note, no repo on purpose
            ret.append(pd)
        return ret

    def full_dependencies(self):
        '''Return a tree of entire dependencies'''
        pds = self.avail()
        return ups.depend.full(self, pds)




def install(version, products_dir, temp_dir = None):
    '''
    Install UPS <version> in <products_dir>, maybe using <temp_dir> to do the build.
    '''
    version_underscore = 'v' + version.replace('.','_')

    if os.path.exists(os.path.join(products_dir, '.upsfiles')):
        return 'Already installed into directory: %s' % os.path.realpath(products_dir)

    if not os.path.exists(products_dir):
        os.makedirs(products_dir)

    temp_dir = temp_dir or tempfile.mkdtemp()
    temp_dir = os.path.realpath(temp_dir)
    print 'Using temporary directory: %s' % temp_dir
    os.path.exists(temp_dir) or os.makedirs(temp_dir)

    srctarball = "ups-%s-source.tar.bz2" % version
    srctarpath = os.path.join(temp_dir, srctarball)
    if not os.path.exists(srctarpath):
        #source_url = "http://oink.fnal.gov/distro/relocatable-ups/%s" % srctarball
        source_url = "http://oink.fnal.gov/distro/packages/ups/%s" % srctarball
        ups.util.download(source_url, srctarpath)

    stf = tarfile.open(srctarpath)
    stf.extractall(temp_dir)
    upsbuilddir = os.path.join(temp_dir, 'ups/' + version_underscore)
    check_call("./build_ups.sh " + temp_dir, shell='/bin/bash', cwd=upsbuilddir)
    #check_call("./tarUpsUpd.sh " + temp_dir, shell='/bin/bash', cwd=upsbuilddir)

    kernel, _,_,_, machine = os.uname()
    want = os.path.join(temp_dir, "ups-%s-%s*.tar.bz2" % (version, kernel))
    bintarball = glob(want)[0]
    tf = tarfile.open(bintarball)
    tf.extractall(products_dir)

    return 'Leaving temporary directory: "%s"' % temp_dir

