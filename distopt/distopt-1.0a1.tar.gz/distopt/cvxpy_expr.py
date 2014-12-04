"""Manipulate cvxpy expressions."""

from cvxpy.atoms.affine.add_expr import AddExpression
from cvxpy.atoms.affine.binary_operators import MulExpression
from cvxpy.atoms.affine.unary_operators import NegExpression
from cvxpy.atoms.elementwise.square import square
from cvxpy.atoms.norm1 import norm1
from cvxpy.atoms.norm2 import norm2
from cvxpy.expressions.constants.constant import Constant
from cvxpy.expressions.variables.variable import Variable
import numpy as np

from distopt.expression_pb2 import Expression as E
from distopt import master_pb2

TYPES = ((Variable, E.VARIABLE),
         (Constant, E.CONSTANT),
         (AddExpression, E.ADD),
         (MulExpression, E.MULTIPLY),
         (NegExpression, E.NEGATE),
         (square, E.SQUARE),
         (norm1, E.NORM_1),
         (norm2, E.NORM_2))


def convert_constant(value, proto):
    if isinstance(value, float):
        proto.scalar = value
    else:
        # TODO(mwytock): Investigate most efficient way to do this
        proto.dense_matrix.value.extend(
            list(np.array(value).reshape(-1, order='F')))

def convert(expr, proto):
    """Convert cxvpy expression to protobuf form."""
    proto.size.dim.extend(expr.size)

    for arg in getattr(expr, "args", []):
        convert(arg, proto.arg.add())

    if isinstance(expr, Constant):
        convert_constant(expr.value, proto.constant)
    elif isinstance(expr, Variable):
        proto.variable.variable_id = "input:%s" % expr.name()

    for expr_cls, expr_type in TYPES:
        if isinstance(expr, expr_cls):
            proto.expression_type = expr_type
            break
    else:
        raise RuntimeError("Unknown type: %s" % type(expr))

def convert_problem(problem, proto):
    convert(problem.objective._expr, proto.objective)
