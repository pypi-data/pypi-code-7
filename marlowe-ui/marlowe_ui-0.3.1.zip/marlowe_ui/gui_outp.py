import tkinter as tk

from . import tktool
from .tktool import validateentry
from .tktool import codedoptionmenu
from .tktool import gui_abstract

from . import defaultparam

from . import gui_size_body

class OutpInform(tk.Frame):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)

        self.checkvars = []
        self.checks = []
        self.mesgs = [
            '1 Primary recoil ranges and summaries of the initial and primary states of the primaries.',
            '2 Distributions of collision-event types.',
            '3 Statistical analyses of sets of cascades. Requires MAXRUN > 1.',
            '4 Distributions of the times of events and of particle energies.',
            '5 Analysis of replacement sequences and channeled trajectory segments.',
            '6 The distant interstitial - vacancy pair distribution.',
            '7 The analysis procedure SINGLE. See Input Record 13.',
            '8 The analysis procedure EXTRA. See Input Record 14.']

        prow = 0
        for t in self.mesgs:
            v = tk.IntVar(self)
            c = tk.Checkbutton(self,
                    text = t,
                    wraplength=250,
                    variable=v, anchor='w', justify='left')
            c.grid(row=prow, column=0, sticky=tk.E+tk.W)
            prow += 1
            self.checkvars.append(v)
            self.checks.append(c)

        self.enabled = True

    def set(self, d):
        for var, v in zip(self.checkvars, d):
            # True is set as 1, False is 0
            var.set(v)

    def get(self):
        return [var.get()==1 for var in self.checkvars]

    def get_nostatechk(self):
        return self.get()

    def clear(self):
        self.set(defaultparam.outp_inform_default)

    def validate(self):
        return None

    def enable(self):
        for w in self.checks:
            w.config(state=tk.NORMAL)
        self.enabled = True

    def disable(self):
        for w in self.checks:
            w.config(state=tk.DISABLED)
        self.enabled = False

    def is_disabled(self):
        return not self.enabled


class Outp(tk.Frame, tktool.gui_abstract.GUIAbstract):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)
        tktool.gui_abstract.GUIAbstract.__init__(self,
                defaultparam=defaultparam.outp_default)

        prow = 0

        # DRNG
        self.drnglabel = tk.Label(self, text='DRNG')
        self.drng = tktool.validateentry.Vec3d(self)
        self.add_widget('drng', self.drng)
        self.drng.config(width=10)
        self.drnglabel.grid(row=prow, column=0, sticky=tk.E)
        self.drng.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # LCS
        self.lcslabel = tk.Label(self, text='LCS')
        self.lcs = tktool.validateentry.Vec2Int(self)
        self.add_widget('lcs', self.lcs)
        self.lcs.config(width=10)
        self.lcslabel.grid(row=prow, column=0, sticky=tk.E)
        self.lcs.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # TRACE
        self.tracelabel = tk.Label(self, text='TRACE')
        self.trace = tktool.validateentry.Vec3Int(self)
        self.add_widget('trace', self.trace)
        self.trace.config(width=10)
        self.tracelabel.grid(row=prow, column=0, sticky=tk.E)
        self.trace.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # LOOK
        self.looklabel = tk.Label(self, text='LOOK')
        self.lookoptions = [
                (0, '0 No description of individual cascades'),
                (1, '1 A summary of cascade properties, with no details ..'),
                (2, '2 Adds escaping atoms, truncated trajetories, ...'),
                (3, '3 Adds vacant sites and interstitials.'),
                (4, '4 Adds complete description of displacement cascade')]
        self.look = tktool.codedoptionmenu.CodedOptionMenu(self,
                self.lookoptions)
        self.add_widget('look', self.look)
        self.look.config(width=15, anchor='w')
        self.looklabel.grid(row=prow, column=0, sticky=tk.E)
        self.look.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # GREX
        self.grexlabel = tk.Label(self, text='GREX')
        self.grexoptions = [
                (False, 'False'),
                (True, 'True')]
        self.grex = tktool.codedoptionmenu.CodedOptionMenu(self,
                self.grexoptions)
        self.add_widget('grex', self.grex)
        self.grexlabel.grid(row=prow, column=0, sticky=tk.E)
        self.grex.grid(row=prow, column=1, sticky=tk.W)
        prow += 1

        # INFORM
        self.informfrm = tk.LabelFrame(self, text='INFORM')
        self.inform = OutpInform(self.informfrm)
        self.add_widget('inform', self.inform)
        self.inform.pack()

        self.informfrm.grid(row=prow, column=0, columnspan=2,
                sticky=tk.EW)

        self.clear()
