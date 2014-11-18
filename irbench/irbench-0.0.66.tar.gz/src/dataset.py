#!/usr/bin/env python
# coding: utf-8

################################################################
# Dataset Builder ##############################################
################################################################

"""
   File Name: dataset.py
      Author: Wan Ji
      E-mail: wanji@live.com
  Created on: Sun Mar 16 12:03:09 2014 CST
"""
DESCRIPTION = """
"""

import random
from utils import *
from google.protobuf import text_format
import cPickle as pickle
import json


class Dataset(object):
    """ This class holds the information of a dataset.

    Layout of dataset: refer the `validate` function
    """

    def __init__(self, name=None, desc=None, images=None, labels=None,
                 dblst=None, qrylst=None, v_simlst=None,
                 trlst=None, valst=None):
        # name of dataset
        self.name = name
        # description to this dataset
        self.desc = desc
        # list of image paths
        self.images = images
        # list of image labels
        self.labels = labels

        # list of database images
        self.dblst = dblst
        # list of query images
        self.qrylst = qrylst
        # list of similairties [required if labels is not specified]
        self.v_simlst = v_simlst

        # (optional) list of training images for DML methods
        self.trlst = trlst
        # (optional) list of validation images for DML methods
        self.valst = valst

    @staticmethod
    def is_list_of(elem_list, elem_type):
        """
        Check if `elem_list` is a list of `elem_type`.
        """
        if type(elem_list) is not list:
            return False

        for elem in elem_list:
            if type(elem) is not elem_type:
                return False
        return True


    def validate(self):
        """
        Validate each fields
        """

        msg = "`name` and `desc` should be `str`"
        if type(self.name) is not str or type(self.desc) is not str:
            raise Exception(msg)

        msg = "`images` should be a list of `str`"
        if not Dataset.is_list_of(self.images, str):
            raise Exception(msg)

        msg = "`labels` should be a list of int"
        if not Dataset.is_list_of(self.labels, int):
            raise Exception(msg)

        msg = "`dblst` should be a list of int"
        if not Dataset.is_list_of(self.dblst, int):
            raise Exception(msg)

        msg = "`qrylst` should be a list of int"
        if not Dataset.is_list_of(self.qrylst, int):
            raise Exception(msg)

        msg = "`v_simlst` should be `dict`"
        msg_key = "`key` in v_simlst should be `float`"
        msg_val = "`val` in v_simlst should be a list of `int`"
        if type(self.v_simlst) is not dict:
            raise Exception(msg)
        for key, val in self.v_simlst.iteritems():
            if type(key) is not float:
                raise Exception(msg_key)
            if Dataset.is_list_of(val, int):
                raise Exception(msg_val)

        msg = "`trlst` should be a list of int"
        if self.trlst and not Dataset.is_list_of(self.trlst, int):
            raise Exception(msg)

        msg = "`valst` should be a list of int"
        if self.valst and not Dataset.is_list_of(self.valst, int):
            raise Exception(msg)


class Builder(object):
    """ Dataset builder
    """

    # basic info
    IMAGE_LIST = 'image.lst'
    LABEL_LIST = 'label.lst'
    IMAGE_DATA = 'image.dat'
    IMAGE_DIR = 'image_dir'

    # search related
    DB_IMG_LIST = 'search/db.lst'
    QRY_IMG_LIST = 'search/query.lst'
    S2Q_LIST = 'search/sim2qry.lst'
    POS_LIST = 'search/pos.lst'
    AMB_LIST = 'search/amb.lst'
    TRAIN_LIST = 'search/train.lst'
    VAL_LIST = 'search/val.lst'

    def __init__(self):
        # protobuf
        self.ds = Dataset()

        # path or name of images
        self.imglst = None
        # label of images
        self.lbslst = None
        # images in database
        self.dblst = None
        # images used as queries
        self.qrylst = None
        # similarity of database images to queries
        self.s2qlst = None
        # image similar to queries
        self.poslst = None
        # image ambiguous to queries
        self.amblst = None
        # images for training
        self.trainlst = None
        # images for training
        self.val_lst = None

        # print the doc string, which includes the PRE-REQURIES of
        # the source dir
        print self.__doc__

    def __def__(self):
        pass

    @classmethod
    def set_parser(cls, parser):
        """ Setup the command line parser
        """
        parser.add_argument('trg_dir', type=str,
                            help='target dir of dataset')

    @classmethod
    def get_name(cls, filepath):
        """ Get name of the file, excluding folder and extension
        """
        return ".".join(os.path.split(filepath)[1].split('.')[:-1])

    def generate(self, trgdir):
        """ Generate the dataset related files.
        """

        pinfo("Generating dataset files ")
        # create target dir
        os.system("mkdir -p %s/search" % trgdir)

        # store image list
        if None != self.imglst:
            np.savetxt(os.sep.join([trgdir, Builder.IMAGE_LIST]),
                       self.imglst, '%s')
            pinfo(".")
        if None != self.lbslst:
            np.savetxt(os.sep.join([trgdir, Builder.LABEL_LIST]),
                       self.lbslst, '%s')
            pinfo(".")
        if None != self.dblst:
            np.savetxt(os.sep.join([trgdir, Builder.DB_IMG_LIST]),
                       self.dblst, '%s')
            np.savetxt(os.sep.join([trgdir, Builder.DB_IMG_LIST+"_1"]),
                       [iid+1 for iid in self.dblst], '%s')
            pinfo(".")
        if None != self.qrylst:
            np.savetxt(os.sep.join([trgdir, Builder.QRY_IMG_LIST]),
                       self.qrylst, '%s')
            np.savetxt(os.sep.join([trgdir, Builder.QRY_IMG_LIST+"_1"]),
                       [iid+1 for iid in self.qrylst], '%s')
            pinfo(".")
        if None != self.trainlst:
            np.savetxt(os.sep.join([trgdir, Builder.TRAIN_LIST]),
                       self.trainlst, '%s')
            np.savetxt(os.sep.join([trgdir, Builder.TRAIN_LIST+"_1"]),
                       [iid+1 for iid in self.trainlst], '%s')
            pinfo(".")
        if None != self.val_lst:
            np.savetxt(os.sep.join([trgdir, Builder.VAL_LIST]),
                       self.val_lst, '%s')
            np.savetxt(os.sep.join([trgdir, Builder.VAL_LIST+"_1"]),
                       [iid+1 for iid in self.val_lst], '%s')
            pinfo(".")
        if None != self.s2qlst:
            for val, lsts in self.s2qlst.iteritems():
                save_lst_of_lst(os.sep.join([trgdir, Builder.S2Q_LIST +
                                             ".%.2f" % val]), lsts)
                save_lst_of_lst_plus(os.sep.join([trgdir, Builder.S2Q_LIST +
                                                  ".%.2f_1" % val]), lsts)
            pinfo(".")
        if None != self.poslst:
            save_lst_of_lst(os.sep.join([trgdir, Builder.POS_LIST]),
                            self.poslst)
            save_lst_of_lst_plus(os.sep.join([trgdir, Builder.POS_LIST+"_1"]),
                                 self.poslst)
            pinfo(".")
        if None != self.amblst:
            save_lst_of_lst(os.sep.join([trgdir, Builder.AMB_LIST]),
                            self.amblst)
            save_lst_of_lst_plus(os.sep.join([trgdir, Builder.AMB_LIST+"_1"]),
                                 self.amblst)
            pinfo(".")
        pinfo(" Done!\n")

    def save(self, path):
        """
        Save the dataset to pkl file.
        """
        self.ds.name = "name"
        self.ds.desc = "desc"
        self.ds.images = list(self.imglst)
        self.ds.labels = [int(lbl) for lbl in self.lbslst]

        self.ds.dblst = [int(iid) for iid in self.dblst]
        self.ds.qrylst = [int(iid) for iid in self.qrylst]
        self.ds.v_simlst = self.s2qlst

        self.ds.trlst = [int(iid) for iid in self.trainlst]
        self.ds.valst = [int(iid) for iid in self.val_lst]

        self.ds.validate()
        with open(path, 'wb') as pklf:
            pickle.dump(self.ds, pklf)

    def load(self, path):
        """
        Load the dataset from pkl file.
        """
        with open(path, 'rb') as pklf:
            self.ds = pickle.load(pklf)
        self.ds.validate()

    def savetxt(self, path):
        """
        Save the dataset to text file.
        """
        raise Exception("Not implemented yet!")
        self.ds.validate()

    def loadtxt(self, path):
        """
        Load the dataset from text file.
        """
        raise Exception("Not implemented yet!")
        self.ds.validate()


class VGGBuilder(Builder):
    """ VGG dataset builder.
    This is the base class for `Oxford` and `Paris`.
    """
    def __init__(self, args):
        Builder.__init__(self)

        pinfo("Loading image list ... ")
        self.imglst = []
        # convert the image path into relative path to the target dir
        for dpath, _, files in os.walk(args.img_dir):
            for fpath in files:
                self.imglst.append(os.path.relpath(os.path.join(dpath, fpath),
                                                   args.trg_dir))
        self.imglst = sorted(self.imglst)
        imnames = [Builder.get_name(path) for path in self.imglst]
        self.lbslst = np.zeros(len(self.imglst), np.int)
        pinfo("Done!\n")

        self.qrylst = []
        self.poslst = []
        self.amblst = []
        self.s2qlst = {args.good: [], args.ok: [], args.junk: []}
        self.trainlst = []
        self.val_lst = []

        clsnum = len(self.ALL_LANDMARKS)
        # class id start from 1, 0 denotes background images
        for (cls_id, landmark) in zip(range(1, clsnum + 1),
                                     self.ALL_LANDMARKS):
            pinfo("\t%s\n" % landmark)
            for i in range(5):
                gtf = "%s_%d" % (landmark, i+1)

                # get query Id
                qname = np.loadtxt("%s/%s_query.txt" % (args.gt_dir, gtf), dtype=np.str).\
                    tolist()[0].replace('oxc1_', '')
                qid = imnames.index(qname)
                self.qrylst.append(qid)

                # get good results
                good_names = loadlist("%s/%s_good.txt" % (args.gt_dir, gtf))
                good_ids = [imnames.index(x) for x in good_names]
                self.s2qlst[args.good].append(good_ids)

                # get ok results
                ok_names = loadlist("%s/%s_ok.txt" % (args.gt_dir, gtf))
                ok_ids = [imnames.index(x) for x in ok_names]
                self.s2qlst[args.ok].append(ok_ids)

                # get junk results
                junk_names = loadlist("%s/%s_junk.txt" % (args.gt_dir, gtf))
                junk_ids = [imnames.index(x) for x in junk_names]
                self.s2qlst[args.junk].append(junk_ids)

                cur_poslst = np.array(ok_ids + good_ids)
                # DONOT exclude query from the positive list
                # cur_poslst = cur_poslst[cur_poslst != qid]
                self.poslst.append(list(cur_poslst))
                self.amblst.append(junk_ids)

            # set labels
            self.lbslst[self.poslst[-1]] = cls_id

        # set db list
        self.dblst = np.array(range(len(self.imglst)))

        self.trainlst = list(set(range(len(self.imglst))).difference(set(self.qrylst)))

        # self.trainlst = []
        # for classid in range(len(self.ALL_LANDMARKS)):
        #     # select images with the same IDs, BUT NOT IN THE QUERY LIST
        #     candidates = [iid for iid in self.dblst[self.lbslst == (classid + 1)]
        #                   if iid not in self.qrylst]
        #     random.shuffle(candidates)
        #     self.trainlst += candidates[:args.selpos]

        # candidates = list(self.dblst[self.lbslst == 0])
        # random.shuffle(candidates)
        # self.trainlst += candidates[:args.selneg]

        pinfo("\n")

    def init_M(self):
        """
        init for metric learning
        """
        all_classes = ['background'] + cls.ALL_LANDMARKS

        pinfo("Preparing for metric learning ... ")
        self.trainlst = []
        qry_lbs = self.lbslst[self.qrylst]
        qry_mask = np.zeros(len(self.qrylst))
        for sel_landmark in cls.SEL_LANDMARKS:
            classid = all_classes.index(sel_landmark)
            qry_mask[qry_lbs == classid] = 1
            candidates = [iid for iid in self.dblst[self.lbslst == (classid+1)]
                          if iid not in self.qrylst]
            random.shuffle(candidates)
            self.trainlst += candidates[:args.selpos]

        candidates = list(self.dblst[self.lbslst == 0])
        random.shuffle(candidates)
        self.trainlst += candidates[:500]

        self.qrylst = [self.qrylst[qid] for qid in range(len(self.qrylst))
                       if qry_mask[qid] > 0]
        self.poslst = [self.poslst[qid] for qid in range(len(self.poslst))
                       if qry_mask[qid] > 0]
        self.amblst = [self.amblst[qid] for qid in range(len(self.amblst))
                       if qry_mask[qid] > 0]

        self.dblst = [iid for iid in self.dblst
                      if iid not in self.trainlst]
        for i in range(len(self.qrylst)):
            self.poslst[i] = [iid for iid in self.poslst[i]
                              if iid not in self.trainlst]
            self.amblst[i] = [iid for iid in self.amblst[i]
                              if iid not in self.trainlst]
        for key in self.s2qlst.keys():
            self.s2qlst[key] = [self.s2qlst[key][qid] for qid
                                in range(len(self.s2qlst[key]))
                                if qry_mask[qid] > 0]
            for i in range(len(self.qrylst)):
                self.s2qlst[key][i] = [iid for iid in self.s2qlst[key][i]
                                       if iid not in self.trainlst]
        self.dblst = [iid for iid in self.dblst
                      if iid not in self.trainlst]
        pinfo("Done\n")

    @classmethod
    def set_parser(cls, parser):
        Builder.set_parser(parser)
        parser.add_argument(
            'img_dir', type=str,
            help="dir containing images extracted from %s" % cls.IMG_DIR_SRC)
        parser.add_argument(
            'gt_dir', type=str,
            help="dir containing groundtruth extracted from %s" % cls.GT_DIR_SRC)
        parser.add_argument('--good', type=float, default=2.0,
                            help="gain value for `good` results")
        parser.add_argument('--ok', type=float, default=1.0,
                            help="gain value for `ok` results")
        parser.add_argument('--junk', type=float, default=0.0,
                            help="gain value for `junk` results")
        parser.add_argument('--selpos', type=int, default=cls.DEF_SELPOS,
                            help="NO. of positive image for each class")
        parser.add_argument('--selneg', type=int, default=cls.DEF_SELNEG,
                            help="number of selected negative")


class Oxford(VGGBuilder):
    """ Oxford-dataset builder.
    Download: http://www.robots.ox.ac.uk/~vgg/data/oxbuildings/

    !!NOTE!! `all_souls_000183.jpg` appeares in both `all_souls` and
             `radcliffe_camera` classes

    ** Follow the original paper, queries are not excluded form the positive list.
    """

    ALL_LANDMARKS = ['all_souls', 'ashmolean', 'balliol', 'bodleian',
                     'christ_church', 'cornmarket', 'hertford', 'keble',
                     'magdalen', 'pitt_rivers', 'radcliffe_camera']
    IMG_DIR_SRC = '`oxbuild_images.tgz`'
    GT_DIR_SRC = '`gt_files_170407.tgz`'
    DEF_SELPOS = 7
    DEF_SELNEG = 500

    def __init__(self, args):
        """ Parse the Oxford dataset
        """
        VGGBuilder.__init__(self, args)


class Paris(VGGBuilder):
    """ Paris-dataset builder.
    Download: http://www.robots.ox.ac.uk/~vgg/data/parisbuildings/

    ** Follow the original paper, queries are not excluded form the positive list.
    """

    ALL_LANDMARKS = ['defense', 'eiffel', 'invalides', 'louvre', 'moulinrouge',
                     'museedorsay', 'notredame', 'pantheon', 'pompidou',
                     'sacrecoeur', 'triomphe']
    IMG_DIR_SRC = '`paris_1.tgzk` and `paris_2.tgz`'
    GT_DIR_SRC = '`paris_120310.tgz`'
    DEF_SELPOS = 15
    DEF_SELNEG = 500

    def __init__(self, args):
        """ Parse the Paris dataset
        """
        VGGBuilder.__init__(self, args)


class OxfordM(Oxford):
    """ Metric Learning Edition of `Oxford`
    """

    # selected classes for metric learning
    SEL_LANDMARKS = ['all_souls', 'ashmolean', 'bodleian', 'christ_church',
                     'hertford', 'magdalen', 'radcliffe_camera']

    def __init__(self, args):
        Oxford.__init__(self, args)
        self.init_M()

    @classmethod
    def set_parser(cls, parser):
        Oxford.set_parser(parser)


class ParisM(Paris):
    """ Metric Learning Edition of `Paris`
    """

    # selected classes for metric learning
    SEL_LANDMARKS = Paris.ALL_LANDMARKS

    def __init__(self, args):
        Paris.__init__(self, args)
        self.init_M()

    @classmethod
    def set_parser(cls, parser):
        Paris.set_parser(parser)


class Holidays(Builder):
    """ Holidays-dataset builder.
    Download: http://lear.inrialpes.fr/~jegou/data.php
    """

    def __init__(self, args):
        """ Parse the Parse dataset
        """
        Builder.__init__(self)

        pinfo("Loading image list ... ")
        # convert the image path into relative path to the target dir
        imnames = [item.split(".jpg")[0] for item in
                   sorted(os.listdir(args.img_dir))]
        self.imglst = [os.path.relpath(os.sep.join([args.img_dir,
                                                    imname + ".jpg"]),
                                       args.trg_dir) for imname in imnames]
        pinfo("Done!\n")

        self.qrylst = []
        self.poslst = []
        self.amblst = []
        self.s2qlst = {args.good: [], args.ok: [], args.junk: []}

        for imname in imnames:
            imidx = imnames.index(imname)
            print imidx, len(self.qrylst)
            if (int(imname) % 100 == 0):
                self.qrylst.append(imidx)
                self.poslst.append([])
                self.amblst.append([imidx])
                self.s2qlst[args.good].append([])
                self.s2qlst[args.ok].append([])
                self.s2qlst[args.junk].append([])
            else:
                self.poslst[len(self.qrylst)-1].append(imidx)
                self.s2qlst[args.ok][len(self.qrylst)-1].append(imidx)

        self.dblst = range(len(self.imglst))
        pinfo("\n")

    def __del__(self):
        pass

    @classmethod
    def set_parser(cls, parser):
        Builder.set_parser(parser)
        parser.add_argument('img_dir', type=str,
                            help="""dir containing images extracted from
                            `jpg1.tar.gz` and `jpg2.tar.gz`""")
        parser.add_argument('--good', type=float, default=2.0,
                            help="gain value for `good` results")
        parser.add_argument('--ok', type=float, default=1.0,
                            help="gain value for `ok` results")
        parser.add_argument('--junk', type=float, default=0.0,
                            help="gain value for `junk` results")


class UKBench(Builder):
    """ UKBench-dataset builder.
    Download: http://vis.uky.edu/~stewe/ukbench/
    """

    def __init__(self, args):
        """ Parse the Parse dataset
        """
        Builder.__init__(self)

        pinfo("Loading image list ... ")
        # convert the image path into relative path to the target dir
        imnames = [item.split(".jpg")[0] for item in
                   sorted(os.listdir(args.img_dir))]
        self.imglst = [os.path.relpath(os.sep.join([args.img_dir,
                                                    imname + ".jpg"]),
                                       args.trg_dir) for imname in imnames]
        pinfo("Done!\n")

        self.qrylst = []
        self.poslst = []
        self.amblst = []

        for idx in range(0, len(imnames), 4):
            self.qrylst.append(idx)
            self.poslst.append(range(idx, idx+4))
            self.amblst.append([])

        self.dblst = range(len(self.imglst))
        pinfo("\n")

    def __del__(self):
        pass

    @classmethod
    def set_parser(cls, parser):
        Builder.set_parser(parser)
        parser.add_argument('img_dir', type=str,
                            help="""dir containing full sized images extracted from
                            `ukbench.zip`""")


class FolderBuilder(Builder):
    """ This `Builder` is for the datasets with two-level folder structure,
        where each sub-folder contains a class.

        256_ObjectCategories
        ├── 001.ak47
        │   ├── 001_0001.jpg
        │   ├── ...
        │   └── 001_0098.jpg
        ├── ...
        │
        ├── 256.toad
        │   ├── 256_0001.jpg
        │   ├── ...
        │   └── 256_0108.jpg
        └── 257.clutter
            ├── 257_0001.jpg
            ├── ...
            └── 257_0827.jpg

      - The constructor will provide common process for preparing the dataset.
      - For special needs on a dataset, extend this class and override the `pre_process`
        and `post_process` rountines.
    """

    def __init__(self, args):
        Builder.__init__(self)

        self.pre_process(args)

        self.selcls = None
        if args.selcls is not None:
            with open(args.selcls) as lstf:
                self.selcls = [line.strip() for line in lstf]

        pinfo("Loading image list ...")
        folders = sorted(os.listdir(args.img_dir));
        self.classes = ["BACKGROUND"]
        self.imglst = []
        self.lbslst = []
        v_discarded = []
        # number of images per class
        num_img_per_cls = args.trnum + args.vanum + args.tsnum

        # scan the dataset
        for fld in folders:
            # if `selcls` is specified and cls_name is not in `it`,
            # then skip this class
            cls_name = self.get_cls_name(fld)
            if self.selcls is not None and cls_name not in self.selcls:
                continue

            if fld == self.BG_CLASS:
                label = 0
                self.classes[0] = cls_name
            else:
                label = len(self.classes)
                self.classes.append(cls_name)

            # scan the subdir for images
            sub_dir = os.path.join(args.img_dir, fld)
            # get image names
            imnames = []
            for imname in os.listdir(sub_dir):
                if imname.endswith('.jpg'):
                    imnames.append(imname)
                else:
                    v_discarded.append(os.path.join(sub_dir, imname))
            # shuffling the images
            np.random.shuffle(imnames)
            # randomly select `num_img_per_cls` images
            imnames = sorted(imnames[:num_img_per_cls])
            # append the selected images to self.imglst
            self.imglst += [os.path.join(sub_dir, imname)
                            for imname in imnames]
            self.lbslst += [label for imname in imnames]
        pinfo(" Done!\n")
        if len(v_discarded) > 0:
            perr("** Discarded files:\n")
            for disc in v_discarded:
                perr("\t\t%s\n" % disc)


        self.dblst = []
        self.qrylst = []
        self.poslst = []
        self.amblst = []
        self.trainlst = []
        self.val_lst = []
        self.s2qlst = {args.pos: []}
        for i in range(len(self.selcls)):
            # get training list
            start_idx = num_img_per_cls * i
            end_idx = start_idx + args.trnum
            self.trainlst += range(start_idx, end_idx)

            # get validation list
            start_idx = end_idx
            end_idx = start_idx + args.vanum
            self.val_lst += range(start_idx, end_idx)

            # get test list (query & db)
            start_idx = end_idx
            end_idx = start_idx + args.tsnum
            self.qrylst += range(start_idx, end_idx)
            self.dblst += range(start_idx, end_idx)

            # get groundtruth
            for j in range(args.tsnum):
                self.poslst.append(range(start_idx, end_idx))
                self.amblst.append([])

        self.s2qlst[args.pos] = self.poslst

        self.post_process(args)

    def pre_process(self, args):
        """
        """
        pass

    def post_process(self, args):
        """
        """
        pass

    def get_cls_name(self, folder):
        """ Get class name from the folder name.
        """
        return folder

    @classmethod
    def set_parser(cls, parser):
        Builder.set_parser(parser)
        parser.add_argument(
            'img_dir', type=str,
            help="root dir contains subfolders for each class")
        parser.add_argument(
            '--selcls', type=str, nargs='?', default=None,
            help="list file contains name of selected classes")
        parser.add_argument(
            '--trnum', type=int, nargs='?', default=cls.DEF_TRNUM,
            help="NO. of training images per class")
        parser.add_argument(
            '--vanum', type=int, nargs='?', default=cls.DEF_VANUM,
            help="NO. of validation images per class")
        parser.add_argument(
            '--tsnum', type=int, nargs='?', default=cls.DEF_TSNUM,
            help="NO. of test images per class")
        parser.add_argument(
            '--pos', type=float, default=1.0,
            help="gain value for `pos` results")


class Caltech101(FolderBuilder):
    """ Caltech101-dataset builder.
    Download: http://www.vision.caltech.edu/Image_Datasets/Caltech101/
    """

    DEF_TRNUM = 30
    DEF_VANUM = 0
    DEF_TSNUM = 20
    BG_CLASS = "BACKGROUND_Google"

    def __init__(self, args):
        FolderBuilder.__init__(self, args)


class Caltech256(FolderBuilder):
    """ Caltech256-dataset builder.
    Download: http://www.vision.caltech.edu/Image_Datasets/Caltech256/
    """

    DEF_TRNUM = 40
    DEF_VANUM = 0
    DEF_TSNUM = 25
    BG_CLASS = "257.clutter"

    def __init__(self, args):
        FolderBuilder.__init__(self, args)

    def get_cls_name(self, folder):
        return folder.split(".")[1]

    def pre_process(self, args):
        pass

    def post_process(self, args):
        pass


# class Caltech(Builder):
#     """ Caltech101/256-dataset builder.
#     Download: http://www.vision.caltech.edu/Image_Datasets/Caltech101/
#               http://www.vision.caltech.edu/Image_Datasets/Caltech256/
# 
#     NOTE: the image list are generated by another program.
#         The list contains lines of image information:
#             `path_of_image_0` `class_label_of_image_0`
#             `path_of_image_1` `class_label_of_image_1`
#             `path_of_image_2` `class_label_of_image_2`
#             ...
#     """
# 
#     def __init__(self, args, pos=1.0):
#         """
#         """
#         Builder.__init__(self)
# 
#         self.s2qlst = {pos: []}
# 
#         pinfo("Loading image list ...")
#         imglst = [line.split() for line in loadlist(args.imglst)]
#         self.imglst = [line[0] for line in imglst]
#         raw_lbs = [int(line[1]) for line in imglst]
#         uniqlbs = list(np.unique(raw_lbs))
#         self.lbslst = np.array([uniqlbs.index(lbl) for lbl in raw_lbs])
#         pinfo(" Done!\n")
# 
#         self.trainlst = np.ndarray(0, np.int)
#         self.dblst = np.ndarray(0, np.int)
#         self.qrylst = np.ndarray(0, np.int)
# 
#         imgnum = len(self.imglst)
#         clsnum = len(uniqlbs)
#         imgrange = np.array(range(imgnum))
#         for i in range(clsnum):
#             cur_ids = imgrange[self.lbslst == i]
#             np.random.shuffle(cur_ids)
#             self.trainlst = np.hstack((self.trainlst, cur_ids[:args.trnum]))
#             self.qrylst = np.hstack((self.qrylst,
#                                      cur_ids[args.trnum:
#                                              args.trnum + args.tsnum]))
#             self.dblst = np.hstack((self.dblst,
#                                     cur_ids[args.trnum:
#                                             args.trnum + args.tsnum]))
# 
#         pinfo("\tGenerating label list ...")
#         self.dlblst = self.lbslst[self.dblst]
#         self.qlblst = self.lbslst[self.qrylst]
#         pinfo(" Done!\n")
# 
#         pinfo("\tGenerating pos list \n")
#         self.poslst = []
#         self.amblst = []
#         qrynum = len(self.qrylst)
#         for qid in range(qrynum):
#             if qid % 10 == 0:
#                 pinfo("\r\t\t%d/%d" % (qid, qrynum))
#             self.poslst.append(self.dblst[self.dlblst == self.qlblst[qid]])
#             self.amblst.append([])
#         self.s2qlst[pos] = self.poslst
#         pinfo("\r\t\t%d/%d\tDone!\n" % (len(self.qrylst), len(self.qrylst)))
# 
#     @classmethod
#     def set_parser(cls, parser):
#         Builder.set_parser(parser)
#         parser.add_argument(
#             'img_dir', type=str,
#             help="`256_ObjectCategories` extracted from `256_ObjectCategories.tar`")
#         parser.add_argument('imglst', type=str,
#                             help="image image list")
#         parser.add_argument('trnum', type=int, nargs='?', default=40,
#                             help="NO. of training images per class")
#         parser.add_argument('tsnum', type=int, nargs='?', default=25,
#                             help="NO. of test images per class")


class ImageNet2012(Builder):
    """ ImageNet 2012 dataset builder.
    Download: http://www.image-net.org/challenges/LSVRC/2012/

    NOTE: the training/validation image list are generated by another program.
        both list contain lines of image information:
            `path_of_image_0` `class_label_of_image_0`
            `path_of_image_1` `class_label_of_image_1`
            `path_of_image_2` `class_label_of_image_2`
            ...
    """

    def __init__(self, args, pos=1.0):
        """
        """
        Builder.__init__(self)

        self.s2qlst = {pos: []}

        pinfo("Loading image list ")
        pinfo(".")
        trainlst = [line.split() for line in loadlist(args.trainlst)]
        pinfo(".")
        vallst = [line.split() for line in loadlist(args.vallst)]
        pinfo(".")
        self.imglst = [line[0] for line in trainlst] + \
            [line[0] for line in vallst]
        pinfo(".")
        pinfo(" Done!\n")

        pinfo("\tGenerating DB/query list ")
        pinfo(".")
        self.dblst = np.array(range(len(trainlst)))
        pinfo(".")
        self.qrylst = np.array(range(len(vallst)))
        pinfo(".")
        pinfo(" Done!\n")

        pinfo("\tGenerating label list ")
        pinfo(".")
        self.dlblst = np.array([int(line[1]) for line in trainlst])
        pinfo(".")
        self.qlblst = np.array([int(line[1]) for line in vallst])
        pinfo(".")
        pinfo(" Done!\n")

        pinfo("\tGenerating pos list \n")
        self.poslst = []
        self.amblst = []
        for qid in self.qrylst:
            if qid % 100 == 0:
                pinfo("\r\t\t%d/%d" % (qid, len(self.qrylst)))
            self.poslst.append(self.dblst[self.dlblst == self.qlblst[qid]])
            self.amblst.append([])
        self.s2qlst[pos] = self.poslst
        pinfo("\r\t\t%d/%d\tDone!\n" % (len(self.qrylst), len(self.qrylst)))

    def __del__(self):
        pass

    @classmethod
    def set_parser(cls, parser):
        Builder.set_parser(parser)
        parser.add_argument('trainlst', type=str,
                            help="""training image list""")
        parser.add_argument('vallst', type=str,
                            help="""validation image list""")


DS_BUILDERS = {
#     'caltech':     Caltech,
    'cal256':      Caltech256,
    'imgnet2012':  ImageNet2012,
    'ukbench':     UKBench,
    'holidays':    Holidays,
    'parism':      ParisM,
    'paris':       Paris,
    'oxfordm':     OxfordM,
    'oxford':      Oxford}