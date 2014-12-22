
# python standard library
import os
import string


RST_EXTENSION = '.rst'
INDEX = 'index.rst'
NEWLINE = '\n'
TOCTREE = NEWLINE + '.. toctree::'
MAXDEPTH = '   :maxdepth: {0}' + NEWLINE
HEADER = TOCTREE + NEWLINE + MAXDEPTH
CONTENTS = '   {0} <{1}>'


def grab_headline(filename):
    """
    A convenience function to grab the first non-empty line

    :param:

     - `filename`: path to a file reachable from this directory

    :return: First non-empty line stripped (or None if all are empty)
    """
    with open(filename) as f:
        for line in f:
            if len(line.strip()):
                return line.strip()


def create_toctree(maxdepth=1, subfolders=None, add_headers=False):
    """
    Sends a toctree to standard out

    :param:

     - `maxdepth`: the depth for the tree (1=module, 2=headings, etc.)
     - `subfolders`: subfolders to add (adds all if None)
     - `add_folders`: use folder names to separate sub-folders
    """
    exists = os.path.exists
    join = os.path.join
    
    contents = sorted(os.listdir(os.getcwd()))
    filenames = (name for name in contents if name.endswith(RST_EXTENSION)
                 and name != INDEX)

    print HEADER.format(maxdepth)

    for filename in filenames:
        pretty_name = grab_headline(filename)
        print CONTENTS.format(pretty_name, filename)

    subfolder_toctree(maxdepth, subfolders, add_headers)
    print
    return


def subfolder_toctree(maxdepth=1, subfolders=None, add_headers=False):
    """
    Creates the toctree for sub-folder indices

    :param:

     - `maxdepth`: Level of sub-headings to include
     - `subfolders`: iterable of sub-folders with index.rst
     - `add_headers`: True- use folder names as separators
    """
    exists = os.path.exists
    join = os.path.join
    
    contents = sorted(os.listdir(os.getcwd()))

    if subfolders is None and add_headers:
        name_indices = ((name, join(name, INDEX)) for name in contents if exists(join(name, INDEX)))
        for name, index in name_indices:
            print name + ":"
            print HEADER.format(maxdepth)
            pretty_name = grab_headline(index)
            print CONTENTS.format(pretty_name, index)
        return
    
    print HEADER.format(maxdepth)
    if subfolders is not None:
        sub_indices = (join(subfolder, INDEX) for subfolder in subfolders)
    else:
        sub_indices = (join(name, INDEX) for name in contents if exists(join(name, INDEX)))
        for sub_index in sub_indices:
            pretty_name = grab_headline(sub_index)
            print CONTENTS.format(pretty_name, sub_index)
    
    return


# python standard library
import unittest
from StringIO import StringIO

# third-party
try:
    from mock import mock_open, patch, call, MagicMock
except ImportError:
    pass    


class TestIndexBuilder(unittest.TestCase):
    def setUp(self):
        self.headline = 'Hummus Cheese'
        self.test_string = '''


{0}
-------------

        Now is the winter of our discontent,
        Made glourious summer by this Son of York.
        '''.format(self.headline)
        self.open_mock = MagicMock(name='open_mock')
        self.file_mock = MagicMock(spec=file, name='file_mock')
        self.open_mock.return_value = self.file_mock
        self.file_mock.__enter__.return_value = StringIO(self.test_string)
        self.lines = {'ummagumma':StringIO('AAAA'),
                      'aoeu':StringIO('BBBB')}
        return

    def test_grab_headline(self):
        """
        Does it grab the headline?
        """        
        open_name = '__builtin__.open'
        with patch(open_name, self.open_mock):
            filename = 'ummagumma'
            grabbed = grab_headline(filename)
            try:
                self.open_mock.assert_called_with(filename)
            except AssertionError as error:
                print self.open_mock.mock_calls
                raise
            self.assertEqual(self.headline, grabbed)

        empty_string = """




        
        """
        self.file_mock.__enter__.return_value = StringIO(empty_string)
        with patch(open_name, self.open_mock):
            self.assertIsNone(grab_headline('aoeusnth'))
        return

