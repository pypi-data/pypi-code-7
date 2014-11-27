"""This test file cover the cno.midas module"""
from os.path import join as pj
import os.path

from cellnopt.core import XMIDAS, MIDASReader, get_share_file, cnodata
from cellnopt.core.midas import *
import numpy

from easydev.easytest import assert_list_almost_equal, TempFile

filenames = ['MD-ToyMMB_bis.csv',
             'MD-LiverDREAM.csv']


def test_all_file():
    # this is a nosetests trick to have one test per file reportig in the output
    # and not just one for all files. This way, we now how many files are tested
    for filename in filenames:
        yield readfiles, filename

   
class TestMidas(object):
    def __init__(self):

        self.m = MIDASReader() # try empty file
        self.m = MIDASReader(cnodata('MD-ToyMMB_bis.csv'))

        assert self.m.nrows == 18
        assert self.m.ncols == 18
        assert self.m.TRcol == range(0,4)
        assert self.m.DAcol == range(4,11)
        assert self.m.DVcol == range(11,18)
        #assert self.m.PJcol == []
        #assert self.m.indices['CellLines'] == [0]
        
        assert self.m.names == [
                           'TR:EGF',
                           'TR:TNFa',
                           'TR:Rafi',
                           'TR:PI3Ki',
                           'DA:Akt',
                           'DA:Hsp27',
                           'DA:NFkB',
                           'DA:Erk',
                           'DA:p90RSK',
                           'DA:Jnk',
                           'DA:cJun',
                           'DV:Akt',
                           'DV:Hsp27',
                           'DV:NFkB',
                           'DV:Erk',
                           'DV:p90RSK',
                           'DV:Jnk',
                           'DV:cJun']

        self.m.nInhibitors
        self.m.nStimuli
        self.m.nCues
        self.m.ntimes
        self.m.namesCues

    def test_getitem(self):
        assert self.m['DV:Akt'].all() == numpy.array([ 0. ,  0.7,  0.7,  0. ,
                 0.7,  0.7,  0. ,  0.7,  0.7,  0. ,  0. , 0. ,  0. ,  0. ,
                 0. ,  0. ,  0. ,  0. ]).all()
        try:
            self.m['dummy']
            assert False
        except:
            assert True
    def _test_delitem(self):
        assert self.m.ncols == 18
        self.m.delitem('DV:Akt')
        self.remove("DA:Akt")
        assert self.m.ncols == 17
        
        try:
            self.m.delitem('dummy')
            assert False
        except:
            assert True

    def test_plots(self):
        self.m.plotMSEs()
        self.m.plotExp()
        self.m.plotSim()
    
    def test_print(self):
        print self.m
        

def test_export():
    #m = MIDASReader(get_share_file("MD-Test.csv"))
    #c = m.export2CNOGraph()
    m = XMIDAS(get_share_file("MD-Test.csv"))
    f = TempFile()
    m.save2midas(f.name)
    m = XMIDAS(f.name)
    f.delete()

def test_celllines():
    c = MIDASReader(get_share_file("MD-MultipleCellLines.csv"), celltype="C1")        



def test_multi_cellline():
    c = XMIDAS(get_share_file("MD-MultipleCellLines.csv"), cellLine="C1")



def readfiles(filename):
    m = MIDASReader(cnodata(filename))


def _test_compare_pycno_vs_cnor():
    # test all sif files 
    for f in filenames:
        yield compare_pycno_vs_cnor, f
    
    
def compare_pycno_vs_cnor(filename):
    """check that the sif file read by CNOR and pyCNO are identical"""
    filename = cnodata(filename)
    try:
        from cellnopt.wrapper import rpack_CNOR as cnor
        from cellnopt.core import midas
 
        mr = cnor.readMIDAS(filename)
        m = midas.MIDASReader(filename)

        assert sorted(list(mr.rx2('DAcol'))) == sorted([x+1 for x in list(m.DAcol)])
        assert sorted(list(mr.rx2('DVcol'))) == sorted([x+1 for x in list(m.DVcol)])
        assert sorted(list(mr.rx2('TRcol'))) == sorted([x+1 for x in list(m.TRcol)])
    except:
        pass

    # TODO(tc): seems that we need to transpose one matrix. do not seem neat
    #assert numpy.array(m.dataMatrix).all() == numpy.array(mr.dataMatrix).transpose().all()









def test_xmidas():
    m = XMIDAS(cnodata("MD-ToyPB.csv"))
    m.df
    assert len(m.names_cues)==4

    assert len(m.experiments) == 10

    assert len(m.names_stimuli)==2
    assert len(m.stimuli)==10

    assert len(m.inhibitors) == 10
    assert len(m.names_inhibitors) == 2

    m.cellLine
    assert len(m.cellLines) == 1
    assert len(m.times ) == 16

    try:
        m.cellLine = "wrong"
        assert False
    except:
        assert True


    # ----------------------------------------- remove methods
    try:
        m.remove_species("dummy")
        assert False
    except:
        assert True
    m.remove_species("erk")
    assert len(m.species) == 5
    m.remove_times(18)
    m.remove_times([12,14])
    m.remove_experiments("experiment_0")
    m.remove_stimuli("p38")
    m.remove_inhibitors("pi3k:i")

    mm = m.copy()
    mm.remove_cellLine("Cell")
    del mm

    # ------------------------------------------- rename methods
    m.rename_cellLine({"Cell": "HT29"})
    m.rename_species({"ap1":'AP1'})
    m.rename_inhibitors({'raf1:i':'RAF1'})
    m.rename_stimuli({'egf':'EGF'})

    # others
    print(m)
    m.get_residual_errors()

    #fails
    #m.rename_time({0:0,2:2*60,4:4*60}) 

def test_xmidas_average():
    m = XMIDAS(get_share_file("MD-average.csv"))
    m.average_replicates()
    m.average_replicates(inplace=True)



def test_xmidas_plot():

    m = XMIDAS(cnodata("MD-ToyPB.csv"))
    m.create_random_simulation()
    m.plot(mode="trend",vmax=.9)
    m.plot(mode="mse")
    m.xplot()


    m = XMIDAS(get_share_file("MD-unnorm.csv"))
    m.plot(mode="mse", logx=True)
    m.df -= 2
    m.plot(mode="mse")

def test_boxplot():
    m = XMIDAS(cnodata("MD-ToyPB.csv"))
    m.boxplot(mode="time")
    m.boxplot(mode="experiment")

def test_radviz():
    m = XMIDAS(cnodata("MD-ToyPB.csv"))
    m.radviz()

def test_dicretise():
    m = XMIDAS(cnodata("MD-ToyPB.csv"))
    m.discretise(inplace=False)
    m.discretize(inplace=False)
    m.discretise(N=3)


def test_heatmap():
    m = XMIDAS(cnodata("MD-ToyPB.csv"))
    m.heatmap()

def test_hcluster():
    m = XMIDAS(cnodata("MD-ToyPB.csv"))
    m.hcluster()
    

def test_xmidas_corr():
    m = XMIDAS(cnodata("MD-ToyPB.csv"))
    m.corr()


def test_norm_time():
    m = XMIDAS(get_share_file("MD-unnorm.csv"))
    m.normalise(mode="time")

def test_norm_control():
    m = XMIDAS(get_share_file("MD-unnorm_exp.csv"))
    m.normalise(mode="control")

def test_xmidas_add_noise():
    m = XMIDAS(cnodata("MD-ToyPB.csv"))
    m.add_uniform_distributed_noise(mode="bounded")
    m.add_uniform_distributed_noise(mode="free")
    m.add_uniform_distributed_noise(inplace=True)
    m.add_gaussian_noise()
    m.add_gaussian_noise(inplace=True)


def test_experiment():
    e = Experiment("AKT", 0, {'TGFa':1}, {'AKT':1}, 10.1)
    e.units = "second"
    try:
        e.units = "dummy"
        assert False
    except:
        assert True
    e.cellLine = "TEST"
    e.protein_name = "zap70"

    e.stimuli = {"TGFa":0}
    assert e.stimuli == {"TGFa":0}

    e.get_cues()
    e.cues_as_dict()

    print(e)



def test_midasbuilder():
    m = MIDASBuilder()
    e1 = Experiment("AKT", 0, {"EGFR":1}, {"AKT":0}, 0.1)
    e2 = Experiment("AKT", 5, {"EGFR":1}, {"AKT":0}, 0.5)
    e3 = Experiment("AKT", 10, {"EGFR":1}, {"AKT":0}, 0.9)
    e4 = Experiment("AKT", 0, {"EGFR":0}, {"AKT":0}, 0.1)
    e5 = Experiment("AKT", 5, {"EGFR":0}, {"AKT":0}, 0.1)
    e6 = Experiment("AKT", 10, {"EGFR":0}, {"AKT":0}, 0.1)
    for e in [e1,e2,e3,e4,e5,e6]:
        m.add_experiment(e)
    m.export2midas("test.csv")
    




def test_experimentS():

     es = Experiments()
     e1 = Experiment("AKT", 0, {"EGFR":1}, {"AKT":0}, 0.1)
     e2 = Experiment("AKT", 5, {"EGFR":1}, {"AKT":0}, 0.5)
     es.add_single_experiments([e1,e2])
     assert len(es)==2



def test_shuffle():

    m = XMIDAS(cnodata("MD-ToyPB.csv"))

    # shuffling over signals should keep the sum over signal constan
    a1 = m.df.sum(axis=0)
    m.shuffle(mode="signals")
    a2 = m.df.sum(axis=0)
    assert_list_almost_equal(a1, a2)
    m.reset()

    # shuffling over index keep sum over a given experiment constant
    a1 = m.df.sum(level="experiment").sum(axis=1)
    m.shuffle(mode="indices")
    a2 = m.df.sum(level="experiment").sum(axis=1)
    assert_list_almost_equal(a1, a2)

    m.shuffle(mode="timeseries")

    m.reset()
    a1 = m.df.sum().sum()
    m.shuffle(mode="all")
    a2 = m.df.sum().sum()
    assert_list_almost_equal([a1], [a2])


def test_scale():
    m = XMIDAS(cnodata("MD-ToyPB.csv"))
    m.scale_max()
    m.scale_min_max()
    m.scale_max_by_experiments()
    m.scale_min_max_by_experiments()
    m.scale_max_across_experiments()
    m.scale_min_max_across_experiments()


    m.scale_max(inplace=False)
    m.scale_min_max(inplace=False)
    m.scale_max_by_experiments(inplace=False)
    m.scale_min_max_by_experiments(inplace=False)
    m.scale_max_across_experiments(inplace=False)
    m.scale_min_max_across_experiments(inplace=False)











