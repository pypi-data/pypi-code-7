"""这是我的第一个python共享模块，它只是一个简单的递归打印数组里的各项内容"""
def print_ever_in_list(Lists):
    for List in Lists:
        if isinstance(List,list):
            print_ever_in_list(List)
        else:
            print(List)
"""就是一个递归而已"""
