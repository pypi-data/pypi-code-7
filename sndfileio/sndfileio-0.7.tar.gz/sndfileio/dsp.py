from scipy import signal
import numpy as np
import warnings

from .util import *

def lowpass_cheby2(samples, freq, sr, maxorder=12):
    """
    Cheby2-Lowpass Filter

    Filter data by passing data only below a certain frequency.
    The main purpose of this cheby2 filter is downsampling.
    
    This method will iteratively design a filter, whose pass
    band frequency is determined dynamically, such that the
    values above the stop band frequency are lower than -96dB.

    samples : Data to filter, type numpy.ndarray.
    freq    : The frequency above which signals are attenuated
              with 95 dB
    sr      : Sampling rate in Hz.
    maxorder: Maximal order of the designed cheby2 filter
    """
    b, a, freq_passband = lowpass_cheby2_coeffs(freq, sr, maxorder)
    return signal.lfilter(b, a, data)


def lowpass_cheby2_coeffs(freq, sr, maxorder=12):
    """
    freq    : The frequency above which signals are attenuated
              with 95 dB
    sr      : Sampling rate in Hz.
    maxorder: Maximal order of the designed cheby2 filter

    Returns --> (b, a, freq_passband)
    """
    
    nyquist = sr * 0.5
    # rp - maximum ripple of passband, rs - attenuation of stopband
    rp, rs, order = 1, 96, 1e99
    ws = freq / nyquist # stop band frequency
    wp = ws # pass band frequency
    # raise for some bad scenarios
    if ws > 1:
        ws = 1.0
        msg = "Selected corner frequency is above Nyquist. " + \
              "Setting Nyquist as high corner."
        warnings.warn(msg)
    while True:
        if order <= maxorder:
            break
        wp = wp * 0.99
        order, wn = signal.cheb2ord(wp, ws, rp, rs, analog=0)
    b, a = signal.cheby2(order, rs, wn, btype='low', analog=0, output='ba')
    return _lowpass_cheby2_coeffs(b, a, wp*nyquist)


def filter_butter_coeffs(filtertype, freq, samplerate, order=5):
    """
    calculates the coefficients for a digital butterworth filter

    filtertype: 'low', 'high', 'band'
    freq      : cutoff freq.
                in the case of 'band': (low, high)

    Returns --> (b, a)
    """
    assert filtertype in ('low', 'high', 'band')
    nyq = 0.5 * samplerate
    if filtertype == 'band':
        low, high = freq
        low  /= nyq
        high /= nyq
        b, a = signal.butter(order, [low, high], btype='band')
    else:
        try:
            freq = freq / nyq
        except TypeError:
            freq = [f/nyq for f in freq]
        b, a = signal.butter(order, freq, btype=filtertype)
    return b, a


def filter_butter(samples, samplerate, filtertype, freq, order=5):
    """
    Filters the samples with a digital butterworth filter

    samples   : mono samples
    filtertype: 'low', 'band', 'high'
    freq      : for low or high, the cutoff freq
                for band, (low, high)
    samplerate: the sampling-rate
    order     : the order of the butterworth filter

    Returns --> the filtered samples

    NB: calls filter_butter_coeffs to calculate the coefficients
    """
    assert filtertype in ('low', 'high', 'band')
    b, a = filter_butter_coeffs(filtertype, freq, samplerate, order=order)
    def func(data):
        return signal.lfilter(b, a, data)
    return apply_multichannel(samples, func)
    

def filter_butter_plot_freqresponse(b, a, samplerate, numpoints=2000):
    """
    Plot the freq. response of the digital butterw. filter 
    defined by the coeffs. (b, a) at `samplerate`

    Returns --> nothing

    See also: filter_butter_coeffs
    """
    import matplotlib.pyplot as plt
    plt.figure(1)
    plt.clf()
    w, h = signal.freqz(b, a, worN=numpoints)
    plt.semilogx((samplerate*0.5/np.pi) * w, np.abs(h))
    plt.xlabel('Freq (Hz)')
    plt.ylabel('Gain')
    plt.grid(True)
    plt.show()
    