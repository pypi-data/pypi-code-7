


def plotDifference(c1,c2):
    c = c1.copy()






"""

    def compute_data(self):
        #signals = [str(x) for x in self.namesSignals]
        #nSignals = len(signals)
        #nexps = self.nCues
        timeSignals = self.times

        exp = []
        #nexps, nSignals = self.data[0].shape

        for i in range(0, self.nExps):
            for j in range(0, self.nSignals):
                exptemp = [numpy.array(self.cnolist.signals[x])[i,j] for x in range(0, len(timeSignals))]
                exp.append(exptemp)
        exp = numpy.array([exp]).reshape(self.nExps, self.nSignals,len(timeSignals))
        return exp


    def add_sim(self, sim):
        assert sim.shape[0] == self.nExps
        assert sim.shape[1] == self.nSignals
        assert sim.shape[2] == self.nTimes
        self.sim.append(sim.copy())


    def _plotMeanCurve(self, markersize=3, logx=False):
        if logx == False:
            times = self.times/max(self.times)
            xt = linspace(0, self.nSignals, self.nSignals*2+1)
            xtlabels = [0,30,0,30,0,30,0,30,0,30,0,30,0,30,60]
        else:
            times = log10(1+self.times)/max(log10(1+self.times))
            m = min(self.times)
            M = float(max(self.times))
            mid = m + (M-m)/2.
            xtlin = linspace(0, self.nSignals, self.nSignals*2+1)
            xt = [int(x)+log10(1+mod(x,1)*M)/log10(1+M) for i,x in enumerate(xtlin)]
            xtlabels = [0,30,0,30,0,30,0,30,0,30,0,30,0,30,60]
        meansim = numpy.mean(numpy.array(self.sim), axis=0)
        stdsim = numpy.std(numpy.array(self.sim), axis=0)
        for i in range(0, self.nExps):
            for j in range(0, self.nSignals):
                # divide data by 1.1 to see results close to 1.
                if logx:
                    errorbar(times+j, meansim[i,j]/1.05+(self.nExps-i-1), yerr=stdsim[i,j], marker='o', ms=markersize, fmt='--', ecolor='b', color='b')
                else:
                    errorbar(times+j, meansim[i,j]/1.05+(self.nExps-i-1), yerr=stdsim[i,j], marker='o', ms=markersize, fmt='--', ecolor='b', color='b')
                if logx:
                    plot(times+j, self.exp[i,j]/1.05+(self.nExps-i-1), 'k-o', markersize=markersize)
                else:
                    plot(times+j, self.exp[i,j]/1.05+(self.nExps-i-1), 'k-o', markersize=markersize)
        gca().set_xticklabels(xtlabels)
        gca().set_xticks(xt)

    def plot(self, filename=None, cmap="heat", logx=False, N=20, margin=0.05):
        clf()
        self._cutAndPlot(cmap=cmap, N=N, margin=margin)
        self._plotCurves(logx=logx)
        axis([0,self.nSignals, 0, self.nExps])
        if filename:
            savefig(filename)

    def plotMean(self, filename=None, cmap="heat", logx=False, N=20, margin=0.05):
        clf()
        self._cutAndPlot(cmap=cmap,N=N, margin=margin)
        self._plotMeanCurve(logx=logx)
        axis([0,self.nSignals, 0, self.nExps])
        if filename:
            savefig(filename)

"""





