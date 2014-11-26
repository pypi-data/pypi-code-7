#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
"""
Lowlevel conversion API for calibre's ``ebook-convert``.
"""
import os
from textwrap import wrap
from base64 import b64encode, b64decode
from tempfile import NamedTemporaryFile as NTFile


import sh


from structures import INPUT_FORMATS, OUTPUT_FORMATS, ConversionResponse


# Functions & objects =========================================================
def convert(input_format, output_format, b64_data):
    """
    Convert `b64_data` fron `input_format` to `output_format`.

    Args:
        input_format (str):  specification of input format (pdf/epub/whatever),
                             see :attr:`INPUT_FORMATS` for list
        output_format (str): specification of output format (pdf/epub/whatever),
                             see :attr:`OUTPUT_FORMATS` for list
        b64_data (str):      base64 encoded data

    Returns:
        ConversionResponse: namedtuple structure with information about output\
                            ``format``, data (``b64_data``) and ``protocol``\
                            from conversion. Structure is defined in \
                            :class:`.ConversionResponse`.

    Raises:
        AssertionError: when bad arguments are handed over
        UserWarning: when conversion failed
    """
    # checks
    assert input_format in INPUT_FORMATS, "Unsupported input format!"
    assert output_format in OUTPUT_FORMATS, "Unsupported output format!"

    with NTFile(mode="wb", suffix="." + input_format, dir="/tmp") as ifile:
        ofilename = ifile.name + "." + output_format

        # save received data to the temporary file
        ifile.write(
            b64decode(b64_data)
        )
        ifile.flush()

        # convert file
        try:
            output = unicode(
                sh.ebook_convert(ifile.name, ofilename).__str__(),
                errors='ignore'
            )
        except sh.ErrorReturnCode_1, e:
            raise UserWarning(
                "Conversion failed:\n" +
                e.message.encode("utf-8", errors='ignore')
            )

        if output_format.upper() + " output written to" not in output:
            raise UserWarning("Conversion failed:\n" + output)

        # read the data from the converted file
        output_data = None
        with open(ofilename, "rb") as ofile:
            output_data = ofile.read()

        # remove temporary
        os.remove(ofilename),

        return ConversionResponse(
            format=output_format,
            b64_data="\n".join(wrap(b64encode(output_data), 80)),
            protocol=output
        )
