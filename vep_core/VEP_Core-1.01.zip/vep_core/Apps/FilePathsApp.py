# coding=utf-8
from Ity.Utilities import FilePaths
import argparse


if __name__ == "__main__":
    #### Parse Input Arguments ####
    parser = argparse.ArgumentParser(description="Given several file paths as positional arguments, print out \"valid\" paths.")
    parser.add_argument('paths', type=str, nargs='+',
                        help="One or more paths a file or a folder of files.")
    parser.add_argument('-e', '--extension', type=str, metavar='EXT', dest='file_extension',
                        help="The file extension (*without* leading '.') of the files we want to filter paths by.")
    parser.add_argument('--debug', action='store_true', dest='debug',
                        help="Print debugging output.")
    #### Actually Do Things ####
    args = parser.parse_args()
    # Get the input files with the appropriate file extension.
    patterns = None
    if args.file_extension is not None:
        patterns = ("\." + args.file_extension + "$",)
    input_paths = FilePaths.valid_paths(args.paths, patterns=patterns, recursion_levels=2, debug=args.debug)
    for path in input_paths:
        print path
    if args.debug:
        print "Got %u paths." % len(input_paths)
