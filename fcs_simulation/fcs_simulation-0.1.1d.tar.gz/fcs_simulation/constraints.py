def soft_assert(constraint):
    try:
        constraint.evaluate()
    except Exception as e:
        print e

def positive(value_or_constraint): # => constraint
    pass

class Constraint(object):
    """Represents a contraint on a possible value. Constraints can be chained"""
    def __init__(self, constraint_chained=None):
        self.constraint_chained = constraint_chained

    def evaluate(self):
        if type(self.constraint_chained)==Constraint:
            return self.constraint_chained.evaluate()
        else:
            self.constraint_chained = self.evaluate_value(self.constraint_chained)
            return self.evaluate()

    def evaluate_value(self, value):
        pass

class Positive(Constraint):
        def evaluate_value(self, value):
            if value >= 0:
                return value
            else:
                assert False


