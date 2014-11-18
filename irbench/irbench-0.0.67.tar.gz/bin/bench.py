#!/usr/bin/env python
# coding: utf-8

#########################################################################
#########################################################################

"""
   File Name: bench.py
      Author: Wan Ji
      E-mail: wanji@live.com
  Created on: Sat Mar 15 12:05:21 2014 CST
"""
DESCRIPTION = """
Image Retrieval Benchmark.

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+ NOTE:
+     If -t[--tmpdir] is not specified, -ow[--overwrite] will have no effect.
+     Otherwise, if -ow specified, the temporal files will be overwrited;
+                if -ow not specified, the programm will read from existing
+                temporal files.
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""

import os
import argparse
import logging

import numpy as np
import scipy.io as spio

from irbench import index
from irbench import evaluate
from irbench.utils import runcmd, load_lst_of_lst

IMAGEFILE = 'image.lst'
LABELFILE = 'label.lst'
SIM_FILE = 'similarity.lst'
TMPF_RANKED = 'ranked'
TMPF_LINIDX = 'linidx'
TMPF_RESULT = 'result'
TMPF_DISTANCE = 'distance'


def getargs():
    """ Parse program arguments.
    """

    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     formatter_class=
                                     argparse.ArgumentDefaultsHelpFormatter)

    # database related options
    parser.add_argument('--dbpath', type=str, required=True,
                        help='path of database features')
    parser.add_argument('--dbitems', type=str,
                        help='list of database items')

    # query related
    parser.add_argument('--qrypath', type=str, required=True,
                        help='path of query features')
    parser.add_argument('--qryitems', type=str,
                        help='list of query items')

    # distraction related
    parser.add_argument('--dispath', type=str, nargs='?', default=None,
                        help='path of distracting features')
    parser.add_argument('--disitems', type=str, nargs='?', default=None,
                        help='list of distracting items')

    # measurement
    parser.add_argument('--preck', type=int, nargs='+', default=None,
                        help="precesion@k, should be integers")
    parser.add_argument('--recallk', type=int, nargs='+', default=None,
                        help="recall@k, should be integers")
    parser.add_argument('--ndcgk', type=int, nargs='+', default=None,
                        help="ndcg@k, should be integers")
    parser.add_argument('--map', const=True, action='store_const',
                        default=False, help='overwrite the temporal files')
    parser.add_argument('--dsinfo', type=str, default=None, nargs='?',
                        help="dataset information [including poslst, amblst, simlst]")
    parser.add_argument('--poslst', type=str, default=None, nargs='?',
                        help="positive list")
    parser.add_argument('--amblst', type=str, default=None, nargs='?',
                        help="ambiguity list")
    parser.add_argument('--simlst', type=str, default=None, nargs='?',
                        help="similarity list")
    parser.add_argument('-m', '--metric', type=str, default=None,
                        help='metric file (mat file containing `M`)')

    add_other_options(parser)

    return parser.parse_args()


def add_other_options(parser):
    """
    Add other options to the parser
    """
    # other options
    parser.add_argument('-k', '--topk', type=int, default=20000,
                        help='number of returned results')
    parser.add_argument('-d', '--distance', type=str, default="cosine",
                        help='type distance metric')
    parser.add_argument('-i', '--indexer', type=str, default="linear",
                        help='type of indexer')
    parser.add_argument('-r', '--ranked', type=str, default=None,
                        help="""evaluate on ranked files directly
                             (skip indexing and querying)""")
    parser.add_argument('-t', '--tmpdir', type=str,
                        help='dir for saving temporal files')
    parser.add_argument('-ow', '--overwrite', const=True, action='store_const',
                        default=False, help='overwrite the temporal files')
    parser.add_argument('--log', type=str, nargs="?", default="INFO",
                        help='overwrite the temporal files')

    # skip the first result or not on evaluation
    parser.add_argument(
        '--skip-map', const=True, action='store_const', default=False,
        help='skip the first result for map computation')
    parser.add_argument(
        '--skip-prec', const=True, action='store_const', default=False,
        help='skip the first result for prec computation')
    parser.add_argument(
        '--skip-recall', const=True, action='store_const', default=False,
        help='skip the first result for recall computation')
    parser.add_argument(
        '--skip-ndcg', const=True, action='store_const', default=False,
        help='skip the first result for ndcg computation')


def rankedload(rankedpath):
    """ Load rank from pickle file
    """

    if os.path.isdir(rankedpath):
        ranklst = sorted([int(fname.split(".")[0])
                          for fname in os.listdir(rankedpath)])
        v_rank = []
        for rid in ranklst:
            v_rank.append(spio.loadmat(
                os.path.join(rankedpath, "%d.mat" % rid))['search_index'])
        ranked = np.hstack(tuple(v_rank))
    else:
        ranked = spio.loadmat(rankedpath)['search_index']

    return ranked


def rankeddump(ranked, rankedpath, batchsize=1000):
    """ Dump rank to pickle file
    """
    if ranked.shape[1] > batchsize:
        runcmd("mkdir -p %s" % rankedpath)
        for rid in range(0, ranked.shape[1], batchsize):
            rest = min(ranked.shape[1] - rid, batchsize)
            spio.savemat(os.path.join(rankedpath, "%d.mat" % rid),
                         {'search_index': ranked[:, rid:rid+rest]})
    else:
        spio.savemat(rankedpath, {'search_index': ranked})


def ranking(args):
    """
    Ranking
    """
    logging.info("################################")
    logging.info("# Building indices #############")
    logging.info("################################")
    if args.metric:
        indexer = index.INDEXER_TABLE[args.indexer](
            distype=args.distance,
            metric=index.Indexer.load_metric(args.metric))
    else:
        indexer = index.INDEXER_TABLE[args.indexer](
            distype=args.distance,
            metric=None)
    logging.info("Indexer created.")

    logging.info("Adding database items - ^^^^^")
    dblst = np.loadtxt(args.dbitems, np.int)

    # logging.info("\t********************************")
    # dblst = dblst[:25600]
    # logging.info("\t* WARNING: FOR DEBUG ONLY! *****")
    # logging.info("\t********************************")

    (startnum, nitems) = indexer.add(args.dbpath, dblst)
    logging.info("Adding database items - $$$$$")
    logging.info("\t(%d items added, %d in total)" %
                 (nitems - startnum, nitems))

    # create idmap
    idmap = dblst

    if None != args.dispath:
        logging.info("Adding distracting items - ^^^^^")
        dislst = np.loadtxt(args.disitems, np.int)
        (startnum, nitems) = indexer.add(args.dispath, dislst)
        logging.info("Adding distracting items - $$$$$")
        logging.info("\t(%d items added, %d in total)" %
                     (nitems - startnum, nitems))

        # mapping distracting list to -1
        idmap = np.hstack((idmap, [-1 for i in dislst]))

    indexer.adjust()

    logging.info("################################")
    logging.info("# Querying #####################")
    logging.info("################################")
    logging.info("Querying - ^^^^^")
    qrylst = np.loadtxt(args.qryitems, np.int)
    ranked = indexer.query(args.qrypath, qrylst, args.topk)
    logging.info("Querying - $$$$$")

    """
    Checking whether the query list is included in the database list.
    **  If it is True, the query item itself should be excluded from the
        ranked list.
    """
    b_exclude = True
    if args.dbpath != args.qrypath:
        # query feature and db feature are not the same,
        # no need for excluding query from results
        b_exclude = False
    else:
        for qid in qrylst:
            # query is not included in db,
            # no need for excluding query from results
            if qid not in dblst:
                b_exclude = False
                break

    if False and not b_exclude:
        logging.warning("Excluding queries from results - ^^^^^")
        ex_ranked = np.ndarray((ranked.shape[0], ranked.shape[1] - 1),
                               ranked.dtype)
        for rid in range(ranked.shape[0]):
            ex_ranked[rid, :] = ranked[rid, ranked[rid, :] != qrylst[rid]]
        ranked = ex_ranked
        logging.warning("Excluding queries from results - $$$$$")

    logging.info("Results mapping - ^^^^^")
    ranked = idmap[ranked]
    logging.info("Results mapping - $$$$$")

    # saving retrieval results
    if None != args.tmpdir:
        dumpath = os.path.sep.join([args.tmpdir, TMPF_RANKED])
        logging.info("Dumping to %s - ^^^^^" % dumpath)
        rankeddump(ranked, dumpath)
        logging.info("Dumping to %s - $$$$$" % dumpath)

    return ranked


def evaluating(args, ranked):
    """
    Evaluating
    """
    logging.info("################################")
    logging.info("# Evaluating ###################")
    logging.info("################################")
    logging.info("Evaluating - ^^^^^")

    eval_res = {}
    evaluator = evaluate.Evaluator()

    # simlst = None
    # if args.ndcgk:
    #     logging.info("\tLoading similarity to query - ^^^^^")
    #     (s2qdir, s2qpre) = os.path.split(dataset.Builder.S2Q_LIST)
    #     s2qdir = os.path.sep.join([args.datadir, s2qdir])
    #     s2qpre += '.'
    #     simlst = [{} for qid in range(ranked.shape[0])]
    #     for fname in os.listdir(s2qdir):
    #         # print s2qpre, fname
    #         if (s2qpre in fname) and (fname[-2:] != "_1"):
    #             simval = float(fname.split(s2qpre)[-1])
    #             simpath = os.path.sep.join([s2qdir, fname])
    #             v_lst = load_lst_of_lst(simpath, int)
    #             for qid in range(ranked.shape[0]):
    #                 simlst[qid][simval] = v_lst[qid]
    #     logging.info("\tLoading similarity to query - $$$$$")

    poslst = None
    amblst = None
    if args.map or args.preck or args.recallk:
        logging.info("\tLoading pos/amb list - ^^^^^")
        poslst = load_lst_of_lst(args.poslst, int)
        amblst = load_lst_of_lst(args.amblst, int)
        logging.info("\tLoading pos/amb list - $$$$$")

    if args.ndcgk:
        logging.warning("\tThis function need refinment!")
    #     eval_res['ndcgk'] = evaluator.eval_rank_ndcgk(
    #         ranked, simlst, {'Ks': args.ndcgk})

    if args.map:
        eval_res['map'] = evaluator.eval_rank_map(
            ranked[1:, :] if args.skip_map else ranked,
            poslst, amblst, {})

    if args.preck:
        eval_res['preck'] = evaluator.eval_rank_preck(
            ranked[1:, :] if args.skip_prec else ranked,
            poslst, amblst, {'Ks': args.preck})

    if args.recallk:
        eval_res['recallk'] = evaluator.eval_rank_recallk(
            ranked[1:, :] if args.skip_recall else ranked,
            poslst, amblst, {'Ks': args.recallk})
    logging.info("Evaluating - $$$$$")

    return eval_res


def main(args):
    """ Main entry.
    """
    print args

    # checking temporal directory
    if None != args.tmpdir:
        if os.path.exists(args.tmpdir):
            if args.overwrite:
                logging.warning("Overwrite %s" % args.tmpdir)
            else:
                logging.fatal("%s already exists!" % args.tmpdir)
        runcmd("mkdir -p %s" % args.tmpdir)

    ################################
    # ranking
    ################################
    if None == args.ranked:
        ranked = ranking(args)
    else:
        ranked = rankedload(args.ranked)

    ################################
    # evaluating
    ################################
    eval_res = evaluating(args, ranked)

    ################################
    # generating reports
    ################################
    evaluate.res_print(eval_res)

    # the following code will be removed in future
    try:
        print "++++++++++++++++++++++++++++++++"
        print "!!!!  %f\t%s\t%s" % \
            (eval_res['map'].mean(0),
            '\t'.join(["%f" % x for x in eval_res['preck'].mean(0)]),
            '\t'.join(["%f" % x for x in eval_res['recallk'].mean(0)]))
        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    except:
        pass

    ################################
    # saving evaluation results
    ################################
    if None != args.tmpdir:
        spio.savemat(os.path.sep.join([args.tmpdir, TMPF_RESULT]), eval_res)


if __name__ == '__main__':
    args = getargs()
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log)
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=numeric_level)
    main(args)
