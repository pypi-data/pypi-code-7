#
#   Copyright (c) 2014, Scott J Maddox
#
#   This file is part of SimpleQW.
#
#   SimpleQW is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   SimpleQW is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public
#   License along with SimpleQW.  If not, see
#   <http://www.gnu.org/licenses/>.
#
#######################################################################

# std lib imports
import unittest

# local imports
from simpleqw import finite_well_1d


class TestFiniteWell1D(unittest.TestCase):
    def testNumStatesScaled(self):
        self.assertEqual(finite_well_1d.num_states_scaled(1.), 1)
        self.assertEqual(finite_well_1d.num_states_scaled(4.5), 3)
        self.assertEqual(finite_well_1d.num_states_scaled(6.0), 4)

    def testEnergyScaled(self):
        self.assertAlmostEqual(finite_well_1d.energy_scaled(1., n=1),
                               1.0925,
                               places=4)
        self.assertAlmostEqual(finite_well_1d.energy_scaled(4.5, n=1),
                               3.2867,
                               places=4)
        self.assertAlmostEqual(finite_well_1d.energy_scaled(4.5, n=2),
                               12.9179,
                               places=4)
        self.assertAlmostEqual(finite_well_1d.energy_scaled(4.5, n=3),
                               27.8821,
                               places=4)
        self.assertAlmostEqual(finite_well_1d.energy_scaled(6., n=1),
                               3.6167,
                               places=4)
        self.assertAlmostEqual(finite_well_1d.energy_scaled(6., n=2),
                               14.3518,
                               places=4)
        self.assertAlmostEqual(finite_well_1d.energy_scaled(6., n=3),
                               31.7736,
                               places=4)
        self.assertAlmostEqual(finite_well_1d.energy_scaled(6., n=4),
                               54.6214,
                               places=4)
    def testEnergy(self):
        self.assertAlmostEqual(finite_well_1d.energy(L=1./2.56158355342,
                                                     m=1, U=1, n=1),
                               0.546246834314,
                               places=4)
        self.assertAlmostEqual(finite_well_1d.energy(L=1e5/2.56158355342,
                                                     m=1, U=1, n=1),
                               0.,
                               places=4)
        self.assertAlmostEqual(finite_well_1d.energy(L=1e-5/2.56158355342,
                                                     m=1, U=1, n=1),
                               1.,
                               places=4)

if __name__ == "__main__":
    unittest.main()