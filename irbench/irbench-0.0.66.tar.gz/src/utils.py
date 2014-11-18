#!/usr/bin/env python
# coding: utf-8

#########################################################################
#########################################################################

"""
   File Name: utils.py
      Author: Wan Ji
      E-mail: wanji@live.com
  Created on: Mon Jan 13 12:50:05 2014 CST
 Description:
"""

import os
import sys
import pickle
import bottleneck
import time
import logging

import numpy as np

from scipy.sparse.csr import csr_matrix

# default timer id is 0
TIME_TIC = {0: 0}


def tic(timer_id=0):
    """
    tic
    """
    global TIME_TIC
    TIME_TIC[timer_id] = time.time()


def toc(timer_id=0):
    """
    toc
    """
    return time.time() - TIME_TIC[timer_id]


def perr(msg):
    """ Print error message.
    """

    sys.stderr.write("%s" % msg)
    sys.stderr.flush()


def pinfo(msg):
    """ Print information message.
    """

    sys.stdout.write("%s" % msg)
    sys.stdout.flush()


def runcmd(cmd):
    """ Run command.
    """

    logging.debug("%s" % cmd)
    os.system(cmd)


def loadlist(lstpath, dtype=str):
    """ load text list
    """
    with open(lstpath) as lstfile:
        # return [[dtype(item) for item in line.strip()] for line in lstfile];
        return [dtype(line.strip()) for line in lstfile]


def load_lst_of_lst(lstpath, dtype=str):
    """ load list of list from file
    """
    lstoflst = []
    with open(lstpath) as lstfile:
        for line in lstfile:
            lstoflst.append([dtype(item) for item in line.split()])
    return lstoflst


def save_lst_of_lst(lstpath, lstoflst):
    """ save list of list to file
    """
    with open(lstpath, "w") as lstfile:
        for lst in lstoflst:
            lstfile.write(" ".join([str(item) for item in lst]) + "\n")


def save_lst_of_lst_plus(lstpath, lstoflst, shift=1):
    """ save list of list to file with shift
    this is for MATLAB in which index starts from 1
    """
    with open(lstpath, "w") as lstfile:
        for lst in lstoflst:
            lstfile.write(" ".join([str(item+shift) for item in lst]) + "\n")


def loadsvm(svmpath):
    """ Load data in SVM format into sparse matrix.
    """
    with open(svmpath) as svmf:
        cases = [line.split() for line in svmf]

    rows = len(cases)
    labels = np.zeros(rows, dtype=int)
    rids = []
    cids = []
    vals = []
    for i in range(rows):
        labels[i] = int(cases[i][0])
        cases[i] = [case.split(":") for case in cases[i][1:]]
        rids += [i for case in cases[i]]
        cids += [int(case[0]) for case in cases[i]]
        vals += [float(case[1]) for case in cases[i]]

    data = np.array(vals)
    ij = np.array([rids, cids])
    return (labels, csr_matrix((data, ij)))


def loadnpy(npypath):
    """ Load (label, feat) in NPY format.
    """
    with open(npypath, 'rb') as npyf:
        label = np.load(npyf)
        feat = np.load(npyf)
    return (label, feat)


def savenpy(label, feat, npypath):
    """ Save (label, feat) in NPY format.
    """
    with open(npypath, 'wb') as npyf:
        np.save(npyf, label)
        np.save(npyf, feat)


def loadmat(matpath):
    """ Load mat from file (txt format)
    """
    with open(matpath) as matf:
        [nrows, ncols] = [int(x) for x in matf.readline().split()]
        mat = np.empty((nrows, ncols))
        for i in range(nrows):
            mat[i, :] = np.array([float(x) for x in matf.readline().split()])
    return mat


def savemat(mat, matpath):
    """ Load mat from file (txt format)
    """
    with open(matpath, "w") as matf:
        matf.write("%d\t%d\n" % (mat.shape[0], mat.shape[1]))
        for i in range(mat.shape[0]):
            matf.write("%s\n" %
                       " ".join([str(x)
                                 for x in mat[i, :].reshape(-1).tolist()[0]]))


def pklload(pklpath):
    """ Load object from pickle file
    """
    with open(pklpath, 'rb') as pklf:
        return pickle.load(pklf)


def pkldump(obj, pklpath):
    """ Dump object to pickle file
    """
    with open(pklpath, 'wb') as pklf:
        return pickle.dump(obj, pklf)


def nsmallest(num, iterable):
    """ Get indices of the `num` smallest items in `iterable`
    """
    idxs = bottleneck.argpartsort(iterable, num)[:num]
    return idxs[iterable[idxs].argsort()]


# def compute_ap(ids, label):
#     """ Compute AP
#     """
#     old_recall    = 0.0;
#     old_precision = 1.0;
#     ap = 0.0;
#
#     vr = [old_recall]
#     vp = [old_precision]
#
#     intersect_size = 0.0;
#     posnum = float((ids == label).sum())
#
#     for i in range(ids.shape[0]):
#         if ids[i] == label:
#             intersect_size += 1.0
#
#             recall    = intersect_size / posnum
#             precision = intersect_size / (i+1)
#             vr.append(recall)
#             vp.append(precision)
#
#             ap += 0.5 * (recall - old_recall) * (old_precision + precision);
#
#             old_recall = recall;
#             old_precision = precision;
#             if intersect_size == posnum:
#                 break
#
#     return (ap, np.array(vr), np.array(vp));
#
# def compute_topk(ids, label, K):
#     """ Compute top-k
#     """
#     hitnum = 0.0
#     posnum = float((ids == label).sum())
#
#     precision = np.zeros(K)
#     recall    = np.zeros(K)
#     for i in range(K):
#         if ids[i] == label:
#             hitnum += 1.0
#         precision[i] = hitnum / (i+1)
#         recall[i]    = hitnum / posnum
#
#     return (precision, recall);


"""
Calculating difference vector
"""


def eucdiff(veca, vecb):
    """ Calculating difference for Euclidean distance
    """
    diff = veca - vecb
    # return similarity
    return -diff.multiply(diff)


def dotdiff(veca, vecb):
    """ Calculating difference for DOT similarity
    """
    return veca.multiply(vecb)
