# -*- coding: utf-8 -*-

import argparse
import sys

from dap2rpm import dap
from dap2rpm import setup

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dap', help='Name of DAP on DAPI or path to local DAP')
    parser.add_argument('-v', '--version', default=None,
        help='Name of DAP version to generate spec for; ignored with local DAP')
    args = vars(parser.parse_args())

    try:
        setup.setup()
    except:
        # TODO: log error
        sys.exit(1)

    d = dap.DAP.get_dap(args['dap'], args['version'])
    print(d.render())
