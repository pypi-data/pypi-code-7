'''
Created on 17 Nov 2014

@author: swest
'''

class KeyWordSearch():
    def __init__(self):        
        self.master_list = []
        return
    
    def exact(self, pmid, abstract, keywords):
        sentences = abstract.split('. ')
        for sentence in sentences:
            for keyword in keywords:
                if keyword in (sentence.lower()).split():
                    self.master_list.append((pmid, keyword, sentence+'.'))
        return 
    
    def export(self, outputfile):
        outfile = open(outputfile, 'a')
        for line in self.master_list:
            out = '\t'.join(line) + '\n'
            outfile.write(out)
            print(out)
        outfile.close()
        return