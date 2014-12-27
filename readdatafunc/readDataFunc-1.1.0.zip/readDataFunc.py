"""The module named readDataFunc.py"""
def readData(the_list,level):
    """This way ..."""
    for eachItem in the_list:
        if isinstance(eachItem,list)==True:
            readData(eachItem,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(eachItem)
