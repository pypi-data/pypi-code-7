import tkinter as tk

from . import tktool
from .tktool import validateentry
from .tktool import codedoptionmenu
from .tktool import oneof
from .tktool import gui_abstract

from . import scon
from . import defaultparam

from . import gui_site_elem
from . import gui_layer_surf
from . import axis



Site = tktool.oneof.OneofFactory(gui_site_elem.SiteElem,
        defaultparam.site_elem_default)

class XtalLayerElem(tk.Frame):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        self.disabled = False

        prow = 0

        # ALAT.a b c
        self.latticelabel = tk.Label(self, text='(a,b,c):')
        self.lattice = tktool.validateentry.Vec3d(self)
        self.lattice.config(width=10)
        self.latticelabel.grid(row=prow, column=0, sticky=tk.E)
        self.lattice.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # ALAT.bc ca ab
        self.anglelabel = tk.Label(self, text='angl:')
        self.angle = tktool.validateentry.Vec3d(self)
        self.angle.config(width=10)
        self.anglelabel.grid(row=prow, column=0, sticky=tk.E)
        self.angle.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        self.crystalframe = tk.Frame(self)

        # centre and poly fields
        self.centrepolylabel = tk.Label(self, text='CRYST.:')
        self.centreoptions = [
                (1, '1: (P) Primitive'),
                (2, '2: (I) Body-centered'),
                (3, '3: (A) End-centered on b-c plane'),
                (4, '4: (B) End-centered on c-a plane'),
                (5, '5: (C) End-centered on a-b plane'),
                (6, '6: (F) Face-centered')]
        self.centre = tktool.codedoptionmenu.CodedOptionMenu(self.crystalframe, self.centreoptions)
        self.centre.config(width=10, anchor='w')
        self.centre.pack(side=tk.LEFT)

        # poly
        #self.polylabel = tk.Label(self, text='POLY:')
        self.polyoptions = [(0, '0: monocrystalline'),
                (1, '1: polycrystalline'),
                (2, '2: amorphous')]
        self.poly = tktool.codedoptionmenu.CodedOptionMenu(self.crystalframe, self.polyoptions)
        self.poly.config(width=10, anchor='w')
        self.poly.pack(side=tk.LEFT)
        self.centrepolylabel.grid(row=prow, column=0, sticky=tk.E)
        self.crystalframe.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # dmax
        self.dmaxlabel = tk.Label(self, text='DMAX')
        self.dmax = tktool.validateentry.Double(self)
        self.dmax.config(width=10)
        self.dmaxlabel.grid(row=prow, column=0, sticky=tk.E)
        self.dmax.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # axis
        self.axisframe = axis.Axis(self)
        self.axisframe.grid(row=prow, column=0, columnspan=2, sticky=tk.E)
        prow += 1

        # rz, atom.lock and atom.order
        self.siteframe = tk.LabelFrame(self, text='SITE')
        self.site = Site(self.siteframe)
        self.site.pack()
        self.siteframe.grid(row=prow, column=0, columnspan=2)
        prow += 1

        # surface option
        self.surfoptframe = tk.LabelFrame(self, text='&SURF opt.')
        self.surfopt = gui_layer_surf.LayerSurfOption(self.surfoptframe)
        self.surfopt.pack()
        self.surfoptframe.grid(row=prow, column=0, columnspan=2)
        prow += 1

        self.clear()

        # surfopt_enabled just controls gui status but does not affect
        # on set() and get() method,

        self.disable_surfopt()

    def set(self, d):
        self.lattice.set(d.get('alat',
            defaultparam.xtal_layer_elem_default['alat'])[0:3])
        self.angle.set(d.get('alat',
            defaultparam.xtal_layer_elem_default['alat'])[3:6])

        self.centre.set(d.get('centre',
            defaultparam.xtal_layer_elem_default['centre']))
        self.dmax.set(d.get('dmax',
            defaultparam.xtal_layer_elem_default['dmax']))
        self.poly.set(d.get('poly',
            defaultparam.xtal_layer_elem_default['poly']))

        # axis is optional, if None is given for axis.set,
        # this frame is disabled.
        self.axisframe.set(d.get('axis', None))

        self.site.set(d.get('site',
            defaultparam.xtal_layer_elem_default['site']))

        if 'surfopt' in d and d['surfopt']:
            self.surfopt.set(d['surfopt'])
        else:
            self.surfopt.set(defaultparam.layer_surfopt_default)

    def get(self):
        d = {}
        if self.is_disabled():
            return d

        d['alat'] = list(self.lattice.get() + self.angle.get())
        d['centre'] = self.centre.get()
        d['dmax'] = self.dmax.get()
        d['poly'] = self.poly.get()

        daxis = self.axisframe.get()
        if daxis:
            d['axis'] = daxis

        d['site'] = self.site.get()
        d['surfopt'] = self.surfopt.get_nostatechk()
        return d

    def clear(self):
        self.set(defaultparam.xtal_layer_elem_default)

    def validate(self):
        err = []
        if self.is_disabled():
            return None
        for n, w in [
                ('lattice', self.lattice),
                ('angle', self.angle),
                ('dmax', self.dmax),
                ('axis', self.axisframe),
                ('site', self.site)
                ]:
            e = w.validate()
            if e:
                err.append((n, e))
        if self.surfopt_enabled:
            e = self.surfopt.validate()
            if e:
                err.append(('surfopt', e))

        return err if err else None

    def enable(self):
        self.lattice.config(state=tk.NORMAL)
        self.angle.config(state=tk.NORMAL)
        self.centre.config(state=tk.NORMAL)
        self.poly.config(state=tk.NORMAL)
        self.dmax.config(state=tk.NORMAL)
        self.axisframe.enable()
        self.site.enable()
        if self.surfopt_enabled:
            self.surfopt.enable()
        else:
            # keep widget disabled
            self.surfopt.disable()
        self.disabled = False

    def disable(self):
        self.lattice.config(state=tk.DISABLED)
        self.angle.config(state=tk.DISABLED)
        self.centre.config(state=tk.DISABLED)
        self.poly.config(state=tk.DISABLED)
        self.dmax.config(state=tk.DISABLED)
        self.axisframe.disable()
        self.site.disable()
        self.surfopt.disable()
        self.disabled = True

    def enable_surfopt(self):
        self.surfopt_enabled = True
        # change gui status
        if not self.is_disabled():
            self.surfopt.enable()

    def disable_surfopt(self):
        self.surfopt_enabled = False
        if not self.is_disabled():
            self.surfopt.disable()

    def is_disabled(self):
        return self.disabled
