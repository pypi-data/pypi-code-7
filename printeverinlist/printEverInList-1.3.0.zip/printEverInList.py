"""这是我的第一个python共享模块，它只是一个简单的递归打印数组里的各项内容"""
"""参数Lists为列表，level为打印每个列表内容缩进制表符数"""
def print_ever_in_list(Lists,level=0,flag=False):
    for List in Lists:
        if isinstance(List,list):
            if flag:
                print_ever_in_list(List,level+1)
            else:
                print_ever_in_list(List,level)
        else:
            for num in range(level):
                print("\t",end='')
            print(List)
"""就是一个递归而已"""
