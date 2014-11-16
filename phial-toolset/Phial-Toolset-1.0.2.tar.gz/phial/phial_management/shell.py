# -*- coding: utf-8 -*-


class   Shell(object):
    def __exec_ipython(self):
        from IPython import start_ipython
        start_ipython(argv=[])

    def __exec_bpython(self):
        import bpython
        bpython.embed()

    @staticmethod
    def initParser(parser):
        parser.add_argument('--shell', action='store_true', help='Run an interactive shell')
        return 'shell'

    def run(self, hdl_phial, args):
        if args.get('shell', False) is True:
            try:
                self.__exec_ipython()
            except ImportError:
                try:
                    self.__exec_bpython()
                except ImportError:
                    print('[Phial][ERRO] Please install IPython or BPython shell!')
            return True
        return False
