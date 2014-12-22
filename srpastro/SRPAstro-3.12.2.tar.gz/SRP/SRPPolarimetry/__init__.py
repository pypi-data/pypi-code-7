""" Init file for SRPPolarimetry

Context : SRP
Module  : Polarimetry
Version : 1.2.0
Author  : Stefano Covino
Date    : 16/07/2014
E-mail  : stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino

Usage   : to be imported

History : (21/02/2012) First named version.
        : (29/02/2012) Wave plate matrix added.
        : (02/09/2013) ISM matrix added.
        : (16/07/2014) PolBias added.
"""


__all__ = ['AluminiumRefractiveIndex', 'MuellerISMMatrix','MuellerMetallicMirrorMatrix',
            'MuellerRotationMatrix','MuellerTransmissionMatrix', 'MuellerHalfWavePlateMatrix',
            'MuellerQuarterWavePlateMatrix','MuellerWavePlateMatrix', 'Pol2Stokes', 'PolBias',
            'Stokes2Pol']



