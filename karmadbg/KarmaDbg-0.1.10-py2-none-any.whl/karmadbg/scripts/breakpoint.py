import pykd

def getBreakpoints():
    bpNumber = pykd.getNumberBreakpoints()
    bpList = []
    for bpIndex in xrange(bpNumber):
        bp = pykd.getBp(bpIndex)
    return bpList 
