# coding: utf-8
""" root gui
"""

import tkinter as tk
import tkinter.ttk

from . import tktool
from .tktool import error

from . import scon

from . import defaultparam

from . import gui_modl
from . import gui_atom
from . import gui_xtal
from . import gui_surf
from . import gui_size
from . import gui_outp
from . import gui_proj
from . import vpar

class Root(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        # count up current row
        prow = 0

        # comment
        tk.Label(self, text='comment1:').grid(row=prow, column=0, sticky=tk.E)
        self.comment1 = tktool.TruncatedEntry(self, limitwidth=80, width=81)
        self.comment1.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        tk.Label(self, text='comment2:').grid(row=prow, column=0, sticky=tk.E)
        self.comment2 = tktool.TruncatedEntry(self, limitwidth=80, width=81)
        self.comment2.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # frame including other records
        #
        # r0: &ATOM | &XTL | MISC.
        #     ------+      |
        # r1: &VPAR |      |

        self.frame2 = tk.Frame(self)
        
        # atom
        self.atomframe = tk.LabelFrame(self.frame2, text='&ATOM') 
        self.atom = gui_atom.Atom(self.atomframe)
        self.atom.pack(fill=tk.BOTH, expand=False)
        self.atomframe.grid(row=0, column=0, sticky=tk.N+tk.EW)

        # vpar
        self.vparframe = tk.LabelFrame(self.frame2, labelwidget=tk.Label(self.frame2, text='&VPAR\n(Inter-atomic Potential)', justify=tk.LEFT))
        self.vpar = vpar.Vpar(self.vparframe)
        self.vpar.pack(fill=tk.BOTH, expand=True)
        self.vparframe.grid(row=1, column=0, sticky=tk.NSEW)
        self.frame2.grid_rowconfigure(1, weight=1)

        # xtal
        self.xtalframe = tk.LabelFrame(self.frame2, text='&XTAL') 
        self.xtal = gui_xtal.Xtal(self.xtalframe)
        self.xtal.pack()
        self.xtalframe.grid(row=0, column=1, rowspan=2, sticky=tk.N+tk.W)

        # tab-switched frames
        self.tab = tkinter.ttk.Notebook(self.frame2)

        # proj
        self.proj = gui_proj.Proj(self.tab)
        self.tab.add(self.proj, text='&PROJ')

        # surf
        self.surf = gui_surf.Surf(self.tab, root=self)
        self.tab.add(self.surf, text='&SURF')

        # modl
        self.modl = gui_modl.Modl(self.tab)
        self.tab.add(self.modl, text='&MODL')

        # outp
        self.outp = gui_outp.Outp(self.tab)
        self.tab.add(self.outp, text='&OUTP')

        # size
        self.size = gui_size.Size(self.tab)
        self.tab.add(self.size, text='&SIZE')

        self.tab.grid(row=0, column=2, rowspan=2, sticky=tk.N+tk.W)

        self.frame2.grid(row=prow, column=0, columnspan=2)

        prow += 1

        # make inter-gui messaging
        self.surf.link_xtallayerelem(self.xtal.layer.view)
            
        # set default value
        self.clear()

    def set(self, v):
        """set data to gui
        """
        self.comment1.set(v.get('comment1',
            defaultparam.root_default['comment1']))
        self.comment2.set(v.get('comment2',
            defaultparam.root_default['comment2']))
        self.modl.set(v.get('modl',
            defaultparam.root_default['modl']))
        self.atom.set(v.get('atom',
            defaultparam.root_default['atom']))
        self.xtal.set(v.get('xtal',
            defaultparam.root_default['xtal']))
        self.surf.set(v.get('surf',
            defaultparam.root_default['surf']))
        self.size.set(v.get('size',
            defaultparam.root_default['size']))
        self.outp.set(v.get('outp',
            defaultparam.root_default['outp']))
        self.proj.set(v.get('proj',
            defaultparam.root_default['proj']))
        self.vpar.set(v.get('vpar',
            defaultparam.root_default['vpar']))
        
    def get(self):
        """return the context of gui in Data structure
        befor get(). validation is recommended 
        retrun value is compatible to the argument for viewparam.ViewParam.map_load
        """
        d = {}
        # commen record
        d['comment1'] = self.comment1.get()
        d['comment2'] = self.comment2.get()

        # modl record
        d['modl'] = self.modl.get()

        # atom record
        d['atom'] = self.atom.get()

        # xtal
        d['xtal'] = self.xtal.get()

        # surf
        d['surf'] = self.surf.get()

        # size
        d['size'] = self.size.get()

        # outp
        d['outp'] = self.outp.get()

        # proj 
        d['proj'] = self.proj.get()

        # vpar
        d['vpar'] = self.vpar.get()

        return d

    def clear(self):
        self.set(defaultparam.root_default)

    def validate(self):
        """validate control value
        return: tuple of (result, reason)
            result: True | False
            reason: structured data to descrive error reason (default is None)
        """
        # comment1 and 2 are automatially truncated in 80 chars

        errordata = {}

        # modl
        errordata['modl'] = self.modl.validate()

        # atom
        errordata['atom'] = self.atom.validate()

        # xtal
        errordata['xtal'] = self.xtal.validate()

        # surf
        errordata['surf'] = self.surf.validate()

        # size
        errordata['size'] = self.size.validate()

        # outp
        errordata['outp'] = self.outp.validate()

        # proj
        errordata['proj'] = self.proj.validate()

        # vpar
        # validate is not implemented yet

        # join error structure
        err = []

        for name, e in errordata.items():
            if e:
                err.append( (name, e) )

        return err if err else None

