#!/usr/bin/env python
'''
General utilities.
'''

import re
import urllib

def match(things, **kwds):
    '''Return list of matching elements from sequence <things>.  

    The <kwds> hold things to match on.  Keys must name attributes of
    the elements of <things> or are ignored.  Values be regular
    expressions (not globs).

    '''
    def match_one(thing):
        for name, pat in kwds.items():
            string = getattr(thing, name, None)
            if string is None:
                continue

            if pat.startswith('re:'):
                pat = pat[3:]
                m = re.match(pat, string)
                if not m:
                    return
                g = m.group()
                if not g:
                    return
                if g != m.string:
                    return
                continue
            if pat != string:
                return

        return thing

    ret = list()
    for thing in things:
        if match_one(thing):
            ret.append(thing)
    return ret

def download(url, target):
    fd = urllib.urlopen(url)
    rc = fd.getcode() 
    if rc == 200:
        open(target,'wb').write(fd.read())
    else:
        raise RuntimeError, 'Failed to download (%d) %s' % (rc, url)
    return target

def slurp_lxml(url):
    '''
    Return an HTML tree object made from the content at the given URL
    '''
    import lxml.html
    fd = urllib.urlopen(url)
    rc = fd.getcode() 
    if rc != 200:
        raise RuntimeError, 'Failed to download (%d) %s' % (rc, url)
    text = fd.read()
    return lxml.html.fromstring(text)

def slurp_bs(url):
    '''
    Return an HTML tree object made from the content at the given URL
    '''
    import BeautifulSoup
    fd = urllib.urlopen(url)
    rc = fd.getcode() 
    if rc != 200:
        raise RuntimeError, 'Failed to download (%d) %s' % (rc, url)
    text = fd.read()
    return BeautifulSoup.BeautifulSoup(text)

# based on 
# http://stackoverflow.com/questions/686147/url-tree-walker-in-python
import sys
parse_re = re.compile('href="([^"]*)".*(..-...-.... ..:..).*?(\d+[^\s<]*|-)')
          # look for          a link    +  a timestamp  + a size ('-' for dir)
def slurp_apache_index(url):
    '''
    Return a list of file/director information from the Apache index at the given <url>.

    List is a tuple of (name, date, size).  If <name> is a directory, <size> is None.
    '''
    try:
        html = urllib.urlopen(url).read()
    except IOError, e:
        raise RuntimeError, 'error fetching %s: %s' % (url, e)
    if not url.endswith('/'):
        url += '/'
    files = parse_re.findall(html)
    ret = []
    for name, date, size in files:
        size = size.strip()
        if size == '-':
            size = None
        ret.append((name.strip(), date.strip(), size))
    return ret



