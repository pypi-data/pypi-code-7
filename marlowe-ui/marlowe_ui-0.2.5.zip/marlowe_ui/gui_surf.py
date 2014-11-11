import tkinter as tk

from . import tktool
from .tktool import validateentry
from .tktool import codedoptionmenu

from . import scon
from . import defaultparam

class Surf(tk.Frame):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        self._xtallayerelem = None

        prow = 0

        # surface (0, 1, 2, 3, or >=6)
        self.surfacelabel = tk.Label(self, text='SURFCE:')
        self.surfaceoptions = [
                (0, '0: No external surfaces'),
                (1, '1: Front'),
                (2, '2: Front + Back side'),
                (3, '3: F+B+limited lateral extent'),
                #(6, '>=6: User supplied (not implemented)')
                (-1, '-1: Internal Primary Atoms mode'),
                ]
        self.surfacevardefault = self.surfaceoptions[0]
        self.surface = tktool.codedoptionmenu.CodedOptionMenu(self, self.surfaceoptions)
        self.surface.config(width=20, anchor='w')
        # reset option in order to introduce command when menu is selected
        self.surface.set_new_option(self.surfaceoptions,
                command=self._surface_action)

        self.surfacelabel.grid(row=prow, column=0, sticky=tk.E)
        self.surface.grid(row=prow, column=1, sticky=tk.W)

        prow += 1

        # LYME (default 1)
        self.lymelabel = tk.Label(self, text='LYME:')
        self.lymeoptions = [(i, str(i)) for i in range(1, scon.nlay+1)]
        self.lymedefault = self.lymeoptions[0]
        self.lyme = tktool.codedoptionmenu.CodedOptionMenu(
                self, self.lymeoptions)
        self.lyme.config(width=4, anchor='w')
        self.lymelabel.grid(row=prow, column=0, sticky=tk.E)
        self.lyme.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # CALC
        # temporally skipped

        # available at surfce == 1, 2, 3
        # (if surfce==0 inner primary atom mode, but is not valid now)
        # SIDES
        self.sideslabel = tk.Label(self, text='SIDES:')
        self.sides = tktool.validateentry.Vec3d(self)
        self.sides.config(width='10')
        self.sideslabel.grid(row=prow, column=0, sticky=tk.E)
        self.sides.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # RSRF
        self.rsrflabel = tk.Label(self, text='RSRF:')
        self.rsrf = tktool.validateentry.Vec3d(self)
        self.rsrf.config(width='10')
        self.rsrflabel.grid(row=prow, column=0, sticky=tk.E)
        self.rsrf.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # valid if surfce == 3
        # CORNER
        # self.cornerlabel = tk.Label(self, text='CORNER:')
        # self.corner = tktool.validateentry.Vec2d(self)
        # self.corner.config(width='10')
        # self.cornerlabel.grid(row=prow, column=0, sticky=tk.E)
        # self.corner.grid(row=prow, column=1, sticky=tk.W)
        # prow += 1

        # EDGE
        self.edgelabel = tk.Label(self, text='EDGE:')
        self.edge = tktool.validateentry.Vec2d(self)
        self.edge.config(width='10')
        self.edgelabel.grid(row=prow, column=0, sticky=tk.E)
        self.edge.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        self.clear()

    def set(self, d):
        if 'surfce' in d:
            idx = d['surfce']
            if -1 <= idx <= 3:
                self.surface.set(idx)
            else:
                self.surface.set(6)
        if 'lyme' in d:
            self.lyme.set(d['lyme'])
        if 'sides' in d:
            self.sides.set(d['sides'])
        if 'rsrf' in d:
            self.rsrf.set(d['rsrf'])
        # if 'corner' in d:
        #    self.corner.set(d['corner'])
        if 'edge' in d:
            self.edge.set(d['edge'])

        self.set_avail_by_surface()

    def get(self):
        d = {}
        d['surfce'] = self.surface.get()
        s = d['surfce']
        if s >= 1 or s == -1:
            d['lyme'] = self.lyme.get()
            d['sides'] = self.sides.get()
            d['rsrf'] = self.rsrf.get()
        if s == 3:
            # d['corner'] = self.corner.get()
            d['edge'] = self.edge.get()
        return d

    def clear(self):
        self.set(defaultparam.surf_default)

    def validate(self):
        err = []
        #r = self.surface.validate()
        #if r:
        #    err.append(('surfce', r))
        s = self.surface.get() 
        if s >= 1 or s == -1:
            r = self.lyme.validate()
            if r:
                err.append(('lyme', r))
            r = self.sides.validate()
            if r:
                err.append(('sides', r))
            r = self.rsrf.validate()
            if r:
                err.append(('rsrf', r))
        if s == 3:
            # r = self.corner.validate()
            # if r:
            #    err.append(('corner', r))
            r = self.edge.validate()
            if r:
                err.append(('edge', r))

        return err if err else None

    def link_xtallayerelem(self, widget):
        self._xtallayerelem = widget

    def _surface_action(self, value):
        self.set_avail_by_surface()

    def _set_avail_by_surface_ext(self):
        # change status outside the widget
        if self._xtallayerelem:
            v = self.surface.get()

            if v in (-1, 1, 2, 3):
                self._xtallayerelem.enable_surfopt()
            else:
                self._xtallayerelem.disable_surfopt()

    def set_avail_by_surface(self):
        s = self.surface.get()
        if s == 0:
            self.lyme.disable()
            self.sides.disable()
            self.rsrf.disable()
            #self.corner.disable()
            self.edge.disable()
        elif s in (-1, 1, 2):
            self.lyme.enable()
            self.sides.enable()
            self.rsrf.enable()
            #self.corner.disable()
            self.edge.disable()
        elif s == 3:
            self.lyme.enable()
            self.sides.enable()
            self.rsrf.enable()
            #self.corner.enable()
            self.edge.enable()
        self._set_avail_by_surface_ext()

    def enable(self):
        self.surface.enable()
        self.set_avail_by_surface()

    def disable(self):
        self.surface.disable()
        self.lyme.disable()
        self.sides.disable()
        self.rsrf.disable()
        #self.corner.disable()
        self.edge.disable()
