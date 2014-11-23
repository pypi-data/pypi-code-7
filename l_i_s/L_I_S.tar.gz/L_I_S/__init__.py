from list_operations import unnest
def LIS(l):
	l = list(map(str, l))
	assert len(set(l)) == len(l), "Input list must contain unique numbers only!"
	result = dict((x, []) for x in l)
	for i in range(len(l)-1, -1, -1):
		store = [result[l[j]] for j in range(i+1, len(l)) if float(l[i]) < float(l[j])]
		if store:
			store = gmls(store)
			for st in store:
				result[l[i]].append(l[i] + ' ' + st)
		else:
			result[l[i]].append(l[i])
	vals = list(result.values())
	return gmls(vals)

def nest(astring):
	return astring.split(' ')

def gmls(alist):
	alist = unnest(alist)
	maxlen = max(map(lambda x: len(x.split(' ')), alist))
	seqs = [seq for seq in map(nest, alist) if len(seq) == maxlen]
	return [' '.join(s) for s in seqs]
