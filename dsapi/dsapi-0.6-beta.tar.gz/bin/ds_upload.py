#!/usr/bin/env python
import dsapi
import os, sys, argparse, json
import time
import pygments
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

def main(server, files_to_upload, log_level):
    api = dsapi.DataStreamAPI(server, CLIENT_ID, CLIENT_SECRET, log_level=log_level)
    for file in files_to_upload:
        print >>sys.stderr, "Starting to upload %s" % file
        api.refresh_token()
        (resource_uri, err_msg) = api.submit_one_zipfile(file)
        final_output = json.dumps(api.get_package_status(resource_uri),sort_keys=True, indent=2, separators=(',', ': '))
        print pygments.highlight(final_output,JsonLexer(),TerminalFormatter(bg="dark"))




if __name__ == "__main__":
    (secret, client_id) = (None, None)
    if 'ING_CLIENT_SECRET' in os.environ:
        secret = os.environ['ING_CLIENT_SECRET']
    if 'ING_CLIENT_ID' in os.environ:
        client_id = os.environ['ING_CLIENT_ID']
    parser = argparse.ArgumentParser("Simple Script to Upload a zip file", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--server', action="store", dest="server", default="https://api.ingenuity.com/", help="url of upload server to construct URIs with")
    parser.add_argument('--client-secret', action="store", default=secret, dest="secret", help="supply client secret on the command line, or set an environment variable named ING_CLIENT_SECRET")
    parser.add_argument('--client-id', action="store", default=client_id, dest="client_id", help="supply client id on the command, or set an environment variable named ING_CLIENT_ID")
    parser.add_argument('--logging-level', action="store", dest="log_level", default="INFO", help="supplying debug will also start file logging for convenience")
    parser.add_argument('files', metavar='file1', nargs='+', help='a file to upload', )
    args = parser.parse_args()
    if not args.secret:
        parser.print_help()
        print >>sys.stderr, "\n\nPlease set the environment variable ING_CLIENT_SECRET \
                \nto be the client secret you find on the ingenuity developers \
                \nsite. You will also need to set ING_CLIENT_ID."
        sys.exit(1)
    else:
        CLIENT_SECRET=args.secret
    if not args.client_id:
        parser.print_help() 
        print >>sys.stderr, "\n\nPlease set the environment variable ING_CLIENT_ID\
                \nto be the client ID you find on the ingenuity developers site."
        sys.exit(1)
    else:
        CLIENT_ID=args.client_id
    if args.files==None:
        parser.print_help()
        print >>sys.stderr, "\n\nERROR:Please supply a valid filename, %s does not appear to be a valid file" % args.pkg
        sys.exit(1)

    main(args.server, args.files, args.log_level)
