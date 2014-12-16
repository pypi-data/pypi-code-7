import copy
import tkinter as tk

from . import tktool
from .tktool import validateentry
from .tktool import codedoptionmenu

from . import gui_filepath

from . import defaultparam

class Modl(tk.Frame):
    def __init__(self, master=None, *args, **kw):
        tk.Frame.__init__(self, master)
        
        # FILE
        self.files = [tk.StringVar(self) for i in range(5)]
        self.fileframe = tk.LabelFrame(self, text='FILE')
        filelabels = ['1', '2', '3', '4', '5']
        for i in range(5):
            frame = tk.Frame(self.fileframe)
            label =  tk.Label(frame, text=filelabels[i])
            filewidget = gui_filepath.Saveas(frame, textvariable=self.files[i])
            label.pack(side=tk.LEFT)
            filewidget.pack(side=tk.LEFT, expand=True, fill=tk.X)

            frame.pack(side=tk.TOP, expand=True, fill=tk.X)
        self.fileframe.pack(expand=True, fill=tk.X)

        # RDNML
        # It might be better to show at each correpond record

        # METRIC (1=AA, 2=nm)
        self.metricframe = tk.Frame(self)
        self.metriclabel = tk.Label(self.metricframe, text='METRIC')
        self.metricoptions = [(1,'1:Ang.'), (2,'2:nm')]
        self.metricwidget = tktool.codedoptionmenu.CodedOptionMenu(self.metricframe, 
                self.metricoptions)

        self.metriclabel.pack(side=tk.LEFT)
        self.metricwidget.pack(side=tk.LEFT)

        self.metricframe.pack(side=tk.TOP, anchor=tk.NW)

        # TRAM
        self.tramframe = tk.Frame(self)
        self.tramlabel = tk.Label(self.tramframe, text='TRAM')
        self.tramoptions = [(False,'False'), (True,'True')]
        self.tramwidget = tktool.codedoptionmenu.CodedOptionMenu(self.tramframe, self.tramoptions)

        self.tramlabel.pack(side=tk.LEFT)
        self.tramwidget.pack(side=tk.LEFT)

        self.tramframe.pack(side=tk.TOP, anchor=tk.NW)

        # surface
        # moved to gui_surf.py

        # KLAY
        # this value is automatically decided by the number of layers
        # described in &XTAL record

        # NM
        self.nmvar = tk.IntVar(self, 4)  
        self.nmframe = tk.Frame(self)
        self.nmlabel = tk.Label(self.nmframe, text='NM')
        self.nmwidget = tktool.validateentry.IntPositive(self.nmframe,
                textvariable=self.nmvar, width=4)

        self.nmlabel.pack(side=tk.LEFT)
        self.nmwidget.pack(side=tk.LEFT)

        self.nmframe.pack(side=tk.TOP, anchor=tk.NW)

        # LORG (0~8)
        self.lorgframe = tk.Frame(self)
        self.lorglabel = tk.Label(self.lorgframe, text='LORG')
        self.lorgoptions = [
                (0, '0: '),
                (1, '1: '),
                (2, '2: '),
                (3, '3: '),
                (4, '4: '),
                (5, '5: '),
                (6, '6: '),
                (7, '7: '),
                (8, '8: '),] # 0,1,...,8
        self.lorgwidget = tktool.codedoptionmenu.CodedOptionMenu(self.lorgframe, self.lorgoptions)
        self.lorgwidget.config(width=20, anchor='w')

        self.lorglabel.pack(side=tk.LEFT)
        self.lorgwidget.pack(side=tk.LEFT)

        self.lorgframe.pack(side=tk.TOP, anchor=tk.NW)
        
        # ICHAN
        self.ichanframe = tk.LabelFrame(self, text='ICHAN')
        self.ichanlabels = ['1', '2', '3', '4']
        self.ichanvar = [tk.IntVar(self) for i in range(4)]
        self.ichanentries = []
        for i in range(4):
            frame = tk.Frame(self.ichanframe)
            label = tk.Label(frame, text=self.ichanlabels[i])
            entry = tktool.validateentry.Int(frame, textvariable=self.ichanvar[i])
            self.ichanentries.append(entry)
            label.pack(side=tk.LEFT)
            entry.pack(side=tk.LEFT)
            frame.pack(side=tk.TOP)
        self.ichanframe.pack(side=tk.TOP)
        
        # DELTA
        self.deltaframe = tk.LabelFrame(self, text='DELTA')
        self.deltalabels = ['1', '2', '3', '4']
        self.deltavar = [tk.DoubleVar(self) for i in range(4)]
        self.deltaentries = []
        for i in range(4):
            frame = tk.Frame(self.deltaframe)
            label = tk.Label(frame, text=self.deltalabels[i])
            entry = tktool.validateentry.Double(frame, textvariable=self.deltavar[i])
            self.deltaentries.append(entry)
            label.pack(side=tk.LEFT)
            entry.pack(side=tk.LEFT)
            frame.pack(side=tk.TOP)
        self.deltaframe.pack(side=tk.TOP)

        # TIM

    def set(self, v):
        if 'file' in v:
            for i, w in zip(v['file'], self.files):
                if i is not None:
                    w.set(i)
                else:
                    w.set('')

        # metric
        if 'metric' in v:
            self.metricwidget.set(v['metric'])

        # tram
        if 'tram' in v:
            self.tramwidget.set(v['tram'])

        # surfce
        # klay

        # nm
        if 'nm' in v:
            self.nmvar.set(v['nm'])

        # lorg
        if 'lorg' in v:
            self.lorgwidget.set(v['lorg'])

        # ichan
        if 'ichan' in v:
            for s, d in zip(v['ichan'], self.ichanvar):
                d.set(s)

        # delta
        if 'delta' in v:
            for s, d in zip(v['delta'], self.deltavar):
                d.set(s)

    def get_file(self):
        a = []
        for w in self.files:
            s = w.get()
            # we need some operation to identify null entry
            s = s.strip()
            if s:
                a.append(s)
            else:
                a.append(None)
        return a

    def get(self):
        # It should be considered, why not d = {} ?
        d = copy.deepcopy(defaultparam.modl_default)
        # file
        d['file'] = self.get_file()
        # metric
        d['metric'] = self.metricwidget.get()
        # tram
        d['tram'] = self.tramwidget.get()

        # surfce
        # klay

        # nm
        d['nm'] = self.nmvar.get()

        # lorg
        d['lorg'] = self.lorgwidget.get()

        # ichan
        d['ichan'] = [w.get() for w in self.ichanvar]

        # ichan
        d['delta'] = [w.get() for w in self.deltavar]

        return d

    def clear(self):
        self.set(defaultparam.modl_default)

    def validate(self):
        err = []
        for i, w in enumerate(self.ichanentries):
            e = w.validate()
            if e:
                err.append(('ICHAN({0:d})'.format(i+1), e))
        for i, w in enumerate(self.deltaentries):
            e = w.validate()
            if e:
                err.append(('DELTA({0:d})'.format(i+1), e))
        return err if err else None
