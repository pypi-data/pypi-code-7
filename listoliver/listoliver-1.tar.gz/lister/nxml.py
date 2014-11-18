'''
Created on 16 Nov 2014

@author: swest
'''

import xml.etree.ElementTree as et
import urllib.request as ur


class NXMLFile():
    def __init__(self, inputfile, html, punctuation, stopwords):
        self.inputfilepath = inputfile
        self.html = html
        self.rem = html + punctuation + stopwords
        return
    
    def parsefile(self):
        if 'http:' in self.inputfilepath or 'ftp' in self.inputfilepath:
            infile = ur.urlopen(self.inputfilepath)
        else:
            infile = open(self.inputfilepath, 'r')
        
        context = et.iterparse(infile, events=('start', 'end'))
        #context = iter(context)
        #print(type(context))
        #event, root = context.next()
        
        pmid = ''
        abstract = ''
        hits = []
        for event, element in context:
            if event == 'end' and \
               (element.tag == 'article-id' or element.tag == 'pub-id') and \
               element.attrib['pub-id-type'] == 'pmid':
                pmid = element.text
            elif event == 'end' and \
               element.tag == 'pub-id':
                pmid = element.text
            #elif event == 'end' and element.tag == 'article-title':
            #    title = element.text
            elif event == 'end' and element.tag == 'abstract':
                abstract = '\n'.join([x.text for x in element.findall('p')])
                element.clear()
                if pmid and abstract:
                    abstract = self.cleaner(abstract)
                    hits.append((pmid, abstract))
                pmid = ''
                abstract = ''
        infile.close()
        return hits
    
    def cleaner(self, abstract):
        #title = ' '.join([x for x in title.split(' ') if x not in self.html])
        abstract = ' '.join([x for x in abstract.split(' ') if x not in self.html])
        return abstract
    
    
        