#!/usr/bin/python
"""
pdf - a parser that deserialises PDF object graphs.

The PDF file-format is actually a generic object serialisation format - it can
represent integers, floats, strings, lists and dicts. It can efficiently store
arbitrary blocks of binary data, and it can even store mutually-recursive data
structures. The actual page-description features of the PDF format are just
conventions about which key-names to look for in which dictionaries and so
forth.

This parser is based on the syntax definitions in the PDF 1.7 specification,
also known as ISO 32000-1:2008, which is available from:

	http://www.adobe.com/devnet/pdf/pdf_reference.html

"""
import unittest
from omega import BaseParser

class PDFParser(BaseParser):
	__grammar = r"""
			# Section 7.2.2, Character Set
			whitespaceChar = '\0' | '\t' | '\n' | '\f' | '\r' | ' ' ;
			eol = '\r' '\n'? | '\n' ;

			# Section 7.2.3, Comments
			comment = '%' (~eol anything)* eol ;

			# "A conforming reader shall ignore comments, and treat them as
			# single whitespace characters."
			whitespace = (whitespaceChar | comment)* -> ' ';
		"""

if __name__ == "__main__":
	unittest.main()
