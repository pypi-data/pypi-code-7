# -*- coding: utf-8 -*-
#
#   Copyright © 2014 Stephan Zevenhuizen
#   SPIEPy, (04-12-2014).
#

'''
    Demonstration image files for SPIEPy.
'''

__all__ = ['list_demo_files', 'load_demo_file']

import demos

def list_demo_files():
    '''
    List filenames of demo images.

    Returns:
        demos : dict
            Dictionary of enumerated filenames for the filename argument in
            the function load_demo_file.
    '''
    return demos.list_demo_files()

def load_demo_file(f_name):
    '''
    Loads the demo file into an image.

    Args:
        f_name : str
            The filename of the demo file.

    Returns:
        im : ndarray
            The image.  
    '''
    return demos.load_demo_file(f_name)
