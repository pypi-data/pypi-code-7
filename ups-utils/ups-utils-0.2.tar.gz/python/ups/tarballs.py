#!/usr/bin/env python
'''
Interact with UPS packaged tarballs.
'''

import os
import urllib

default_url_pattern = 'http://oink.fnal.gov/distro/packages/{name}/{tarball}'

# fixme move this and similar use in commands.py to some util module
def download(url, target):      
    if not os.path.exists(target):
        urllib.urlretrieve(url, target)

def form_url(me, url_pattern = default_url_pattern):
    '''
    Form the URL to a package given its ManifestEntry object <me>
    '''
    return url_pattern.format(**me._asdict())

    

