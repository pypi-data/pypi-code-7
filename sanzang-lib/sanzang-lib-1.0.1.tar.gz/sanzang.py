# Copyright (c) 2014 the Sanzang Lib authors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""
Module for table-based translation from the CJK languages.

This module implements core functionality of the Sanzang system, including
the most common functions from Sanzang Utils. Using this module, you can
reformat CJK text, load translation tables, perform table-based string
substitution, and make table-based string translations.

"""

import re


def reflow(text):
    """
    Reformat CJK text according to its punctuation.

    Given a string, this function will reformat ("reflow") the text so that
    words and terms are not broken apart between lines. The function first
    strips out any leading margins as used by CBETA texts. It then
    collapses all line breaks, and reformats the text according to
    horizontal spacing and punctuation.

    The string to be formatted should not include any incomplete CBETA
    margins, as this formatting function can only reliably remove whole
    margins that follow the standard format.

    Margin format: X01n0020_p0404a01(00)║

    """
    # Remove CBETA margins.
    text = re.sub(r'^[T|X].*?║', '', text, flags=re.M)

    # Separate poetry from prose. If the line is short and starts with a space,
    # then add another space at the end to separate it from the following text.
    #
    text = re.sub(r'^　(.{1,15})$', '　\\1　', text, flags=re.M)

    # Collapse newlines.
    text = text.replace('\n', '')

    # Ender followed by non-ender: newline in between.
    text = re.sub(
        r'([：，；。？！」』.;:\?])([^：，；。？！」』.;:\?])',
        '\\1\n\\2', text, flags=re.M)

    # Non-starter, non-ender, followed by a starter: newline in between.
    text = re.sub(
        r'([^「『　\t：，；。？！」』.;:\?\n])([「『　\t])',
        '\\1\n\\2', text, flags=re.M)

    # Adjust newlines and return.
    if len(text) > 0 and text[-1] != '\n':
        text += '\n'
    return text


def reflow_file(fd_in, fd_out):
    """
    Reformat CJK text from one file object to another (buffered).

    Given input and output file objects, reformat CJK text from one to the
    other according to the punctuation and horizontal spacing. I/O is
    buffered for higher performance.

    """
    enders = '：，；。？！」』.;:?'
    buffer_size = 1000
    str_buf = ''
    line_n = 0

    for line in fd_in:
        line_n += 1
        str_buf = str_buf + line
        if line_n % buffer_size == 0:
            i = len(str_buf) - 1
            while i > 0:
                if str_buf[i-1] in enders and str_buf[i] not in enders:
                    fd_out.write(reflow(str_buf[:i]))
                    str_buf = str_buf[i:]
                    i = -1
                else:
                    i = i - 1
    if len(str_buf) > 0:
        fd_out.write(reflow(str_buf))


def read_table(table_fd):
    """
    Read a translation table from a file.

    Given an open file object, read a well-formatted translation table and
    return its contents to the caller. The translation table is assumed to
    be internally consistent and sorted properly according to standards for
    translation tables. Blank lines are ignored. If an individual record is
    formatted incorrectly, then a RuntimeError exception will be raised.

    """
    tab = []
    width = -1
    for line in table_fd.read().split('\n'):
        rec = [f.strip() for f in line.split('|')]
        if width != -1 and width == len(rec):
            tab.append(rec)
        elif width == -1 and len(rec) > 1:
            width = len(rec)
            tab.append(rec)
        elif line.strip() != '':
            raise RuntimeError('Table error: ' + line.strip())
    return tab


def subst(table, text):
    """
    Make 1-to-1 string substitutions using a two-column table.

    Given a translation table and a text, perform 1-to-1 string
    substitution on the text, replacing terms in the first column of the
    table with the corresponding terms in the second column. Substitution
    is performed on three forms for each term: the original term, all
    lowercase, and all uppercase.

    """
    for term1, term2 in table:
        text = text.replace(term1, term2)
        text = text.replace(term1.lower(), term2.lower())
        text = text.replace(term1.upper(), term2.upper())
    return text


def subst_file(table, fd_in, fd_out):
    """
    Make string substitutions from file to file (buffered).

    Given the contents of a two-column translation table, along with input
    and output file objects, make one-to-one string substitutions using
    buffered I/O.

    """
    buffer_size = 1000
    str_buf = ''
    line_no = 1
    for line in fd_in:
        str_buf += line
        if line_no % buffer_size == 0:
            fd_out.write(subst(table, str_buf))
            str_buf = ''
        line_no += 1
    fd_out.write(subst(table, str_buf))


def vocab(table, text):
    """
    Return a new table containing only the vocabulary in the source text.

    Create a new translation table containing only the rules that are
    relevant for the given text. This is created by checking all source
    terms against a copy of the text.

    """
    text_rules = []
    text_copy = str(text)
    for rec in table:
        if rec[0] in text_copy:
            text_copy = text_copy.replace(rec[0], '\x1f')
            text_rules.append(rec)
    return text_rules


def tr_raw(table, text):
    """
    Translate text using a table, return raw texts in a list.

    Perform translation of a text by applying the rules in a translation
    table. The result is a list of strings representing each column in the
    translation table. For example, the first element in the list will be
    the original source text, the second element will be the first target
    language, etc.

    """
    rules = vocab(table, text)
    text = text.replace('\x1f', '')
    collection = [text]
    for col_no in range(1, len(table[0])):
        trans = text
        for rec in rules:
            trans = trans.replace(rec[0], '\x1f' + rec[col_no] + '\x1f')
        trans = trans.replace('\x1f\n', '\n')
        trans = trans.replace('\x1f\x1f', ' ')
        trans = trans.replace('\x1f', ' ')
        collection.append(trans)
    return collection


def tr_fmt(table, text, start=1):
    """
    Translate text using a table, return a formatted listing string.

    Perform translation of a text by applying rules in a translation table,
    and return a formatted string. The formatted string represents the
    source text and its translations collated together and organized by
    line number and by translation table column number.

    """
    collection = tr_raw(table, text)
    for i in range(0, len(collection)):
        collection[i] = collection[i].rstrip().split('\n')
    listing = ''
    for line_no in range(0, len(collection[0])):
        for col_idx in range(0, len(table[0])):
            listing += '%d.%d|%s\n' % (
                start + line_no,
                col_idx + 1,
                collection[col_idx][line_no])
        listing += '\n'
    return listing


def tr_file(table, fd_in, fd_out):
    """
    Translate from one file to another (buffered).

    Given a table, an input file object, and an output file object, apply
    the translation table rules to the input text and write the translation
    as a formatted string to the output. This function uses buffered
    translation for higher performance.

    """
    buffer_size = 100
    str_buf = ''
    line_no = 1
    for line in fd_in:
        str_buf += line
        if line_no % buffer_size == 0:
            fd_out.write(tr_fmt(table, str_buf, line_no - buffer_size + 1))
            str_buf = ''
        line_no += 1
    position = line_no - str_buf.count('\n')
    fd_out.write(tr_fmt(table, str_buf, position))
