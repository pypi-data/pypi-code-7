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
$Maintainer: Hannes Roest $
$Authors: Hannes Roest $
--------------------------------------------------------------------------
"""

# Script to generate a set of SWATH MS files for testing
# 
# This script will generate a set of files that look like SWATH MS files with
# different properties. Specifically, it will allow to se the
# IsolationWindowOffset (lower/upper) to different values to mimick what
# OpenMS/pwiz do when converting a file.
# 

import pyopenms
import numpy
from scipy.stats import norm

assert pyopenms.__version__ == "1.11"

def getChromatogramExperiment(rt_offset, base_intensity, nr_precursors, nr_transitions, nr_datapoints, prec_mz=True):
    exp = pyopenms.MSExperiment()
    for prec_cnt in range(nr_precursors):
        for ch in (2,3):
            charge_mult = 2**ch 
            # New precursor, get RT center and compute transitions
            center_rt = (prec_cnt + 1) * 1000  + rt_offset
            for chrom_cnt in range(nr_transitions):
                # New chrom
                transition_id = "chromatogram_pep%s/%s_%s" % (prec_cnt, ch, chrom_cnt) 
                chrom = pyopenms.MSChromatogram()
                chrom.setNativeID(transition_id)
                # Intensity multiplier to produce more interesting graphs
                int_multiplier = base_intensity * (chrom_cnt+1) *(5*prec_cnt+1)*charge_mult
                # Calculate chromatogram data
                pk_list = []
                for rt_cnt in range(nr_datapoints):
                    rt = center_rt - 1*(nr_datapoints/2.0-rt_cnt)
                    intensity = norm.pdf( (rt_cnt - nr_datapoints/2.0 )/ (nr_datapoints /10.0) ) * int_multiplier
                    pk_list.append( (rt, intensity))
                chromdata = numpy.array(pk_list, dtype=numpy.float32)
                chrom.set_peaks(chromdata)
                if prec_mz:
                    # get Precursor
                    prec = pyopenms.Precursor()
                    prec.setMZ( (1200.0 + 10*prec_cnt) / ch )
                    chrom.setPrecursor(prec)
                exp.addChromatogram(chrom)
    return exp

def getTransitionExp(peptide_sequences, nr_transitions, prec_mz=True):
    traml = pyopenms.TargetedExperiment()
    prot = pyopenms.Protein()
    prot.id = "PROTEINA"
    traml.addProtein(prot)

    for prec_cnt in range(len(peptide_sequences)):
        for ch in (2,3):
            # New peptide
            peptide = pyopenms.Peptide()
            peptide.setChargeState(ch)
            peptide.sequence = peptide_sequences[prec_cnt]
            peptide.id = "%s_%s/%s" % (prec_cnt, peptide.sequence, ch) 
            peptide.protein_refs = [ prot.id ]
            traml.addPeptide(peptide)
            for chrom_cnt in range(nr_transitions):
                transition_id = "chromatogram_pep%s/%s_%s" % (prec_cnt, ch, chrom_cnt) 
                # New transition
                tr = pyopenms.ReactionMonitoringTransition()
                tr.setNativeID(transition_id)
                tr.setPeptideRef(peptide.id)
                if prec_mz:
                    # get Precursor
                    prec = pyopenms.Precursor()
                    prec.setMZ(400 + 10*prec_cnt)
                    tr.setPrecursorMZ(400 + 10*prec_cnt)
                traml.addTransition(tr)
    return traml

exp= getChromatogramExperiment(0, 1, 2, 6, 100, True) 
pyopenms.MzMLFile().store("dataset2_file1.mzML", exp)
exp = getChromatogramExperiment(20, 10, 2, 6, 100, True) 
pyopenms.MzMLFile().store("dataset2_file2.mzML", exp)
exp = getChromatogramExperiment(40, 25, 2, 6, 100, True) 
pyopenms.MzMLFile().store("dataset2_file3.mzML", exp)

traml = getTransitionExp(["PEPTIDER", "PEPTIDEK"], 6, True) 
pyopenms.TraMLFile().store("dataset2_description.TraML", traml)


