#!/usr/bin/env python
# coding: utf-8

"""
Fourier Representation
"""

# Third-Party Libraries
from numpy import *
from numpy.fft import *

#
# Metadata
# ------------------------------------------------------------------------------
#
from .about_fourier import *

#
# Contents
# ------------------------------------------------------------------------------
#
def F(x, **kwargs):
    """
    Computes the Fourier transform of the object `x`.

    If the argument `x` is a numpy array, its spectral representation 
    is the Discrete-Time Fourier Transform (DTFT), 
    the function of the frequency $f$ given by:

    $$
    x(f) = \Delta t \sum_{j=0}^{n_x-1} x_n \exp(-2 i \pi f j \Delta t)
    $$

    Otherwise, the spectral representation depends on the object type.

    Arguments
    ---------
    `x:`
      : the object to transform, either a `numpy.ndarray` (1-dim.) or an object 
        that implements the Fourier protocol -- roughly speaking, that has a
        Fourier transform method `__F__`. 
        
    The extra arguments in `kwargs` are dependent of the object type.
    For numpy arrays, they are:

    `dt:`
      : sampling time, type `float`, defaults to `1.0`.

    `n:`
      : minimal number of points used in spectrum estimation; type `int`, 
        defaults to `None`.

    `power_of_two:`
      : if `True`, forces the FFT used in the implementation of the transform 
        to be applied on a power of two number of samples ; defaults to `False`.

    `window:` 
      : window applied to the signal before the transform : a function of an 
        integer `n` that returns a 1-dim. numpy array of floats of length `n`
        (such as `numpy.bartlett`, `numpy.hanning`, etc.). 
        By default, the rectangular window (`numpy.ones`) is used.
    
    Returns
    -------
    `Fx`: function.
        Spectral representation of `x`.

    See also
    --------
    `filters.AR`, `filters.FIR`, `numpy.fft`.
    """
    try:
        return x.__F__(**kwargs)
    except AttributeError:
        pass

    x = array(x, copy=False)
    if not len(shape(x)) == 1:
        raise TypeError("`x` is not 1-dimensional.")

    dt           = kwargs.get("dt"          , 1.0)
    n            = kwargs.get("n"           , None)
    power_of_two = kwargs.get("power_of_two", None)
    window       = kwargs.get("window"      , ones)

    nx = len(x)
    x = x * window(nx)

    if n is None and power_of_two is None:
        # exact spectrum computation.
        def Fx(f):
            f = ravel(f)
            Fx_ = zeros((len(f),), dtype=complex64)
            for i, f_ in enumerate(f):
                Fx_[i] = dt * dot(exp(-1j * 2 * pi * f_ * arange(nx) * dt), x)
            return Fx_

            # DEPRECATED: clean but prone to memory errors (n^2 behavior)
            # f = reshape(f, (1, len(f)))
            # n = reshape(arange(nx), (nx, 1))
            # return dt * dot(x, exp(-1j * 2 * pi * dt * n * f))
            
        Fx.fft = None
    else:
        n = n or 1
        n = max(n, nx)
        if power_of_two:
            n = int(2**ceil(log2(n)))
        fft_x = fft(x, n)
        # fft-based, 0-order spectrum interpolation.
        def Fx(f):
            k = (round_((ravel(f) * n * dt)) % n).astype(uint64)
            return dt * fft_x[k]
        Fx.fft = fft_x    
    return Fx

