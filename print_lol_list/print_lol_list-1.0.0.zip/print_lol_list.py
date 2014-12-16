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
def print_lol(the_list):
    for item in the_list:
        if isinstance(item, list):
            print_lol(item)
        else:
            print(item)



if __name__ == '__main__':
    main()


