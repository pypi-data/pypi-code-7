#!/usr/bin/python
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

import csv, sys


"""
Doc :
    Convert CSV files into SQL tables and insert statements

    Original script from http://jeff.mikels.cc/posts/csv2sql-script/
"""

try:
    import win32file
except:
    win32file = None


def log(message):
    if not quiet:
        try:
            print message
        except UnicodeEncodeError:
            print message.encode("utf8")


def logError(message):
    try:
        sys.stderr.write(message + "\n")
    except UnicodeEncodeError:
        sys.stderr.write(message.encode("utf8"))


def getSQLHeader():
    return """
-- csv2sql conversion
-- http://jeff.mikels.cc
-- 
-- --------------------------------------------------------
-- 
"""



def makeCreateTable(h, example):
    global tableName
    global types
    retval = "\nDROP TABLE IF EXISTS `%s`;" % tableName
    retval += "\n-- HEADER ROW\n-- %s" % "//".join(h)
    retval += "\nCREATE TABLE `%s` (" % tableName
    retval += "\n  `id` INT NOT NULL AUTO_INCREMENT,"

    types = []
    for v,ex in zip(h, example):
        #try to figure out which type of data we have
        mytype  = 'TEXT'
        try:
            float(ex)
            mytype = 'DOUBLE'
        except: pass
        try:
            int(ex)
            mytype = 'INT'
        except: pass
        retval += "\n  `%s` %s," % (v.replace(' ','_').replace('_ID','_old_ID') , mytype)
        types.append( mytype )

    retval += "\n  PRIMARY KEY (`id`)"
    retval += "\n);\n\n"

    return retval


def makeInsert(h,r):
    global tableName
    global types
    retval = ""
    retval += "\n-- DATA ROW\n-- %s" % " / ".join(r).replace('\n','\\n').replace('\r','\\r')
    if len(r) > len(h):
        retval += "\n-- SKIPPING THIS ROW: DATA HAS MORE ELEMENTS THAN HEADER.\n"
        return retval


    while len(r) < len(h):
        r.append("")


    retval += "\nINSERT INTO `%s` (" % tableName

    for v in h[:-1]:
        if v == '_ID':
            v = '_old_ID'
        retval += "`%s`," % v.replace(' ','_')

    v = h[-1]
    retval += "`%s`) VALUES (" % v.replace(' ','_')

    for v,t in zip(r[:-1], types[:-1]):
        if t in ['INT', 'DOUBLE']: 
            retval += "%s," % v.replace("'","''")
        else: retval += "'%s'," % v.replace("'","''")

    v = r[-1]
    if types[-1] in ['INT', 'DOUBLE']: 
        retval += "%s);\n\n" % v.replace("'","''")
    else: retval += "'%s');\n\n" % v.replace("'","''")
    return retval


def printUsage():
    print """---------------------------------------------
USAGE: csv2sql.py input [output] [tableName]

If output is not specified or is '-', sql statements will be sent to stdout."

If tableName is not specified, the table name will be automatically generated
from input filename or output filename.

    'contacts.sql' --> tablename = 'contacts'.

Complete workflow:
    
    python csv2sql.py input.csv tablename.sql
    mysql --database=hroest < tablename.sql 
    """

def main(argv):
    global tableName
    global types

    if len(argv) <= 1:
        printUsage()
        return 1

    input = file(argv[1],'r')
    tableName = argv[1].replace('.csv','').replace(' ','_')

    if len(argv) == 2:
        output = sys.stdout
    else:
        if argv[2] == '-':
            output = sys.stdout
        else:
            output = file(argv[2],'w')
            tableName = argv[2].replace('.sql','').replace(' ','_')

    if len(argv) == 4:
        tableName = argv[3].replace(' ','_')

    #c = csv.reader(input,dialect='excel')
    c = csv.reader(input)

    data = []
    for row in c:
        data.append(row)

    input.close()

    header = data[0]
    
    output.write(getSQLHeader())
    output.write(makeCreateTable(header, data[1]))

    for row in data[1:]:
        #sql = "%s\n%s" % (sql,makeInsert(header, row))
        output.write(makeInsert(header, row))

    output.close()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
