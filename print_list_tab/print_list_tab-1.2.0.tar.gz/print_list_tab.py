"""
这是一个print_list_tab.py模块，提供了一个名为print_list()的函数
用来打印列表，其中包含或者不包含嵌套列表
"""
def print_list_tab(the_list, level=0):
    """
    这个函数有一个位置参数，名为the_list，这可以是任何Python列表
    (包含或者不包含嵌套列表)，所提供列表中的各个数据项会(递归地)
    打印在屏幕上，而且各占一行
    第二个参数名为level，用来在遇到嵌套列表时插入制表符，默认的
    缺省值为0
    """
    for each_item in the_list:
        if isinstance(each_item, list):
            print_list_tab(each_item, level+1)
        else:
            """
            使用level的值来控制使用多少个制表符
            每一层缩进显示一个TAB制表符
            """
            for tab_stop in range(level):
                print("\t", end='')
            print(each_item)
            
