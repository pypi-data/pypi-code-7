
# python standard library
import textwrap
import subprocess
import shlex
from itertools import izip

# this package
from ape.infrastructure.baseclass import BaseClass
from ape.infrastructure.strings import NEWLINE, BLUE, BOLD, RED, RESET


output_documentation = __name__ == '__builtin__'


if output_documentation:
    indent = ' ' * 5
    tw = textwrap.TextWrapper(width=80, subsequent_indent=indent,
                              drop_whitespace=False)
    text = """
A Little Text:

Now is the winter of our discontent;
Made glorious summer by this Son of York;
And all the clouds that lour'd upon our house;
In the deep bosom of the ocean buried.
"""
    wrapped_text = tw.fill(text)
    print wrapped_text


if output_documentation:
    tw.initial_indent = indent
    header = 'A Little Text:\n'
    text = """
Now is the winter of our discontent;
Made glorious summer by this Son of York;
And all the clouds that lour'd upon our house;
In the deep bosom of the ocean buried.
"""
    print header
    headerless_wrapped_text = tw.fill(text)
    print headerless_wrapped_text


if output_documentation:
    tw.drop_whitespace = True    
    print header
    headerless_wrapped_text = tw.fill(text)
    print headerless_wrapped_text


if output_documentation:
    tw.initial_indent = ' ' * 4
    headerless_wrapped_text = tw.fill(text)
    print header
    print headerless_wrapped_text


if output_documentation:
    long_text = text * 100
    long_wrapped_text = tw.fill(long_text)
    command = shlex.split('echo "{0}" | less -R'.format(long_wrapped_text))

    subprocess.check_call(command)
    try:
        subprocess.check_call('ummagumma')
    except OSError as error:
        print wrapped_text    


class HelpPage(BaseClass):
    """
    A class to construct and print help-pages.
    """
    def __init__(self, sections, headers=None, wrap=70, pager='less -R',
                 body_indent="    ",
                 add_formatting=True):
        """
        HelpPage constructor

        :param:

         - `sections`: a dict of header: section-text
         - `headers` : a list of keys for the sections (in the order you want them)
         - `wrap`: Maximum width for the output
         - `pager`: Command to pipe the output to
         - `body_indent`: string to use to indent the section-text
         - `add_formatting`: If False, print without ANSI codes
        """
        self._headers = headers
        self.sections = sections
        self.wrap = wrap
        self.pager = pager
        self.body_indent = body_indent
        self.add_formatting = add_formatting        
        
        self._command = None
        self._bold_headers = None
        self._formatted_text = None
        self._text = None
        self._text_wrapper = None
        self._formatting = None
        return

    @property
    def headers(self):
        """
        The headers for the text
        """
        if self._headers is None:
            self._headers = self.sections.keys()
        return self._headers
    
    @property
    def text_wrapper(self):
        """
        TextWrapper to fill the text
        """
        if self._text_wrapper is None:
            initial_indent = self.body_indent
            self._text_wrapper = textwrap.TextWrapper(width=self.wrap,
                                                      initial_indent=initial_indent,
                                                      subsequent_indent=self.body_indent)
        return self._text_wrapper

    @property
    def formatting(self):
        """
        Dictionary of format-name: ANSI code
        """
        if self._formatting is None:
            keys = 'blue red reset bold'.split()
            values = (BLUE, RED, RESET, BOLD)
            self._formatting = dict(izip(keys, values))
        return self._formatting

    @property
    def command(self):
        """
        List of strings to send to the Popen
        """
        if self._command is None:
            self._command = shlex.split(self.pager)
        return self._command

    @property
    def bold_headers(self):
        """
        A dictionary of header: formatted bold header
        """
        bold_formatter = "{bold}{header}{bold}\n"
        if self._bold_headers is None:
            bolds = (bold_formatter.format(bold=self.formatting['bold'],
                                           header=header)
                                           for header in self.headers)
            self._bold_headers = dict(izip(self.headers, bolds))
        return self._bold_headers

    @property
    def formatted_text(self):
        """
        A dictionary of header:formatted body text
        """
        if self._formatted_text is None:
            def fill(text):
                lines = text.splitlines()
                lines = [self.text_wrapper.fill(line) for line in lines]
                return NEWLINE.join(lines)
            formatted = (self.sections[header].format(**self.formatting) for header in self.headers)
            filled = (fill(text) for text in formatted)
            self._formatted_text = dict(izip(self.headers, filled))
        return self._formatted_text
            
    @property
    def text(self):
        """
        The concatenated and formatted text
        """
        if self._text is None:
            self._text = "\n".join([self.bold_headers[header] + self.formatted_text[header]
                                    for header in self.headers])
        return self._text

    def __call__(self):
        """
        Sends the help-message to the pager
        """
        try:
            subprocess.Popen(self.command, stdin=subprocess.PIPE).communicate(self.text)
        except OSError as error:
            self.logger.debug(error)
            print self.text
        return
# end class HelpPage    


#python standard library
import unittest    


class TestHelpPage(unittest.TestCase):
    """
    Trying to mock the subprocess calls is too much

    so this just checks the attributes
    """

    def test_constructor(self):
        """
        Does it build?
        """
        arguments = {'name': 'TestHelp',
                     'short_description': 'A thing that does things.',                     
                     'synopsis': 'testhelp --option [optional]',
                     'description': 'TestHelp tests the help',
                     'configuration': "set it up an run it",
                     'options': 'Nothing is allowed. Everything is permitted.',
                     'return_value': "$45.99",
                     'errors':"OopsICrappedMyPantsError",
                     'files':'/usr/bin/testhelp.py',
                     'notes':"The fog is getting thicker. And Leon's getting larger.",
                     'bugs':"This does not work.",
                     'example':"Make a jazz noise here.",
                     'authors':"Me, myself, and I",
                     'see_also':"Nothing, this is all you need."}
        
        pager = HelpPage(headers=sorted(arguments.keys()),
                         sections=arguments)

        self.assertEqual(arguments, pager.sections)
        self.assertEqual(sorted(arguments.keys()), pager.headers)
        self.assertEqual(pager.wrap, 70)
        self.assertEqual('less -R', pager.pager)
        self.assertEqual(' ' * 4, pager.body_indent)
        self.assertEqual('less -R'.split(), pager.command)
        self.assertEqual(True, pager.add_formatting)
        return


if __name__ == '__main__':
    headers = 'title poem author source'.split()
    poem = """
    They fuck you up, your mum and dad.
        They may not mean to, but they do.
    They fill you with the faults they had
        And add some extra, just for you.
    
    But they were fucked up in their turn
        By fools in old-style hats and coats,
    Who half the time were soppy-stern
        And half at one another's throats.
    
    Man hands on misery to man.
        It deepens like a coastal shelf.
    Get out as early as you can,
        And don't have any kids yourself.
    """
    poem = textwrap.dedent(poem)
    title='{red}This Be The Verse{reset}'
    author = '{blue}Philip Larkin{reset}'
    source = 'http://www.poetryfoundation.org/poem/178055'
    sections = dict(zip(headers, (title, poem, author, source)))
    pager = HelpPage(headers = headers,
                     sections = sections)
    pager()
