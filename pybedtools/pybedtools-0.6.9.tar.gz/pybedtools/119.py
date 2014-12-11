import pybedtools
x = pybedtools.example_bedtool('gdc.bam')
g = pybedtools.example_bedtool('gdc.gff')
y = x.coverage(g, d=True)
z = y.saveas()
