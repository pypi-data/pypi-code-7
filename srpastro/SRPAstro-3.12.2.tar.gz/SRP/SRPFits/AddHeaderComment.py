""" Utility functions and classes for SRP

Context : SRP
Module  : Fits.py
Version : 1.1.2
Author  : Stefano Covino
Date    : 21/07/2014
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : AddHeaderComment (fitsfile, commentlist, outfilename=None)
            "fitfile" is the FITS file name.
            "commentlist" is a list with the comments to add.
            "outfilename" optional filename for output. Else input file file is overwritten.
            
            Function returns two values: (res, code). If res is False code reports the problem 
                (codes are in SRP.SRPFits.FitsConstants). Else res is True.

Remarks :

History : (01/10/2010) First version.
        : (25/04/2011) Input and output file names can be different.
        : (27/04/2011) Always list in output.
        : (21/07/2014) Better management of non-standard FITS headers.
"""

import warnings

import pyfits
import FitsConstants

def AddHeaderComment (fitsfile, commentlist, outfilename=None):
    try:
        hdr = pyfits.open(fitsfile)
    except IOError:
        return False,FitsConstants.FitsFileNotFound
    heder = hdr[0].header    
    for i in commentlist:
        heder.add_comment(i)
    #
    warnings.resetwarnings()
    warnings.filterwarnings('ignore', category=UserWarning, append=True)
    if outfilename == None:
        hdr.writeto(fitsfile,clobber=True,output_verify='ignore')
    else:
        hdr.writeto(outfilename,clobber=True,output_verify='ignore')
    warnings.resetwarnings() 
    warnings.filterwarnings('always', category=UserWarning, append=True)    
    return True,FitsConstants.FitsOk
