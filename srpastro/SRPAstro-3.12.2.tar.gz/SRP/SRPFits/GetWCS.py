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

History : (15/07/2010) First version.
        : (20/12/2010) Possibility of badly formatted ECS header included.
        : (23/08/2013) NUMPY_MODE in wcs.
        : (16/12/2014) Manage wrong FITS headers.
"""

import FitsConstants
import astLib.astWCS as aw
from GetHeader import GetHeader
import FitsConstants



def GetWCS (fitsfile, extension=0, orig00=False):
    heder = GetHeader(fitsfile,extension)
    if heder[1] == FitsConstants.FitsHeaderFound:
        try:
            wcs = aw.WCS(heder[0],mode='pyfits')
            wcs.NUMPY_MODE = orig00
        except IOError:
            return None,FitsConstants.FitsFileNotFound
        except ValueError:
            return None,FitsConstants.FitsWCSNotKnown
        return wcs,FitsConstants.FitsWCSFound
    else:
        return None,FitsConstants.FitsFileNotFound

