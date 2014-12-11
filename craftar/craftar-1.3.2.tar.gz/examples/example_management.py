#  (C) Catchoom Technologies S.L.
#  Licensed under the MIT license.
#  https://github.com/catchoom/craftar-python/blob/master/LICENSE
#  All warranties and liabilities are disclaimed.

from optparse import OptionParser
from pprint import pprint
import craftar

"""
Demonstrates listing, creation, updating and deletion of every type of object
(i.e. collection, item, reference image, and collection token).

- Requires an account at https://my.craftar.net
- The @api_key is your management api key. Get it at
https://my.craftar.net/accounts/apis/
- The @filename is a valid reference image filename.
- Don't set the @hostname, unless you are using a custom platform.
"""


def run_management(api_key, filename, items_per_page=5, hostname=None):
    """
    Basic example of listing, creating, updating and finally deleting
    each type of object, using CraftAR's Management API.
    """

    if hostname:
        craftar.settings.MANAGEMENT_HOSTNAME = hostname

    print("\n- Retrieving first %s collections..." % items_per_page)
    collection_list = craftar.get_collection_list(
        api_key,
        limit=items_per_page,
        offset=0,
    )
    for collection in collection_list:
        print("%s: %s" % (collection["uuid"], collection["name"]))

    print("\n- Creating collection...")
    collection = craftar.create_collection(
        api_key,
        name="My API collection",
    )
    collection_uuid = collection["uuid"]
    pprint(collection)

    print("\n- Retrieving collection...")
    collection = craftar.get_collection(
        api_key,
        uuid=collection_uuid,
    )
    pprint(collection)

    print("\n- Updating collection...")
    new_name = "My edited API collection"
    success = craftar.update_collection(
        api_key,
        uuid=collection_uuid,
        name=new_name,
    )
    print("Updated: %s, name: '%s'" % (success, new_name))

    print("\n- Retrieving collection...")
    collection = craftar.get_collection(
        api_key,
        uuid=collection_uuid,
    )
    pprint(collection)

    print("\n- Retrieving first %s tokens..." % items_per_page)
    token_list = craftar.get_token_list(
        api_key,
        limit=items_per_page,
        offset=0,
        collection=collection_uuid,
    )
    for t in token_list:
        print("Collection: %s Token: %s" % (t["collection"], t["token"]))

    print("\n- Creating token...")
    token = craftar.create_token(
        api_key,
        collection=collection_uuid,
    )
    token_id = token["token"]
    pprint(token)

    print("\n- Deleting token...")
    success = craftar.delete_token(
        api_key,
        token=token_id,
    )
    print("Deleted: %s" % success)

    print("\n- Retrieving first %s items..." % items_per_page)
    item_list = craftar.get_item_list(
        api_key,
        limit=items_per_page,
        offset=0,
        collection=collection_uuid,
    )
    for i in item_list:
        print("%s: %s" % (i["uuid"], i["name"]))

    print("\n- Creating item...")
    item = craftar.create_item(
        api_key,
        name="My API item",
        collection=collection_uuid,
        url="http://example.com",
        custom="Lorem Ipsum",
    )
    item_uuid = item["uuid"]
    pprint(item)

    print("\n- Retrieving first %s items..." % items_per_page)
    item_list = craftar.get_item_list(
        api_key,
        limit=items_per_page,
        offset=0,
        collection=collection_uuid,
    )
    for i in item_list:
        print("%s: %s" % (i["uuid"], i["name"]))

    print("\n- Retrieving item...")
    item = craftar.get_item(
        api_key,
        uuid=item_uuid,
    )
    pprint(item)

    print("\n- Updating item...")
    new_name = "My edited API item"
    success = craftar.update_item(
        api_key,
        uuid=item_uuid,
        name=new_name,
        custom="New Lorem Ipsum",
    )
    print("Updated: %s, name: '%s'" % (success, new_name))

    print("\n- Retrieving item...")
    item = craftar.get_item(
        api_key,
        uuid=item_uuid,
    )
    pprint(item)

    print("\n- Retrieving first %s images..." % items_per_page)
    image_list = craftar.get_image_list(
        api_key,
        limit=items_per_page,
        offset=0,
        item=item_uuid,
    )
    for i in image_list:
        print("%s: %s" % (i["uuid"], i["name"]))

    print("\n- Uploading image...")
    image = craftar.create_image(
        api_key,
        item=item_uuid,
        filename=filename,
    )
    image_uuid = image["uuid"]
    pprint(image)

    print("\n- Retrieving image...")
    image = craftar.get_image(
        api_key,
        uuid=image_uuid,
    )
    print("uuid: %s" % image["uuid"])
    pprint(image)

    print("\n- Deleting image...")
    success = craftar.delete_image(
        api_key,
        uuid=image_uuid,
    )
    print("Deleted: %s" % success)

    print("\n- Deleting item...")
    success = craftar.delete_item(
        api_key,
        uuid=item_uuid,
    )
    print("Deleted: %s" % success)

    print("\n- Deleting collection...")
    success = craftar.delete_collection(
        api_key,
        uuid=collection_uuid,
    )
    print("Deleted: %s" % success)


if __name__ == '__main__':
    usage = "usage: %prog -a API_KEY -f FILENAME [-H HOSTNAME]"
    parser = OptionParser(usage, version="%prog 1.0")
    parser.add_option('-a', '--api_key',
                      dest='api_key',
                      help="Management API key.")
    parser.add_option('-f', '--filename',
                      dest='filename',
                      help='Reference image that will be uploaded')
    parser.add_option('-H', '--hostname',
                      dest='hostname',
                      default=False,
                      help='CraftAR management API hostname')
    (options, args) = parser.parse_args()

    if not options.api_key:
        parser.error("Missing parameter: -a API_KEY")

    if not options.filename:
        parser.error("Missing parameter: -f FILENAME")

    run_management(api_key=options.api_key, filename=options.filename,
                   hostname=options.hostname)
