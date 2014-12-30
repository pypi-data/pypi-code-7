from pyQCDH.BedBimFam import BedBimFam, Bed
import os
import pandas
import numpy as np

# os.chdir("/Users/kaiyin/Desktop/mmp/")
# trio = BedBimFam("/Users/kaiyin/Desktop/mmp/mmp13")
# data = trio.fam.read(usecols=["IID", "FID"])
# print(data.head())
# data = trio.fam.read()
# print(data.head())
# data = trio.bim.read()
# print(data.head())
# data = trio.bim.read(usecols=["SNP", "CHR", "GDIST"])
# print(data.head())
# trio.bim.count_lines()
# trio.fam.count_lines()
# trio.n_snps
# trio.n_individuals

os.chdir("/Users/kaiyin/Desktop/testbed")
trio = BedBimFam("test")

###################################
## test reading bim files
###################################
# trio.bim.count_lines()
# x = trio.bim.read(usecols="all")
# x = trio.bim.read(usecols=["SNP"])
# print(x.head())

###################################
## test reading fam files
###################################
# x = trio.fam.read(usecols=["FID", "IID", "PID"])

##################################
# test reading bed files
##################################
x = trio.bed.read_all()
print(x)
x = trio.bed.read_cols([0, 1, 2])
print(x)
x = trio.bed.read_snps(["snp1", "snp2"])
print(x)
x.corr(x)
x.corr()

# ###################################
# ## test join data frames
# ###################################
# df1 = pandas.DataFrame(np.random.randn(10, 2))
# df1
# df2 = pandas.DataFrame(np.random.randn(10, 4))
# df2
# df = pandas.concat([df1, df2], axis=1)
# df



