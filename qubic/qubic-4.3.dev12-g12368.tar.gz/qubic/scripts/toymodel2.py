from __future__ import division

import matplotlib.pyplot as mp
import numexpr as ne
import numpy as np
from scipy.constants import c, pi
from pyoperators import MaskOperator
from pysimulators import create_fitsheader, SceneGrid
from qubic import QubicInstrument, QubicScene

NU = 150e9                   # [Hz]
NSIDE = 256

FOCAL_LENGTH = 0.3           # [m]

SOURCE_POWER = 1             # [W]
SOURCE_THETA = np.radians(0) # [rad]
SOURCE_PHI = np.radians(45)  # [rad]

NPOINT_FOCAL_PLANE = 512**2  # number of detector plane sampling points

scene = QubicScene(NU / 1e9, nside=NSIDE, kind='I')
qubic = QubicInstrument(detector_ngrids=1)

FOCAL_PLANE_LIMITS = (np.nanmin(qubic.detector.vertex[..., 0]),
                      np.nanmax(qubic.detector.vertex[..., 0]))  # [m]
# to check energy conservation (unrealistic detector plane):
#FOCAL_PLANE_LIMITS = (-4, 4) # [m]


#################
# FOCAL PLANE
#################
nfp_x = int(np.sqrt(NPOINT_FOCAL_PLANE))
a = np.r_[FOCAL_PLANE_LIMITS[0]:FOCAL_PLANE_LIMITS[1]:nfp_x*1j]
fp_x, fp_y = np.meshgrid(a, a)
fp_spacing = (FOCAL_PLANE_LIMITS[1] - FOCAL_PLANE_LIMITS[0]) / nfp_x


############
# DETECTORS
############
header = create_fitsheader((nfp_x, nfp_x), cdelt=fp_spacing, crval=(0, 0),
                           ctype=['X---CAR', 'Y---CAR'], cunit=['m', 'm'])
focal_plane = SceneGrid.fromfits(header)
integ = MaskOperator(qubic.detector.all.removed) * \
        focal_plane.get_integration_operator(
            focal_plane.topixel(qubic.detector.all.vertex[..., :2]))


###############
# COMPUTATIONS
###############
E = qubic.get_response(scene, SOURCE_THETA, SOURCE_PHI, SOURCE_POWER,
                       x=fp_x.ravel(), y=fp_y.ravel(), area=fp_spacing**2)
E.shape = (nfp_x, nfp_x)
I = np.abs(E)**2
D = integ(I)


##########
# DISPLAY
##########
mp.figure()
mp.imshow(np.log10(I), interpolation='nearest', origin='lower')
mp.autoscale(False)
qubic.detector.plot(transform=focal_plane.topixel)
mp.figure()
mp.imshow(D, interpolation='nearest')
mp.gca().format_coord = lambda x, y: 'x={} y={} z={}'.format(x, y, D[x, y])
mp.show()
print('Given {} horns, we get {} W in the detector plane and {} W in the detec'
      'tors.'.format(int(np.sum(qubic.horn.open)), np.sum(I), np.sum(D)))
