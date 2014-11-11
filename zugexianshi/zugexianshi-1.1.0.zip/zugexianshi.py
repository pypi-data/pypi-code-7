def zugexianshi(liebiao,shuojin=False,level=0):
    for liebiaoxian in liebiao:
        if isinstance(liebiaoxian,list):
            zugexianshi(liebiaoxian,shuojin,level+1)
        else:
            if shuojin:
                print("\t"*level,end='')
            print(liebiaoxian)

a=["a","b"]
b=["aa","bb",a]
c=[b,"aaa","bbb"]
