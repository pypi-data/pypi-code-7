
"""
A parser for the algebraic formulas used to specify a query to ALPACA.
"""

__author__ = "Johannes Köster"
__license__ = "MIT"


import re
import ast
from collections import namedtuple


SAMPLEPLUS = "SamplePlus"
PLUS = "Plus"
MINUS = "Minus"


AlgebraNode = namedtuple("AlgebraNode", "type children")


IDENTIFIER = re.compile("[^\+\-\(\)\s]+")


def parse(expression):
    """Parse an query expression."""
    expression = IDENTIFIER.sub(
        lambda match: '"{}"'.format(match.group()), expression
    )
    parser = FormulaParser()
    node = compile(expression, "expression", "eval", ast.PyCF_ONLY_AST)
    return parser.visit(node)


def get_samples(formula):
    """Get samples from node."""
    def _get_samples(node):
        if node.type == SAMPLEPLUS:
            return node.children
        return (sample for child in node.children for sample in _get_samples(child))
    return sorted(_get_samples(formula))


class FormulaParser(ast.NodeVisitor):

    def visit_Expression(self, node):
        """Parse an expression and recurse into children."""
        children = list(ast.iter_child_nodes(node))
        if len(children) > 1:
            raise SyntaxError(
                "Invalid algebraic expression.",
                (None, node.lineno, node.col_offset, None)
            )
        return self.visit(children[0])

    def visit_BinOp(self, node):
        """Parse a binary operator."""
        left, op, right = ast.iter_child_nodes(node)
        left = self.visit(left)
        right = self.visit(right)

        if isinstance(op, ast.Add):
            if all(child.type == SAMPLEPLUS for child in (left, right)):
                return AlgebraNode(SAMPLEPLUS, left.children | right.children)
            else:
                return AlgebraNode(PLUS, [left, right])
        elif isinstance(op, ast.Sub):
            return AlgebraNode(MINUS, [left, right])
        else:
            raise SyntaxError(
                "Unknown operator.",
                (None, op.lineno, op.col_offset, None)
            )

    def visit_Str(self, node):
        """Parse a string."""
        sample_name = node.s
        try:
            return AlgebraNode(SAMPLEPLUS, set([sample_name]))
        except KeyError:
            raise SyntaxError(
                "Unknown sample accession.",
                (None, node.lineno, node.col_offset, None)
            )
