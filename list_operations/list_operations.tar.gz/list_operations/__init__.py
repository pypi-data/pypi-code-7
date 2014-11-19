def unnest(alist):
    store = []
    def inner(lst):
        for i in lst:
            if type(i).__name__ in ['str', 'float', 'int']:
                store.append(i)
            else:
                inner(i)
        return store
    return inner(alist)

def list2dict(lista):
    def counts(charact):
        return lista.count(charact)
    return dict(set(list(zip(lista, list(map(counts, lista))))))
