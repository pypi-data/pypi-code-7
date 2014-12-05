import emzed


_default_ff_metabo = dict(common_noise_threshold_int=1000.0,
                          common_chrom_peak_snr=3.0,
                          common_chrom_fwhm=25.0,
                          mtd_mass_error_ppm=15.0,
                          mtd_reestimate_mt_sd='true',
                          mtd_trace_termination_criterion='outlier',
                          mtd_trace_termination_outliers=5,
                          mtd_min_sample_rate=0.5,
                          mtd_min_trace_length=3.0,
                          mtd_max_trace_length=350.0,
                          epdet_width_filtering='off',
                          epdet_min_fwhm=3.0,
                          epdet_max_fwhm=60.0,
                          epdet_masstrace_snr_filtering='false',
                          ffm_local_rt_range=10.0,
                          ffm_local_mz_range=10.0,
                          ffm_charge_lower_bound=1,
                          ffm_charge_upper_bound=3,
                          ffm_report_summed_ints='false',
                          ffm_disable_isotope_filtering='true',
                          ffm_use_smoothed_intensities='true')


_fast_ff_metabo = _default_ff_metabo.copy()


_fast_ff_metabo.update(dict(common_noise_threshold_int=50000.0,
                            common_chrom_peak_snr=5.0,
                            mtd_mass_error_ppm=20.0,
                            mtd_trace_termination_outliers=3,
                            mtd_min_trace_length=10.0,
                            mtd_max_trace_length=500.0,
                            epdet_min_fwhm=10.0,
                            epdet_max_fwhm=80.0,
                            ffm_disable_isotope_filtering="false",
                            ))


def run_feature_finder(peakmap, run_fast=False, updated_params=None):
    """
    runs pyopenms metabo feature finder with appropriate settings for orbitrap ms.

    run_fast=True  only detects dominating peaks and is fast.
    run_fast=False detects many more peaks but is slower.
    """

    if run_fast:
        config = _fast_ff_metabo.copy()
    else:
        config = _default_ff_metabo.copy()

    if updated_params is not None:
        config.update(updated_params)

    t = emzed.ff.runMetaboFeatureFinder(peakmap, **config)
    return t
