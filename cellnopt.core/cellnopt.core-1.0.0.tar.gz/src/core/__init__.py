"""CellNOpt.Core


:: 

    from cellnopt.core import *



"""
import adj2sif
from adj2sif import *

import asp
from asp import *

import sif
from sif import *

import cnograph
from cnograph import *

import converter
from converter import *

import reactions
from reactions import *

import metabolites
from metabolites import *

import oldmidas
from oldmidas import *
import midas
from midas import *
import oldmidas
from oldmidas import MIDASReader

import normalisation
from normalisation import *

import sbml
from sbml import *

import sif2asp
from sif2asp import *

import sop2sif
from sop2sif import *


import tools
from tools import *

import XMLMidas
from XMLMidas import *


try:
    from cellnopt.data import cnodata
except:
    print("Be aware that we could not import cellnopt.data.cnodata. Install cellnopt.data")
    pass

def get_share_file(filename):
    import easydev
    return easydev.get_share_file("cellnopt.core", "data", filename)

def data(filename):
    import easydev
    return easydev.get_share_file("cellnopt.core", "data", filename)
    

