""" Utility functions and classes for SRP

Context : SRP
Module  : Fits.py
Version : 1.2.0
Author  : Stefano Covino
Date    : 16/12/2014
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (23/05/2010) First version.
        : (14/02/2012) Possibility to read extensions.
        : (16/12/2014) Manage wrong FITS headers.
"""

import pyfits
import FitsConstants

def GetHeader (fitsfile, ext=0):
    try:
        hdr = pyfits.open(fitsfile)
    except IOError:
        return None,FitsConstants.FitsFileNotFound
    hdr[ext].verify('silentfix+ignore')
    heder = hdr[ext].header
    return heder,FitsConstants.FitsHeaderFound
    

    
