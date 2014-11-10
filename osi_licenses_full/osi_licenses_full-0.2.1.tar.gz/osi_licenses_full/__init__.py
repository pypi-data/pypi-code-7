import argparse
import os
from fuzzywuzzy import process

base_dir = os.path.dirname(__file__)

def main():
    p = argparse.ArgumentParser()

    subparsers = p.add_subparsers(help="commands", dest='command')

    list_parser = subparsers.add_parser('list', help="List Available Licenses")
 
    create_parser = subparsers.add_parser('create', help="Create License File")

    create_parser.add_argument('license', nargs=1, help="License to print the text of")
    create_parser.add_argument('outfile', nargs=1, help="The File to write to")

    args = p.parse_args()

    licenseFile = os.path.join(base_dir, '..', os.sep, 'licenses', os.sep)
    licenseList = os.listdir(licenseFile)

    if args.command == "list":
        print "Available License Files"
        for license in licenseList:
            print license
        return 

    license = args.license

    licenseName = process.extractOne(license, licenseList)

    print "License File:", licenseName[0]

    licenseFile = os.path.join(licenseFile, licenseName[0])

    licenseText = None

    with open(licenseFile) as licenseFile:
        licenseText =  licenseFile.read()

    with open(args.outfile[0], 'w+') as outFile:
        outFile.write(licenseText)

    #print licenseText

if __name__ == '__main__':
    main()
