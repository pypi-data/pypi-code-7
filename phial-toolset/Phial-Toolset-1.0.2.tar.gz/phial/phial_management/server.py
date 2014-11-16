# -*- coding: utf-8 -*-


class   Server(object):
    @staticmethod
    def initParser(parser):
        parser.add_argument('--server', '-s', action='store_true', help='Run embedded HTTP server')
        return 'server'

    def run(self, hdl_phial, args):
        if args.get('server', False) is True:
            hdl_phial.runServer()
            return True
        return False
