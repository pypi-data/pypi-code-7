
# python standard library
import __builtin__
import sys



print __builtin__.open.__doc__


class FakeFile(object):
    def __init__(self, name):
        self.name = name
        return

try:        
    with FakeFile('cow') as f:
        f.write()
except AttributeError as error:
    print str(error)


class FakeFile(object):
    def __init__(self, name):
        self.name = name
        return

    def __exit__(self):
        return

try:        
    with FakeFile('cow') as f:
        f.write()
except AttributeError as error:
    print str(error)


class FakeFile(object):
    def __init__(self, name):
        self.name = name
        return

    def __enter__(self):
        return

    def __exit__(self):
        return

try:        
    with FakeFile('cow') as f:
        f.write()
except TypeError as error:
    print str(error)


class FakeFile(object):
    def __init__(self, name):
        self.name = name
        return

    def __enter__(self):
        """Setup the file"""
        self.output = sys.stdout
        return self

    def __exit__(self, type, value, traceback):
        """Tear it down"""
        self.output.flush()
        print "{0} is exited".format(self.name)
        return 

    def write(self, text):
        self.output.write(text)
        return

    def close(self):
        print "{0} is closed".format(self.name)
        self.output.close()
        return

with FakeFile('cow') as f:
    f.write("pie\n")


from contextlib import closing

class FakeFile(object):
    def __init__(self, name):
        self.name = name

    def write(self, text):
        print text

    def close(self):
        print "{0} has been closed".format(self.name)
        return

with closing(FakeFile('noexit')) as fake:
    fake.write('ummagumma')
