import sys
import time

import numpy as np

from . import pytwalk

from .formatnum import format_uncertainty
from .fitproblem import FitProblem, MultiFitProblem


def preview(models=[], weights=None):
    """Preview the models in preparation for fitting"""
    problem = _make_problem(models=models, weights=weights)
    result = Result(problem, problem.getp())
    result.show()
    return result


#"mesh","meshsteps",
#    --mesh=var OR var+var
#        plot chisq line or plane
#    --meshsteps=n
#        number of steps in the mesh
# For mesh plots, var can be a fitting parameter with optional
# range specifier, such as:
#
#   P[0].range(3,6)
#
# or the complete path to a model parameter:
#
#   M[0].sample[1].material.rho.pm(1)

def mesh(problem, vars=None, n=40):
    x, y = [np.linspace(low, high, n)
            for low, high in problem.bounds().T]
    p1, p2 = vars

    def fn(xi, yi):
        p1.value, p2.value = xi, yi
        problem.model_update()
        # print problem.summarize()
        return problem.chisq()
    z = [[fn(xi, yi) for xi in x] for yi in y]
    return x, y, np.asarray(z)


def mesh_models(models=[], weights=None, vars=None, n=40):
    problem = _make_problem(models=models, weights=weights)
    mesh(problem, vars, n)


def fit(models=[], weights=None, fitter=None, **kw):
    """
    Perform a fit
    """
    problem = _make_problem(models=models, weights=weights)
    if fitter is not None:
        t0 = time.clock()
        opt = fitter(problem)
        x = opt.solve(**kw)
        print("time %g" % (time.clock() - t0))
    else:
        x = problem.getp()
    result = Result(problem, x)
    result.show()

    return result


def show_chisq(chisq, fid=None):
    """
    Show chisq statistics on a drawing from the likelihood function.

    dof is the number of degrees of freedom, required for showing the
    normalized chisq.
    """
    if fid is None:
        fid = sys.stdout
    v, dv = np.mean(chisq), np.std(chisq, ddof=1)
    lo, hi = min(chisq), max(chisq)

    valstr = format_uncertainty(v, dv)
    fid.write(
        "Chisq for samples: %s,  [min,max] = [%g,%g]\n" % (valstr, lo, hi))


def show_stats(pars, points, fid=None):
    """
    Print a stylized list of parameter names and values with range bars.

    Report mean +/- std of the samples as the parameter values.
    """
    if fid is None:
        fid = sys.stdout

    val, err = np.mean(points, axis=0), np.std(points, axis=0, ddof=1)
    data = [(p.name, p.bounds, v, dv) for p, v, dv in zip(pars, val, err)]
    for name, bounds, v, dv in sorted(data, cmp=lambda x, y: cmp(x[0], y[0])):
        position = int(bounds.get01(v) * 9.999999999)
        bar = ['.'] * 10
        if position < 0:
            bar[0] = '<'
        elif position > 9:
            bar[9] = '>'
        else:
            bar[position] = '|'
        bar = "".join(bar)
        valstr = format_uncertainty(v, dv)
        fid.write("%40s %s %-15s in %s\n" % (name, bar, valstr, bounds))


def show_correlations(pars, points, fid=None):
    """
    List correlations between parameters in descending order.
    """
    R = np.corrcoef(points.T)
    corr = [(i, j, R[i, j])
            for i in range(len(pars))
            for j in range(i + 1, len(pars))]
    # Trim those which are not significant
    corr = [(i, j, r) for i, j, r in corr if abs(r) > 0.2]
    corr = list(sorted(corr, cmp=lambda x, y: cmp(abs(y[2]), abs(x[2]))))

    # Print the remaining correlations
    if len(corr) > 0:
        fid.write("== Parameter correlations ==\n")
        for i, j, r in corr:
            fid.write("%s X %s: %g\n" % (pars[i].name, pars[j].name, r))


class TWalk:

    def __init__(self, problem):
        self.twalk = pytwalk.pytwalk(n=len(problem.getp()),
                                     U=problem.nllf,
                                     Supp=problem.valid)

    def run(self, N, x0, x1):
        self.twalk.Run(T=N, x0=x0, xp0=x1)
        return np.roll(self.twalk.Output, 1, axis=1)


class Result:

    def __init__(self, problem, solution):
        nllf = problem.nllf(solution)  # TODO: Shouldn't have to recalculate!
        self.problem = problem
        self.solution = np.array(solution)
        self.points = np.array([np.hstack((nllf, solution))], 'd')

    def mcmc(self, samples=1e5, burnin=None, walker=TWalk):
        """
        Markov Chain Monte Carlo resampler.
        """
        if burnin is None:
            burnin = int(samples / 10)
        if burnin >= samples:
            raise ValueError("burnin must be smaller than samples")

        opt = walker(self.problem)
        x0 = np.array(self.solution)
        self.problem.randomize()
        x1 = self.problem.getp()
        points = opt.run(N=samples, x0=x0, x1=x1)
        self.points = np.vstack((self.points, points[burnin:]))
        self.problem.setp(self.solution)

    def resample(self, samples=100, restart=False, fitter=None, **kw):
        """
        Refit the result multiple times with resynthesized data, building
        up an array in Result.samples which contains the best fit to the
        resynthesized data.  *samples* is the number of samples to generate.
        *fitter* is the (local) optimizer to use. The kw are the parameters
        for the optimizer.
        """
        opt = fitter(self.problem)
        points = []
        try:  # TODO: some solvers already catch KeyboardInterrupt
            for i in range(samples):
                print("== resynth %d of %d" % (i, samples))
                self.problem.resynth_data()
                if restart:
                    self.problem.randomize()
                else:
                    self.problem.setp(self.solution)
                x = opt.solve(**kw)
                nllf = self.problem.nllf(x)  # TODO: don't recalculate!
                points.append(np.hstack((nllf, x)))
                print(self.problem.summarize())
                print("[chisq=%g]" % (nllf * 2 / self.problem.dof))
        except KeyboardInterrupt:
            pass
        self.points = np.vstack([self.points] + points)

        # Restore the original solution
        self.problem.restore_data()
        self.problem.setp(self.solution)

    def show_stats(self):
        if self.points.shape[0] > 1:
            self.problem.setp(self.solution)
            show_chisq(self.points[:, 0] * 2 / self.problem.dof)
            show_stats(self.problem.parameters, self.points[:, 1:])
            show_correlations(self.problem.parameters, self.points[:, 1:])

    def save(self, basename):
        """
        Save the parameter table and the fitted model.
        """
        # TODO: need to do problem.setp(solution) in case the problem has
        # changed since result was created (e.g., when comparing multiple
        # fits). Same in showmodel()
        self.problem.setp(self.solution)
        fid = open(basename + ".par", "w")
        fid.write(self.problem.summarize() + "\n")
        fid.close()
        self.problem.save(basename)
        if self.points.shape[0] > 1:
            fid = open(basename + ".mc", "w")
            parhead = "\t".join(p.name for p in self.problem.parameters)
            fid.write("# nllf\t%s\n" % parhead)
            np.savetxt(fid, self.points, delimiter="\t")
            fid.close()
        return self

    def show(self):
        """
        Show the model parameters and plots
        """
        self.showmodel()
        self.showpars()
        return self

    def plot(self):
        self.problem.plot()
        return self

    def showmodel(self):
        print("== Model parameters ==")
        self.problem.setp(self.solution)
        self.problem.show()

    def showpars(self):
        print("== Fitted parameters ==")
        self.problem.setp(self.solution)
        print(self.problem.summarize())


def _make_problem(models=[], weights=None):
    if isinstance(models, (tuple, list)):
        if len(models) > 1:
            problem = MultiFitProblem(models, weights=weights)
        else:
            problem = FitProblem(models[0])
    else:
        problem = FitProblem(models)
    return problem
