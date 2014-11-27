from cellnopt.core.sop2sif import SOP2SIF
import easydev



filename = easydev.get_share_file("cellnopt.core", "data", "data.sop") 

import tempfile

def test_sop2sif():
    s2s = SOP2SIF(filename)
    f = tempfile.NamedTemporaryFile()
    s2s.export2sif(filename=f.name, include_and_gates=False)
    f = tempfile.NamedTemporaryFile()
    s2s.export2sif(filename=f.name, include_and_gates=True)

    print len(s2s.specID)
    #assert len(s2s.reacID) == 173
    assert len(s2s.reacID) == 348
    
    assert len([x for x in s2s.specID if x.startswith("and")==False])



