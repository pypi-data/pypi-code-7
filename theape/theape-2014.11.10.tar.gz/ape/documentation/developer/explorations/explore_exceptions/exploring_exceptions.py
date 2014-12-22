
# python standard library
import os

# this package
from ape.commoncode.code_graphs import module_diagram, class_diagram


class FakeException(Exception):
    pass


this_file = os.path.join(os.getcwd(), 'exploring_exceptions.py')
module_diagram_file = module_diagram(module=this_file, project='exploreexception')
print ".. image:: {0}".format(module_diagram_file)


class_diagram_file = class_diagram(class_name="FakeException",
                                   level=2,
                                    filter='OTHER',
                                    module=this_file)
print ".. image:: {0}".format(class_diagram_file)


class OverrideError(Exception):
    def __init__(self, bum, phillips, message):
        self.bum = bum
        self.phillips = phillips
        self.message = message
def raise_bum_phillips(bum, phillips):
    if bum != 'tramp':
        raise OverrideError(bum=bum,
                            phillips=phillips,
                            message='I killed a {0} with my {1}'.format(bum, phillips))

try:
    raise_bum_phillips('tramp', 'pino')
    raise_bum_phillips('hobo', 'screwdriver')
except OverrideError as error:
    print "Bum Type: {0}".format(error.bum)
    print "Phillips Classification: {0}".format(error.phillips)
    print error.message


class AError(Exception):
    def __init__(self, name, rank, message):
        self.name = name
        self.rank = rank
        self.message = message
        return

class BError(AError):
    pass

class CError(BError):
    pass

class DError(BError):
    pass


def d_run(name, rank):
    """
    :raise: DError
    """
    raise DError(name=name, rank=rank, message='{0} not like'.format(name))

def c_run(name, rank):
    """
    :raise: CError
    """
    raise CError(name=name, rank=rank, message='My name is {0} and I approve this message'.format(name))

def b_run(name, rank, children):
    """
    :raise: BError
    """
    print "b_run says:"
    if children == 'c':
        try:
            c_run('cable', 'cougar')
        except CError as error:
            print error
        try:
            c_run('crusty', 'captain')
        except DError as error:
            # DError is a sibling to CError, you can't catch them
            print "This Won't Show"
    elif children == 'd':
        try:
            d_run('dan', 'donkey')
        except DError as error:
            print error
        try:
            d_run('don', 'diablo')
        except CError as error:
            #CError is a sibling to DError
            print "This won't show"
    raise BError(name, rank, '{1} says: What the hell do I do with "{0}"?'.format(children,
                                                                     name))
    
def fatal_error():
    """
    :raise: AError
    """
    raise AError('adolph', 'arschloch', "Catch this or die.")

def a_run():
    """
    Calls b_run, catches BError exceptions and below
    """
    errors = []
    try:
        # this raises a CError, child of BError
        b_run('bob', 'builder', 'c')
    except BError as error:
        errors.append(error)
    try:
        # this raises a DError, child of BError
        b_run('babe', 'bilder', 'd')        
    except BError as error:
        errors.append(error)
    try:
        # this raises a BError
        b_run('brunhilde', 'butterball', 'e')
    except BError as error:
        print error

    print "a_run says:"
    for error in errors:
        if error.name == 'don':
            print "{0} is dead".format(error.rank)
        else:
            print "I never much cared for {0} {1}.".format(error.rank,
                                                           error.name)
    # fatal_error raises AError, parent of BError
    try:
        fatal_error()
    except BError as error:
        print "This won't be seen."
        print error.message

try:
    a_run()
except AError as error:
    print "\nAError:"
    print error.message    


try:
    b_run('bob', 'builder', 'c')
except BError as error:
    print error


class AError(Exception):
    def __init__(self, name, rank, message):
        self.name = name
        self.rank = rank
        self.message = message
        return

    def __str__(self):
        return "{0}: {1}".format(self.__class__.__name__, self.message)


class BError(AError):
    pass

class B2Error(AError):
    pass

class CError(BError):
    pass

class DError(BError):
    pass


try:
    a_run()
except AError as error:
    print "Un-Caught:"
    print error
