#-------------------------------------------------------------------------------
# Name:        open file and read
# Purpose:
#
# Author:      Lennon
#
# Created:     17/12/2014
# Copyright:   (c) Lennon 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def printDialog():
    import os
    os.chdir(r'E:\Workspace\python\nester\chap3')

    try:
        data = open("sketch.txt")

        for eachLine in data:
            try:
                (role, spokenContent) = eachLine.split(':', 1)
                print(role, end='')
                print(' said: ', end='')
                print(spokenContent, end='')
            except ValueError:
                print(eachLine, end='')

        data.close()

    except IOError:
        print("open file failed.", end='')

def main():
    printDialog()

if __name__ == '__main__':
    main()
