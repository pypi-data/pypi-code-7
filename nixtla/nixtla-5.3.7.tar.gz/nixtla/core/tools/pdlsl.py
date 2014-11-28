# -*- coding: utf-8 -*-
'''
Created on Avr 24, 2013

@author: curiel
'''
import inspect
from nixtla.core.tools.infix import Infix

iff = Infix(lambda x, y: DoubleImplication(x, y))
then = Infix(lambda x, y: Implication(x, y))
seq = Infix(lambda x, y: Sequence(x, y))
#until = Infix(lambda x, y: Until(x, y))


class Formula(object):
    ''''''
    
    def __or__(self, other):
        '''|'''
        if isinstance(other, Infix):
            TypeError('CORRECT FORMAT formula1 <<infix>> formula2')
        return Or(self, other)

    def __and__(self, other):
        '''&'''
        return And(self, other)

    def __not__(self):
        '''~'''
        return Not(self)
    
    def __invert__(self):
        '''~'''
        return Not(self)
    
    #def __mul__(self, i):
    #    '''*'''
    #    return TransitiveClosure(self, i)
    
    #def __rshift__(self, other):
    #    '''>> (->)'''
    #    return Implication(self, other)
        
    #def __lshift__(self, other):
    #    '''<< (<->)'''
    #    return DoubleImplication(self, other)
    
    def __eq__(self, other_formula):
        if self.__class__ != other_formula.__class__:
            return False
        return str(self) == str(other_formula) 
    
    def __ne__(self, other_formula):
        return not self == other_formula
    
    def __mod__(self, other_formula):
        return Test(self, other_formula)
    
    def agents(self):
        raise ValueError("Not Implemented")
    
    def atomize(self):
        raise ValueError("Not Implemented")
    
    def validate(self, *atoms):
        raise ValueError("Not Implemented")
    
    def falsify(self, *atoms):
        raise ValueError("Not Implemented")
    
    def remove(self, *atoms):
        raise ValueError("Not Implemented")
    
    @classmethod
    def from_lambda(cls, lambda_object):
        '''We assume we have REMOVABLE atoms as placeholders'''
        if hasattr(lambda_object, "__call__"):
            if lambda_object.__name__ == "<lambda>":
                qty_of_args = len(inspect.getargspec(lambda_object)[0])
                removable = Atom("REMOVABLE")
                try:
                    arg_vector = [removable for i in range(0, qty_of_args)]
                    instanced_lambda = lambda_object(*arg_vector)
                    return instanced_lambda.remove(removable)
                except:
                    '''lambda didn't accept a formula as input, we try with a
                    string'''
                    arg_vector = ["REMOVABLE" for i in range(0, qty_of_args)]
                    instanced_lambda = lambda_object(*arg_vector)
                    return instanced_lambda.remove(removable)
        raise TypeError("from_lambda has to receive a lambda function")
    
    @classmethod
    def from_hand_lambda(cls, lambda_object):
        '''We assume we have hands as lambda parameters'''
        if hasattr(lambda_object, "__call__"):
            if lambda_object.__name__ == "<lambda>":
                qty_of_args = len(inspect.getargspec(lambda_object)[0])
                if qty_of_args >= 2:
                    # Two hands
                    return lambda_object("R","L")|lambda_object("L","R")
        raise TypeError("from_hand_lambda has to receive a lambda with at least 2 args")
    
    @classmethod
    def from_lambda_combinatoric(cls, lambda_object, combinations):
        '''We want all possible combinations of the lambda object'''
        if hasattr(lambda_object, "__call__"):
            if lambda_object.__name__ == "<lambda>":
                qty_of_args = len(inspect.getargspec(lambda_object)[0])
                or_formula = None

                for combination in combinations:
                    try:
                        or_formula |= lambda_object(combination)
                    except:
                        or_formula = lambda_object(combination)
                # Two hands
                return or_formula
        raise TypeError("from_lambda_combinatoric has to receive a lambda with at most 1 positional arg")


class Atom(Formula):
    
    def __init__(self, name, agent=None):
        self._name = name
        self.agent = agent

    def __str__(self):
        return str(self._name)
    
    def atomize(self):
        return set([str(self)])
    
    def agents(self):
        return set([self.agent])
    
    def validate(self, *atoms):
        for atom in atoms:
            if str(atom) == str(self):
                return top
        return self
        
    def falsify(self, *atoms):
        for atom in atoms:
            if str(atom) == str(self):
                return bottom
        return self
    
    def remove(self, *atoms):
        for atom in atoms:
            if str(atom) == str(self):
                return None
        return self
    
    __repr__ = __str__ 


class UnaryFormula(Formula):
    
    def __init__(self, term, operator_str):
        if isinstance(term, bool):
            if term:
                term = top
            else:
                term = bottom
        if not isinstance(term, Formula):
            raise TypeError("The term is not a valid formula")
        self.terms = [term]
        self.operator_str = operator_str
        self.operator = None
        
    def __str__(self):
        return self.operator_str + " " + str(self.terms[0])
    
    def atomize(self):
        return self.terms[0].atomize()
    
    def agents(self):
        return self.terms[0].agents()
    
    def validate(self, *atoms):
        try:
            return self.operator(self.terms[0].validate(*atoms))
        except:
            raise ValueError("This formula cannot substitute atoms")
    
    def falsify(self, *atoms):
        try:
            return self.operator(self.terms[0].falsify(*atoms))
        except:
            raise ValueError("This formula cannot substitute atoms")
        
    def remove(self, *atoms):
        try:
            removed_atoms_in_term = self.terms[0].remove(*atoms)
            if removed_atoms_in_term != None:
                return self.operator(removed_atoms_in_term)
            else:
                return None
        except:
            raise ValueError("This formula cannot substitute atoms")
    
    __repr__ = __str__ 
    

class Not(UnaryFormula):
    
    def __init__(self, term):
        super(Not, self).__init__(term, "~")
        self.operator = (lambda term: ~ term)


class Necessity(UnaryFormula):

    def __init__(self, term, action):
        super(Necessity, self).__init__(term, "[" + str(action) + "]")
        self.action = action
        self.operator = (lambda action: (lambda term: nec[action](term)))(action)
    

class Possibility(UnaryFormula):
    
    def __init__(self, term, action):
        super(Possibility, self).__init__(term, "<" + str(action) + ">")
        self.action = action
        self.operator = (lambda action: (lambda term: pos[action](term)))(action)


class Until(UnaryFormula):
    
    def __init__(self, term):
        #super(Possibility, self).__init__(term, "<" + str(action) + ">")
        super(Until, self).__init__(term, "UNTIL")
        self.operator = (lambda term: Until(term))


class BinaryFormula(Formula):
    
    def __init__(self, term1, term2, operator_str):
        
        if isinstance(term1, bool):
            if term1:
                term1 = top
            else:
                term1 = bottom
        
        if isinstance(term2, bool):
            if term2:
                term2 = top
            else:
                term2 = bottom 
        
        if not isinstance(term1, Formula):
            raise TypeError("The first term is not a valid formula")
        elif not isinstance(term2, Formula):
            import ipdb;ipdb.set_trace()
            raise TypeError("The second term is not a valid formula")
        
        self.terms = [term1, term2] 
        self.operator_str = operator_str
        self.operator = None

    def __str__(self):
        return "(" + str(self.terms[0]) + " " +self.operator_str + " " +str(self.terms[1]) + ")" 
    
    def atomize(self):
        return self.terms[0].atomize().union(self.terms[1].atomize())
    
    def agents(self):
        return self.terms[0].agents().union(self.terms[1].agents())
    
    def validate(self, *atoms):
        try:
            return self.operator(self.terms[0].validate(*atoms),
                                 self.terms[1].validate(*atoms))
        except:
            raise ValueError("This formula cannot substitute atoms")
    
    def falsify(self, *atoms):
        try:
            return self.operator(self.terms[0].falsify(*atoms),
                                 self.terms[1].falsify(*atoms))
        except:
            raise ValueError("This formula cannot substitute atoms")
        
    def remove(self, *atoms):
        try:
            removed_atoms_in_term_0 = self.terms[0].remove(*atoms)
            removed_atoms_in_term_1 = self.terms[1].remove(*atoms)
            if removed_atoms_in_term_0 != None and removed_atoms_in_term_1 != None:
                return self.operator(removed_atoms_in_term_0,
                                     removed_atoms_in_term_1)
            elif removed_atoms_in_term_0 != None:
                return removed_atoms_in_term_0
            elif removed_atoms_in_term_1 != None:
                return removed_atoms_in_term_1
            else:
                return None
        except:
            #import ipdb;ipdb.set_trace()
            raise ValueError("This formula cannot substitute atoms")
    
    __repr__ = __str__


class Implication(BinaryFormula):

    def __init__(self, term1, term2):
        super(Implication, self).__init__(term1, term2, "=>")
        self.operator = (lambda term1, term2: term1 <<then>> term2)

#     def value(self, *valuation):
#         return not self.terms[0].value(*valuation) and self.terms[1].value(*valuation)


class DoubleImplication(BinaryFormula):

    def __init__(self, term1, term2):
        super(DoubleImplication, self).__init__(term1, term2, "<=>")
        self.operator = (lambda term1, term2: term1 <<iff>> term2)
    

class And(BinaryFormula):

    def __init__(self, term1, term2):
        super(And, self).__init__(term1, term2, "&")
        self.operator = (lambda term1, term2: term1 & term2)


class Or(BinaryFormula):

    def __init__(self, term1, term2):
        super(Or, self).__init__(term1, term2, "|")
        self.operator = (lambda term1, term2: term1 | term2)

class Sequence(BinaryFormula):
    
    def __init__(self, term1, term2):
        super(Sequence, self).__init__(term1, term2, " FOLLOWED BY ")
        self.operator = (lambda term1, term2: term1 <<seq>> term2)
# class Until(BinaryFormula):
#     
#     def __init__(self, term1, term2):
#         super(Until, self).__init__(term1, term2, " U ")
#         self.operator = (lambda term1, term2: term1 <<until>> term2)


top = Atom("True")
bottom = ~top


class Action(object):
    ''''''
    
    def __add__(self, other):
        '''+'''
        return Concatenation(self, other)

    def __floordiv__(self, other):
        '''//'''
        return Concurrence(self, other)
    
    def __xor__(self, other):
        '''^'''
        return Union(self, other)
    
    def __sub__(self, other):
        '''-, empty'''
        return Empty(self, other)

    def __pow__(self, i):
        '''**i'''
        try:
            if i <= 0:
                return TransitiveClosure(self, 1)
            else:
                return TransitiveClosure(self, i)
        except:
            return TransitiveClosure(self, 1)
    
    def __eq__(self, other_action):
        if self.__class__ != other_action.__class__:
            return False
        return str(self) == str(other_action)
    
    def __ne__(self, other_action):
        return not self == other_action
    
    def __str__(self):
        return "(" + str(self.terms[0]) + " " + self.operator_str + " " + str(self.terms[1]) + ")" 

    def atomize(self):
        raise ValueError("Not Implemented")
    
    def agents(self):
        raise ValueError("Not Implemented")
    
    __repr__ = __str__
    

class AtomAction(Action):
    '''[atom_action]formula'''
    def __init__(self, name, agent=None):
        self._name = name
        self.agent = agent
    
    def __str__(self):
        return str(self._name)

    def atomize(self):
        return set([str(self)])
    
    def agents(self):
        return set([self.agent])

    __repr__ = __str__
    

class Concatenation(Action):
    '''[alpha+beta]formula is equivalent to [alpha][beta]formula'''
    def __init__(self, action1, action2):
        self.terms=[action1, action2]
        self.operator_str = "+"
        
    def atomize(self):
        return self.terms[0].atomize().union(self.terms[1].atomize())
    
    def agents(self):
        return self.terms[0].agents().union(self.terms[1].agents())


class Concurrence(Action):
    '''[alpha//beta]formula is equivalent to [alpha]formula & [beta]formula'''
    def __init__(self, action1, action2):
        if not isinstance(action1, Action) and not isinstance(action2, Action):
            raise TypeError("Concurrence must have at least one action")
        self.terms=[action1, action2]
        self.operator_str = "//"
        
    def atomize(self):
        if isinstance(self.terms[0], Action) and isinstance(self.terms[1], Action):
            return self.terms[0].atomize().union(self.terms[1].atomize())
        elif isinstance(self.terms[0], Action):
            return self.terms[0].atomize()
        else:
            return self.terms[1].atomize()
        
    def agents(self):
        if isinstance(self.terms[0], Action) and isinstance(self.terms[1], Action):
            return self.terms[0].agents().union(self.terms[1].agents())
        elif isinstance(self.terms[0], Action):
            return self.terms[0].agents()
        else:
            return self.terms[1].agents()


class Union(Action):
    '''[alpha//beta]formula is equivalent to [alpha]formula | [beta]formula'''
    def __init__(self, action1, action2):
        self.terms=[action1, action2]
        self.operator_str = "^"
        
    def atomize(self):
        return self.terms[0].atomize().union(self.terms[1].atomize())
    
    def agents(self):
        return self.terms[0].agents().union(self.terms[1].agents())
    
        
class Empty(Action):
    
    def __init__(self, action1, articulator):
        self.terms = [action1, articulator]
        self.operator_str = "-"
        
    def atomize(self):
        return self.terms[0].atomize()
    
    def agents(self):
        return self.terms[0].agents()
    

class Test(Action):
    '''[formula?]formula1 is equivalent to formula->formula1'''
    def __init__(self, term1, term2):
        if isinstance(term1, bool):
            if term1:
                term1 = top
            else:
                term1 = bottom
        
        if isinstance(term2, bool):
            if term2:
                term2 = top
            else:
                term2 = bottom 
        if not isinstance(term1, Formula):
            raise ValueError("Not a testable formula")
        elif not isinstance(term2, Formula):
            raise ValueError("Not a testable formula")
        
        self.terms = [term1, term2]
        self.operator_str = "?"

    def __str__(self):
        #return "(" + str(self.terms[0]) + " == " + str(self.terms[1]) + self.operator_str + ")"
        return str(self.terms[0]) + self.operator_str

    def atomize(self):
        return set([str(self)])
    
    def agents(self):
        return self.terms[0].agents()

    __repr__ = __str__
    
    
class TransitiveClosure(Action):
    '''[alpha*i]formula is equivalent to formula & [alpha][alpha*(i-1)]formula'''
    def __init__(self, action, i):
        self.terms=[action]
        if isinstance(i, str) or i < 0:
            self.counter = -1
            self.operator_str = "**"
        else:
            self.counter = i
            self.operator_str = "**"+str(i)
        
        # If no more repetitions, it's not a transitive closure
        if self.counter == 0:
            return action
        
    def __str__(self):
        return "(" + str(self.terms[0]) + " " + self.operator_str + ")"
    
    def atomize(self):
        return self.terms[0].atomize()
    
    def agents(self):
        return self.terms[0].agents()
    
    __repr__ = __str__


test = (lambda formula: formula % top)

skip = test(top)
fail = test(bottom)


class ModalOperator(object):
    
    def __getitem__(self, action):
        raise NotImplementedError("Operator not implemented")


class NecessityOperator(ModalOperator):
    
    def __init__(self):
        pass
    
    def __getitem__(self, action):
        if not isinstance(action, Action):
            raise TypeError("Not an action")
        return (lambda action: (lambda formula: Necessity(formula, action)))(action)
    
    
class PossibilityOperator(ModalOperator):
    
    def __init__(self):
        pass
    
    def __getitem__(self, action):
        if not isinstance(action, Action):
            #raise TypeError("Not an action")
            return (lambda first_in_seq: (lambda second_in_seq: Sequence(first_in_seq,
                                                                         second_in_seq))
                    )(action)
        return (lambda action: (lambda formula: Possibility(formula, action)))(action)

nec = NecessityOperator()
pos = PossibilityOperator()