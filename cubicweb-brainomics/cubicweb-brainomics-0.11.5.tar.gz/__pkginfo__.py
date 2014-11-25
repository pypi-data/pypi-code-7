# pylint: disable=W0622
"""cubicweb-brainomics application packaging information"""

modname = 'brainomics'
distname = 'cubicweb-brainomics'

numversion = (0, 11, 5)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'Cube for the Brainomics Project, see http://www.brainomics.net/'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ =  {'cubicweb': '>= 3.18.5',
                'cubicweb-questionnaire': '>= 0.7.0',
                'cubicweb-neuroimaging': '>= 0.7.0',
                'cubicweb-genomics': '>= 0.10.0',
                'cubicweb-medicalexp': '>= 0.12.2',
                'cubicweb-card': None,
                'cubicweb-bootstrap': '>= 0.6.0',
                'cubicweb-squareui': '>= 0.3.5',
                'cubicweb-comment': None,
                'cubicweb-jqplot': None,
                'cubicweb-clinipath': '>= 0.2.2',
                }
__recommends__ = {'cubicweb-vtimeline': '>= 0.5.0'}


from os import listdir as _listdir
from os.path import join, isdir
from glob import glob

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', modname)

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')
            and not isdir(join(dirpath, fname))]

data_files = [
    # common files
    [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
    ]
# check for possible extended cube layout
for dname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'wdoc',
              'i18n', 'migration', 'importers',
              'data/bootstrap', 'data/bootstrap/css', 'data/bootstrap/img',
              'data/images', 'data/img',
              'data/SlickGrid', 'data/Slickgrid/controls',
              'data/SlickGrid/images', 'data/SlickGrid/plugins'):
    if isdir(dname):
        data_files.append([join(THIS_CUBE_DIR, dname), listdir(dname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package

