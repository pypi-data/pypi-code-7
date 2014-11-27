from __future__ import print_function

import argparse

import data_uri.encoder

def run():

    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('--verbose', '-v',
            action='count',
            default=0,
            help='Increase Verbosity'
    )

    parser.add_argument('file',
            metavar='file',
            help='File to encode/decode'
    )

    args = parser.parse_args()

    print(data_uri.encoder.EncodeBase64(open(args.file).read()))

if __name__ == "__main__":
    run()
