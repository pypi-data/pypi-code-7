""" Exemplo de comentario com muitas linhas"""
def print_lol(mylist,ident=False,level=0):
    # outro comentario
    for e0 in mylist:
        if isinstance(e0,list):
            print_lol(e0,ident,level+1)
        else:
            if ident:
                for tab in range(level):
                    print("\t",end='')
            print(e0)
