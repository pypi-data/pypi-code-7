#-------------------------------------------------------------------------------
# Name:        print_lol_list
# Purpose:
#
# Author:      Lennon
#
# Created:     16/12/2014
# Copyright:   (c) Lennon 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():
    pass

def sayHello():
    print("Hello")

def main():
    pass

#print a list
def print_lol(the_list, indent=False, level=0):
    for item in the_list:
        if isinstance(item, list):
            print_lol(item, indent, level+1)
        else:
            if indent:
                for spaceNum in range(level):
                    print('\t', end='')
            print(item)



if __name__ == '__main__':
    main()


