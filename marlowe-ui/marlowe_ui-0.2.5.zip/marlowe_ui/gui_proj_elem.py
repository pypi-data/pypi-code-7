import tkinter as tk

from . import tktool
from .tktool import validateentry
from .tktool import codedoptionmenu

from . import scon
from . import defaultparam

class ProjElem(tk.Frame):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        prow = 0

        # prim
        self.primoptions = [
                (0, '0:Full cascade'),
                (1, '1:PKA and initial disp.'),
                (2, '2:PKA only')
                ]
        self.prim = tktool.codedoptionmenu.CodedOptionMenu(self,
                self.primoptions)
        self.prim.config(width=10, anchor='w')
        self.primlabel = tk.Label(self, text='PRIM:')
        self.primlabel.grid(row=prow, column=0, sticky=tk.E)
        self.prim.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # maxrun
        self.maxrunlabel = tk.Label(self, text='MAXRUN:')
        self.maxrun = tktool.validateentry.Int(self)
        self.maxrun.config(width=10)
        self.maxrunlabel.grid(row=prow, column=0, sticky=tk.E)
        self.maxrun.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # laip
        self.laiplabel = tk.Label(self, text='LAIP:')
        self.laip = tktool.validateentry.Int(self)
        self.laip.config(width=10)
        self.laiplabel.grid(row=prow, column=0, sticky=tk.E)
        self.laip.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # ekip
        self.ekiplabel = tk.Label(self, text='EKIP:')
        self.ekip = tktool.validateentry.Double(self)
        self.ekip.config(width=10)
        self.ekiplabel.grid(row=prow, column=0, sticky=tk.E)
        self.ekip.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        #trmp
        self.trmpoptions = [
                (True, 'T:external cood. of LYME layer'),
                (False, 'F:internal coord. of LYME layer')]
        self.trmp = tktool.codedoptionmenu.CodedOptionMenu(self,
                self.trmpoptions)
        self.trmp.config(anchor='w', width=20)
        self.trmplabel = tk.Label(self, text='TRMP:')
        self.trmplabel.grid(row=prow, column=0, sticky=tk.E)
        self.trmp.grid(row=prow, column=1, sticky=tk.W+tk.E)
        prow += 1

        # raip
        self.raip = tktool.validateentry.Vec3d(self)
        self.raip.config(width=10)
        self.raiplabel = tk.Label(self, text='RAIP:')
        self.raiplabel.grid(row=prow, column=0, sticky=tk.E)
        self.raip.grid(row=prow, column=1, sticky=tk.W+tk.E)
        prow += 1

        # refip
        self.refip = tktool.validateentry.Vec3d(self)
        self.refip.config(width=10)
        self.refiplabel = tk.Label(self, text='REFIP:')
        self.refiplabel.grid(row=prow, column=0, sticky=tk.E)
        self.refip.grid(row=prow, column=1, sticky=tk.W+tk.E)
        prow += 1

        # lrip
        self.lriplabel = tk.Label(self, text='LRIP:')
        self.lrip = tktool.validateentry.Int(self)
        self.lrip.config(width=10)
        self.lriplabel.grid(row=prow, column=0, sticky=tk.E)
        self.lrip.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # leap
        self.leapoptions = [
                (0, '0:Isotropic in all space'),
                (1, '1:Isotropic in z >=0 hemisphere'),
                (2, '2:Isotorpic in first octant'),
                (3, '3:1/48 space bordered by <001>, <111>, <101>'),
                (4, '4:Specify beam direction by BEAM or THA and PHI record.\n'
                    + 'Aleatory is applied on beam divergence and initial position'),
                (5, '5:Similar to 4, but aleatory is applied only initial position'),
                (6, '6:Similar to 6, but no aleatory is applied.'),
                # (10, '10:user specified' ),
                (20, '20:Selected uniformly in the initial impact parallelogram given by LYME layer'),
                (21, '21:area bounded by 20 and AXISA'),
                (22, '22:area bounded by 20, AXISA, and AXISB'),
                (23, '23:Selected uniformly in an ellipse inscribed in the initial impact parallelogram'),
                (25, '25:Specify initial position. Aleatory is taken into account.'),
                (26, '26:Specify initial position. Aleatory is not taken into account.'),
                #(30, '30:'),
                ]
        self.leap = tktool.codedoptionmenu.CodedOptionMenu(self,
                self.leapoptions)
        self.leap.config(anchor='w', width=10)
        self.leaplabel = tk.Label(self, text='LEAP:')
        self.leaplabel.grid(row=prow, column=0, sticky=tk.E)
        self.leap.grid(row=prow, column=1, sticky=tk.W+tk.E)
        prow += 1

        #miller
        self.milleroptions = [
                (True, 'T: Use Miller indices'),
                (False, 'F: Use THA and PHI')]
        self.miller = tktool.codedoptionmenu.CodedOptionMenu(self,
                self.milleroptions)
        self.miller.config(anchor='w', width=20)
        # reset option in order to introduce command when menu is selected
        self.miller.set_new_option(self.milleroptions, command=self._miller_action)
        self.millerlabel = tk.Label(self, text='MILLER:')
        self.millerlabel.grid(row=prow, column=0, sticky=tk.E)
        self.miller.grid(row=prow, column=1, sticky=tk.W+tk.E)
        prow += 1

        # beam
        self.beam = tktool.validateentry.Vec3d(self)
        self.beam.config(width=10)
        self.beamlabel = tk.Label(self, text='BEAM:')
        self.beamlabel.grid(row=prow, column=0, sticky=tk.E)
        self.beam.grid(row=prow, column=1, sticky=tk.W+tk.E)
        prow += 1

        # tha
        self.thalabel = tk.Label(self, text='THA:')
        self.tha = tktool.validateentry.Double(self)
        self.tha.config(width=10)
        self.thalabel.grid(row=prow, column=0, sticky=tk.E)
        self.tha.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # phi
        self.philabel = tk.Label(self, text='PHI:')
        self.phi = tktool.validateentry.Double(self)
        self.phi.config(width=10)
        self.philabel.grid(row=prow, column=0, sticky=tk.E)
        self.phi.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # dvrg
        self.dvrglabel = tk.Label(self, text='DVRG:')
        self.dvrg = tktool.validateentry.Double(self)
        self.dvrg.config(width=10)
        self.dvrglabel.grid(row=prow, column=0, sticky=tk.E)
        self.dvrg.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # ranx
        self.ranxs = []
        self.ranxrowlabels = []
        self.ranxrowframes = []
        ranxcolumns = 4
        # calculate how to align cells 4*q + r
        q, r = divmod(scon.nrnx, ranxcolumns)
        for i in range(scon.nrnx):
            r, c = divmod(i, ranxcolumns)
            if c == 0:
                # prepare label
                if r == 0:
                    ranxlabel = tk.Label(self,
                            text='RANX({0:d}-):'.format(i+1))
                else:
                    ranxlabel = tk.Label(self,
                            text='({0:d}-):'.format(i+1))
                self.ranxrowlabels.append(ranxlabel)

                # prepare frame
                self.ranxrowframes.append(tk.Frame(self))
            
            # Int entry box
            ranx = tktool.validateentry.Int(self.ranxrowframes[r])
            ranx.config(width=8)
            ranx.pack(side=tk.LEFT)
            self.ranxs.append(ranx)

        for lab, fra in zip(self.ranxrowlabels, self.ranxrowframes):
            lab.grid(row=prow, column=0, sticky=tk.E)
            fra.grid(row=prow, column=1, sticky=tk.W)
            prow += 1

        # new
        self.newlabel = tk.Label(self, text='NEW:')
        self.new = tktool.validateentry.Int(self)
        self.new.config(width=10)
        self.newlabel.grid(row=prow, column=0, sticky=tk.E)
        self.new.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        self.clear()

    def _select_beam_method(self):
        """command when miller is changed"""
        if self.miller.get():
            self.beam.config(state=tk.NORMAL)
            self.tha.config(state=tk.DISABLED)
            self.phi.config(state=tk.DISABLED)
        else:
            self.beam.config(state=tk.DISABLED)
            self.tha.config(state=tk.NORMAL)
            self.phi.config(state=tk.NORMAL)

    def _miller_action(self, value):
        self._select_beam_method()

    def set(self, d):
        ranx = d.get('ranx', defaultparam.proj_elem_default['ranx'])
        for w, v in zip(self.ranxs, ranx):
            w.set(v)
        self.maxrun.set(
                d.get('maxrun',
                    defaultparam.proj_elem_default['maxrun']))
        self.prim.set(
                d.get('prim',
                    defaultparam.proj_elem_default['prim']))
        self.new.set(
                d.get('new',
                    defaultparam.proj_elem_default['new']))
        self.ekip.set(
                d.get('ekip',
                    defaultparam.proj_elem_default['ekip']))
        self.leap.set(
                d.get('leap',
                    defaultparam.proj_elem_default['leap']))
        self.trmp.set(
                d.get('trmp',
                    defaultparam.proj_elem_default['trmp']))
        self.raip.set(
                d.get('raip',
                    defaultparam.proj_elem_default['raip']))
        self.laip.set(
                d.get('laip',
                    defaultparam.proj_elem_default['laip']))
        self.refip.set(
                d.get('refip',
                    defaultparam.proj_elem_default['refip']))
        self.lrip.set(
                d.get('lrip',
                    defaultparam.proj_elem_default['lrip']))
        self.miller.set(
                d.get('miller',
                    defaultparam.proj_elem_default['miller']))
        self.beam.set(
                d.get('beam',
                    defaultparam.proj_elem_default['beam']))
        self.tha.set(
                d.get('tha',
                    defaultparam.proj_elem_default['tha']))
        self.phi.set(
                d.get('phi',
                    defaultparam.proj_elem_default['phi']))
        self.dvrg.set(
                d.get('dvrg',
                    defaultparam.proj_elem_default['dvrg']))

        self._select_beam_method()

    def get(self):
        d = {}
        d['ranx'] = [w.get() for w in self.ranxs]
        d['maxrun'] = self.maxrun.get()
        d['prim'] = self.prim.get()
        d['new'] = self.new.get()
        d['ekip'] = self.ekip.get()
        d['leap'] = self.leap.get()
        d['trmp'] = self.trmp.get()
        d['raip'] = self.raip.get()
        d['laip'] = self.laip.get()
        d['refip'] = self.refip.get()
        d['lrip'] = self.lrip.get()
        d['miller'] = self.miller.get()
        d['beam'] = self.beam.get_nostatechk()
        d['tha'] = self.tha.get_nostatechk()
        d['phi'] = self.phi.get_nostatechk()
        d['dvrg'] = self.dvrg.get()
        return d

    def clear(self):
        self.set(defaultparam.proj_elem_default)

    def validate(self):
        err = []

        for i, w in enumerate(self.ranxs):
            e = w.validate()
            if e:
                err.append(('RANX{0:d}'.format(i+1), e))
        e = self.maxrun.validate()
        if e:
            err.append(('MAXRUN', e))
        e = self.new.validate()
        if e:
            err.append(('NEW', e))
        e = self.ekip.validate()
        if e:
            err.append(('EKIP', e))

        e = self.raip.validate()
        if e:
            err.append(('RAIP', e))
            
        e = self.laip.validate()
        if e:
            err.append(('LAIP', e))

        e = self.refip.validate()
        if e:
            err.append(('REFIP', e))

        e = self.lrip.validate()
        if e:
            err.append(('LRIP', e))

        if self.miller.get():
            e = self.beam.validate()
            if e:
                err.append(('BEAM', e))
        else:
            e = self.tha.validate()
            if e:
                err.append(('THA', e))

            e = self.phi.validate()
            if e:
                err.append(('PHI', e))

        e = self.dvrg.validate()
        if e:
            err.append(('DVRG', e))

        return err if err else None

    def enable(self):
        for w in self.ranxs:
            w.config(state=tk.NORMAL)
        self.maxrun.config(state=tk.NORMAL)
        self.prim.config(state=tk.NORMAL)
        self.new.config(state=tk.NORMAL)
        self.ekip.config(state=tk.NORMAL)
        self.leap.config(state=tk.NORMAL)
        self.trmp.config(state=tk.NORMAL)
        self.raip.config(state=tk.NORMAL)
        self.laip.config(state=tk.NORMAL)
        self.refip.config(state=tk.NORMAL)
        self.lrip.config(state=tk.NORMAL)
        self.miller.config(state=tk.NORMAL)
        self._select_beam_method()
        # self.beam.config(state=tk.NORMAL)
        # self.tha.config(state=tk.NORMAL)
        # self.phi.config(state=tk.NORMAL)
        self.dvrg.config(state=tk.NORMAL)

    def disable(self):
        for w in self.ranxs:
            w.config(state=tk.DISABLED)
        self.maxrun.config(state=tk.DISABLED)
        self.prim.config(state=tk.DISABLED)
        self.new.config(state=tk.DISABLED)
        self.ekip.config(state=tk.DISABLED)
        self.leap.config(state=tk.DISABLED)
        self.trmp.config(state=tk.DISABLED)
        self.raip.config(state=tk.DISABLED)
        self.laip.config(state=tk.DISABLED)
        self.refip.config(state=tk.DISABLED)
        self.lrip.config(state=tk.DISABLED)
        self.miller.config(state=tk.DISABLED)
        self.beam.config(state=tk.DISABLED)
        self.tha.config(state=tk.DISABLED)
        self.phi.config(state=tk.DISABLED)
        self.dvrg.config(state=tk.DISABLED)
