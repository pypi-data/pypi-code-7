'''这个模块是用来处理列表中数据的，提供了一个edit_list
    函数，目的是打印列表中所有的数据,这个函数可以
    处理复杂的多重嵌套列表'''

def edit_list(the_list):
    '''the_list是这个函数的参数，
    首先将数据传给the_list参数，然后对列表中每一个数据
    做判断，如果该数据是嵌套的列表那么递归调用，如果不是列表
    打印出该数据'''
    for new_list in the_list:
        if isinstance(new_list,list):
            edit_list(new_list)      
        else:
            print(new_list)
