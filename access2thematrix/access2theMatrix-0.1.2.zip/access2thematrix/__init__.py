# -*- coding: utf-8 -*-
#
#   Copyright © 2014 Stephan Zevenhuizen
#   access2theMatrix, (06-12-2014).
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

'''
    access2theMatrix is a Python library for accessing Omicron NanoTechnology's
    MATRIX Control System result files. Only topography image data will be
    accessed by this library.
'''

__version__ = '0.1.2'

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
