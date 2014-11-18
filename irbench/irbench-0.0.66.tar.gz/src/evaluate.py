#!/usr/bin/env python
# coding: utf-8

#########################################################################
#########################################################################

"""
   File Name: evaluation.py
      Author: Wan Ji
      E-mail: wanji@live.com
  Created on: Fri Mar 14 17:38:03 2014 CST
"""
DESCRIPTION = """
"""

import os
import logging
import multiprocessing
import numpy as np

import dataset
from utils import load_lst_of_lst, pinfo


class Evaluator(object):
    """ Evaluator
    """
    def __init__(self, nproc=min(80, multiprocessing.cpu_count())):
        """
        Evaluator
        """
        logging.info("\t++++++++++++++++++++++++++++++++")
        logging.info("\t+ Multiprocessing information  +")
        logging.info("\t+   Pool size: %3d             +" % (nproc))
        logging.info("\t++++++++++++++++++++++++++++++++")

        self.nproc = nproc
        self.pool = multiprocessing.Pool(processes=nproc)

    def __del__(self):
        self.pool.close()
        self.pool.join()

    def eval_rank(self, parlst, procfunc):
        """

        """
        nqrys = len(parlst)
        chunksize = min(max(1, nqrys / self.nproc), 100)

        eval_res = [[] for qid in range(nqrys)]
        logging.info("\t\tEvaluating %s - ^^^^^" % str(procfunc))
        for rid, res in enumerate(self.pool.imap_unordered(procfunc, parlst,
                                                           chunksize)):
            logging.debug("\t\t\t%d/%d" % (rid, nqrys))
            eval_res[res[0]] = res[1]
        logging.info("\t\tEvaluating %s - $$$$$" % str(procfunc))
        return np.array(eval_res)

    def eval_rank_sim2query(self, ranked, simlst, procfunc, params):
        """
        Evaluate ranked results based on similarity to query
        """
        nqrys = ranked.shape[0]
        parlst = zip(range(nqrys), simlst, list(ranked),
                     [params for qid in range(nqrys)])
        return self.eval_rank(parlst, procfunc)

    def eval_rank_posamb(self, ranked, poslst, amblst, procfunc, params):
        """
        Evaluate ranked results based on pos/amb list
        """
        nqrys = ranked.shape[0]
        parlst = zip(range(nqrys), poslst, amblst, list(ranked),
                     [params for qid in range(nqrys)])
        return self.eval_rank(parlst, procfunc)

    def eval_rank_ndcgk(self, ranked, simlst, params):
        """
        Evaluate map
        """
        return self.eval_rank_sim2query(ranked, simlst,
                                        compute_ndcg, params)

    def eval_rank_map(self, ranked, poslst, amblst, params):
        """
        Evaluate map
        """
        return self.eval_rank_posamb(ranked, poslst, amblst,
                                     compute_ap, params)

    def eval_rank_recallk(self, ranked, poslst, amblst, params):
        """
        Evaluate recall@k
        """
        if ranked.shape[0] is 55:
            ranked = ranked[:, 1:]
        return self.eval_rank_posamb(ranked, poslst, amblst,
                                     compute_recallk, params)

    def eval_rank_preck(self, ranked, poslst, amblst, params):
        """
        Evaluate prec@k
        """
        if ranked.shape[0] is 55:
            ranked = ranked[:, 1:]
        return self.eval_rank_posamb(ranked, poslst, amblst,
                                     compute_preck, params)


def compute_ap(v_list):
    """ Compute AP for a single query
    """
    qid = v_list[0]
    poslst = set(v_list[1])
    amblst = set(v_list[2])
    ranklst = v_list[3]
    # pardic = v_list[4]

    avgp = 0.0

    old_recall = 0.0
    old_precision = 1.0

    intersect_size = 0
    posnum = float(len(poslst))
    count = 0.0

    for resid in ranklst:
        if (resid in amblst):
            continue

        count += 1.0

        if (resid in poslst):
            intersect_size += 1

        if (len(poslst) == 0):
            recall = 0
            precision = 1.0
        else:
            recall = intersect_size / posnum
            precision = intersect_size / count

        avgp += (recall - old_recall) *    \
            ((old_precision + precision) / 2.0)

        if recall >= 1.0:
            break

        old_recall = recall
        old_precision = precision
    return (qid, avgp)


def compute_preck(v_list):
    """ Compute precision at K for a single query
    """

    qid = v_list[0]
    poslst = v_list[1]
    # amblst = v_list[2]
    ranklst = v_list[3]
    pardic = v_list[4]

    v_k = pardic['Ks']
    n_k = len(v_k)

    preck = np.ndarray(n_k)
    for i in range(n_k):
        cur_k = v_k[i]
        topk = set(ranklst[:cur_k])
        posnum = float(len(topk.intersection(poslst)))
        # ambnum = len(topk.intersection(amblst))
        # preck[i] = float(posnum) / (cur_k - ambnum)
        preck[i] = posnum / cur_k

    return (qid, preck)


def compute_recallk(v_list):
    """ Compute precision at K for a single query
    """

    qid = v_list[0]
    poslst = v_list[1]
    # amblst = v_list[2]
    ranklst = v_list[3]
    pardic = v_list[4]

    v_k = pardic['Ks']
    n_k = len(v_k)
    n_pos = len(poslst)

    recallk = np.ndarray(n_k)
    for i in range(n_k):
        cur_k = v_k[i]
        topk = set(ranklst[:cur_k])
        posnum = float(len(topk.intersection(poslst)))
        recallk[i] = posnum / n_pos

    return (qid, recallk)


def compute_ndcg(v_list):
    """ Compute precision at K for a single query
    """
    qid = v_list[0]
    s2qlst = v_list[1]
    ranklst = v_list[2]
    v_k = v_list[3]['Ks']

    ndcg_k = np.ndarray(len(v_k))

    max_k = v_k[-1]
    ranklst = ranklst[:max_k]
    rellst = np.zeros(max_k)
    for i in range(max_k):
        for val, lst in s2qlst.iteritems():
            if ranklst[i] in lst:
                rellst[i] = val
                break

    bestlst = []
    for val in sorted(s2qlst.keys(), reverse=True):
        lst = s2qlst[val]
        rest = max_k - len(bestlst)
        if rest <= len(lst):
            bestlst += [val for i in range(rest)]
            break
        bestlst += [val for i in range(len(lst))]
    if len(bestlst) < max_k:
        bestlst += [0 for i in range(max_k - len(bestlst))]
    bestlst = np.array(bestlst)
    # print np.vstack((bestlst, rellst))

    old_k = 0
    old_z = 0
    old_g = 0

    for i in range(len(v_k)):
        cur_k = v_k[i]
        cur_range = np.array(range(old_k, cur_k))
        cur_g = old_g + ((2 ** rellst[cur_range] - 1) /
                         np.log2(cur_range + 2)).sum()
        cur_z = old_z + ((2 ** bestlst[cur_range] - 1) /
                         np.log2(cur_range + 2)).sum()

        ndcg_k[i] = cur_g / cur_z

        old_k = cur_k
        old_z = cur_z
        old_g = cur_g

    return (qid, ndcg_k)


EVALUATORS = {
    'ndcgk':    compute_ndcg,
    'preck':   compute_preck,
    'recallk': compute_recallk,
    'map':     compute_ap}


def res_print(results):
    """
    Printing results
    """
    pinfo("\n\n")
    pinfo("================ Results ================\n")
    for trg, res in results.iteritems():
        pinfo("%s:\n" % trg)
        # print " ".join("%.4f" % x for x in list(np.array(res).mean(0)))
        try:
            pinfo("%s\n" % " ".join("%.4f" % x for x in np.array(res).mean(0)))
        except TypeError as err:
            logging.debug(err.message)
            pinfo("%f\n" % np.array(res).mean(0))
        # print np.array(res)
        pinfo("-----------------------------------------\n")


def eval_rank(ranked, datadir, targets,
              nproc=multiprocessing.cpu_count()):
    """ Evaluate mAP
    """

    eval_posamb = ['map', 'preck', 'recallk']
    eval_s2q = ['ndcgk']
    eval_posamb_hit = []
    eval_s2q_hit = []
    for trg in targets:
        if trg in eval_posamb:
            eval_posamb_hit.append(trg)
        if trg in eval_s2q:
            eval_s2q_hit.append(trg)

    # number of queries
    nqrys = ranked.shape[0]
    # # convert ranked results to list
    # ranklst = list(ranked)
    # evaluation results
    eval_res = {}

    logging.info("\t++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    logging.info("\t+ Multiprocessing information                          +")
    pool_size = min(80, nproc)
    chunksize = min(max(1, nqrys / pool_size), 100)
    logging.info("\t+  Pool size: %3d      Chunk size: %3d                 +" %
                 (pool_size, chunksize))
    logging.info("\t++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    pool = multiprocessing.Pool(processes=pool_size)
    if len(eval_s2q_hit) > 0:
        logging.info("\t################################################")
        logging.info("\t# Evaluating by similarity to queries ##########")
        logging.info("\t################################################")

        # loading similarity to query
        (s2qdir, s2qpre) = os.path.split(dataset.Builder.S2Q_LIST)
        s2qdir = os.path.sep.join([datadir, s2qdir])
        s2qpre += '.'

        simlst = [{} for qid in range(nqrys)]
        for fname in os.listdir(s2qdir):
            # print s2qpre, fname
            if (s2qpre in fname) and (fname[-2:] != "_1"):
                simval = float(fname.split(s2qpre)[-1])
                simpath = os.path.sep.join([s2qdir, fname])
                v_lst = load_lst_of_lst(simpath, int)
                for qid in range(nqrys):
                    simlst[qid][simval] = v_lst[qid]

        for trg in eval_s2q_hit:
            parlst = zip(range(nqrys), simlst, list(ranked),
                         [targets[trg] for qid in range(nqrys)])
            eval_res[trg] = [[] for qid in range(nqrys)]
            logging.info("\t\tEvaluating %s - ^^^^^" % trg)
            for rid, res in enumerate(pool.imap_unordered(EVALUATORS[trg],
                                                          parlst, chunksize)):
                logging.debug("\t\t\t%d/%d" % (rid, nqrys))
                eval_res[trg][res[0]] = res[1]
            # for par in parlst:
            #     res = EVALUATORS[trg](par)
            #     pinfo("\r\t\t\t%d/%d" % (par[0], nqrys))
            #     eval_res[trg][res[0]] = res[1]
            eval_res[trg] = np.array(eval_res[trg])
            logging.info("\t\tEvaluating %s - $$$$$" % trg)

    if len(eval_posamb_hit) > 0:
        logging.info("\t################################################")
        logging.info("\t# Evaluating by positive/ambiguous list ########")
        logging.info("\t################################################")

        pospath = os.path.sep.join([datadir, dataset.Builder.POS_LIST])
        ambpath = os.path.sep.join([datadir, dataset.Builder.AMB_LIST])
        poslst = load_lst_of_lst(pospath, int)
        amblst = load_lst_of_lst(ambpath, int)

        for trg in eval_posamb_hit:
            # if trg in ['preck', 'recallk'] and ranked.shape[0] == 55:
            #     parlst = zip(range(nqrys), poslst, amblst, list(ranked[:, 1:]),
            #                 [targets[trg] for qid in range(nqrys)])
            # else:
            #     parlst = zip(range(nqrys), poslst, amblst, list(ranked),
            #                 [targets[trg] for qid in range(nqrys)])
            parlst = zip(range(nqrys), poslst, amblst, list(ranked),
                         [targets[trg] for qid in range(nqrys)])
            eval_res[trg] = [[] for qid in range(nqrys)]
            logging.info("\t\tEvaluating %s - ^^^^^" % trg)
            for rid, res in enumerate(pool.imap_unordered(EVALUATORS[trg],
                                                          parlst, chunksize)):
                logging.debug("\t\t\t%d/%d" % (rid, nqrys))
                eval_res[trg][res[0]] = res[1]
            # for par in parlst:
            #     res = EVALUATORS[trg](par)
            #     pinfo("\r\t\t\t%d/%d" % (par[0], nqrys))
            #     eval_res[trg][res[0]] = res[1]
            eval_res[trg] = np.array(eval_res[trg])
            logging.info("\t\tEvaluating %s - $$$$$" % trg)

    pool.close()
    pool.join()
    return eval_res
