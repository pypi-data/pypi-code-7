#!/usr/bin/env python
import dsapi
import os, sys, argparse, json
import time
import pygments
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter
def main(server, resource_uri, log_level):
    api = dsapi.DataStreamAPI(server, CLIENT_ID, CLIENT_SECRET, log_level=log_level)
    final_output = json.dumps(api.get_package_status(resource_uri),sort_keys=True, indent=2, separators=(',', ': '))
    print pygments.highlight(final_output,JsonLexer(),TerminalFormatter(bg="dark"))



if __name__ == "__main__":
    (secret, client_id) = (None, None)
    if 'ING_CLIENT_SECRET' in os.environ:
        secret = os.environ['ING_CLIENT_SECRET']
    if 'ING_CLIENT_ID' in os.environ:
        client_id = os.environ['ING_CLIENT_ID']
    parser = argparse.ArgumentParser("Simple Script to check status of package", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--server', action="store", dest="server", default="https://api.ingenuity.com", help="url of upload endpoint")
    parser.add_argument('--status_url', action="store", dest="status_url", help="status_url_of_package")
    parser.add_argument('--dp_id', action="store", dest="dp_id", help="DP_ID of package")
    parser.add_argument('--client-secret', action="store", default=secret, dest="secret", help="supply client secret on the command line, or set an environment variable named ING_CLIENT_SECRET")
    parser.add_argument('--client-id', action="store", default=client_id, dest="client_id", help="supply client id on the command, or set an environment variable named ING_CLIENT_ID")
    parser.add_argument('--logging-level', action="store", dest="log_level", default="INFO", help="supplying debug will also start file logging for convenience")
    args = parser.parse_args()
    dp_query = args.server + "/v1/datapackages/"
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
    if args.status_url==None and args.dp_id==None:
        parser.print_help()
        print >>sys.stderr, "\n\nERROR:Please supply a status url or a DP_ID to make a status query"
        sys.exit(1)
    if args.dp_id:
        status_url = dp_query  + args.dp_id
    else:
        status_url = args.status_url
    main(args.server, status_url, args.log_level)
