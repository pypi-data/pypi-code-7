"""
time python feature_alignment.py --method best_overall --in strep_align/Strep*Repl[12]_R02/split_hroest_K1208*_all_peakgroups.xls --fdr_cutoff 0.01 --max_rt_diff 60 --max_fdr_quality 0.2,0.3,0.01  --frac_selected 1.0 --target_fdr 0.01

time python feature_alignment.py --method best_cluster_score --in strep_align/Strep*Repl[12]_R02/split_hroest_K1208*_all_peakgroups.xls --fdr_cutoff 0.008 --max_rt_diff 30 --max_fdr_quality 0.15,0.32,0.01 --frac_selected 1.0 --target_fdr 0.01

"""


from feature_alignment import *
import numpy
from msproteomicstoolslib.math.chauvenet import chauvenet
from msproteomicstoolslib.format.SWATHScoringReader import *
infiles = [
'strep_align/Strep0_Repl1_R02/split_hroest_K120808_all_peakgroups_aligned.xls',
'strep_align/Strep0_Repl1_R03/split_hroest_K120808_all_peakgroups_aligned.xls',
'strep_align/Strep0_Repl2_R02/split_hroest_K120808_all_peakgroups_aligned.xls',
'strep_align/Strep0_Repl2_R03/split_hroest_K120808_all_peakgroups_aligned.xls'
] 
infiles = [
'strep_align/Strep0_Repl1_R02/split_hroest_K120808_all_peakgroups.xls',
'strep_align/Strep0_Repl2_R02/split_hroest_K120808_all_peakgroups.xls',
'strep_align/Strep10_Repl1_R02/split_hroest_K120808_all_peakgroups.xls',
'strep_align/Strep10_Repl2_R02/split_hroest_K120808_all_peakgroups.xls',
]


class Opt():pass

options = Opt()
options.rt_diff_cutoff = 30
options.fdr_cutoff = 0.01
options.aligned_fdr_cutoff = 0.15
options.method = "best_overall" # "best_cluster_score"

reader = SWATHScoringReader.newReader(infiles, "openswath")
this_exp.runs = reader.parse_files(False)

# Map the precursors across multiple runs, determine the number of
# precursors in all runs without alignment.
multipeptides = this_exp.get_all_multipeptides(options.fdr_cutoff)

# this_exp.rt_align_all_runs(multipeptides, alignment_fdr_threshold = 0.0001, use_scikit=False)
# alignment = this_exp.align_features(multipeptides, 30, 0.01, 0.2)


# for 4 runs
options.rt_diff_cutoff = 60
options.fdr_cutoff = 0.01
options.aligned_fdr_cutoff = 0.255
options.method = "best_overall" # "best_cluster_score"
multipeptides = this_exp.get_all_multipeptides(options.fdr_cutoff)
alignment = align_features(multipeptides, options.rt_diff_cutoff, options.fdr_cutoff, options.aligned_fdr_cutoff, options.method)
this_exp.print_stats(multipeptides, alignment, None, options.fdr_cutoff)

for m in multipeptides:
    for p in m.get_peptides():
        p.unselect_all()

# for 4 runs
options.rt_diff_cutoff = 30
options.fdr_cutoff = 0.005
options.aligned_fdr_cutoff = 0.31
options.method = "best_cluster_score"
multipeptides = this_exp.get_all_multipeptides(options.fdr_cutoff)
print "Nr multipeptides", len(multipeptides)
alignment = align_features(multipeptides, options.rt_diff_cutoff, options.fdr_cutoff, options.aligned_fdr_cutoff, options.method)
this_exp.print_stats(multipeptides, alignment, None, options.fdr_cutoff)


pseudo_align_features(multipeptides, options.rt_diff_cutoff, options.fdr_cutoff, options.aligned_fdr_cutoff, options.method)

