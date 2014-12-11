#!/usr/bin/env python
'''
Interact with a UPS package mirror
'''

# FIXME: make a generic mirror object that can have specifics given in a configuration file.


import os
import shelve
import urllib

from . import manifest
from . import util




class Oink(object):
    '''
    The original "oink" mirror.
    '''

    server='oink.fnal.gov'
    tarball_urlpat = 'http://{server}/distro/packages/{name}/{tarball}'
    manifest_urlpat = 'http://{server}/distro/manifest/{suite}/{version}/{manifest}'
    manifest_binpat = '{suite}-{version_dotted}-{flavor}-{quals_dashed}_MANIFEST.txt'
    manifest_srcpat = '{suite}-{version_dotted}-source_MANIFEST.txt'

    def __init__(self, cachedir = '~/.ups-util/cache/'):
        cachedir = os.path.expanduser(os.path.expandvars(cachedir))
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)
        self._shelf = shelve.open(os.path.join(cachedir, 'ups-mirror-oink'))
        self.mfs = dict()
        self.mes = set()
        for mfname, mftext in self._shelf.items():
            self._add_manifest_nocache(mfname, mftext)

    def _add_manifest_nocache(self, mfname, mftext):
        mflist = manifest.parse_text(mftext)
        self.mfs[mfname] = mflist
        for me in mflist:
            self.mes.add(me)
        return mflist

    # api
    def add_manifest(self, mfname, mftext):
        '''
        Add a manifest named <mfname> and consisting of text <mftext>.
        '''
        mflist = self._add_manifest_nocache(mfname, mftext)
        self._shelf[mfname] = mftext
        return mflist

    def manifest_name(self, suite, version, flavor, quals = ''):
        '''
        Return the manifest file name.
        '''
        assert version.startswith('v')
        version_dotted = version[1:].replace('_','.')
        quals_dashed = quals.replace(':','-')
        if flavor == 'source':
            return self.manifest_srcpat.format(**locals())
        return self.manifest_binpat.format(**locals())

    def manifest_url(self, suite, version, flavor, quals = ''):
        '''
        Return URL to the manifest file.
        '''
        mfname = self.manifest_name(suite, version, flavor, quals)
        return self.manifest_urlpat.format(server=self.server, manifest=mfname, **locals())
        
    # api
    def load_manifest(self, suite, version, flavor, quals=''):
        '''
        Load a manifest, return list of ManifestElements
        '''
        mfname = self.manifest_name(suite, version, flavor, quals)
        mf = self.mfs.get(mfname)
        if mf: return mf

        url = self.manifest_url(suite, version, flavor, quals)
        print 'Downloading manifest: "%s"' % url
        mftext = manifest.download(url)
        if not mftext: 
            raise RuntimeError, 'Failed to download: %s' % url 
            return

        mflist = self.add_manifest(mfname, mftext)
        return mflist

    # api
    def avail(self, mfname = None):
        '''Return known available entries for manifest named <mfname>.  

        If no name is given, all are returned.
        '''
        if not mfname:
            return self.mes
        return self.mfs.get(mfname)


    def download(self, me, path, force = False):
        target = os.path.join(path, me.tarball)
        if os.path.exists(target):
            if force:
                os.remove(target)
            else:
                return target
        url = self.tarball_urlpat.format(name=me.name, version=me.version, tarball=me.tarball, server=self.server)
        return util.download(url, target)
        
class Scisoft(Oink):
    server='scisoft.fnal.gov'
    tarball_urlpat = 'http://{server}/scisoft/packages/{name}/{version}/{tarball}'
    manifest_urlpat = 'http://{server}/scisoft/manifest/{suite}/{version}/{manifest}'
    manifest_binpat = '{suite}-{version_dotted}-{flavor}-{quals_dashed}_MANIFEST.txt'
    manifest_srcpat = '{suite}-{version_dotted}-source_MANIFEST.txt'
    pass
    
def find_manifests(server, limit = None):
    '''Return a list of URLs to all manifest files found.

    The URL patterns for manifest files must be like:
    # <url>/<suite>/v<version_underscore>/*_MANIFEST.txt

    Note, this assumes simple Apache index lists and fails to work on
    the idiocy that is served by the new scisoft server.

    '''

    if server == 'oink':        # fixme factor out
        url = 'http://oink.fnal.gov/distro/manifest/'
    if server == 'scisoft':
        url = 'http://scisoft.fnal.gov/scisoft/manifest/'
    assert url                  # fixme

    manifests = list()

    for name,date,size in util.slurp_apache_index(url):
        if size:                # skip files
            continue
        if name.endswith('/'):
            name = name[:-1]
        suite_dir = name
        if limit and suite_dir not in limit:
            continue
        suite_url = os.path.join(url, suite_dir)
        #print suite_url
        for vname, vdate, vsize in util.slurp_apache_index(suite_url):
            if vsize:           # skip files
                continue
            ver_url = os.path.join(url, suite_dir, vname)
            #print ver_url
            mans = [n for n,d,s in util.slurp_apache_index(ver_url) if s and n.endswith('_MANIFEST.txt')]
            manifests += [os.path.join(ver_url, m) for m in mans]

    return manifests
    
    

def make(name = 'scisoft', *args, **kwds):
    if name == 'oink':
        return Oink(*args, **kwds)
    if name == 'scisoft':
        return Scisoft(*args, **kwds)
    KeyError, 'Unknown ups mirror: "%s"' % name
