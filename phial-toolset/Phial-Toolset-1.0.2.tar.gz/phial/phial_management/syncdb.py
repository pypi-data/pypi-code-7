# -*- coding: utf-8 -*-


class   SyncDB(object):
    @staticmethod
    def initParser(parser):
        parser.add_argument('--syncdb', action='store_true', help='Create tables on database')
        return 'syncdb'

    def run(self, hdl_phial, args):
        if args.get('syncdb', False) is True:
            try:
                from peewee import OperationalError, InternalError
            except ImportError:
                print('[Phial][ERRO] Peewee is not installed')
                return True
            mod_path = '%s.models' % hdl_phial.appname
            try:
                hdl = __import__(mod_path, fromlist=[mod_path.split('.')[-1]])
                for im in getattr(hdl, '__all__', []):
                    item_hdl = getattr(hdl, im, None)
                    if item_hdl is not None:
                        try:
                            item_hdl.create_table()
                        except (OperationalError, InternalError) as e:
                            print('  --> {:.<45} {:<25}'.format('%s.%s ' % (mod_path, im), e))
                        else:
                            print('  --> {:.<45} {:<25}'.format('%s.%s ' % (mod_path, im), 'OK'))
                    else:
                        print('[Phial][WARN] Model "%s.%s" does not exist' % (mod_path, im))
            except ImportError as e:
                print('[Phial][ERRO] %s' % e)
            return True
        return False
