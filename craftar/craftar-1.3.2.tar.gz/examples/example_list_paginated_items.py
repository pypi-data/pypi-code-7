#  (C) Catchoom Technologies S.L.
#  Licensed under the MIT license.
#  https://github.com/catchoom/craftar-python/blob/master/LICENSE
#  All warranties and liabilities are disclaimed.

from optparse import OptionParser
import craftar

"""
Lists all your items. If needed, they can be limited to a specific collection.

- Requires an account and a collection with items at https://my.craftar.net
- The @api_key is your management api key. Get it at
https://my.craftar.net/accounts/apis/
- You can limit the result to a specific @collection.
- Don't set the @hostname, unless you are using a custom platform.
"""


def list_paginated_items(api_key, items_per_page=25, collection=None,
                         hostname=None):
    "List all items, paginated by @items_per_page"

    if hostname:
        craftar.settings.MANAGEMENT_HOSTNAME = hostname

    offset = 0

    while True:
        print("- Retrieving items %s to %s..." % (offset + 1,
                                                  offset + items_per_page))

        item_list = craftar.get_item_list(
            api_key=api_key,
            limit=items_per_page,
            offset=offset,
            collection=collection,
        )

        for i in item_list:
            print("%s: %s" % (i["uuid"], i["name"]))
        offset += items_per_page
        if len(item_list) < items_per_page:
            print("No more items!")
            return

if __name__ == '__main__':
    usage = "usage: %prog -a API_KEY [-c COLLECTION -H HOSTNAME]"
    parser = OptionParser(usage, version="%prog 1.0")
    parser.add_option('-a', '--api_key',
                      dest='api_key',
                      help="Management API key.")
    parser.add_option('-c', '--collection',
                      dest='collection',
                      default=False,
                      help='Collection UUID')
    parser.add_option('-H', '--hostname',
                      dest='hostname',
                      default=False,
                      help='CraftAR recognition API hostname')
    (options, args) = parser.parse_args()

    if not options.api_key:
        parser.error("Missing parameter: -a API_KEY")

    list_paginated_items(api_key=options.api_key,
                         collection=options.collection,
                         hostname=options.hostname)
