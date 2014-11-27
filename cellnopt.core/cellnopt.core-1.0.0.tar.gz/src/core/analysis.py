# -*- python -*-
#
#  This file is part of the cinapps.tcell package
#
#  Copyright (c) 2012-2013 - EMBL-EBI
#
#  File author(s): Thomas Cokelaer (cokelaer@ebi.ac.uk)
#                    Luca Cerone (luca.cerone@ebi.ac.uk)
#
#  Distributed under the GLPv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  website: www.cellnopt.org
#
##############################################################################

from cellnopt.core.cnograph import CNOGraph
import numpy

__all__ = [ "CNOAnalysis" ]


class CNOAnalysis(object):
    """Class to ease the analysis of performances of algorithms using CellNOpt.
    """

    def __init__(self, pkn = None , exp = None , predicted_vertices = None , predicted_network = None):
        """Constructor for the CNOAnalysis class.
        """

