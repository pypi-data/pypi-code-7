#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""
=========================================================================
        msproteomicstools -- Mass Spectrometry Proteomics Tools
=========================================================================

Copyright (c) 2013, ETH Zurich
For a full list of authors, refer to the file AUTHORS.

This software is released under a three-clause BSD license:
 * Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
 * Neither the name of any author or any participating institution
   may be used to endorse or promote products derived from this software
   without specific prior written permission.
--------------------------------------------------------------------------
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL ANY OF THE AUTHORS OR THE CONTRIBUTING
INSTITUTIONS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------
$Maintainer: Hannes Roest$
$Authors: Hannes Roest$
--------------------------------------------------------------------------
"""

from xml.etree.cElementTree import iterparse
from lxml.etree import iterparse as xiterparse
import xml.etree.cElementTree as etree
import re
import base64
import struct
from struct import unpack
import numpy


def get_chr_idx2(filename, chunksize=8192, lookback_size=100):
    # Will fast parse through the file and find all occurences of <chromatogram
    # id=... using regex and store it in a dictionary.
    chrom_positions = {}
    chromcnt = -1
    # regexes to be used
    import re 
    chromexp = re.compile("<\s*chromatogram\s*id=\"([^\"]*)\"")
    chromcntexp = re.compile("<\s*chromatogramList\s*count=\"([^\"]*)\"")
    # open file
    fh = open(filename, "rb") 
    prev_chunk = ""
    while True:
         # read a chunk of data
        offset = fh.tell()
        chunk = fh.read(chunksize)
        if not chunk: break
         # append a part of the previous chunk since we have cut in the middle
         # of text (to make sure we dont miss anything)
        if len(prev_chunk) > 0:
            chunk = prev_chunk[-lookback_size:] + chunk
            offset -= lookback_size
        prev_chunk = chunk
        # find all occurencecs of chromexp and add to the dictionary
        for m in chromexp.finditer(chunk):
            chrom_positions[m.group(1)] = offset + m.start()
        m = chromcntexp.search(chunk)
        if m is not None:
            chromcnt = int(m.group(1))
    assert chromcnt == len(chrom_positions)
    return chrom_positions

def get_chrom_index(fh):
    # Assumptions made:
    # i) there is no space between the opening tag and the first letter
    # ii) the count attribute and the id attribute are on the SAME line as <chromatogram
    # iii) there is at most one chromatogram tag per line
    chrom_positions = {}
    chromcnt = -1
    count_ex = re.compile("count=\"(\d*)\"")
    id_ex = re.compile("id=\"([^\"]*)\"")
    while True:
        line_offset = fh.tell()
        l = fh.readline()
        if len(l) == 0: break
        if l.find("<chromatogram") != -1:
            if l.find("<chromatogramList") != -1:
                m = count_ex.search(l)
                if m is not None:
                    chromcnt = int(m.group(1))
            else: 
                m = id_ex.search(l)
                if m is not None:
                    chrom_positions[m.group(1)] = line_offset
    assert chromcnt == len(chrom_positions)
    return chrom_positions

def parse_chrom_at(source, position):
    source.seek( position ) 
    context = iterparse(source, events=("end",) )
    for event, elem in context:
        if elem.tag[ -12: ] == 'chromatogram': 
            return get_chromatogram(elem)

class Chromatogram():
    pass

def get_chromatogram(e):
    chrom = Chromatogram()
    for child in e.getchildren():
        if child.tag == 'precursor':
            pass
        if child.tag == 'product':
            pass
        if child.tag == 'userParam':
            pass
        if child.tag == 'cvParam':
            pass
        if child.tag == 'binaryDataArrayList':
            for array in child.getchildren():
                compression = False
                datatype = "?"
                content = "?"
                for t in array.getchildren():
                    if t.tag == 'binary':
                        data = t.text
                    if t.tag == 'cvParam':
                        # print t.tag, t.get("name")
                        accession = t.get("accession")
                        # print accession 
                        # print accession == "MS:1000523"
                        if accession == "MS:1000521":
                            datatype = 32
                        elif accession == "MS:1000523":
                            datatype = 64
                        elif accession == "MS:1000574":
                            compression = True
                        elif accession == "MS:1000576":
                            compression = False
                        elif accession == "MS:1000514":
                            content = "mz"
                        elif accession == "MS:1000515":
                            content = "intensity"
                        elif accession == "MS:1000595":
                            content = "time"
                #
                if compression:
                    raise Exception("Cannot handle compression")
                decoded = base64.standard_b64decode(t.text)
                # 1.3455 s until here = 25% of all time
                # 
                # byte order is always little endian (<)
                # print datatype
                if datatype == 32:
                    res = [unpack('<f', decoded[i:i+4]) for i in range(0, len(decoded), 4)] 
                elif datatype == 64:
                    res = [unpack('<d', decoded[i:i+8]) for i in range(0, len(decoded), 8)] 
                else:
                    raise Exception("Unknown datatype"), datatype
                # 5.33 s until here = 100% of all time
                if content == "intensity":
                    chrom.intensity = res
                elif content == "time":
                    chrom.time = res
    return chrom
