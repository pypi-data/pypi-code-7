# -*- python -*-
#
#  This file is part of the cinapps.tcell package
#
#  Copyright (c) 2012-2013 - EMBL-EBI
#
#  File author(s): Thomas Cokelaer (cokelaer@ebi.ac.uk)
#
#  Distributed under the GLPv3 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-3.0.html
#
#  website: www.cellnopt.org
#
##############################################################################
"""This module contains a base class to manipulate reactions

.. testsetup:: converter

    from cellnopt.core import *
    c = Interactions()


.. todo:: merge Interactions and Reactions class together
"""
from __future__ import print_function

from easydev import Logging

import numpy

from tools import CNOError

__all__ = ["Interactions", "Reaction"]


class Reaction(object):
    """A Reaction class 

    A Reaction can encode logical AND and OR as well as NOT::

        >>> from cellnopt.core import Reaction
        >>> r = Reaction("A+B=C") # a OR reaction
        >>> r = Reaction("A^B=C") # an AND reaction
        >>> r = Reaction("A&B=C") # an AND reaction
        >>> r = Reaction("C=D")   # an activation
        >>> r = Reaction("!D=E")  # a NOT reaction

            r.name
            r.rename_species(old, new)
            r._valid_reaction("a=b")
    """
    valid_symbols = ["+","!", "&", "^"]
    def __init__(self, reaction=None, strict_rules=True):
        """

        :param str reaction:
        :param bool strict_rules: if True, reactions cannot start with =, ^ or ^
            signs.
        """
        self._strict_rules = strict_rules
        self._reaction = None
        if reaction:
            self.name = reaction

    def _set_reaction(self, reaction):
        if reaction:
            reaction = self._valid_reaction(reaction)
        self._reaction = reaction[:]
    def _get_reaction(self):
        return self._reaction
    name = property(_get_reaction, _set_reaction)

    def _get_species(self, reac=None):
        """

            >>> r = Reaction("!a+c^d^e^f+!h=b")
            >>> r._get_species()
            ['a' ,'c', 'd', 'r' ,'f' ,'h' ,'b']
        """
        if reac==None:
            reac = self.name[:]
        import re
        species = re.split("[+|=|^|!]", reac)
        species = [x for x in species if x]
        return species
    
    def rename_species(self, old, new):
        """

        difficulties: (1) if a species is called BAC, replace A by D must 
        not touch BAC names (2) delimiters such as !, +, ^ should be taken 
        into account
        """
        raise NotImplementedError
        new = self._valid_species(new)
        lhs, rhs = self.name.split("=")
        if old == rhs:
            rhs = new
        #species = self._get_species(lhs)
        new_lhs = []
        for c in lhs:
            new_lhs.append(c)
        print(new_lhs, rhs)
        reac = "=".join([new_lhs, rhs])
        self.name = reac


    def _valid_reaction(self, reaction):
        reaction = reaction.strip()
        reaction = reaction.replace("&", "^")
        if self._strict_rules:
            if reaction[0] in ["=", "^" , "+"]:
                raise CNOError("Reaction (%s) cannot start with %s" %
                        (reaction, "=, ^, +"))
        # = sign is compulsary
        if "=" not in reaction:
            raise CNOError("Reaction (%s) must contain a = sign" % reaction)
        lhs, rhs = reaction.split("=")
        for this in self.valid_symbols:
            if this in rhs:
                raise CNOError("Found an unexpected character (%s) in the LHS of reactions %s" % (reaction, self.valid_symbols))
        if "&" in lhs or "^" in lhs:
            if lhs == "":
                raise CNOError("Found an AND gate without RHS (%s)" % (reaction))
        return reaction

    def _valid_species(self, species):
        species = species.strip()
        for c in self.valid_symbols: 
            if c in species:
                raise CNOError("species must not contains any of the special symbols =, &, ^, +")
        return species


    def __str__(self):
        if self.name: return self.name
        else: return ""


class Interactions(object):
    """Interactions is a Base class to manipulate reactions (e.g., A=B)

    You can create list of reactions using the **=**, **!**, **+** 
    and **^** characters with the following meaning::

        >>> from cellnopt.core import *
        >>> c = Interactions()
        >>> c.add_reaction("A+B=C") # a OR reaction
        >>> c.add_reaction("A^B=C") # an AND reaction
        >>> c.add_reaction("A&B=C") # an AND reaction
        >>> c.add_reaction("C=D")   # an activation
        >>> c.add_reaction("!D=E")  # a NOT reaction

     #. The **!** sign indicates a NOT logic.
     #. The **+** sign indicates a OR.
     #. The **=** sign indicates a relation.
     #. The **^** or **&** signs indicate an AND ut **&** are replaced by **^**.

    .. warning:: meaning of + sign is OR so A+B=C is same as 2 reactions: A=C, B=C

    Now, we can get the species::

        >>> c.specID
        ['A', 'B', 'C', 'D', 'E']

    Remove one::

        >>> c.remove_species("A")
        >>> c.reacID
        ["B=C", "C=D", "!D=E"]

    .. seealso:: :class:`cellnopt.core.reactions.Reactions` and :class:`cellnopt.core.sif.SIF`
    """

    valid_symbols = ["+","!", "&", "^"]
    def __init__(self, format="cno", strict_rules=True):
        self._reacID = []
        self._notMat = None
        self._interMat = None
        self._format = format
        self._logging = Logging("INFO")
        self._reaction = Reaction(strict_rules=strict_rules)
        

    def _reac2spec(self, reac):
        """simple function to extract species from a reaction """
        self._reaction._valid_reaction(reac)
        reac = reac.replace("!","") # we don't care about the NOT here
        reac = reac.replace("__or__","+")  # just to find the species
        reac = reac.replace("^","+")  # just to find the species
        lhs, rhs = reac.split("=")

        specID = []
        specID.extend([x for x in lhs.split('+') if x])
        specID.extend([x for x in rhs.split('+') if x])
        specID = set(specID)
        return specID

    def _get_species(self):
        """Extract the specID out of reacID"""
        specID = set() # use set to prevent duplicates

        # extract species from all reacID and add to the set
        for reac in self.reacID:
            specID = specID.union(self._reac2spec(reac))

        # sort (transformed to a list)
        specID = sorted(specID)
        #self._specID = specID
        return specID
    namesSpecies = property(fget=_get_species, doc="alias to specID")
    specID = property(_get_species, doc="return species")

    def _get_reacID(self):
        return self._reacID
    reacID = property(fget=_get_reacID)

    def _get_lhs_species(self, reac, remove_not=True):
        """Return independent species

        reac = "A+!B+C=D"
        _get_lhs_species returns ['A', 'B', 'C']

        used by _build_interMat
        """
        lhs = reac.split('=')[0]  # keep only lhs
        lhs = lhs.split('+')      # split reactions
        lhs = [x for x in lhs if len(x)>0]
        if remove_not == True:
            lhs = [x.replace('!','') for x in lhs]
        return lhs

    def __str__(self):
        _str = "reactions: %s " % len(self.reacID)
        _str += "species: %s " % len(self.specID)
        return _str

    def remove_species(self, species_to_remove):
        """Removes species from the reacID list

        :param str,list species_to_remove:


        .. note:: If a reaction is "a+b=c" and you remove specy "a", 
            then the reaction is not enterely removed but replace by "b=c"

        """
        # make sure we have a **list** of species to remove
        if isinstance(species_to_remove, list):
            pass
        elif isinstance(species_to_remove, str):
            species_to_remove = [species_to_remove]
        else:
            raise TypeError("species_to_remove must be a list or string")

        reacIDs_toremove = []
        reacIDs_toadd = []
        #['pRB' in s2s._reac2spec(x) for x in s2s.reacID if 'pRB' in x]
        for reac in self.reacID:
            lhs = self._get_lhs_species(reac)  # lhs without ! sign
            rhs = reac.split("=")[1]

            # two cases: either a=b or a+d+e=b
            # if we remove a, the first reaction should be removed but the
            # second should just be transformed to d+e=b

            # RHS contains a specy to remove, we do want the reaction
            if rhs in species_to_remove:
                reacIDs_toremove.append(reac)
                continue

            # otherwise, we need to look at the LHS. If the LHS is of length 1,
            # we are in the first case (a=b) and it LHS contains specy to
            # remove, we do not want to keep it.
            if len(lhs) == 1:
                if lhs[0] in species_to_remove:
                    reacIDs_toremove.append(reac)
                    continue

            # Finally, if LHS contains 2 species or more, separated by + sign,
            # we do no want to remove the entire reaction but only the
            # relevant specy. So to remove a in "a+b=c", we should return "b=c"
            # taking care of ! signs.
            for symbol in ["+", "^"]:
                if symbol not in reac:
                    continue
                else:
                    lhs_with_neg = [x for x in reac.split("=")[0].split(symbol)]
                    new_lhs = symbol.join([x for x in lhs_with_neg if x.replace("!", "") not in species_to_remove])
                    if len(new_lhs):
                        new_reac = new_lhs + "=" + rhs
                        reacIDs_toremove.append(reac)
                        reacIDs_toadd.append(new_reac)

        level = self._logging.level
        self._logging.level = "ERROR"
        for reac in reacIDs_toremove:
            self.remove_reaction(reac)
        for reac in reacIDs_toadd:
            self.add_reaction(reac)
        self._logging.level = level


    def add_reaction(self, reaction):
        """Adds a reaction in the list of reactions

        In logical formalism, the inverted hat stand for OR but there is no such
        key on standard keyboard so we use the + sign instead. The AND is
        defined with either the ^ or & sign. Finally the NOT is 
        defined by the ! sign. Valid reactions are therefore::

            a=b
            a+c=d
            a&b=e
            a^b=e  # same as above
            !a=e

        Example::

            >>> c = Interactions()
            >>> c.add_reaction("a=b")
            >>> assert len(c.reacID) == 1

        .. warning & symbol are replaced by ^ internally.

        """
        # remove any trailing white space. Important to get proper species names
        reaction = self._reaction._valid_reaction(reaction)
        reaction = self._sort_reaction(reaction)

        if reaction not in self.reacID:
            self._reacID.append(reaction)
        else:
            self._logging.info("%s already in the list of reactions" % reaction)
        # update whatever is needed to be updated.
        #self.specID = sorted(set(self.specID).union(self._reac2spec(reaction)))

    def _sort_reaction(self, reaction):
        """Rearrange species of the LHS in alphabetical order

        ::

            >>> s.sort_reaction("b+a=c")
            "a+b=c"

        """
        lhs, rhs = reaction.split("=")
        lhs = [x for x in lhs.split("+")] # left species with ! sign   ["b","!a","c"]
        if len(lhs) == 1:
            return reaction
        # if more than one specy, we must rearrange them taking care of ! signs
        species = self._get_lhs_species(reaction)  # without ! signs ["b", "a", "c"]

        sorted_indices = numpy.argsort(species)
        new_lhs = []
        for i in sorted_indices:
            new_lhs.append(lhs[i])
        new_reac = "=".join(["+".join(new_lhs), rhs])
        return new_reac

    def remove_reaction(self, reaction):
        """Remove a reaction from the reacID list

            >>> c = Interactions()
            >>> c.add_reaction("a=b")
            >>> assert len(c.reacID) == 1
            >>> c.remove_reaction("a=b")
            >>> assert len(c.reacID) == 0
        """
        if reaction in self.reacID:
            self._reacID.remove(reaction)
            #self.get_specID_from_reacID()

    def search(self, specy, strict=False, verbose=True):
        """Prints and returns reactions that contain the specy name

        Decomposes reactions into species first

        :param str specy:
        :param bool strict: decompose reaction search for the provided specy 
            name 
        :return: a Interactions instance with relevant reactions

        """
        r = Interactions()
        for x in self.reacID:
            species = self._reac2spec(x)
            if strict == True:
                for this in species:
                    if specy.lower() == this.lower():
                        if verbose:
                            print(x)
                        r.add_reaction(x)
            else:
                for this in species:
                    if specy.lower() in this.lower():
                        if verbose:
                            print(x)
                        r.add_reaction(x)
                        continue
        return r



