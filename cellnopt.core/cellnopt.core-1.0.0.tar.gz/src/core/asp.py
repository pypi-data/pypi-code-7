# -*- python -*-
#
#  This file is part of XXX software
#
#  Copyright (c) 2011-2012 - EBI-EMBL
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  website: http://www.ebi.ac.uk/~cokelaer/XXX
#
##############################################################################
"""ASP related


"""
import pandas as pd
from .cnograph import CNOGraph
from .sif import SIF

__all__ = ["NET", "net2reaction", "CASPOModels"]



class NET(object):
    """Class to manipulate reactions in NET format.

    The NET format ::

        species1 -> species2 sign

    where sign can be either the + or - character.


    Examples are::

            A -> B +
            A -> B -



    """
    def __init__(self, filename=None):
        """.. rubric:: constructor

        :param str filename: optional filename containing NET reactions
            if provided, NET reactions are converted into reactions (see
            :class:`cellnopt.core.reactions.Reactions`

        """
        self._net = []
        if filename:
            self._readnet(filename=filename)

    def _readnet(self, filename=None):
        """read NET file


        """
        if filename == None:
            filename = self.filename
        try:
            f = open(filename, 'r')
            data = f.read()
            data = data.splitlines()
            for i,row in enumerate(data):
                if len(row)>0:
                    self.add_net(row)
                else:
                    print("warning. found an empty line")
        except IOError, e:
            raise IOError(e)
        else:
            # if the file was opened, let us close it.
            f.close()

    def write2sif(self, filename):
        """Write SIF reactions into a file"""
        sif = SIF()
        for net in self.net:
            sif.add_reaction(net2reaction(net))
        sif.save(filename)

    def _get_net(self):
        return self._net
    net = property(_get_net)

    def add_net(self, net):
        self._check(net)
        self._net.append(net)

    def _check(self, net):
        try:
            _split_net(net)
        except Exception, e:
            raise Exception(e)

    def __str__(self):
        txt = ""
        for row in self.net:
            txt += row + "\n"
        return txt

def _split_net(data):
    try:
        lhs, rhs = data.split("->")
    except:
        raise ValueError("net2reaction: it seems your net string is not correct. could not find -> characters")
    lhs = lhs.strip()
    try:
        rhs, sign = rhs.split()
    except:
       raise ValueError("RHS of your net string could not be split. missing  space ? ")
    if sign not in ['+', '-']:
        raise ValueError("found invalid sign. Must be either + or - character")
    return (lhs, rhs, sign)


def net2reaction(data):
    """convert a NET string to a reaction

    a NET string can be one of ::

        A -> B +
        C -> D -

    where + indicates activation and - indicates inhibition

    .. doctest::

        >>> assert net2reaction("A -> B +") == "A=B"
        >>> assert net2reaction("A -> B -") == "!A=B"

    """
    lhs, rhs ,sign = _split_net(data)
    if sign == "+":
        reaction = "=".join([lhs, rhs])
    elif sign == "-":
        reaction = "!" + "=".join([lhs, rhs])
    return reaction






class CASPOModels(object):
    """Class to read and plot models as exported by CASPO


    .. plot::
        :include-source:
        :width: 80%

        >>> from cellnopt.core import *
        >>> filename = get_share_file("caspo_models.csv")
        >>> m = asp.CASPOModels(filename)
        >>> m.plotdot(model_number=0)  # indices are m.df.index
        >>> m.plotdot() # average model, whcih can be obtained with  m.get_average_model()

    .. note:: One difficulty is the way ANDs are coded in different software. In CASPO,
        the AND gate is coded as "A+B=C". Note that internally we use ^ especially
        in CNOGraph. Then, an AND edge is splitted in sub edges. so, A+B=C is made
        of 3 edges A -> A+B=C , B -> A+B=C and A+B=C -> C. This explains the wierd
        code in :meth:`plotdot`.

    """
    def __init__(self, filename):
        print("Deprecated. USe Models class instead.")
        self.filename = filename
        self.df = pd.read_csv(self.filename)
        self.df.columns = [x.replace("+", "^") for x in self.df.columns]

        self.cnograph = CNOGraph()
        for this in self.df.columns:
            self.cnograph.add_reaction(this)

    def get_average_model(self):
        """Returns the average model

        """
        return self.df.mean(axis=0)


    def plotdot(self, model_number=None, *args, **kargs):
        """

        :param int model_number: model_number as shown by :attr:`df.index`
            if not provided, the average is taken
        """
        if model_number==None:
            model = self.get_average_model()
        else:
            model = self.df.ix[model_number]

        for edge in self.cnograph.edges(data=True):
            link = edge[2]['link']
            if "^" not in edge[0] and "^" not in edge[1]:
                if link=="-":
                    name = "!"+edge[0]+"="+edge[1]
                else:
                    name = edge[0]+"="+edge[1]
                value = model[name]
            elif "^" in edge[0]:
                value = model[edge[0]]
            elif "^" in edge[1]:
                value = model[edge[1]]
            else:
                raise ValueError()
            self.cnograph.edge[edge[0]][edge[1]]["label"] = value
            self.cnograph.edge[edge[0]][edge[1]]["average"] = value

        self.cnograph.plotdot(edge_attribute="average", **kargs)

    def export2sif(self, filename):
        """Exports 2 SIF using the "and" convention

        can read the results with CellNOptR for instance

            >>> library(CellNOptR)
            >>> plotModel(readSIF("test.sif"))
        """
        self.cnograph.export2sif(filename)


