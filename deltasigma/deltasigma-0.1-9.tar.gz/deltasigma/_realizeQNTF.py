from __future__ import division
import numpy as np

from . import evalTF
from ._utils import _get_zpk

def realizeQNTF(ntf, form='FB', rot=False, bn=None):
    """Convert a quadrature NTF into an ABCD matrix

    The basic idea is to equate the value of the loop filter at a set of
    points in the z-plane to the values of :math:`L_1 = 1-1/H` at those points.

    The order of the zeros is used when mapping the NTF onto the chosen topology.

    Supported structures are:

    * 'FB': Feedback
    * 'PFB': Parallel feedback
    * 'FF': Feedforward (bn is the coefficient of the aux DAC)
    * 'PFF': Parallel feedforward

    Not currently supported - feel free to send in a patch:

    * 'FBD'    FB with delaying quantizer  NOT SUPPORTED YET
    * 'FFD'    FF with delaying quantizer  NOT SUPPORTED YET

    **Parameters:**

    ntf : lti object or supported description
        The NTF to be converted.
    form : str
        The form to be used. See above for the currently supported
        topologies.
    rot : bool, optional
        Set ``rot`` to ``True`` to rotate the states to make as
        many coefficients as possible real. 
    bn : float, optional
        Coefficient of the auxiliary DAC, to be specified for a
        'PFF' form.

    """
    #Code common to all forms
    ntf_z, ntf_p, _ = _get_zpk(ntf)
    order = max(ntf_p.shape)
    A = np.diag(ntf_z)
    A[1:order + 1:A.shape[0]] = 1
    if form == 'PFB' or form == 'PFF':
        # partition the NTF zeros into in-band and image-band
        fz = np.angle(ntf_z)/(2*np.pi)
        f0 = fz[0]
        inband_zeros = abs(fz - f0) < abs(fz + f0)
        n_in = np.sum(inband_zeros)
        imageband_zeros = not inband_zeros
        n_im = np.sum(imageband_zeros)
        if any(imageband_zeros[(n_in + 1 -1):imageband_zeros.shape[0]] != 1):
            raise ValueError('Please put the image-band zeros at the end of' +
                             'the ntf zeros')
        if n_im > 0:
            A[(n_in + 1 -1), (n_in -1)] = 0
    D = np.zeros(shape=(1, 2), dtype='float64')
    # Find a set of points in the z-plane that are not close to zeros of H
    zSet = np.zeros(shape=(np.dot(2, order), 1), dtype='float64')
    for i in range(1, (np.dot(order, 2) +1)):
        z = np.dot(2, rand(1, 1)) - 1 + np.dot(1j, (np.dot(2, rand(1, 1)) - 1))
        while any(abs(z - np.array([ntf_z, zSet]).reshape(1, -1)) < 0.1):
            z = np.dot(2, rand(1, 1)) - 1 + np.dot(1j, (np.dot(2, rand(1, 1)) - 1))
        zSet[(i -1)] = z
    # Evaluate L1 = 1-1/H at these points
    L1 = 1 - 1.0/evalTF(ntf, zSet)
    if 'FB' == form:
        B = np.zeros(shape=(order, 2), dtype='float64')
        C = np.array([np.zeros(shape=(1, order - 1), dtype='float64'), 1]).reshape(1, -1)
        # Compute F = C * inv(zI-A) at each z in zSet
        F = np.zeros(shape=(max(zSet.shape), order), dtype='float64')
        I = eye(order)
        for i in range(1, (max(zSet.shape) +1)):
            F[(i -1), :] = np.dot(C, inv(np.dot(zSet[(i -1)], I) - A))
        B[:, 1] = np.linalg.solve(F, L1)
        if rot == 1:
            ABCD = np.array([A, B[:, 1], C, 0]).reshape(1, -1)
            for i in range(1, (order +1)):
                phi = angle(ABCD[(i -1), -1])
                ABCD[(i -1), :] = np.dot(ABCD[(i -1), :], exp(np.dot(- 1j, phi)))
                ABCD[:, (i -1)] = np.dot(ABCD[:, (i -1)], exp(np.dot(1j, phi)))
            A, B2, C, D2 = partitionABCD(ABCD) # nargout=4
            B[:, 1] = B2
        B[0, 0] = abs(B[0, 1])
    elif 'PFB' == form:
        B = np.zeros(shape=(order, 2), dtype='float64')
        C = np.array([np.zeros(shape=(1, n_in - 1), dtype='float64'), 1, np.zeros(shape=(1, n_im - 1), dtype='float64'), 1]).reshape(1, -1)
        # Compute F = C * inv(zI-A) at each z in zSet
        F = np.zeros(shape=(max(zSet.shape), order), dtype='float64')
        I = eye(order)
        for i in range(1, (max(zSet.shape) +1)):
            F[(i -1), :] = np.dot(C, inv(np.dot(zSet[(i -1)], I) - A))
        B[:, 1] = np.linalg.solve(F, L1)
        if rot == 1:
            ABCD = np.array([A, B[:, 1], C, 0]).reshape(1, -1)
            for i in range(1, (order +1)):
                phi = angle(ABCD[(i -1), -1])
                ABCD[(i -1), :] = np.dot(ABCD[(i -1), :], exp(np.dot(- 1j, phi)))
                ABCD[:, (i -1)] = np.dot(ABCD[:, (i -1)], exp(np.dot(1j, phi)))
            A, B2, C, D2 = partitionABCD(ABCD) # nargout=4
            B[:, 1] = B2
        B[0, 0] = abs(B[0, 1])
    elif 'FF' == form:
        B0 = np.array([1, np.zeros(shape=(order - 1, 1), dtype='float64')]).reshape(1, -1)
        B = B0
        B[-1] = bn
        # Compute F = inv(zI-A)*B at each z in zSet
        F = np.zeros(shape=(order, max(zSet.shape)), dtype='float64')
        I = eye(order)
        for i in range(1, (max(zSet.shape) +1)):
            F[:, (i -1)] = np.dot(inv(np.dot(zSet[(i -1)], I) - A), B)
        C = L1.T / F
        if rot == 1:
            ABCD = np.array([A, B, C, 0]).reshape(1, -1)
            for i in range(2, (order - 1 +1)):
                phi = angle(ABCD[-1, (i -1)])
                ABCD[(i -1), :] = np.dot(ABCD[(i -1), :], exp(np.dot(1j, phi)))
                ABCD[:, (i -1)] = np.dot(ABCD[:, (i -1)], exp(np.dot(- 1j, phi)))
            A, B, C, D2 = partitionABCD(ABCD) # nargout=4
        B = np.array([- B0, B]).reshape(1, -1)
    elif 'PFF' == form:
        B0 = np.array([1, np.zeros(shape=(order - 1, 1), dtype='float64')]).reshape(1, -1)
        B = B0
        B[(n_in + 1 -1)] = 1
        # Compute F = inv(zI-A)*B at each z in zSet
        F = np.zeros(shape=(order, max(zSet.shape)), dtype='float64')
        I = eye(order)
        for i in range(1, (max(zSet.shape) +1)):
            F[:, (i -1)] = np.dot(inv(np.dot(zSet[(i -1)], I) - A), B)
        C = L1.T / F
        if rot == 1:
            ABCD = np.array([A, B, C, 0]).reshape(1, -1)
            for i in range(2, (order - 1 +1)):
                phi = angle(ABCD[-1, (i -1)])
                ABCD[(i -1), :] = np.dot(ABCD[(i -1), :], exp(np.dot(1j, phi)))
                ABCD[:, (i -1)] = np.dot(ABCD[:, (i -1)], exp(np.dot(- 1j, phi)))
            A, B, C, D2 = partitionABCD(ABCD) # nargout=4
        B = np.array([B0, B]).reshape(1, -1)
    else:
        raise ValueError('Sorry, form %s is not supported.' % form)
    ABCD = np.hstack((np.vstack((A, B)), np.vstack((C, D))))
    return ABCD
