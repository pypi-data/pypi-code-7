import tkinter as tk

from . import tktool
from .tktool import oneof

from . import scon
from . import defaultparam

from . import gui_xtal_layer_elem as elem

XtalLayer = tktool.oneof.OneofFactory(elem.XtalLayerElem, defaultparam.xtal_layer_elem_default)
