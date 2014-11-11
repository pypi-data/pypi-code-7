import tkinter as tk

from . import tktool
from .tktool import validateentry
from .tktool import codedoptionmenu

from . import scon
from . import defaultparam

class SizeBody(tk.Frame):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        prow = 0

        # RB
        # enabile and disable control will be needed
        self.rbs = []
        self.rblabels = []
        for i in range(scon.nrbx):
            if i == 0:
                rblabel = tk.Label(self, text='RB({0:d}):'.format(i+1))
            else:
                rblabel = tk.Label(self, text='({0:d}):'.format(i+1))
            rb = tktool.validateentry.Double(self)
            rb.config(width=10)
            rblabel.grid(row=prow, column=0, sticky=tk.E)
            rb.grid(row=prow, column=1, sticky=tk.W)
            self.rbs.append(rb)
            self.rblabels.append(rblabel)
            prow += 1

        # XILIM
        self.xilims = []
        self.xilimlabels = []
        for i in range(4):
            if i == 0:
                xilimlabel = tk.Label(self, text='XILIM({0:d})[nm]:'.format(i+1))
            elif i == 2:
                xilimlabel = tk.Label(self, text='({0:d})[nm]:'.format(i+1))
            else:
                xilimlabel = tk.Label(self, text='({0:d})[base]:'.format(i+1))
            xilim = tktool.validateentry.Double(self)
            xilim.config(width=10)
            xilimlabel.grid(row=prow, column=0, sticky=tk.E)
            xilim.grid(row=prow, column=1, sticky=tk.W)
            self.xilims.append(xilim)
            self.xilimlabels.append(xilimlabel)
            prow += 1

        # SLICE:
        self.slicelabel = tk.Label(self, text='SLICE:')
        self.slice = tktool.validateentry.Double(self)
        self.slice.config(width=10)
        self.slicelabel.grid(row=prow, column=0, sticky=tk.E)
        self.slice.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # STEP
        self.steplabel = tk.Label(self, text='STEP:')
        self.step = tktool.validateentry.Double(self)
        self.step.config(width=10)
        self.steplabel.grid(row=prow, column=0, sticky=tk.E)
        self.step.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # LIFO
        self.lifolabel = tk.Label(self, text='LIFO')
        self.lifooptions = [(False, 'False'), (True, 'True')]
        self.lifo = tktool.codedoptionmenu.CodedOptionMenu(self,
                self.lifooptions)
        self.steplabel.grid(row=prow, column=0, sticky=tk.E)
        self.step.grid(row=prow, column=1, sticky=tk.W)

        self.clear()

    def set(self, d):
        xval = d.get('rb', defaultparam.size_body_default['rb'])
        for w, x in zip(self.rbs, xval):
            w.set(x)

        xval = d.get('xilim', defaultparam.size_body_default['xilim'])
        for w, x in zip(self.xilims, xval):
            w.set(x)

        self.slice.set(d.get('slice',
            defaultparam.size_body_default['slice']))
        self.step.set(d.get('step',
            defaultparam.size_body_default['step']))
        self.lifo.set(d.get('lifo',
            defaultparam.size_body_default['lifo']))

    def get(self):
        d = {}
        d['rb'] = [w.get() for w in self.rbs]
        d['xilim'] = [w.get() for w in self.xilims]
        d['slice'] = self.slice.get()
        d['step'] = self.step.get()
        d['lifo'] = self.lifo.get()
        return d

    def clear(self):
        self.set(defaultparam.size_body_default)

    def validate(self):
        err = []
        for n, w in [
                ('slice', self.slice),
                ('step', self.step)]:
            e = w.validate()
            if e:
                err.append((n, e))
        return err if err else None

    def enable(self):
        for w in self.rbs:
            w.config(state=tk.NORMAL)
        for w in self.xilims:
            w.config(state=tk.NORMAL)
        self.slice.config(state=tk.NORMAL)
        self.step.config(state=tk.NORMAL)
        self.lifo.config(state=tk.NORMAL)

    def disable(self):
        for w in self.rbs:
            w.config(state=tk.DISABLED)
        for w in self.xilims:
            w.config(state=tk.DISABLED)
        self.slice.config(state=tk.DISABLED)
        self.step.config(state=tk.DISABLED)
        self.lifo.config(state=tk.DISABLED)
