'''
This module contains a wrapper for Python's built-in json module to make it
easier to use.
'''

# Imports #####################################################################
import json
import re
import sys


if sys.version_info[0] == 3:
    basestring = str


###############################################################################
def container_to_ascii(item):
    '''Converts all items from unicode to ascii, where needed.  This is a
    recursive function.  You may pass in any container or object, however,
    only basic types will be converted: scalars, lists, and dictionaries.
    Everything else will be ignored.

    Examples::
        >>> print(container_to_ascii(int(4)))
        4
        >>> print(container_to_ascii(['test', u'test']))
        ['test', 'test']
        >>> print(container_to_ascii({u'one': u'test', u'two': 2, u'three':
        ... {'test': 2}, 4: [1, 2, 3, u'four']}))
        {'one': 'test', 4: [1, 2, 3, 'four'], 'three': {'test': 2}, 'two': 2}
        >>>
    '''
    result = None

    if sys.version_info[0] == 2 and type(item) is unicode:
        result = item.encode('ascii')
    elif type(item) is list:
        result = list(map(lambda x: container_to_ascii(x), item[:]))
    elif type(item) is dict:
        result = dict()
        for key, value in item.items():
            result[container_to_ascii(key)] = container_to_ascii(value)
    else:
        result = item

    return result


###############################################################################
class MyEncoder(json.JSONEncoder):
    '''Simple decoder that returns the dict of an object.'''
    def default(self, obj):
        if hasattr(obj, '__dict__'):
            return dict(obj.__dict__)
        else:
            return json.JSONEncoder.default(self, obj)


###############################################################################
class JSON(object):
    '''This object is used to load JSON data from a string or file.  It will
    remove any comment-only lines, and try to give some indication of why JSON
    failed to load (e.g. trailing comma).

    JSON reads much like Python; [] is for a list of items, {} is for a
    dictionary.

    Some important notes:

    * single-quotes (B{'}) are invalid; always use double-quotes (B{"})
    * A Python B{None} is represented by a JSON B{null}
    * A list cannot end with a trailing comma (a comma after the last item in
      the list)

    Comments:

    * JSON does not supports comments.  This functionality was added to this
      class to make life easier.

    We support the following types of comments

    * A line consisting of 0 or more whitespace characters followed by ``//``
    * Text ending a line with 1 or more whitespace characters followed
      by ``//``
    * All text in between ``/*`` and ``*/``

    Examples

        .. code-block:: python
            :linenos:

            // this line is ignored
            {"key": 5} // the rest of the line is ignored
            {"key": 5 /*,"key2": 6*/}  // key2 and the remainder is ignored
            {"key": 5}// INVALID!  At least 1 whitespace character
                      // before // for hanging comments

    '''

    RE_TRAILING_COMMA = re.compile(r',\s*[,}\]]')
    RE_MISSING_VALUE = re.compile(r':\s*[,}\]]')
    RE_MISSING_COMMA = re.compile(r'[}\]]\s*[{\[]')

    def _prep_json_string(self, string):
        '''This functions prepares the string for JSON loading.  It will:
            -  check for trailing commas and raise a ValueError if found
            -  check for missing values and raise a ValueError if found
            -  remove all comments
            -  return an array of lines split on "\n" (so self.load errors make
                more sense)
        '''
        # Remove all comments
        string = re.sub(re.compile(r'((^\s*//|\s+//).*?$)|(/\*.*?\*/)',
                                   flags=re.MULTILINE | re.DOTALL),
                        '', string)

        # Check for trailing commas
        if self.RE_TRAILING_COMMA.search(string):
            location = string.find(
                self.RE_TRAILING_COMMA.search(string).group(0))
            context = string[location - 40:location + 10]
            raise ValueError("Trailing comma found in JSON string near: " +
                             context)

        # Check for missing values
        if self.RE_MISSING_VALUE.search(string):
            location = string.find(
                self.RE_MISSING_VALUE.search(string).group(0))
            context = string[location - 40:location + 10]
            raise ValueError("Missing value found in JSON string near: " +
                             context)

        # Check for missing commas
        if self.RE_MISSING_COMMA.search(string):
            location = string.find(
                self.RE_MISSING_COMMA.search(string).group(0))
            context = string[location - 40:location + 10]
            raise ValueError("Missing comma found in JSON string near: " +
                             context)

        lines = string.split("\n")
        lines = [x.strip() for x in lines if x.strip()]
        return lines

    def load(self, string=None, path=None, force_ascii=True):
        '''Loads JSON data from either a string or a file.'''
        if string is None and path is None:
            raise Exception("Must pass in either string or path")

        if string:
            lines = self._prep_json_string(string)
        elif path:
            with open(path, 'rb') as pfile:
                text = pfile.read().decode()
            lines = self._prep_json_string(text)
        else:
            raise ValueError("Must enter either string or path")

        try:
            json_data = json.loads('\n'.join(lines))
        except ValueError as err:
            if re.search(r"line (\d+)", str(err)):
                line = int(re.search(r"line (\d+)", str(err)).group(1))
                context = '\n'.join(lines[line - 4:line + 4])
                if ("Expecting property name" in str(err)) and \
                   ("'" in context):
                    print("Possible invalid single-quote around here (JSON "
                          "only supports double-quotes):")
                    print(context)
                elif "Expecting property name" in str(err):
                    print("Possible trailing comma somewhere around here:")
                    print(context)
                else:
                    print("Error somewhere around here:")
                    print(context)
            raise

        if force_ascii:
            json_data = container_to_ascii(json_data)

        return json_data

    def store(self, data, path, cls=MyEncoder):
        '''Write the data to a JSON formatted file.'''
        if sys.version_info[0] == 3:
            bytedata = bytes(encode(data, cls), 'UTF-8')
        else:
            bytedata = encode(data, cls)
        with open(path, 'wb') as pfile:
            pfile.write(bytedata)


def encode(data, cls=MyEncoder):
    '''encode the provided data in JSON format'''
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '),
                      cls=cls)


class JSONComment(object):
    '''A simple object to contain information about a comment found in a JSON
    file/string.'''
    def __init__(self, _type, line_number, comment, setting=None):
        self._type = _type  # "line"  # "hanging", "inline"
        self._line_number = line_number
        self._comment = comment
        self._setting_name = setting


class CommentedJSON(JSON):
    '''This object is used to _approximately_ keep the comments in the stored
    text file.  The order and format of the original file **is not kept**.  The
    data is translated to Python native objects.  In the case of a dictionary,
    key order is not guaranteed.  This object does not attempt to re-order the
    output.

    **Known Issues**

    - Line comments not immediately preceding a setting are ignored
    - ``/*  */`` style comments are discarded
    - Block comments not associated with a setting are ignored, with the
      exception of a comment at the top of the file (called the _header_)
    - Settings with the same name will collide
    - Guaranteed not to work well with complex JSON

    **TODO**

    Find/write a proper lexer
    '''
    RE_ANY_COMMENT = re.compile(r'((^\s*//|\s+//).*?$)|(/\*.*?\*/)')
    RE_LINE_COMMENT = re.compile("^(\s*//.*)")
    RE_HANING_COMMENT = re.compile('^\s*["{}\[\]0-9].*(// .*)$')

    def __init__(self):
        super(CommentedJSON, self).__init__()

        self._comments = []
        self._header = []

    def _setting_name(self, line):
        '''Returns the name of a setting found in the line (the first item found
        that is surrounded by double-quotes).
        '''
        if CommentedJSON.RE_ANY_COMMENT.match(line):
            return
        elif re.match("^\s*\"(.*?)\"", line):
            return re.match("^\s*\"(.*?)\"", line).group(1)
        elif re.match("^\s*(.*?),", line):
            return re.match("^\s*(.*?),", line).group(1)

        return

    def _setting_line_comment(self, line):
        '''Returns any line comment for the given setting found in the line.'''
        setting = self._setting_name(line)
        if not setting:
            return

        comments = [x for x in self._comments if (
            x._setting_name and
            (setting == x._setting_name) and
            (x._type == "line"))]

        if comments:
            return comments[0]._comment

        return

    def _setting_hanging_comment(self, line):
        '''Returns any hanging comment for the given setting found in the
        line (non-comment followed by //*).'''
        setting = self._setting_name(line)
        if not setting:
            return

        comments = [x for x in self._comments if (
            x._setting_name and
            (setting == x._setting_name) and
            (x._type == "hanging"))]

        if comments:
            return comments[0]._comment

        return

    def load(self, string=None, path=None, force_ascii=True):
        '''Loads JSON data from either a string or a file.  The _template_
        of the file will be used during as_string() and store().

        :param basestring string: The string to parse
        :param basestring path: The path of the file to parse
        :param bool force_ascii: For lazy people who refuse to use unicode; the
            data returned is guaranteed to be ascii.

        :returns: JSON encoded data
        '''
        json_data = super(CommentedJSON, self).load(string, path, force_ascii)

        if string:
            lines = string.split("\n")
        elif path:
            with open(path, 'rb') as pfile:
                text = pfile.read().decode()
            lines = text.split("\n")
        else:
            raise ValueError("Must enter either string or path")

        header = True
        for index, line in enumerate(lines):
            line = line.rstrip()
            if CommentedJSON.RE_LINE_COMMENT.match(line):
                comment = CommentedJSON.RE_LINE_COMMENT.match(line).group(1)
                obj = JSONComment("line", index, comment)
                if self._setting_name(lines[index + 1]):
                    obj._setting_name = self._setting_name(lines[index + 1])

                if header:
                    self._header.append(comment)
                else:
                    self._comments.append(obj)
            elif CommentedJSON.RE_HANING_COMMENT.match(line):
                comment = CommentedJSON.RE_HANING_COMMENT.match(line).group(1)
                setting = self._setting_name(line)

                obj = JSONComment("hanging", index, comment, setting)
                self._comments.append(obj)
                header = False
            else:
                header = False

        return json_data

    def as_string(self, data, cls=MyEncoder, force_ascii=True):
        string = encode(data, cls)

        if self._header:
            result = "\n".join(self._header)
            result += "\n"
        else:
            result = ""

        lines = string.split("\n")

        for index, line in enumerate(lines):
            if self._setting_line_comment(line):
                result += "\n{0}\n{1}\n".format(
                    self._setting_line_comment(line), line)
            elif self._setting_hanging_comment(line):
                result += "{0}  {1}\n".format(
                    line, self._setting_hanging_comment(line).strip())
            else:
                result += line
                result += "\n"

        if force_ascii:
            result = container_to_ascii(result)

        return result

    def store(self, data, path, cls=MyEncoder):
        '''Write the data to a JSON formatted file while attempting to keep
        comments.'''
        if sys.version_info[0] == 3:
            bytedata = bytes(self.as_string(data, cls), 'UTF-8')
        else:
            bytedata = self.as_string(data, cls)
        with open(path, 'wb') as pfile:
            pfile.write(bytedata)
