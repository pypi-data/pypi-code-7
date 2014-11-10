#!/usr/bin/env python
# Copyright (c) 2014, The MITRE Corporation. All rights reserved.
# For license information, see the LICENSE.txt file

import libtaxii.messages_11 as tm11
import libtaxii.clients as tc
from libtaxii.scripts import TaxiiScript


class FulfillmentClient11Script(TaxiiScript):
    parser_description = 'TAXII 1.1 Poll Fulfillment Client'
    path = '/services/poll/'

    def get_arg_parser(self, *args, **kwargs):
        parser = super(FulfillmentClient11Script, self).get_arg_parser(*args, **kwargs)
        parser.add_argument("--collection", dest="collection", default="default", help="Data Collection that this Fulfillment request applies to. Defaults to 'default'.")
        parser.add_argument("--result-id", dest="result_id", required=True, help="The result_id being requested.")
        parser.add_argument("--result-part-number", dest="result_part_number", type=int, default=1, help="The part number being requested. Defaults to '1'.")
        return parser

    def create_request_message(self, args):
        poll_fulf_req = tm11.PollFulfillmentRequest(message_id=tm11.generate_message_id(),
                                                    collection_name=args.collection,
                                                    result_id=args.result_id,
                                                    result_part_number=args.result_part_number)
        return poll_fulf_req

    def handle_response(self, response, args):
        super(FulfillmentClient11Script, self).handle_response(response, args)
        if response.message_type == MSG_POLL_RESPONSE and response.more:
            print "This response has More=True, to request additional parts, use the following command:"
            print "  fulfillment_client --collection %s --result-id %s --result-part-number %s\r\n" % \
                (response.collection_name, response.result_id, response.result_part_number + 1)


def main():
    script = FulfillmentClient11Script()
    script()

if __name__ == "__main__":
    main()
