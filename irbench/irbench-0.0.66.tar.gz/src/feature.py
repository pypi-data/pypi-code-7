#!/usr/bin/env python
# coding: utf-8

#########################################################################
#########################################################################

"""
   File Name: feature.py
      Author: Wan Ji
      E-mail: wanji@live.com
  Created on: Fri Mar 14 17:26:08 2014 CST
"""
DESCRIPTION = """
"""

import os
import logging

import numpy as np
import scipy.io as spio
from scipy.sparse import csr_matrix

from utils import loadsvm


class FeatLoader(object):
    """ load feature from dir
    """
    BATCHTEMP = '%s/feat_%d'

    def __init__(self, featpath, featlst=None):
        """ Initialize the loader
        """
        # indices of features to be loaded
        self.featlst = featlst
        # number of features in the processed batches
        self.n_procfeat = 0
        # next batch to be processed
        self.next_batch = 0

        # init the list of batches
        self.pathlst = []
        if os.path.isdir(featpath):
            fnames = os.listdir(featpath)
            fidxs = [int(batf.split("_")[1].split(".")[0]) for batf in fnames]
            self.pathlst = [os.path.sep.join([featpath, fnames[idx]]) for
                            idx in np.array(fidxs).argsort()]
        else:
            self.pathlst.append(featpath)

    @classmethod
    def loadfeat(cls, featpath):
        """ Load feature from file.
        """
        featname = os.path.split(featpath)[1]
        try:
            logging.debug("Load `%s` as NPY - ^^^^^" % featname)
            prel = np.load(featpath)
            # parse as sparse matrix
            if len(prel) == 2:
                feat = csr_matrix((prel[0], prel[1]))
            # parse as dense matrix
            else:
                feat = prel
            logging.debug("Load `%s` as NPY - $$$$$" % featname)
        except IOError as err:
            logging.debug("%s" % err.message)
            logging.debug("Load `%s` as NPY - failed" % featname)
            try:
                logging.debug("Load `%s` as MAT - ^^^^^" % featname)
                feat = spio.loadmat(featpath)['feat']
                logging.debug("Load `%s` as MAT - $$$$$" % featname)
            except ValueError as err:
                logging.debug("%s" % err.message)
                logging.debug("Load `%s` as MAT - failed" % featname)

                logging.debug("Load `%s` as SVM - ^^^^^" % featname)
                feat = loadsvm(featpath)[1]
                logging.debug("Load `%s` as SVM - $$$$$" % featname)
        return feat

    def load_next(self):
        """ Load next batch
        """

        # no more batches
        if self.next_batch >= len(self.pathlst):
            return None, None
        # no more list items
        if self.featlst is not None and self.n_procfeat > self.featlst.max():
            return None, None

        # if batch file not exist, an exception will be raised
        batchpath = self.pathlst[self.next_batch]
        feat = FeatLoader.loadfeat(batchpath)

        self.next_batch += 1

        n_procfeat_next = self.n_procfeat + feat.shape[0]
        # get the list of relative index in current batch
        idxlst = None
        if self.featlst is not None:
            idxlst = [idx for idx in self.featlst if
                      (idx < n_procfeat_next and idx >= self.n_procfeat)]
            feat = feat[[idx - self.n_procfeat for idx in idxlst], :]
        self.n_procfeat = n_procfeat_next
        return feat, idxlst
