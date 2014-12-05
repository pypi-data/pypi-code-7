
import numpy as np
from feature_detector import run_feature_finder

def remove_shoulder_peaks(pm, rtmin, rtmax, mzmin, mzmax):
    """
    removes shoulder peaks in pm aroung the one dominating peak in given
    window rtmin..rtmax, mzmin..mzmax

    works inplace.
    """

    mzmean = 0.5 * (mzmin + mzmax)
    ###############################################################################################
    #
    # the following calculation of min_mz_dist and following parameters are  is highly dependent on
    # the used ms device !!!
    #
    min_mz_dist = 0.425 * (2e-5 * mzmean ** 2 + 0.0444 * mzmean - 4.3335) / 1000.0

    t_thresh = 1.1                         # cutting line starts 10 % above max shoulder peak
    shoulder_peak_max_dist = 0.18          # m/z width of shoulder peak range
    shoulder_peak_min_dist = min_mz_dist   # min m/z diff of shoulder peaks to main peak
    shoulder_peak_max_proportion = 0.03    # max quotient I(shoulder_peak) / I(main_peak)

    #
    ###############################################################################################

    rts, intensities = pm.chromatogram(mzmin, mzmax, rtmin, rtmax, msLevel=1)

    # find maximal intensity and correspondig rt values
    max_intensity, rt_with_max_intensity = max(zip(intensities, rts))

    # find mz_at_max_intensity value in mz-windows where max peak appears
    spec_at_max_intensity = [s for s in pm.spectra if s.rt == rt_with_max_intensity][0]
    peaks = spec_at_max_intensity.peaks
    peaks_in_window = peaks[(mzmin <= peaks[:, 0]) & (peaks[:, 0] <= mzmax)]
    mz_at_max_intensity = peaks_in_window[np.argmax(peaks_in_window[:, 1]), 0]

    upper_limit_shoulder_intensity = shoulder_peak_max_proportion * max_intensity

    for spec in pm.spectra:
        if rtmin <= spec.rt <= rtmax:
            peaks = spec.peaks

            # find indices of peaks below upper_limit_shoulder_intensity
            mask = (peaks[:, 1] <= upper_limit_shoulder_intensity)

            # no peaks below this threshold ? we have to catch this as np.max below throws
            # exception if argument ist empty.
            if not len(peaks[mask]):
                continue

            max_shoulder_intensity = np.max(peaks[mask, 1])

            # we draw two lines starting at
            #
            #      (mz_at_max_intensity, t_thresh * max_shoulder_intensity)
            #
            # falling down to
            #
            #      (mz_at_max_intensity +/- shoulder_peak_max_dist, 0)
            #
            # then we erase all peaks which have a min distance of shoulder_peak_min_dist
            # to mz_at_max_intensity and where the intensity is below these lines

            mz_dist = np.abs(peaks[:, 0] - mz_at_max_intensity)
            limit = max_shoulder_intensity * (t_thresh - mz_dist / shoulder_peak_max_dist)

            idx = (peaks[:, 1] < limit) & (mz_dist >= shoulder_peak_min_dist)
            spec.peaks[idx, 1] = 0.0


def cleanup_peakmap(peak_map, updated_config=None):
    """
    Tries to find shoulder peaks in given peak map and removes them.
    This routine is very specific for data from orbitrap ms device.
    this functions has no return value, it works inplace.
    """

    if updated_config is None:
        updated_config = dict()

    t = run_feature_finder(peak_map, run_fast=True, **updated_config)

    peaks = zip(t.rtmin, t.rtmax, t.mzmin, t.mzmax)
    peak_map = t.peakmap.uniqueValue()
    for peak in peaks:
        remove_shoulder_peaks(peak_map, peak[0], peak[1], peak[2], peak[3])
