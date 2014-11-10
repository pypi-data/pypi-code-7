"""Contains functions for calculating VV- and VT- rates
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"


from .crosssection import vt_integral_fho, vv_integral_fho
from .particles import Molecule
import numpy as np


def vt_rate_fho(T: float, idata: np.ndarray, molecule: Molecule, i: int, delta: int, model: str='VSS') -> float:
    """Calculates the VT transition rate constant using the FHO probability and VSS or rigid sphere cross-section models
    for the following process: **M(i) + P -> M(i + delta) + P**

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule which undergoes the VT transition
    i : int
        the vibrational level of the molecule
    delta : int
        the change in vibrational level of the molecule
    model : str, optional
        the elastic crosssection model to be used, possible values:
            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'

    Returns
    -------
    float
        The VT transition rate

    """
    return 8. * vt_integral_fho(T, 0, idata, molecule, i, delta, model, False)


def vv_rate_fho(T: float, idata: np.ndarray, molecule1: Molecule, molecule2: Molecule, i: int, k: int, i_delta: int,
                model: str='VSS') -> float:
    """Calculates the VV transition rate constant using the FHO probability and VSS or rigid sphere cross-section models
    for the following process: **M1(i) + M2(k) -> M1(i + i_delta) + M2(k - i_delta)**

    Parameters
    ----------
    T : float
        the temperature of the mixture
    idata : 1-D array-like
        the array of interaction data
    molecule1 : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule M1
    molecule2 : Molecule or any subclass (MoleculeMultiT, MoleculeOneT)
        the molecule M2
    i : int
        the vibrational level of molecule M1
    k : int
        the vibrational level of molecule M2
    i_delta : int
        the change in vibrational level of molecule M1
    model : str, optional
        the elastic crosssection model to be used, possible values:
            * 'RS' (Rigid Sphere model)
            * 'VSS' (Variable Soft Sphere model)
            * 'GSS' (Generalized Soft Sphere model)

        defaults to 'VSS'

    Returns
    -------
    float
        The VV transition rate

    """
    return 8. * vv_integral_fho(T, 0, idata, molecule1, molecule2, i, k, i_delta, model, False)