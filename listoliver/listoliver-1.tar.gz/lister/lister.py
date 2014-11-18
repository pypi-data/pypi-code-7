#!/usr/bin/env python

'''
Author: Oliver Bonham-Carter
Date: 12 November 2014: lister3_ii.py (NXML reader)
Description:
    ***HAS BEEN HEAVILTY MODIFIED BY SEAN --- THE REMAINDER OF THE DESCRIPTION MAY NOT APPLY


    Sean's Copy of Lister
    Program to scan nxml pubmed article summaries files for key words. 
    
    The corpus documents are in nxml format and come from:
    ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/

'''

import sys
from lister import get
from lister import nxml
from lister import keyWordSearch as kws

class Lister():
    def __init__(self):
        return
    
    def main(self):
        g = get.Get(sys.argv)
        if g.args['h'] == 'yes': self.help(); return
        punctuation, html, stopwords, inputfiles, keywords = g.inputs()
        outputfile = g.outputfile()
        
        for inputfile in inputfiles:
            n = nxml.NXMLFile(inputfile, html, punctuation, stopwords)
            hits = n.parsefile()
            k = kws.KeyWordSearch()
            for pmid, abstract in hits:
                k.exact(pmid, abstract, keywords)
            k.export(outputfile)
        return
    
    def help(self):
        p = ''
        p += '\nHELP\n'
        p += '\tARGUMENTS\n'
        p += '\n\t\t-h\t--help\thelp\n'
        p += '\t\t-p argument\t--punctuation=\targument'
        p += '\n\nno i didnt finish writing help'
        print(p)
        return
    
def main():        
    stick = Lister()
    stick.main()        