'''
Created on May 22, 2014

@author: marscher
'''
import os
import unittest
import subprocess
import numpy as np

from uuid import uuid1
from subprocess import CalledProcessError

class TestMMClusterKmeans(unittest.TestCase):
    """
    basic test, runs mm_cluster with kmeans and checks that k clusters have
    been written to given output file.
    """

    def setUp(self):
        # setup args for mm_cluster
        self.args = ['../mm_cluster','-i','../../ipython/resources/Trypsin_pc12.dat',
                     '-algorithm', 'kmeans']
        self.kmeans_output = str(uuid1())
        self.k = 10
        
    def testClusterKmeans(self):
        name = self.kmeans_output
        kmean_args = ['-k', str(self.k), '-o', name]
        
        # call script
        subprocess.check_call(self.args + kmean_args)
        
        current = np.loadtxt(name)
        self.assertTrue(current.shape[0] == self.k, "not enough cluster centers written out.")
        os.remove(self.kmeans_output)
        
    def testInvalidArgs1(self):
        # negative k
        kmean_args = ['-k', '-1']
        # call script
        self.assertRaises(CalledProcessError, subprocess.check_call, (self.args + kmean_args))
        
        kmean_args[-1] = '0'
        self.assertRaises(CalledProcessError, subprocess.check_call, (self.args + kmean_args))
        
    def testInvalidClustersFile(self):
        kmean_args = ['-k', '10', '-o', os.path.dirname(os.path.abspath(__file__))]
        self.assertRaises(CalledProcessError, subprocess.check_call, (self.args + kmean_args))
        
if __name__ == "__main__":
    unittest.main()