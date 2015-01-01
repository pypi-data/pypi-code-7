from pyteomics import mzid
with mzid.read("/home/lev/Downloads/swedcad_100.mzid", retrieve_refs=True, iterative=False) as f:
    for _ in f:
        pass
