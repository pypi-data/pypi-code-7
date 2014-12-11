"""
Count motifs along sliding windows of UTRs from a GFF file.

This uses example data shipped with pybedtools.
"""

import pybedtools


def filtfunc(f):
    return f[2] == 'UTR'


def renamer(f):
    # BEDTools sees the featuretype of a GFF file as the "name" when using
    # makewindows, so we need to set the featuretype to be the ID.  Or whatever
    # GFF attribute is of interest.
    f[2] = f['ID']
    return f


# Prepare the UTRs file
utrs = pybedtools.example_bedtool('gdc.gff')\
    .filter(filtfunc).saveas()\
    .each(renamer).saveas()

# 20-bp windows, labeled by their name and an integer
windows = pybedtools.BedTool().window_maker(b=utrs, w=20, i='srcwinnum' )

# Count up the number of features in each window
motifs = pybedtools.example_bedtool('gdc.bed')

# Last column of this file will have the number of motifs hitting that window
results = windows.intersect(motifs, c=True)
