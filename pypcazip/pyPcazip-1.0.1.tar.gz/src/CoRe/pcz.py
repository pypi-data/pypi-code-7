#!/usr/bin/python
'''
The pcz class.
'''
from MDAnalysis.analysis.align import *
import numpy as np
from scipy.linalg import *
import struct
import logging as log
import sys
from time import time
try:
    import h5py
    h5py_available = True
except ImportError:
    h5py_available = False

class Pcz:
    def __init__(self, cofasu, version='PCZ6',target=None, covar=None, quality=90.0,
                 req_evecs=None, rank=-2, preload=False):
        '''
        Initialises a new pcz object with the data from the given
        cofasu object. 'Target' can be a precalculated global average
        structure. 'Covar' can be a precalculated covariance matrix.
        The quality setting defaults to 90%. 'log'
        provides a hook for a python logger instance.
        '''

        self.preloaded = preload
        self.version = version
        self.cofasu = cofasu
        self.quality = quality
        self.natoms = self.cofasu.natoms
        self.nframes = self.cofasu.numframes()

        if ((log is not None) and (rank == 0)):
            log.info('Pcz: {} atoms and {} snapshots'.format(self.natoms, self.nframes))
        if covar is None:
            if ((log is not None) and (rank == 0)):
                log.info('Pcz: least-squares fitting snapshots')
            if target is None:
                self._avg = cofasu.fitted_average()
            else:
                self._avg = target

            if ((log is not None) and (rank == 0)):
                log.info('Pcz: calculating covariance matrix')
            cv = self.cofasu.cov(self._avg, preload=preload)
        else:
            cv = covar

        if ((log is not None) and (rank == 0)):
            log.info('Pcz: diagonalizing covariance matrix')
        time_diag_cov_0 = time()
        w, v = eigh(cv)

        cs = np.cumsum(w[::-1])
        self.totvar = cs[-1]
        tval = cs[-1] * self.quality / 100
        i = 0
        while cs[i] < tval:
            i += 1

        i += 1
        self.nvecs = i
        self._evals = w[-1:-(i + 1):-1]
        self._evecs = v[:, -1:-(i + 1):-1].T
        time_diag_cov_1 = time()
        if ((log is not None) and (rank == 0)):
            log.info(
                'Pcz: Time for diagonalizing covariance matrix: {:.2f} s\n'.format(time_diag_cov_1 - time_diag_cov_0))

        if ((log is not None) and (rank == 0)):
            log.info('Pcz: calculating projections')
        time_proj_calc_0 = time()
        if self.preloaded:
            trj = np.zeros((self.nframes, self.natoms * 3))
            for i in range(self.nframes):
                mob = self.cofasu.coords(i)
                mob -= mob.mean(axis=0)
                R, rms = rotation_matrix(self._avg, mob)
                trj[i, :] = np.dot(mob, R).flatten() - self._avg.flatten()

            self._projs = np.dot(trj, self._evecs.T).T
        time_proj_calc_1 = time()
        if ((log is not None) and (rank == 0)):
            log.info('Pcz: Time for calculating projections: {:.2f} s\n'.format(time_proj_calc_1 - time_proj_calc_0))

    def avg(self):
        """
        Returns the average structure contained in the pcz file
        as an (natoms,3) numpy array.
        """
        return self._avg

    def eval(self, ival):
        """
        Returns an eigenvalue from the file.
        """
        if ival >= self.nvecs:
            print 'Error - only ', self.nvecs, ' eigenvectors present'
            return 0.0
        else:
            return self._evals[ival]

    def evals(self):
        """
        Returns an array of all eigenvalues in the file.
        """
        return self._evals

    def evec(self, ivec):
        """
        Returns a chosen eigenvector from the file in the
        form of a (3*natoms) numpy array.
        """
        if ivec >= self.nvecs:
            print 'Error - only ', self.nvecs, 'eigenvectors present'
            return None
        else:
            return self._evecs[ivec, :]

    def evecs(self):
        """
        Returns all eigenvectors in the file in the form of a
        (nvecs,3*natoms) numpy array.
        """
        return self._evecs

    def proj(self, iproj):
        """
        Returns an array of the projections along a given eigenvector. There
        will be one value per snapshot.
        """
        if iproj >= self.nvecs:
            print 'Error - only ', self.nvecs, 'eigenvectors present'
            return None
        else:
            return self._projs[iproj, :]



    def write(self, filename,  title='Created by pcz.write()'):
        """
        Write out the PCZ file. At the moment only the PCZ4 and PCZ6 formats
        are  implemented.
        """
        if self.version == 'UNKN':
            if h5py_available:
                self.version = 'PCZ7'
            else:
                self.version = 'PCZ6'
                print "WARNING: The PCZ6 format will be used because the h5py module required for PCZ7 is not available. Please install the PCZ7 extra requirements to be able to use it. The command to do this is: pip install pyPcazip[PCZ7]"


        if self.version != 'PCZ4' and self.version != 'PCZ6' and self.version != 'PCZ7':
            raise TypeError('Only PCZ4/6/7 formats supported')

        log.info("Using "+self.version+" format")

        if self.version == 'PCZ4' or self.version == 'PCZ6':
            f = open(filename, 'wb')
            f.write(struct.pack('4s80s3if', self.version, title, self.natoms, self.nframes, self.nvecs, self.totvar))
            f.write(struct.pack('4i', 0, 0, 0, 0))
            for v in self.avg().flatten():
                f.write(struct.pack('f', v))
            for i in range(self.nvecs):
                for v in self.evec(i):
                    f.write(struct.pack('f', v))
                f.write(struct.pack('f', self.eval(i)))

                # All in memory
                if self.preloaded:
                    projection = self.proj(i)

                # loop file (low memory demand)
                else:
                    projection = np.zeros(self.nframes)
                    for t in range(self.nframes):

                        mob = self.cofasu.coords(t)
                        mob -= mob.mean(axis=0)
                        R, rms = rotation_matrix(self._avg, mob)

                        time_step_coords = np.dot(mob, R).flatten() - self._avg.flatten()
                        projection[t] = np.dot(time_step_coords, self._evecs[i].T).T

                if self.version == 'PCZ4':
                    for v in projection:
                        f.write(struct.pack('f', v))
                elif self.version == 'PCZ6':
                    pinc = (projection.max() - projection.min()) / 65534
                    p0 = (projection.max() + projection.min()) / 2
                    f.write(struct.pack('2f', p0, pinc))
                    for v in projection:
                        f.write(struct.pack('h', np.int16((v - p0) / pinc)))

                else:
                    print 'Error - only PCZ4 and PCZ6 formats supported'

            f.close()
            return
        elif self.version == 'PCZ7':
            if not h5py_available:
                print "Error: h5py module not available. Please install the PCZ7 extra requirements to be able to use it. The command to do this is: pip install pyPcazip[PCZ7]"
                sys.exit(0)
            f = h5py.File(filename, "w")
            # Write evecs and evalues
            evec_array = []
            eval_array = []
            for evec_index in xrange(self.nvecs):
                evec_array.append([])
                for v in self.evec(evec_index):
                    evec_array[evec_index].append(v)
                eval_array.append(self.eval(evec_index))
            f.create_dataset("evec_dataset", (self.nvecs, (3 * self.natoms)), dtype='f', data=np.array(evec_array))
            f.create_dataset("eval_dataset", (self.nvecs,), dtype='f', data=np.array(eval_array))
            # Write reference coordinates
            f.create_dataset("ref_coord_dataset", (len(self.avg().flatten()),), dtype='f',
                             data=np.array(self.avg().flatten()))
            # Write properties
            f.attrs['version'] = self.version
            f.attrs['title'] = title
            f.attrs['natoms'] = self.natoms
            f.attrs['nframes'] = self.nframes
            f.attrs['nvecs'] = self.nvecs
            f.attrs['quality'] = self.totvar

            # Loop on every ts
            proj_dataset = f.create_dataset("proj_dataset", (self.nframes, self.nvecs), dtype='i16')
            p0_dataset = f.create_dataset("p0_dataset", (self.nframes,), dtype='f')
            pinc_dataset = f.create_dataset("pinc_dataset", (self.nframes,), dtype='f')



            for ts_index in xrange(self.nframes):
                projection_values = []
                for evec_index in xrange(self.nvecs):
                    # Prepare coords of ts
                    if self.preloaded:
                        projection_values.append(self.proj(evec_index)[ts_index])
                    else:
                        mob = self.cofasu.coords(ts_index)
                        mob -= mob.mean(axis=0)
                        R, rms = rotation_matrix(self._avg, mob)
                        time_step_coords = np.dot(mob, R).flatten() - self._avg.flatten()
                        projection_values.append((np.dot(time_step_coords, self._evecs[evec_index].T).T).item(0))

                # Write coords of ts
                projection_values = np.array(projection_values)
                pinc = (projection_values.max() - projection_values.min()) / 65534
                if pinc == 0:
                    pinc == numpy.nextafter(0, 1)
                p0 = (projection_values.min() + projection_values.max()) / 2
                p0_dataset[ts_index] = p0
                pinc_dataset[ts_index] = pinc
                projection_values = projection_values - p0
                proj_dataset[ts_index] = (projection_values / pinc).astype(np.int16)


        else:
            raise TypeError('Only PCZ4/6/7 formats supported')