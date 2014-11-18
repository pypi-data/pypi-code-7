#!/usr/bin/env python
# coding: utf-8

#########################################################################
#########################################################################

"""
   File Name: index.py
      Author: Wan Ji
      E-mail: wanji@live.com
  Created on: Fri Mar 14 17:34:07 2014 CST
"""
DESCRIPTION = """
"""

import logging
import multiprocessing
from itertools import izip
import operator
import array
# import pdb

import numpy as np
import scipy as sp

import scipy.io as spio
from scipy.sparse import csr_matrix
from utils import nsmallest, \
    tic, toc
from distance import distFunc, \
    DotProduct_DML, DotProduct_DML_Diagonal
from feature import FeatLoader
from bitmap import BitMap


class Indexer(object):
    """ Index for retrieval
    """

    def __init__(self, distype, metric=None):
        self.nitems = 0
        self.dim_mask = None
        self.distype = distype
        self.set_metric(metric)

    def __del__(self):
        pass

    @staticmethod
    def load_metric(metric_path):
        """
        Load metric
        """
        try:
            logging.info("Loading metric ... ")
            metric = spio.loadmat(metric_path)['M']
            logging.info("full ")
        except:
            metric = np.loadtxt(metric_path)
            if metric.shape[0] % 1000:
                logging.warning("metric dimension: %d" % metric.shape[0])
            metric[metric < 1e-5] = 0
            logging.info("diagonal ")
            logging.info("metric loaded!")
        return metric

    @staticmethod
    def ordered(num_lst):
        """
        Check if a list is ordered
        """
        arr_lst = np.array(num_lst)
        return (arr_lst[1:] - arr_lst[:-1]).min() > 0

    def set_metric(self, metric):
        """
        Set metric
        """

        # non-metric
        if None == metric:
            self.distfunc = distFunc[self.distype]
            self.metric = None
        # diagnaol metric
        elif metric.ndim == 1:
            self.distfunc = DotProduct_DML_Diagonal
            self.dim_mask = np.arange(metric.shape[0])[metric != 0]
            self.metric = metric[self.dim_mask]
        # dense metric
        elif metric.ndim == 2:
            self.distfunc = DotProduct_DML
            self.metric = metric
        # error
        else:
            raise Exception("BAD METRIC!")

    def add(self, featpath, featlst=None):
        """ Add features to index
        """
        raise Exception("%s.add(%s, %s) is not ready to use!\n" %
                        (self.__class__.__name__,
                         featpath.__name__, featlst.__name__))

    def query(self, featpath, qrylst=None, topk=None):
        """ Query
        """
        raise Exception("%s.query(%s, %s, %s) is not ready to use!\n" %
                        (self.__class__.__name__,
                         featpath.__name__, qrylst.__name__, topk.__name__))

    def adjust(self):
        """
        Adjust the indexer for better performance.
        Can be called at any place.
        """
        raise Exception("%s.adjust() is not ready to use!\n" %
                        (self.__class__.__name__))


def proc_nsmallest(v_par):
    """
    Select n smallest items
    """
    qid = v_par[0]
    dist = v_par[1]
    topk = v_par[2]
    return (qid, nsmallest(topk, dist))


def query_single2(v_par):
    """
    Single query2
    """
    qid = v_par[0]
    query = v_par[1]
    topk = v_par[2]
    indexer = v_par[3]

    featmat = indexer.featmat
    idxs = indexer.idxs
    metric = indexer.metric
    distfunc = indexer.distfunc

    tic(1)
    bmap = BitMap(featmat.shape[0])
    for wid in query.nonzero()[1]:
        for iid in idxs[wid]:
            bmap.set(iid)
    candlst = [iid for iid in range(bmap.size()) if bmap.test(iid)]
    logging.debug("\tTime for gathering list:    %.4fs" % toc(1))

    retk = min(featmat.shape[0], topk)
    ranked = np.ones((1, retk)) * -1
    # return empty results
    if len(candlst) == 0:
        return (qid, ranked)

    logging.debug("number of candidates: %d" % len(candlst))
    tic(2)
    if metric is None:
        distlst = distfunc(featmat[candlst], query)
    else:
        distlst = distfunc(featmat[candlst], metric, query)
    logging.debug("\tTime for gathering dist:    %.4fs" % toc(2))
    distlst = distlst.toarray().reshape(-1)
    logging.debug("\tTime for gathering dist:    %.4fs" % toc(2))

    tic(2)
    dist = np.array(distlst)
    cand = np.array(candlst)
    candtopk = min(dist.shape[0], retk)
    ranked[0, :candtopk] = cand[proc_nsmallest((0, dist, candtopk))[1]]
    if retk > candtopk:
        rand_res = set(range(featmat.shape[0])).difference(
            set(ranked[0, :candtopk]))
        ranked[0, candtopk:retk] = list(rand_res)[:retk-candtopk]

    logging.debug("\tTime for ranking:           %.4fs" % toc(2))

    logging.info("Time for querying:          %.4fs" % toc(1))

    return (qid, ranked)


def query_single3(v_par):
    """
    Single query3
    """
    qid = v_par[0]
    query = v_par[1]
    topk = v_par[2]
    indexer = v_par[3]

    idxs = indexer.idxs
    # metric = indexer.metric
    # distfunc = indexer.distfunc

    retk = min(indexer.nitems, topk)

    """
    Method - 1
    ----------------
    candidates = {}
    for (wid, wval) in izip(query.nonzero()[1], query.data):
        for (iid, val) in izip(idxs[wid][0], idxs[wid][1]):
            candidates[iid] = candidates.get(iid, 0) + \
                indexer.dist_core(wval, val)

    candtopk = min(len(candidates), retk)

    ranked = np.ones((1, retk)) * -1
    candidates = sorted(candidates.iteritems(), key=operator.itemgetter(1))
    ranked[0, :candtopk] = [item[0] for item in candidates]
    """

    """
    Method - 2
    ----------------
    """
    dist = np.zeros(indexer.nitems, np.float)
    for (wid, wval) in izip(query.nonzero()[1], query.data):
        dist[idxs[wid][0]] += indexer.dist_core(wval, idxs[wid][1])
    ranked = nsmallest(retk, dist)

    return (qid, np.array(ranked).reshape(1, -1))


class Linear(Indexer):
    """ Linear scan
    """

    def __init__(self, distype='cosine', metric=None,
                 nproc=multiprocessing.cpu_count()):
        Indexer.__init__(self, distype, metric)
        self.featmat = None
        self.b_sparse = None
        self.pool = multiprocessing.Pool(processes=min(40, nproc))

    def __del__(self):
        """
        """
        self.pool.close()
        self.pool.join()
        Indexer.__del__(self)

    def add(self, featpath, featlst=None):
        """ Add features to index
        """
        if featlst is not None and not Indexer.ordered(featlst):
            logging.error("`featlst` is not ordered!")

        startnum = self.nitems

        loader = FeatLoader(featpath, featlst)
        logging.info("Loading first batch - ^^^^^")
        feat = loader.load_next()[0]
        self.b_sparse = 'todense' in dir(feat)
        logging.info("Loading first batch - $$$$$")

        logging.info("Initializing `featmat` - ^^^^^")
        if self.b_sparse:
            v_data = []
            v_i = []
            v_j = []
            logging.info("Initializing `featmat` - $$$$$ (sparse)")
        else:
            featmat = np.ndarray((len(featlst), feat.shape[1]), feat.dtype)
            logging.info("Initializing `featmat` - $$$$$ (dense)")

        logging.info("Loading batches - ^^^^^")
        nextpos = 0
        while feat is not None:
            if self.b_sparse:
                if self.dim_mask is not None:
                    logging.warning("Detect sparse feature with metric, ")
                    logging.warning("Reducing dimension: %d -> %d - ^^^^^" %
                                    (feat.shape[1], sum(self.dim_mask)))
                    feat = feat[:, self.dim_mask]
                    logging.warning("Reducing dimension: %d -> %d - $$$$$" %
                                    (feat.shape[1], sum(self.dim_mask)))
                v_data.append(feat.data)
                v_i.append(feat.nonzero()[0] + nextpos)
                v_j.append(feat.nonzero()[1])
            else:
                featmat[nextpos:nextpos + feat.shape[0]] = feat
            nextpos += feat.shape[0]
            feat = loader.load_next()[0]
        logging.info("Loading batches - $$$$$")

        self.nitems += nextpos

        if self.b_sparse:
            featmat = csr_matrix((np.hstack(v_data),
                                  (np.hstack(v_i), np.hstack(v_j))))
            logging.debug("sparse number: %d" % featmat.shape[0])

        if None == self.featmat:
            self.featmat = featmat
        else:
            self.featmat = np.vstack((self.featmat, featmat)) if not self.b_sparse \
                else sp.sparse.vstack((self.featmat, featmat), "csr")

        return (startnum, self.nitems)

    def get_dim(self):
        """ Get dimension of feature
        """
        return self.featmat.shape[1]

    def query_batch(self, query, topk):
        """ Query by batch
        """

        tic()
        if None == self.metric:
            dist = self.distfunc(self.featmat, query)
        else:
            dist = self.distfunc(self.featmat, self.metric, query)
        logging.debug("%s, %s, %.4f" %
                      (str(query.shape), str(self.featmat.shape), toc()))
        logging.debug("METRIC: %s" % str(self.metric))
        logging.debug("Time for computing dists: %.4fs" % toc())

        if self.b_sparse:
            dist = dist.toarray()

        if topk <= dist.shape[1]:
            # return dist.argsort(1)[:, :topk]

            ################################################################
            # The code bellow supposed to be faster than the above one,    #
            # but actually the numpy implementation is faster!!!           #
            ################################################################
            # ranked = dist.argsort(1)[:, :topk]
            # for i in range(ranked.shape[0]):
            #     print dist[i, ranked[i, :5]]
            # return ranked
            nqrys = dist.shape[0]
            ranked = np.ndarray((nqrys, topk), np.int64)
            parlst = [(qid, dist[qid, :], topk) for qid in range(nqrys)]
            for rid, res in enumerate(self.pool.imap_unordered(proc_nsmallest,
                                                               parlst, 10)):
                logging.debug("\t\t%d/%d" % (rid, nqrys))
                ranked[res[0]] = res[1]
            return ranked
        else:
            ranked = dist.argsort(1)
            # for i in range(ranked.shape[0]):
            #     print dist[i, ranked[i, :5]]
            return ranked

    def query(self, featpath, qrylst=None, topk=None):
        """ Query
        """
        if qrylst is not None and not Indexer.ordered(qrylst):
            logging.warning("`qrylst` is not ordered!")

        topk = min(topk, self.nitems) if topk else self.featmat.shape[0]

        ranked = np.ndarray((len(qrylst), topk), np.int64)

        """
        Important notes!!!
            if the qrylst is not ordered and the queries are loaded from
            multiple files, we need to reorder the ranked list in terms
            of queries
        """
        # how many files are the queries load from
        filenum = 0
        ranklst = []

        loader = FeatLoader(featpath, qrylst)
        q_start = 0
        query, idxlst = loader.load_next()
        while query is not None:
            if query.shape[0] == 0:
                query, idxlst = loader.load_next()
                continue

            filenum += 1
            ranklst += idxlst

            if self.dim_mask is not None:
                logging.warning("Detect sparse query feature with metric!")
                logging.warning("Reducing dimension: %d -> %d - ^^^^^" %
                                (query.shape[1], sum(self.dim_mask)))
                query = query[:, self.dim_mask]
                logging.warning("Reducing dimension: %d -> %d - $$$$$" %
                                (query.shape[1], sum(self.dim_mask)))

            q_end = q_start + query.shape[0]

            qrybatch = 1000
            for i in range(q_start, q_end, qrybatch):
                i_end = min(i + qrybatch, q_end)
                tic()
                ranked[i:i_end, :] = self.query_batch(
                    query[i - q_start:i_end - q_start, :], topk)
                logging.info("\t%d~%d / %d, Time: %.4f" %
                             (i, i_end - 1, q_end, toc()))
            q_start = q_end

            query, idxlst = loader.load_next()

        # re-ordering the ranked list in terms of queries
        if not Indexer.ordered(qrylst) and filenum > 0:
            qrylst = qrylst.tolist()
            tmp_ranked = ranked
            ranked = np.ndarray((len(qrylst), topk), np.int64)
            for i in range(len(qrylst)):
                ranked[qrylst.index(ranklst[i]), :] = tmp_ranked[i, :]

        return ranked

    def adjust(self):
        """
        Adjust the indexer for better performance.
        Can be called at any place.
        """
        logging.debug("No additional process required for Indexer(%s)." %
                      self.__class__.__name__)


class Inverted(Linear):
    """ Inverted Index
    """

    @staticmethod
    def dotproduct_core(x, y):
        return - x * y

    @staticmethod
    def euclidean_core(x, y):
        return (x - y) ** 2

    def __init__(self, distype='cosine', metric=None,
                 nproc=multiprocessing.cpu_count()):
        Linear.__init__(self, distype, metric, nproc)
        logging.warning("Only sparse BoW is supported by %s currently" %
                        self.__class__.__name__)

        self.IDX_ARR_TYPE = 'I'
        self.VAL_ARR_TYPE = 'f'

        self.IDX_ARR2NPY = {
            'I': {4: np.uint32, 8: np.uint64},
            'L': {4: np.uint32, 8: np.uint64}}
        self.VAL_ARR2NPY = {'f': np.single, 'd': np.double}

        self.IDX_NPY_TYPE = self.IDX_ARR2NPY[self.IDX_ARR_TYPE][
            array.array(self.IDX_ARR_TYPE).itemsize]
        self.VAL_NPY_TYPE = self.VAL_ARR2NPY[self.VAL_ARR_TYPE]

        self.idxs = []
        self.featdim = None
        self.adjust = self.adjust0
        self.query_single = query_single3

        if distype == "dotproduct":
            self.dist_core = Inverted.dotproduct_core
        elif distype == "euclidean":
            self.dist_core = Inverted.euclidean_core
        else:
            raise Exception("Unsupported distance type for inverted index: %s"
                            % distype)

    def __del__(self):
        Linear.__del__(self)

    def add(self, featpath, featlst=None, featdim=None):
        """ Add features to index
        """
        if featlst is not None and not Indexer.ordered(featlst):
            logging.error("`featlst` is not ordered!")

        startnum = self.nitems

        loader = FeatLoader(featpath, featlst)

        logging.info("Loading first batch - ^^^^^")

        feat = loader.load_next()[0]
        b_sparse = 'todense' in dir(feat)
        featdim = featdim if featdim else feat.shape[1]

        if self.b_sparse is None:
            self.b_sparse = b_sparse
        elif self.b_sparse != b_sparse:
            raise Exception("Sparsity of features is not consistent!")

        if self.featdim is None:
            self.featdim = featdim
        elif self.b_sparse:
            self.featdim = max(self.featdim, featdim)
        elif self.featdim != featdim:
            raise Exception("Dimension of dense features is not consistent!")

        logging.info("Loading first batch - $$$$$")

        logging.info("Initializing `featmat` - ^^^^^")
        if self.b_sparse:
            rest = self.featdim - len(self.idxs)
            if rest > 0:
                self.idxs += [[array.array(self.IDX_ARR_TYPE),
                               array.array(self.VAL_ARR_TYPE)]
                              for wid in xrange(rest)]

            logging.info("Initializing `featmat` - $$$$$ (sparse)")
        else:
            featmat = np.ndarray((len(featlst), feat.shape[1]), feat.dtype)
            logging.info("Initializing `featmat` - $$$$$ (dense)")

        logging.info("Loading batches - ^^^^^")
        nextpos = 0
        time_cost = 0
        while feat is not None:
            tic()
            if self.b_sparse:
                if self.dim_mask is not None:
                    logging.warning("Detect sparse feature with metric, ")
                    logging.warning("Reducing dimension: %d -> %d - ^^^^^" %
                                    (feat.shape[1], sum(self.dim_mask)))
                    feat = feat[:, self.dim_mask]
                    logging.warning("Reducing dimension: %d -> %d - $$$$$" %
                                    (feat.shape[1], sum(self.dim_mask)))

                rids, cids = feat.nonzero()
                for (rid, cid, val) in izip(rids, cids, feat.data):
                    self.idxs[cid][0].append(rid)
                    self.idxs[cid][1].append(val)
            else:
                featmat[nextpos:nextpos + feat.shape[0]] = feat
            time_cost += toc()
            nextpos += feat.shape[0]
            feat = loader.load_next()[0]
        logging.info("Loading batches - $$$$$")
        logging.info("Time for indexing: %.4fs" % time_cost)

        self.nitems += nextpos

        if not self.b_sparse:
            if self.featmat is None:
                self.featmat = featmat
            else:
                self.featmat = np.vstack((self.featmat, featmat))

        return (startnum, self.nitems)

    def adjust2(self):
        logging.info("Adjusting index - ^^^^^")
        tic()
        self.idxs = [set() for wid in range(self.featmat.shape[1])]
        rids, cids = self.featmat.nonzero()
        logging.debug("\tpreparing done: %.4fs" % toc())
        for (rid, cid) in izip(rids, cids):
            self.idxs[cid].add(rid)
        logging.info("Adjusting index - $$$$$ (Time costs: %.4fs)!" % toc())

    def adjust3(self):
        logging.info("Adjusting index - ^^^^^")
        tic()
        self.idxs = [dict() for wid in range(self.featmat.shape[1])]
        rids, cids = self.featmat.nonzero()
        logging.debug("\tpreparing done: %.4fs" % toc())
        for (rid, cid, val) in izip(rids, cids, self.featmat.data):
            self.idxs[cid][rid] = val
        logging.info("Adjusting index - $$$$$ (Time costs: %.4fs)!" % toc())

    def adjust0(self):
        logging.info("Adjusting index - ^^^^^")
        tic()
        for i in xrange(len(self.idxs)):
            if len(self.idxs[i][0]) == 0:
                self.idxs[i] = (np.ndarray(0, self.IDX_NPY_TYPE),
                                np.ndarray(0, self.VAL_NPY_TYPE))
            else:
                self.idxs[i] = (np.frombuffer(self.idxs[i][0], self.IDX_NPY_TYPE),
                                np.frombuffer(self.idxs[i][1], self.VAL_NPY_TYPE))
        logging.info("Adjusting index - $$$$$ (Time costs: %.4fs)!" % toc())

    def query_batch(self, query, topk):
        nqrys = query.shape[0]
        dbsize = self.nitems
        topk = min(dbsize, topk)
        ranked = np.ndarray((nqrys, topk), np.int64)

        logging.info("Preparing parlst - ^^^^^")
        # shared_data_base = np.ctypeslib.as_ctypes(self.featmat.data)
        # shared_nz_i_base = np.ctypeslib.as_ctypes(self.featmat.nonzero()[0])
        # shared_nz_j_base = np.ctypeslib.as_ctypes(self.featmat.nonzero()[1])
        parlst = [(qid, query[qid], topk, self) for qid in range(nqrys)]
        logging.info("Preparing parlst - $$$$$")

        logging.info("Querying - ^^^^^")
        # for rid, res in enumerate(self.pool.imap_unordered(self.query_single,
        #                                                    parlst)):
        #     pinfo("\r\t\t\t%d/%d" % (rid, nqrys))
        #     ranked[res[0], :] = res[1]

        for qid in range(nqrys):
            tic(1)
            ranked[qid, :] = self.query_single(parlst[qid])[1]
            logging.info("Time: %.4fs" % toc(1))
        logging.info("Querying - $$$$$")
        return ranked


INDEXER_TABLE = {
    'linear':   Linear,
    'inverted': Inverted,
    'default':  Indexer}
