'''
Created on 16 Nov 2014

@author: swest
'''

import getopt
import os


class Get():
    def __init__(self, args):
        self.args = self.opts(args[1:])
        return
    
    def inputs(self):
        punctuation = self.inputlist(self.args['p'])
        html = self.inputlist(self.args['t'])
        stopwords = self.inputlist(self.args['s'])
        inputfiles = self.inputfiles(self.args['i'])
        keywords = self.inputlist(self.args['k'])
        return punctuation, html, stopwords, inputfiles, keywords
    
    def outputfile(self):
        return self.args['o']
    
    def opts(self, options):
        shortops = 'hp:t:s:i:o:k:'
        longops = ['help', 'punctuation=', 'html=', 'stopwords=', 'input=', 'output=', 'keywords=']
        opts = getopt.getopt(options, shortops, longops)
        
        args = {'h': '', 'p': '', 't': '', 's': '', 'i': '', 'o': '', 'k': ''}
        for (opt, arg) in opts[0]:
            if opt == '-h' or opt == '--help':
                args['h'] = 'yes'
            elif opt == '-p' or opt == '--punctuation':
                args['p'] = arg
            elif opt == '-t' or opt == '--html':
                args['t'] = arg
            elif opt == '-s' or opt == '--stopwords':
                args['s'] = arg
            elif opt == '-i' or opt == '--input':
                args['i'] = arg
            elif opt == '-o' or opt == '--output':
                args['o'] = arg
            elif opt == '-k' or opt == '--keywords':
                args['k'] = arg
        return args

    def inputlist(self, arg):
        inlist = []        
        infile = open(arg, 'r')
        for line in infile:
            inlist.append(line.replace('\n', ''))
        return inlist
    
    def inputfiles(self, arg):
        infiles = [] 
        context = os.walk(arg)
        for walk in context:
            for file in walk[2]:
                if file.endswith('nxml'):
                    tfile = os.path.join(walk[0], file)
                    infiles.append(tfile)
        return infiles
    
    