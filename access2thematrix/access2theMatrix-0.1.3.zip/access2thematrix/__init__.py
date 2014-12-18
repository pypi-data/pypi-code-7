# -*- coding: utf-8 -*-
#
#   Copyright © 2014 Stephan Zevenhuizen
#   access2theMatrix, (18-12-2014).
#

'''
    access2theMatrix is a Python library for accessing Omicron NanoTechnology's
    MATRIX Control System result files. Only topography image data will be
    accessed by this library.
'''

__version__ = '0.1.3'

__all__ = ['Im', 'MtrxData']

import access2thematrix

class Im(access2thematrix.Im):
    '''access2theMatrix_image_structure'''

class MtrxData(access2thematrix.MtrxData):
    '''
        The methods to open result files and to select one out of the four
        traces (forward/up, backward/up, forward/down and backward/down).

    '''

    def open(self, result_data_file):
        '''
        Opens a MATRIX Control System result file.

        In attribute scan the images are stored. In attribute param the
        metadata and parameters of the experiment are stored. See source code.

        Parameters
        ----------
        result_data_file : str
            The pathname of the MATRIX Control System result file.

        Returns
        -------
        traces : dict
            Dictionary of enumerated tracenames for the trace parameter in
            the instancemethod select_image.
        message : str
            Error or succes message of the opening of the file.
        '''
        return access2thematrix.MtrxData.open(self, result_data_file)

    def select_image(self, trace = access2thematrix.MtrxData.ALL_TRACES[0]):
        '''
        The selected image is returned.

        Parameters
        ----------
        trace : str, optional
            Use the traces dictionary, a return from the open method, to set
            this parameter.

        Returns
        -------
        im : access2theMatrix_image_structure
            Returns a Im class (image structure) containing the selected
            image and metadata.
        message : str
            Error or succes message of the image selection.
        '''
        return access2thematrix.MtrxData.select_image(self, trace)
