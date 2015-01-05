"""This is the “nester.py" module, and it provides one function called
    listloop() which prints lists that may or may not include nested lists."""

def listloop(the_list, level):
    """This function takes a positional argument called “the_list", which is any
        Python list (of, possibly, nested lists). Each data item in the provided list
        is (recursively) printed to the screen on its own line.
        A second argument is used to insert tab stops when a nested list is encountered"""
    for i in the_list:
        if isinstance(i, list):
            listloop(i, level+1)
        else:
            for tab_stop in range(level):
                print("\t", end='')
            print(i)