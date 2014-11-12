'''
Created on 2 oct. 2014

@author: coissac
'''

import urllib2
import os
import imp
import base64
import zipimport
import importlib

from distutils.version import LooseVersion
from distutils.errors import DistutilsError
from distutils import log


from obidistutils.serenity.globals import PIP_MINVERSION, \
                                          local_pip                       # @UnusedImport
                    
                    
from obidistutils.serenity.util import get_serenity_dir
import sys
import pkgutil


def is_pip_installed(minversion=PIP_MINVERSION):
    try:
        import pip  # @UnresolvedImport
        ok = LooseVersion(pip.__version__) >= LooseVersion(minversion)
    except:
        ok = False
        
    return ok

def get_a_pip_module(minversion=PIP_MINVERSION):
    
    global local_pip

    tmpdir = get_serenity_dir()
    
    if not local_pip:    
        if not is_pip_installed(minversion):
            try:
                pipinstallscript = urllib2.urlopen('https://bootstrap.pypa.io/get-pip.py')
            except:
                raise DistutilsError,"Pip (>=%s) is not install on your system and I cannot install it" % PIP_MINVERSION
            
            script = pipinstallscript.read()
            getpip_py = os.path.join(tmpdir, "get-pip.py")
            with open(getpip_py, "wb") as fp:
                log.info("Downloading temporary pip...")
                fp.write(script)
                log.info("   done.")
                
            getpip = imp.load_source("getpip",getpip_py)
            ZIPFILE=getpip.ZIPFILE
    
            pip_zip = os.path.join(tmpdir, "pip.zip")
            with open(pip_zip, "wb") as fp:
                log.info("Installing temporary pip...")
                fp.write(base64.decodestring(ZIPFILE))
                log.info("   done.")
                
            # Add the zipfile to sys.path so that we can import it
            sys.path = [pip_zip] + sys.path
            
    
        pipmodule = importlib.import_module('pip') 
            
        # Prepare the CERT certificat for https download
            
        cert_path = os.path.join(tmpdir, "cacert.pem")
        
        with open(cert_path, "wb") as cert:
            cert.write(pkgutil.get_data("pip._vendor.requests", "cacert.pem"))
            
        os.environ.setdefault("PIP_CERT", cert_path)
           
        assert LooseVersion(pipmodule.__version__) >= minversion, \
               "Unable to find suitable version of pip get %s instead of %s" % (pipmodule.__version__,
                                                                                minversion)
        local_pip.append(pipmodule)
       
    return local_pip[0]
            
