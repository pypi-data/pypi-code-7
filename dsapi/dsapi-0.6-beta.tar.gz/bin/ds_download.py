#!/usr/bin/env python
import dsapi
import os, sys, argparse, json, urllib
import time
import pygments
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter
def main(server, dp_id, output_filename, log_level):
    api = dsapi.DataStreamAPI(server, CLIENT_ID, CLIENT_SECRET, log_level=log_level)
    api.refresh_token()
    output_file = api.export_vcf(dp_id, output_file=output_filename)
    if(output_file == None):
        print >>sys.stderr, "Unable to export VCF, sample not activated"


if __name__ == "__main__":
    (secret, client_id) = (None, None)
    if 'ING_CLIENT_SECRET' in os.environ:
        secret = os.environ['ING_CLIENT_SECRET']
    if 'ING_CLIENT_ID' in os.environ:
        client_id = os.environ['ING_CLIENT_ID']
    parser = argparse.ArgumentParser("Simple Script to check status of package", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--server', action="store", dest="server", default="https://api.ingenuity.com", help="url of upload endpoint")
    parser.add_argument('--export_vcf', action="store", dest="vcf_filename", help="optional vcf output (default DP_ID.VCF)")
    parser.add_argument('--dp_id', action="store", dest="dp_id", help="DP_ID of package")
    parser.add_argument('--client-secret', action="store", default=secret, dest="secret", help="supply client secret on the command line, or set an environment variable named ING_CLIENT_SECRET")
    parser.add_argument('--client-id', action="store", default=client_id, dest="client_id", help="supply client id on the command, or set an environment variable named ING_CLIENT_ID")
    parser.add_argument('--logging-level', action="store", dest="log_level", default="INFO", help="supplying debug will also start file logging for convenience")
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
    if args.dp_id==None:
        parser.print_help()
        print >>sys.stderr, "\n\nERROR:Please supply a DP_ID to export a vcf"
        sys.exit(1)
    if not args.vcf_filename: 
        output_filename = args.dp_id + ".vcf"
    else: 
        output_filename = args.vcf_filename
    main(args.server, args.dp_id, output_filename, args.log_level)
