import serial
import argparse
from .. import ftdicbus as cbus
import itertools
import obex 
import at
import functools
import collections
import time
import re
import logging
import os
import dateutil.parser as dateparser
import sys

logger = logging.getLogger(__name__)

TIMEOUT = 3.0
BAUDRATE = 115200

MAX_CLOSE_TRY = 5

class Tc65i:
    File = collections.namedtuple('File', 'type permission owner group size modified name')
    File.aligns = '<<<<><<'
    def __init__(self, ser):
        self.obex_mode = False
        self.ser = ser

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self._close_obex()

    def _open_obex(self):
        if not self.obex_mode:
            at.send(self.ser, 'AT\\Q3')
            at.send(self.ser, 'AT^SQWE=0')
            at.send(self.ser, 'AT^SQWE=3')
            obex.connect(self.ser)
            self.obex_mode = True
            logger.info('obex mode opened')

    def _close_obex(self):
        if self.obex_mode:
            obex.disconnect(self.ser)
            for close_try in xrange(MAX_CLOSE_TRY):
                try:
                    logger.debug('trying ({} left) to close obex mode'.format(close_try))
                    at.send(self.ser, '+++', term_char='', timeout=1)
                    break
                except at.ATException, e:
                    pass
                    
            if close_try == MAX_CLOSE_TRY:
                raise IOError('Cannot close obex mode. tc65i does not respond to +++ after %d tries' % MAX_CLOSE_TRY)
            at.send(self.ser, 'ATE')
            self.obex_mode = False
            logger.info('obex mode closed')

    def obexer(f):
        def actual(*args, **kwargs):
            self = args[0]
            if not self.obex_mode:
                self._open_obex()
            args = (self.ser,) + args[1:]
            return getattr(obex, f.__name__)(*args, **kwargs)
        return functools.wraps(f)(actual)

    def ater(f):
        def actual(*args, **kwargs):
            self = args[0]
            if self.obex_mode:
                self._close_obex()
            args = (self.ser,) + args[1:]
            return getattr(at, f.__name__)(*args, **kwargs)
        return functools.wraps(f)(actual)

    @ater
    def send(*args, **kwargs): pass

    @ater
    def getconfig(*args, **kwargs): pass

    @obexer
    def getfile(*args, **kwargs): pass

    @obexer
    def putfile(*args, **kwargs): pass
    
    @obexer
    def listdir(*args, **kwargs): pass

    @obexer
    def changedir(*args, **kwargs): pass
    
    @obexer
    def removeobject(*args, **kwargs): pass

    @obexer
    def erasestorage(*args, **kwargs): pass
    
    @obexer
    def makedir(*args, **kwargs): pass

    @obexer
    def proctriplet(*args, **kwargs): pass
    
    @obexer
    def abort(*args, **kwargs): pass
   
    def freespace(self):
        return self.proctriplet(obex.Triplet.frombytes([0x32, 0x01, 0x02]))

    def totalspace(self):
        return self.proctriplet(obex.Triplet.frombytes([0x32, 0x01, 0x01]))

    def lsconfig(self):
        res = []
        p = re.compile('("[^\"]*")')
        for e in self.getconfig():
            confstr = p.findall(e)
            if confstr:
                res.append('AT^SCFG={},{}'.format(confstr[0], ','.join(confstr[1:])))
        return '\n'.join(res)

    def lsall(self, dir=None, parent=''):
        def check_perm(p, ctx):
            return p if p in ctx else '-'
            
        def ls_perms(ctx):
            return check_perm('R', ctx) + check_perm('W', ctx) + check_perm('D', ctx)

        rootelem = self.listdir()
        if len(rootelem) == 0:
            return []
        
        files = []
        for child in rootelem:
            up = child.attrib.get('user-perm', '')
            gp = child.attrib.get('group-perm', '')
            op = child.attrib.get('other-perm', '')
            mod = child.attrib.get('modified', '')
            if mod:
                mod = dateparser.parse(mod)
            perm =  ('d' if child.tag == 'folder' else '-') + ls_perms(up) + ls_perms(gp) + ls_perms(op)
            name = child.attrib.get('name', '')
            file = Tc65i.File(
                child.attrib.get('type', ''),
                perm,
                child.attrib.get('owner', ''),
                child.attrib.get('group', ''),
                child.attrib.get('size', '0'),
                mod,
                parent+'/'+ name,
                )
            files.append(file)
            if file.permission[0] == 'd' and 'R' in file.permission:
                self.changedir(dir=name)
                kids = self.lsall(parent=(file.name))
                self.changedir("..")
                files += kids
        return files

    @classmethod
    def formatfiles(cls, files):

        def max_item_len(items, ind):
            return max([len(str(item[ind])) for item in items])

        titles = map(str.capitalize, cls.File._fields)
        files_str = [tuple(map(str, f._asdict().values())) for f in files]
        max_lengths = [max_item_len([titles] + files_str, i) for i in range(len(titles))]
        titlef_str = ' '.join(['{{:^{}}}'] * len(max_lengths)).format(*max_lengths)
        f_str = ' '.join(['{{:{}{}}}'] * len(max_lengths)).format(*itertools.chain(*zip(cls.File.aligns, max_lengths)))
        file_list = [f_str.format(*file) for file in files_str]
        return '\n'.join([titlef_str.format(*titles)] + file_list)

def print_settings(modem, *args):
    print(modem.lsconfig())

def list_dir(modem, param, args):
    files = modem.lsall()
    print('Available {} of {} bytes'.format(modem.freespace(), modem.totalspace()))
    print(modem.formatfiles(files))

def put_file(modem, path, args):
    destpath = args.destination + '/' + os.path.basename(path)
    with open(path, 'r') as f:
        modem.removeobject(destpath)
        modem.putfile(destpath, f)
    logger.info('transferred {} to {}'.format(path, destpath))

def get_file(modem, path, args):
    destfile = open(args.destination, 'w') if args.destination != '' else sys.stdout
    try:
        destfile.write(modem.getfile(path))
    finally:
        if args.destination != '': destfile.close()

def make_dir(modem, dir, args):
    logger.info('creating ' + dir)
    modem.makedir(dir)

def remove(modem, file, args):
    logger.info('deleting ' + file)
    modem.removeobject(file)

def format(modem, param, args):
    logger.info('formatting ...')
    modem.erasestorage()
    logger.info('formatted')

def run(modem, path, args):
    logger.info('running {} ...'.format(path))
    m = re.match('(a\:)?\/*(.*)', path)
    res = modem.send('AT^SJRA="a:/{}"'.format(m.group(2)))
    logger.info('AT result: {}'.format(res))

def abort(modem, *args):
    logger.info('aborting ...')
    modem.abort()

def atcmd(modem, command, args):
    logger.info('running at command {} ...'.format(command))
    res = modem.send(command)
    logger.info(res)

def dump(modem, *args):
    while True:
        sys.stdout.write(modem.ser.read(1))
        sys.stdout.flush()

class Run(argparse.Action):
    def __init__(self,
        option_strings,
        dest, **kwargs):
        super(Run, self).__init__(option_strings, dest, **kwargs)
        self.func = getattr(kwargs, 'func', None)
    def __call__(self, parser, namespace, values, option_string=None):
        if not hasattr(namespace, 'actions'):
            namespace.actions = []
        if len(values) == 0:
            pairs = [(self,None)]
        elif isinstance(values, basestring):
            pairs = [(self,values)]
        else:
            pairs = [(self,v) for v in values]
        namespace.actions.extend(pairs)

def main():

    root_logger = logging.getLogger('')
    handler = logging.StreamHandler()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.ERROR)

    parser = argparse.ArgumentParser()
    act_grp = parser.add_argument_group('available commands (all are recursive)')
    act_grp.add_argument('-ls', '--list-dir', 
        help='list directory contents', action=Run, nargs=0).func = list_dir
    act_grp.add_argument('-pf', '--put-file', metavar='FILE', nargs='+',
        help='put file (to remote --destination directory optionally)', action=Run).func = put_file
    act_grp.add_argument('-gf', '--get-file', metavar='PATH', nargs='+',
        help='get file (to local --destination directory optionally)', action=Run).func = get_file
    act_grp.add_argument('-rm', '--remove', metavar='PATH', nargs='+',
        help='delete file or directory', action=Run).func = remove
    act_grp.add_argument('-md', '--make-dir', metavar='PATH', nargs='+',
        help='create new directory', action=Run).func = make_dir
    act_grp.add_argument('-fm', '--format', action=Run, nargs=0,
        help='erase entire storage').func = format
    act_grp.add_argument('-ru', '--run', action=Run, metavar='PATH', nargs=1,
        help='run jar').func = run
    act_grp.add_argument('-ab', '--abort', action=Run, nargs=0,
        help='abort running application').func = abort
    act_grp.add_argument('-at', '--exec-at', action=Run, metavar='AT_COMMAND', nargs='+',
        help='execute AT command and print the result').func = atcmd
    act_grp.add_argument('-ps', '--print-settings', 
        help='print settings', action=Run, nargs=0).func = print_settings
    act_grp.add_argument('-du', '--dump', 
        help='dump from modem', action=Run, nargs=0).func = dump

    dbg_grp = parser.add_mutually_exclusive_group()
    dbg_grp.add_argument('-d', '--debug', action='store_true', help='print debugging information')
    dbg_grp.add_argument('-v', '--verbose', action='store_true', help='try to be a bit more verbose')

    parser.add_argument('-n', '--no-cbus', action='store_true', help='do not change cbus pins')
    parser.add_argument('-D', '--destination', metavar='PATH', help='destination directory', default='')
    parser.add_argument('-p', '--port', metavar='DEVICE', help='serial device to connect', required=True)
    
    args = parser.parse_args()

    if not hasattr(args, 'actions'):
        print('No commands defined')
        parser.print_help()
        return
    
    if args.verbose:
        root_logger.setLevel(logging.INFO)
    if args.debug:
        handler.setFormatter(logging.Formatter('[%(filename)s:%(lineno)d] %(message)s'))
        root_logger.setLevel(logging.DEBUG)

    if not args.no_cbus:
        cbus.set_cbus_pins(args.port, cbus.TC65I_MODE)
    try:
        with serial.serial_for_url(args.port) as ser:
            ser.timeout = TIMEOUT
            ser.baudrate = 115200
            with Tc65i(ser) as modem:
                for action, param in args.actions if hasattr(args, 'actions') else []:
                    action.func(modem, param, args)
    finally:
        if not args.no_cbus:
            cbus.set_cbus_pins(args.port, cbus.MSP430_UART_MODE)

if __name__ == '__main__':
    main()