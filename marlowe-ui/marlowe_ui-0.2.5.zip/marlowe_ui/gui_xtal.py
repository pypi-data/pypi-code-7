import tkinter as tk

from . import tktool
from .tktool import validateentry
from .tktool import codedoptionmenu

from . import scon
from . import defaultparam

from . import gui_xtal_layer

class Xtal(tk.Frame):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        prow = 0

        # QUIT | NEWS | UNIT | BASE

        # quit
        self.quitlabel = tk.Label(self, text='QUIT:')
        self.quitoptions = [(False, 'F: run normaly'), (True, 'T: terminates immediately after reporting on the target crystal')]
        self.quit = tktool.codedoptionmenu.CodedOptionMenu(self, self.quitoptions)
        self.quit.config(width=10, anchor='w')
        self.quitlabel.grid(row=prow, column=0, sticky=tk.W)
        self.quit.grid(row=prow+1, column=0, sticky=tk.EW)

        # news
        self.newslabel = tk.Label(self, text='NEWS:')
        self.newsoptions = [(1, '1: Input data, crystal densities, and brief notes ...'),
                (2, '2: Adds the interatomic separations and the neighbor lists ...'),
                (3, '3: Adds the transformation matrices relating the internal orthogonal coordinate system ...'),
                (4, '4: Adds a complete description of the crystallite ...')]
        self.news = tktool.codedoptionmenu.CodedOptionMenu(self, self.newsoptions)
        self.news.config(width=10, anchor='w')
        self.newslabel.grid(row=prow, column=1, sticky=tk.W)
        self.news.grid(row=prow+1, column=1, sticky=tk.EW)

        # unit
        self.unitlabel = tk.Label(self, text='UNIT:')
        self.unitoptions = [(-1, '-1: refer BASE value in &MODL.METRIC unit'),
                (0, '0: in &MODL.METRIC unit'),
                (1, '1: use lattice edge a'),
                (2, '2: use lattice edge b'),
                (3, '3: use lattice edge c')]
        self.unit = tktool.codedoptionmenu.CodedOptionMenu(self, self.unitoptions)
        self.unit.config(width=10, anchor='w')
        self.unitlabel.grid(row=prow, column=2, sticky=tk.W)
        self.unit.grid(row=prow+1, column=2, sticky=tk.EW)

        # base
        self.baselabel = tk.Label(self, text='BASE:')
        self.base = tktool.validateentry.Double(self)
        self.base.config(width=10)
        self.baselabel.grid(row=prow, column=3, sticky=tk.W)
        self.base.grid(row=prow+1, column=3, sticky=tk.EW)

        prow += 2

        # xtal_layer
        self.layerfrm = tk.LabelFrame(self, text='LAYER')
        self.layer = gui_xtal_layer.XtalLayer(self.layerfrm)
        self.layer.pack()
        self.layerfrm.grid(row=prow, columnspan=4)
        prow += 1

        self.clear()

    def set(self, v):
        self.quit.set(v.get('quit', defaultparam.xtal_default['quit']))
        self.news.set(v.get('news', defaultparam.xtal_default['news']))
        self.unit.set(v.get('unit', defaultparam.xtal_default['unit']))
        self.base.set(v.get('base', defaultparam.xtal_default['base']))
        self.layer.set(v.get('layer', defaultparam.xtal_default['layer']))
            
    def get(self):
        d = {}
        d['quit'] = self.quit.get()
        d['news'] = self.news.get()
        d['unit'] = self.unit.get()
        d['base'] = self.base.get()
        d['layer'] = self.layer.get()

        return d

    def clear(self):
        self.set(defaultparam.xtal_default)

    def validate(self):
        err = []
        for n, w in [('base', self.base)]:
            e = w.validate()
            if e:
                err.append((n, e))
        return err if err else None
