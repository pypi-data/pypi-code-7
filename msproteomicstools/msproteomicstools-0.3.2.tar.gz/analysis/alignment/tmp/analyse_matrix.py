import csv, re
r = csv.reader(open("/tmp/align_out_matrix.csv"), delimiter="\t")
header = r.next()
runs = set([])
for headerl in header:
    if headerl == "Peptide": continue
    if headerl == "Protein": continue
    runs.update(set([headerl[headerl.find("_"):] ]) )

fields_per_run = ( len(header) -1) / len(runs) 
res = dict( [ (i,0) for i in range( len(runs) ) ] )
res_decoy = dict( [ (i,0) for i in range( len(runs) ) ] )
res_pep = dict( [ (i, set([])) for i in range( len(runs) ) ] )
res_pep_decoy = dict( [ (i, set([])) for i in range( len(runs) ) ] )
res_prot = dict( [ (i, set([])) for i in range( len(runs) ) ] )
res_prot_decoy = dict( [ (i, set([])) for i in range( len(runs) ) ] )
prot_per_pep = {}
for line in r:
    precursor = line[0]
    protein = line[1]
    peptide = precursor.split("_")[1].split("/")[0]
    peptide = re.sub('[^A-Z]+', '', peptide)
    thisline = [ (line[i], line[i+1]) for i in range(2,len(header)-1,fields_per_run)]
    intensity = [ l[0] for l in thisline]
    if precursor.find("DECOY") != -1: 
        res_decoy[ intensity.count("NA") ] += 1
        peptide = precursor.split("_")[2].split("/")[0]
        peptide = re.sub('[^A-Z]+', '', peptide)
        res_pep_decoy[ intensity.count("NA") ].update([ peptide ])
        res_prot_decoy[ intensity.count("NA") ].update([ protein ])
    else:
        res[ intensity.count("NA") ] += 1
        res_pep[ intensity.count("NA") ].update([ peptide ])
        res_prot[ intensity.count("NA") ].update([ protein ])
        if intensity.count("NA") == 0:
            t = prot_per_pep.get(protein, {})
            t[peptide] = 0
            prot_per_pep[protein] = t


for k in range(1,len(runs)):
    res_pep[k].update( res_pep[k-1] )
    res_pep_decoy[k].update( res_pep_decoy[k-1] )
    res_prot[k].update( res_prot[k-1] )
    res_prot_decoy[k].update( res_prot_decoy[k-1] )

for k in res:
    print "Present in %s runs are %s target precursors (%s decoys, %0.2f %%)" % (len(runs)-k,res[k], res_decoy[k], res_decoy[k]*100.0/(res[k]+res_decoy[k]))

for k in res:
    print "Present in %s runs are %s target peptides (%s decoys, %0.2f %%)" % (len(runs)-k,len(res_pep[k]), len(res_pep_decoy[k]), len(res_pep_decoy[k])*100.0/(len(res_pep[k])+len(res_pep_decoy[k])))

for k in res:
    print "Present in %s runs are %s target proteins (%s decoys, %0.2f %%)" % (len(runs)-k,len(res_prot[k]), len(res_prot_decoy[k]), len(res_prot_decoy[k])*100.0/(len(res_prot[k])+len(res_prot_decoy[k])))

b = [len(v) for k,v in prot_per_pep.iteritems()]
len([bb for bb in b if bb <= 1])
len([bb for bb in b if bb <= 2])
len([bb for bb in b if bb <= 3])
len([bb for bb in b if bb <= 4])
len([bb for bb in b if bb <= 5])
len(b)







