
from pypsi.os import PypsiThread
import sys
import threading
import os
import readline

class FileStream(object):

    def __init__(self, path, mode):
        self.path = path
        self.mode = mode
        self.s = None

    def get_stream(self):
        if not self.s:
            self.s = open(self.path, self.mode)
        return self.s

    def cleanup(self):
        if not self.s.closed:
            self.s.close()


class StreamWrapper(object):

    def __init__(self, s):
        self.s = s

    def get_stream(self):
        return self.s

    def cleanup(self):
        if not self.s.closed:
            self.s.close()


class PypsiStdStream(object):

    def __init__(self, s, width=None):
        self.s = s
        self.width = width
        self.r = None

    def redirect(self, s, width=None):
        if s not in (self, self.s):
            self.r = (self.s, self.width)
            self.s = s
            self.width = width

    def close(self):
        if not self.s.closed and self.s.fileno() > 2:
            self.s.close()
        else:
            print("Not closing", file=sys.stderr)

        if self.r:
            print("Reloading redirect", file=sys.stderr)
            self.s, self.width = self.r
            self.r = None

    #def __iter__(self):
    #    return self.s.__iter__()

    #def __next__(self):
    #    self.s.__next__()

    def __getattr__(self, name):
        return getattr(self.s, name)

    def __setattr__(self, name, value):
        if name in ('s', 'width', 'r'):
            super(PypsiStdStream, self).__setattr__(name, value)
        else:
            setattr(self.s, name, value)


class Statement(object):

    def __init__(self, cmd, stdin, stdout, stderr, op):
        self.cmd = cmd
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.op = op
        self.rc = None

    def get_streams(self):
        return (self.stdin.get_stream(), self.stdout.get_stream(),
                self.stderr.get_stream())

    def cleanup_streams(self):
        self.stdin.cleanup()
        self.stdout.cleanup()
        self.stderr.cleanup()


class StatementThread(PypsiThread):

    def __init__(self, shell, stmt, is_primary=False):
        super(StatementThread, self).__init__()
        self.shell = shell
        self.stmt = stmt
        self.is_primary = is_primary
        self.rc = None

    def __str__(self):
        return "{} [{}, {}]".format(self.stmt.cmd, self.stmt.stdin, self.stmt.stdout)

    def run(self):
        try:
            self.setup()
            #print("Run:", self.stmt, file=sys.stderr)
        except:
            raise
            self.cleanup()
            return self.rc

        try:
            self.rc = self.shell.execute(self.stmt)
        except:
            #raise
            #import traceback
            #traceback.print_exc(file=sys.stderr)
            return self.rc
        finally:
            self.cleanup()

    def setup(self):
        if self.is_primary:
            sys.stdin.redirect(self.stmt.stdin)
            sys.stdout.redirect(self.stmt.stdout)
            sys.stderr.redirect(self.stmt.stderr)
        else:
            sys.stdin._add_proxy(self.stmt.stdin)
            sys.stdout._add_proxy(self.stmt.stdout)
            sys.stderr._add_proxy(self.stmt.stderr)

    def cleanup(self):
        try:
            
            self.stmt.stdout.close()
            self.stmt.stdin.close()
            self.stmt.stderr.close()

            if not self.is_primary:
                sys.stdin._delete_proxy()
                sys.stdout._delete_proxy()
                sys.stderr._delete_proxy()
        except:
            raise
            #import traceback
            #traceback.print_exc(file=sys.stderr._get())


def create_pipe_streams():
    stdin, stdout = os.pipe()
    return (
        os.fdopen(stdin, 'r'),
        os.fdopen(stdout, 'w')
    )


class PipeStatement(object):

    def __init__(self, shell, threads=None):
        self.shell = shell
        self.threads = threads or []

    def add(self, stmt):
        if self.threads:
            stdin, stdout = create_pipe_streams()
            stmt.stdin = stdin
            self.threads[-1].stmt.stdout = stdout
        self.threads.append(StatementThread(self.shell, stmt))

    def __nonzero__(self):
        return len(self.threads) > 0

    def run(self):
        (*bgs, fg) = self.threads
        fg.is_primary = True
        for bg in bgs:
            bg.start()
        rc = fg.run()
        return rc

    def clear(self):
        self.threads = []


    def __str__(self):
        return '\n'.join([ str(s) for s in self.threads])





def process_statements(shell, stmts):
    pipe = PipeStatement(shell)
    rc = None
    for stmt in stmts:
        if stmt.op == '|':
            pipe.add(stmt)
        else:
            if pipe:
                pipe.add(stmt)
                print(pipe)
                rc = pipe.run()
                pipe.clear()
            else:
                rc = shell.execute(stmt)

            if stmt.op == '&&' and rc != 0:
                return rc
            elif stmt.op == '||' and rc == 0:
                return rc
    return rc
    #if pipe:
    #    rc = pipe.run()
    #    return rc


class ThreadLocalProxy(object):

    def __init__(self, obj):
        self._proxies = {}
        self._add_proxy(obj)

    def _add_proxy(self, obj, tid=None):
        tid = tid or threading.get_ident()
        self._proxies[tid] = obj

    def _delete_proxy(self, tid=None):
        tid = tid or threading.get_ident()
        del self._proxies[tid]

    def _get(self, tid=None):
        tid = tid or threading.get_ident()
        return self._proxies[tid]

    #def __iter__(self):
    #    return self._get().__iter__()

    #def __next__(self):
    #    return self._get().__next__()

    def __getattr__(self, name):
        return getattr(self._get(), name)

    def __setattr__(self, name, value):
        if name in ('_proxies',):
            super(ThreadLocalProxy, self).__setattr__(name, value)
        else:
            setattr(self._get(), name, value)




def test():
    class TestShell(object):
        def execute(self, stmt):
            if stmt.cmd == 'first':
                #s = input("Command: ")
                #print(s)
                #sys.stdin._add_proxy(sys.stdin._get().s)
                #print("Goodbye:", g)
                print("Hello:", sys.stdin.readline())
                print("Goodbye:", sys.stdin.readline())
            else:
                print("Begin second")
                #for line in sys.stdin.readlines():
                #    print("From Other Thread:", line.strip())
                print("From other thread:", sys.stdin.read())
            return 0

    shell = TestShell()
    sys.stdin = ThreadLocalProxy(PypsiStdStream(sys.stdin))
    sys.stdout = ThreadLocalProxy(PypsiStdStream(sys.stdout))
    sys.stderr = ThreadLocalProxy(PypsiStdStream(sys.stderr))

    #sys.__stdin__ = sys.stdin._get()
    #sys.__stdout__ = sys.stdout._get()

    stmts = [
        Statement('first', sys.stdin._get(), sys.stdout._get(), sys.stderr._get(), '|'),
        Statement('secod', sys.stdin._get(), sys.stdout._get(), sys.stderr._get(), None)
    ]

    print(hasattr(sys.stdin, '__iter__'))

    #s = input("prompt: ")
    #print(s)

    #print("Before")
    process_statements(shell, stmts)
