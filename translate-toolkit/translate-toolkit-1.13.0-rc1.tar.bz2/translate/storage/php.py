#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2004-2008 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Classes that hold units of PHP localisation files :class:`phpunit` or
entire files :class:`phpfile`. These files are used in translating many
PHP based applications.

Only PHP files written with these conventions are supported:

.. code-block:: php

   <?php
   $lang['item'] = "vale";  # Array of values
   $some_entity = "value";  # Named variables
   define("ENTITY", "value");
   $lang = array(
      'item1' => 'value1'    ,   #Supports space before comma
      'item2' => 'value2',
   );
   $lang = array(    # Nested arrays
      'item1' => 'value1',
      'item2' => array(
         'key' => 'value'    ,   #Supports space before comma
         'key2' => 'value2',
      ),
   );

Nested arrays without key for nested array are not supported:

.. code-block:: php

   <?php
   $lang = array(array('key' => 'value'));

The working of PHP strings and specifically the escaping conventions which
differ between single quote (') and double quote (") characters are
implemented as outlined in the PHP documentation for the
`String type <http://www.php.net/language.types.string>`_.
"""

import logging
import re

from translate.storage import base


def phpencode(text, quotechar="'"):
    """Convert Python string to PHP escaping.

    The encoding is implemented for
    `'single quote' <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.single>`_
    and `"double quote" <http://www.php.net/manual/en/language.types.string.php#language.types.string.syntax.double>`_
    syntax.

    heredoc and nowdoc are not implemented and it is not certain whether this
    would ever be needed for PHP localisation needs.
    """
    if not text:
        return text
    if quotechar == '"':
        # \n may be converted to \\n but we don't.  This allows us to preserve
        # pretty layout that might have appeared in muliline entries we might
        # lose some "blah\nblah" layouts but that's probably not the most
        # frequent use case. See bug 588
        escapes = [
            ("\\", "\\\\"), ("\r", "\\r"), ("\t", "\\t"),
            ("\v", "\\v"), ("\f", "\\f"), ("\\\\$", "\\$"),
            ('"', '\\"'), ("\\\\", "\\"),
        ]
        for a, b in escapes:
            text = text.replace(a, b)
        return text
    else:
        return text.replace("%s" % quotechar, "\\%s" % quotechar)


def phpdecode(text, quotechar="'"):
    """Convert PHP escaped string to a Python string."""

    def decode_octal_hex(match):
        r"""decode Octal \NNN and Hex values"""
        if "octal" in match.groupdict():
            return match.groupdict()['octal'].decode("string_escape")
        elif "hex" in match.groupdict():
            return match.groupdict()['hex'].decode("string_escape")
        else:
            return match.group

    if not text:
        return text
    if quotechar == '"':
        # We do not escape \$ as it is used by variables and we can't
        # roundtrip that item.
        escapes = [
            ('\\"', '"'), ("\\\\", "\\"), ("\\n", "\n"), ("\\r", "\r"),
            ("\\t", "\t"), ("\\v", "\v"), ("\\f", "\f"),
        ]
        for a, b in escapes:
            text = text.replace(a, b)
        text = re.sub(r"(?P<octal>\\[0-7]{1,3})", decode_octal_hex, text)
        text = re.sub(r"(?P<hex>\\x[0-9A-Fa-f]{1,2})", decode_octal_hex, text)
        return text
    else:
        return text.replace("\\'", "'").replace("\\\\", "\\")


class phpunit(base.TranslationUnit):
    """A unit of a PHP file: a name, a value, and any comments associated."""

    def __init__(self, source=""):
        """Construct a blank phpunit."""
        self.escape_type = None
        super(phpunit, self).__init__(source)
        self.name = ""
        self.value = ""
        self.translation = ""
        self._comments = []
        self.source = source

    def setsource(self, source):
        """Set the source AND the target to be equal."""
        self._rich_source = None
        self.value = phpencode(source, self.escape_type)

    def getsource(self):
        return phpdecode(self.value, self.escape_type)
    source = property(getsource, setsource)

    def settarget(self, target):
        self._rich_target = None
        self.translation = phpencode(target, self.escape_type)

    def gettarget(self):
        return phpdecode(self.translation, self.escape_type)
    target = property(gettarget, settarget)

    def __str__(self):
        """Convert to a string. Double check that unicode is handled somehow."""
        source = self.getoutput()
        if isinstance(source, unicode):
            return source.encode(getattr(self, "encoding", "UTF-8"))
        return source

    def getoutput(self):
        """Convert the unit back into formatted lines for a php file."""
        return "\n".join(self._comments + ["%s='%s';\n" % (self.name, self.translation or self.value)])

    def addlocation(self, location):
        self.name = location

    def getlocations(self):
        return [self.name]

    def addnote(self, text, origin=None, position="append"):
        if origin in ['programmer', 'developer', 'source code', None]:
            if position == "append":
                self._comments.append(text)
            else:
                self._comments = [text]
        else:
            return super(phpunit, self).addnote(text, origin=origin,
                                                position=position)

    def getnotes(self, origin=None):
        if origin in ['programmer', 'developer', 'source code', None]:
            return '\n'.join(self._comments)
        else:
            return super(phpunit, self).getnotes(origin)

    def removenotes(self):
        self._comments = []

    def isblank(self):
        """Return whether this is a blank element, containing only comments."""
        return not (self.name or self.value)

    def getid(self):
        return self.name


class phpfile(base.TranslationStore):
    """This class represents a PHP file, made up of phpunits."""
    UnitClass = phpunit

    def __init__(self, inputfile=None, encoding='utf-8'):
        """Construct a phpfile, optionally reading in from inputfile."""
        super(phpfile, self).__init__(unitclass=self.UnitClass)
        self.filename = getattr(inputfile, 'name', '')
        self._encoding = encoding
        if inputfile is not None:
            phpsrc = inputfile.read()
            inputfile.close()
            self.parse(phpsrc)

    def __str__(self):
        """Convert the units back to lines."""
        lines = []
        for unit in self.units:
            lines.append(str(unit))
        return "".join(lines)

    def parse(self, phpsrc):
        """Read the source of a PHP file in and include them as units."""
        newunit = phpunit()
        lastvalue = ""
        value = ""
        invalue = False
        incomment = False
        inarray = False
        valuequote = ""  # Either ' or ".
        equaldel = "="
        enddel = ";"
        prename = ""
        keys_dict = {}
        line_number = 0

        # For each line in the PHP translation file.
        for line in phpsrc.decode(self._encoding).split("\n"):
            line_number += 1
            commentstartpos = line.find("/*")
            commentendpos = line.rfind("*/")

            # If a multiline comment starts in the current line.
            if commentstartpos != -1:
                incomment = True

                # If a comment ends in the current line.
                if commentendpos != -1:
                    newunit.addnote(line[commentstartpos:commentendpos+2],
                                    "developer")
                    incomment = False
                else:
                    newunit.addnote(line[commentstartpos:], "developer")

            # If this a multiline comment that ends in the current line.
            if commentendpos != -1 and incomment:
                newunit.addnote(line[:commentendpos+2], "developer")
                incomment = False

            # If this is a multiline comment which started in a previous line.
            if incomment and commentstartpos == -1:
                newunit.addnote(line, "developer")
                continue

            # If an array starts in the current line and is using array syntax
            if (line.lower().replace(" ", "").find('array(') != -1 and
                line.lower().replace(" ", "").find('array()') == -1):
                # If this is a nested array.
                if inarray:
                    prename = prename + line[:line.find('=')].strip() + "->"
                else:
                    equaldel = "=>"
                    enddel = ","
                    inarray = True
                    prename = line[:line.find('=')].strip() + "->"
                continue

            # If an array ends in the current line, reset variables to default
            # values.
            if inarray and line.find(');') != -1:
                equaldel = "="
                enddel = ";"
                inarray = False
                prename = ""
                continue

            # If a nested array ends in the current line, reset prename to its
            # parent array default value by stripping out the last part.
            if inarray and line.find('),') != -1:
                prename = prename[:prename.find("->")+2]
                continue

            # If the current line hosts a define syntax translation.
            if line.lstrip().startswith("define("):
                equaldel = ","
                enddel = ");"

            equalpos = line.find(equaldel)
            hashpos = line.find("#")
            doubleslashpos = line.lstrip().find("//")

            # If this is a '#' comment line or a '//' comment that starts at
            # the line begining.
            if 0 <= hashpos < equalpos or doubleslashpos == 0:
                # Assume that this is a '#' comment line
                newunit.addnote(line.strip(), "developer")
                continue

            # If equalpos is present in the current line and this line is not
            # part of a multiline translation.
            if equalpos != -1 and not invalue:
                # Get the quoting character which encloses the translation
                # (either ' or ").
                valuequote = line[equalpos+len(equaldel):].lstrip()[0]

                if valuequote in ['"', "'"]:
                    # Get the location for the translation unit. prename is the
                    # array name, or blank if no array is present. The line
                    # (until the equal delimiter) is appended to the location.
                    location = prename + line[:equalpos].strip()

                    # Check for duplicate entries.
                    if location in keys_dict.keys():
                        # TODO Get the logger from the code that is calling
                        # this class.
                        logging.error("Duplicate key %s in %s:%d, first "
                                      "occurrence in line %d", location,
                                      self.filename, line_number,
                                      keys_dict[location])
                    else:
                        keys_dict[location] = line_number

                    # Add the location to the translation unit.
                    newunit.addlocation(location)

                    # Save the translation in the value variable.
                    value = line[equalpos+len(equaldel):].lstrip()[1:]
                    lastvalue = ""
                    invalue = True
            else:
                # If no equalpos is present in the current line, but this is a
                # multiline translation.
                if invalue:
                    value = line

            # Get the end delimiter position.
            enddelpos = value.rfind(enddel)

            # Process the current line until all entries on it are parsed.
            while enddelpos != -1:
                # Check if the latest non-whitespace character before the end
                # delimiter is the valuequote.
                if value[:enddelpos].rstrip()[-1] == valuequote:
                    # Save the value string without trailing whitespaces and
                    # without the ending quotes.
                    newunit.value = lastvalue + value[:enddelpos].rstrip()[:-1]
                    newunit.escape_type = valuequote
                    lastvalue = ""
                    invalue = False

                # If there is more text (a comment) after the translation.
                if not invalue and enddelpos != (len(value) - 1):
                    commentinlinepos = value.find("//", enddelpos)
                    if commentinlinepos != -1:
                        newunit.addnote(value[commentinlinepos+2:].strip(),
                                        "developer")

                # If the translation is already parsed, save it and initialize
                # a new translation unit.
                if not invalue:
                    self.addunit(newunit)
                    value = ""
                    newunit = phpunit()

                # Update end delimiter position to the previous last appearance
                # of the end delimiter, because it might be several entries in
                # the same line.
                enddelpos = value.rfind(enddel, 0, enddelpos)
            else:
                # After processing current line, if we are not in an array,
                # fall back to default dialect (PHP simple variable syntax).
                if not inarray:
                    equaldel = "="
                    enddel = ";"

            # If this is part of a multiline translation, just append it to the
            # previous translation lines.
            if invalue:
                lastvalue = lastvalue + value + "\n"
