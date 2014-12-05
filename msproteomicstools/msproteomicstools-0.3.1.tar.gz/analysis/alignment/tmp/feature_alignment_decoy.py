#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
=========================================================================
        msproteomicstools -- Mass Spectrometry Proteomics Tools
=========================================================================

Copyright (c) 2013, ETH Zurich
For a full list of authors, refer to the file AUTHORS.

This software is released under a three-clause BSD license:
 * Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
 * Neither the name of any author or any participating institution
   may be used to endorse or promote products derived from this software
   without specific prior written permission.
--------------------------------------------------------------------------
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL ANY OF THE AUTHORS OR THE CONTRIBUTING
INSTITUTIONS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------
$Maintainer: Hannes Roest$
$Authors: Hannes Roest$
--------------------------------------------------------------------------
"""

from feature_alignment import *
import time

def handle_args():
    usage = "" #usage: %prog --in \"files1 file2 file3 ...\" [options]" 
    usage += "\nThis program will select all peakgroups below the FDR cutoff in all files and try to align them to each other."
    usage += "\nIf only one file is given, it will act as peakgroup selector (best by m_score)" + \
            "\nand will apply the provided FDR cutoff."

    parser = argparse.ArgumentParser(description = usage )
    parser.add_argument('--in', dest="infiles", nargs = '+', help = 'A list of mProphet output files containing all peakgroups (use quotes around the filenames)')
    parser.add_argument("--out", dest="outfile", default="feature_alignment_outfile", help="Output file with filtered peakgroups for quantification (only works for OpenSWATH)")
    parser.add_argument("--out_matrix", dest="matrix_outfile", default="", help="Matrix containing one peak group per row")
    parser.add_argument("--out_ids", dest="ids_outfile", default="", help="Id file only containing the ids")
    parser.add_argument("--out_meta", dest="yaml_outfile", default="", help="Outfile containing meta information, e.g. mapping of runs to original directories")
    parser.add_argument("--target_fdr", dest="target_fdr", default=0.01, type=float, help="target FDR cutoff to use, default 0.01 (1%%)", metavar='0.01')
    parser.add_argument("--max_rt_diff", dest="rt_diff_cutoff", default=30, type=float, help="Maximal difference in RT for two aligned features", metavar='30')
    parser.add_argument('--file_format', default='openswath', help="Which input file format is used (openswath or peakview)")

    experimental_parser = parser.add_argument_group('experimental options')

    experimental_parser.add_argument("--nr_high_conf_exp", default=1, type=int, help="Number of experiments in which the peptide needs to be identified with high confidence (e.g. above fdr_curoff)", metavar='1')
    experimental_parser.add_argument('--realign_runs', action='store_true', default=False, help="Tries to re-align runs based on their true RT (instead of using the less accurate iRT values by computing a spline against a reference run)")
    experimental_parser.add_argument("--alignment_score", dest="alignment_score", default=0.0001, type=float, help="Minimal score needed for a feature to be considered for alignment between runs", metavar='0.0001')

    args = parser.parse_args(sys.argv[1:])

    if args.infiles is None:
        raise Exception("This program needs infiles to be specified.")

    return args

def main(options):

    """
    import glob
    infiles = glob.glob("strep_align/Strep*0_Repl[12]_R0[2]/*all_peakgroups.xls")
    target_fdr = 0.01
    alignment_score = 0.0001
    nr_high_conf_exp = 1
    rtdiff = 10
    """
    realign_runs = True
    method = "global_best_cluster_score"

    # Read the files
    start = time.time()
    reader = SWATHScoringReader.newReader(options.infiles, options.file_format, "minimal")
    runs = reader.parse_files(realign_runs)
    # Create experiment
    this_exp = Experiment()
    this_exp.set_runs(runs)
    print("Reading the input files took %ss" % (time.time() - start) )

    multipeptides = this_exp.get_all_multipeptides(options.target_fdr, verbose=True)
    spl_aligner = SplineAligner()
    tcoll = spl_aligner.rt_align_all_runs(this_exp, multipeptides, options.alignment_score, False)
    this_exp.transformation_collection = tcoll

    ## Calculate optimal fdr
    decoy_frac = compute_decoy_frac(multipeptides, options.target_fdr)
    fdr_cutoff_calculated = find_iterate_fdr(multipeptides, decoy_frac)

    alignment = AlignmentAlgorithm().align_features(multipeptides, options.rt_diff_cutoff, fdr_cutoff_calculated, options.target_fdr, "global_best_cluster_score")

    # Filter 
    for mpep in multipeptides:
        # check if at least one is below the new FDR cutoff
        if min([pg.get_fdr_score() for pg in mpep.get_selected_peakgroups() ]) > fdr_cutoff_calculated:
            for p in mpep.get_peptides():
                p.unselect_all()
        # check if we have found enough
        if len( mpep.get_selected_peakgroups() ) < options.nr_high_conf_exp: 
            for p in mpep.get_peptides():
                p.unselect_all()

    this_exp.print_stats(multipeptides, alignment, None, fdr_cutoff_calculated, 0.0, 1)
    options.min_frac_selected = 0.0
    trafo_fnames = this_exp.write_to_file(multipeptides, options)

def find_iterate_fdr(multipeptides, decoy_frac):
    decoy_pcnt = decoy_frac*100
    fdrrange = numpy.arange(0.05,1,0.05)
    for fdr in fdrrange:
        calc_fdr = calc_precursor_fr(multipeptides, fdr/100.0 )*100
        print fdr, calc_fdr
        if calc_fdr > decoy_pcnt:
            break
        prev_fdr = fdr
        prev_calc_fdr = calc_fdr
    # Linear interpolation
    res = prev_fdr + (fdr-prev_fdr) * (decoy_pcnt-prev_calc_fdr)/(calc_fdr-prev_calc_fdr)
    return res/100.0

    final_calc_fdr = calc_precursor_fr(multipeptides, res/100.0 )*100

def calc_precursor_fr(multipeptides, target_fdr):
    allpg_cnt = 0
    alldecoypg_cnt = 0
    for mpep in multipeptides:
        count = False
        decoy = False
        for pep in mpep.get_peptides():
            if pep.get_best_peakgroup().get_fdr_score() < target_fdr:
                count = True
            if pep.get_decoy():
                decoy = True
        if count:
            allpg_cnt += 1
        if decoy and count:
            alldecoypg_cnt += 1
    return alldecoypg_cnt *1.0 / allpg_cnt

def compute_decoy_frac(multipeptides, target_fdr):
    allpg_cnt = 0
    alldecoypg_cnt = 0
    for mpep in multipeptides:
        for pep in mpep.get_peptides():
            if pep.get_best_peakgroup().get_fdr_score() < target_fdr:
                allpg_cnt += 1
                if pep.get_decoy():
                    alldecoypg_cnt += 1


    decoy_frac = alldecoypg_cnt *1.0 / allpg_cnt
    return decoy_frac

if __name__=="__main__":
    options = handle_args()
    main(options)
