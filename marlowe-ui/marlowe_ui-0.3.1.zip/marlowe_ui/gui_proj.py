import tkinter as tk

import tkinter.messagebox

from . import tktool
from .tktool import validateentry
from .tktool import codedoptionmenu
from .tktool import error
from .tktool import oneof

from . import scon
from . import defaultparam

from . import gui_proj_elem

Proj = tktool.oneof.OneofFactory(gui_proj_elem.ProjElem,
        defaultparam.proj_elem_default)
