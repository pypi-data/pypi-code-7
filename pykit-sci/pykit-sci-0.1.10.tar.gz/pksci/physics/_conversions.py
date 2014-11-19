# -*- coding: utf-8 -*-
"""
=========================================================
Functions for physics (:mod:`pksci.physics._conversions`)
=========================================================

.. currentmodule:: pksci.physics._conversions

"""
from __future__ import absolute_import, division, print_function

__docformat__ = 'restructuredtext'

from pint import UnitRegistry

import numpy as np

from ..tools.refdata import hc

__all__ = ['ke2v', 'v2ke', 'wvl2nrg', 'nrg2wvl',
           'photon_wvl2photon_nrg', 'photon_nrg2photon_wvl']


ureg = UnitRegistry()
Qty = ureg.Quantity


def ke2v(ke, mass=None, mass_units='amu',
         ke_units='eV', v_units='angstrom/ps',
         magnitude_only=False):
    u"""
    Convert :math:`KE` of particle with mass :math:`m` to speed :math:`v`.

    .. math::

       v = \\sqrt{\\frac{2 KE}{m}}

    Parameters
    ----------
    ke : float or Quantity object
        kinetic energy
    mass : float
        particle mass
    mass_units : str, optional
        particle mass units
    ke_units : str, optional
        kinetic energy units
    v_units : str, optional
        speed units
    magnitude_only : bool, optional
        if: ``False``, return result as a :py:class:`pint.Quantity`
        else: return return result magnitude

    Returns
    -------
    v : float or Quantity
        speed of particle :math:`v`.

    Examples
    --------

    First, let's import the Atom and Atoms classes along with this function.

    >>> from pksci.chemistry import Atom, Atoms
    >>> from pksci.physics import ke2v

    Now create a carbon atom "ion"

    >>> Cion = Atom('C')

    Convert the kinetic energy (default units: ``eV``) of a ``30 eV``
    carbon ion to speed in the default units of \u212b/ps:

    >>> ke2v(30, mass=Cion.m)
    <Quantity(219.54428518, 'angstrom / picosecond')>

    Same thing, but now output with prettyprint formatting:

    >>> print('{:.2fP}'.format(ke2v(30, mass=Cion.m)))
    219.54 angstrom/picosecond

    Same thing, but speed in units of ``mph``:

    >>> print('{:.3P}'.format(ke2v(30, mass=Cion.m, v_units='mph')))
    4.91e+04 mph

    Same thing, but speed in units of ``ft/femtosecond``:

    >>> print('{:.3P}'.format(ke2v(30, mass=Cion.m, v_units='ft/fs')))
    7.20e-11 foot/femtosecond

    Same thing, but speed in units of ``m/s``:

    >>> print('{:.3P}'.format(ke2v(30, mass=Cion.m, v_units='m/s')))
    2.20e+04 meter/second

    Now let's make an ``Atoms`` object with two Nitrogen atoms:

    >>> N = Atom('N')
    >>> N2 = Atoms([N for i in range(2)])
    >>> N2.m == 2 * N.m  # Does N2 have twice the mass of N?
    True  # Of course not true physically due to binding energy mass loss.

    So what's the speed of a :math:`N_2` molecule with
    :math:`KE=50` ``eV``?:

    >>> print('{:.1fP}'.format(ke2v(50, mass=N2.m)))
    185.6 angstrom/picosecond

    Now let's make an ``Atoms`` object with 60 Carbon atoms to
    represent a buckeyball:

    >>> C = Atom('C')
    >>> C60 = Atoms([C for i in range(60)])
    >>> C60.m == 60 * C.m  # Does C60 have 60 times the mass of C?
    True  # Of course not true physically due to binding energy mass loss.

    So what's the speed of a :math:`C_{60}` molecule with
    :math:`KE=50` ``eV``?:

    >>> print('{:.1fP}'.format(ke2v(50, mass=C60.m)))
    36.6 angstrom/picosecond

    """
    if isinstance(ke, (int, float)):
        ke = Qty(ke, ke_units)
    else:
        ke = Qty(ke.magnitude, ke.units)

    if mass is None:
        raise TypeError('mass must be an int or float')

    m = Qty(mass, mass_units)
    m.ito('eV/({})**2'.format(v_units))

    v = np.sqrt(2 * ke / m)
    if magnitude_only:
        return v.magnitude
    else:
        return v


def v2ke(v, mass=None, mass_units='amu',
         ke_units='eV', v_units='angstrom/ps',
         magnitude_only=False):
    u"""
    Convert speed :math:`v` of particle with mass :math:`m` to kinetic energy:

    .. math::

       KE = \\frac{1}{2}mv^2

    Parameters
    ----------
    v : float or Quantity object
        speed of particle
    mass : float
        particle mass
    mass_units : str, optional
        particle mass units
    ke_units : str, optional
        kinetic energy units
    v_units : str, optional
        speed units
    magnitude_only : bool, optional
        if: ``False``, return result as a :py:class:`pint.Quantity`
        else: return return result magnitude

    Returns
    -------
    ke : Quantity or float
        kinetic energy of particle, :math:`KE`.

    """
    if isinstance(v, (int, float)):
        v = Qty(v, v_units)
    else:
        v = Qty(v.magnitude, v.units)

    if mass is None:
        raise TypeError('mass must be an int or float')

    m = Qty(mass, mass_units)
    m.ito('eV/({})**2'.format(v_units))

    ke = 0.5 * m * v**2
    if magnitude_only:
        return ke.magnitude
    else:
        return ke


def photon_wvl2photon_nrg(photon_wvl):
    u"""
    Convert photon wavelength :math:`\\lambda` to energy :math:`E_{\\gamma}`

    .. math::

       E_{\\gamma} = \\frac{hc}{\\lambda}

    where

    .. math::
       h = 4.135667516\\times 10^{-15}\\, \\mathrm{eV\\cdot{}s}

    .. math::
       c = 299792458\\times 10^9\\, \\mathrm{nm/s}

    .. math::
       hc \\approx 1239.84\\, \\mathrm{eV\\cdot nm}

    Parameters
    ----------
    photon_wvl : array_like
        Photon wavelength in **nanometers**.

    Returns
    -------
    photon_nrg : float
        Equivalent photon energy

    """
    return hc / photon_wvl

vphoton_wvl2photon_nrg = np.vectorize(photon_wvl2photon_nrg)


def wvl2nrg(wvl):
    """Alias function for :py:func:`photon_wvl2photon_nrg`"""
    return photon_wvl2photon_nrg(wvl)

vwvl2nrg = np.vectorize(wvl2nrg)


def photon_nrg2photon_wvl(photon_nrg):
    u"""
    Convert photon energy :math:`E_{\\gamma}` to wavelength :math:`\\lambda`

    .. math::

       \\lambda = \\frac{hc}{E_{\\gamma}}

    where

    .. math::
       h = 4.135667516\\times 10^{-15}\\, \\mathrm{eV\\cdot{}s}

    .. math::
       c = 299792458\\times 10^9\\, \\mathrm{nm/s}

    .. math::
       hc \\approx 1239.84\\, \\mathrm{eV\\cdot nm}

    Parameters
    ----------
    photon_nrg : float
        Photon energy

    Returns
    -------
    photon_wvl : float
        Equivalent photon wavelength

    """
    return hc / photon_nrg

vphoton_nrg2photon_wvl = np.vectorize(photon_nrg2photon_wvl)


def nrg2wvl(nrg):
    """Alias function for :py:func:`photon_nrg2photon_wvl`"""
    return photon_nrg2photon_wvl(nrg)

vnrg2wvl = np.vectorize(nrg2wvl)
