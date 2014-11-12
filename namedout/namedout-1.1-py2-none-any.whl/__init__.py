import os
import sys
import inspect
import dbglibnames

class DBG(object):
    @staticmethod
    def __call__(*args):
        stack = inspect.stack()[1]
        line = stack[4] or ''
        line = (''.join(line)).strip()
        if line:
            names = list(dbglibnames.go(line, 'dbg'))
        else:
            names = [''] * len(args)
        out = ['%s == %s\n' % (x, y) for x, y in zip(names, args)]
        sys.stdout.writelines(out)

    @staticmethod
    def __nonzero__():
        return not os.path.dirname(sys.argv[0])

dbg = DBG()

if __name__ == '__main__':
    dbg(bool(dbg))
    a = 1
    dbg(a, os.__name__, dir(os.path)[0], sys.modules.keys()[0])
    dbg(True)
