import tkinter as tk

from . import tktool
from .tktool import validateentry
from .tktool import gui_abstract

from . import defaultparam

class LayerSurfOption(tk.Frame, tktool.gui_abstract.GUIAbstract):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)
        tktool.gui_abstract.GUIAbstract.__init__(self,
                defaultparam=defaultparam.layer_surfopt_default)

        prow = 0

        # depth
        self.depthlabel = tk.Label(self, text='DEPTH')
        self.depth = tktool.validateentry.Double(self)
        self.depth.config(width=10)
        self.add_widget('depth', self.depth)

        self.depthlabel.grid(row=prow, column=0, sticky=tk.E)
        self.depth.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # origin
        self.originlabel = tk.Label(self, text='ORIGIN')
        self.origin = tktool.validateentry.Vec3d(self)
        self.origin.config(width=10)
        self.add_widget('origin', self.origin)

        self.originlabel.grid(row=prow, column=0, sticky=tk.E)
        self.origin.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # lo
        self.lolabel = tk.Label(self, text='LO')
        self.lo = tktool.validateentry.IntPositive(self)
        self.lo.config(width=10)
        self.add_widget('lo', self.lo)

        self.lolabel.grid(row=prow, column=0, sticky=tk.E)
        self.lo.grid(row=prow, column=1, sticky=tk.W)
        prow += 1
