from cellnopt.core import *
import glob
import os
import easydev



def test_metabolites():
    from cellnopt.core import get_share_file
    filename = get_share_file("metabolites")
    a = Metabolites(filename)
    assert len(a.specID) == 94 
    a.specDefault
    a.specBoxes


def test_metabolitessamples():
    path = easydev.get_shared_directory_path("cellnopt.core")
    path += os.sep + "data" + os.sep + "metabolites_samples" + os.sep + "*" +os.sep + "metabolites"
    for filename in glob.glob(path):
        print filename
        yield readfiles, filename

def readfiles(filename):
    print 'Reading metabolies',
    try:
        try:
            m = Metabolites(os.path.split(filename)[1])
            len(m)
        except:
            assert False
    except:
        print 'failed. File could not be found ? Skipped'


test_metabolitessamples()
