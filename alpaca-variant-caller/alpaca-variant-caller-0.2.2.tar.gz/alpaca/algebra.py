
"""
A parser for the algebraic formulas used to specify a query to ALPACA.
"""

__author__ = "Johannes Köster"
__license__ = "MIT"

import numpy as np

from alpaca.utils import AlpacaError


def parse(expression, samples):
    identifiers = {
        sample: SamplePlus(sample) for sample in samples
    }
    return eval(expression, identifiers)


def get_samples(formula):
    # provide inorder traversal of sample ids but do not repeat them
    def _get_samples(node):
        if isinstance(node, SamplePlus):
            yield from node.children
        else:
            for child in node.children:
                yield from _get_samples(child)
    return list(_get_samples(formula))


class AlgebraNode:

    def __add__(self, other):
        return Plus(self, other)

    def __sub__(self, other):
        return Minus(self, other)

    def __call__(self, **params):
        raise AlpacaError("Syntax error in query: params can be only given for sums of samples or single samples.")


class SamplePlus(AlgebraNode):
    param_names = {"het"}

    def __init__(self, *children):
        self.children = list(children)
        self.params = {}

    @property
    def heterozygosity(self):
        return self.params.get("het", None)

    def __add__(self, other):
        if isinstance(other, SamplePlus):
            if self.params != other.params:
                return Plus(self, other)
            old = set(self.children)
            return SamplePlus(*(
                self.children +
                [child for child in other.children if child not in old]
            ))

    def __call__(self, **params):
        if set(params.keys()) != self.param_names:
            raise AlpacaError(
                "Only the following parameters are allowed in "
                "the query:\n{}".format(self.param_names)
            )
        self.params = params
        return self

    def __str__(self):
        s = " + ".join(map(str, self.children))
        if len(self.children) > 1:
            s = "({})".format(s)
        return "{}{}".format(s, self.params)


class Plus(AlgebraNode):
    def __init__(self, *children):
        self.children = children

    def __str__(self):
        return "({})".format(" + ".join(map(str, self.children)))


class Minus(AlgebraNode):
    def __init__(self, *children):
        self.children = children

    def __str__(self):
        return "({})".format(" - ".join(map(str, self.children)))
