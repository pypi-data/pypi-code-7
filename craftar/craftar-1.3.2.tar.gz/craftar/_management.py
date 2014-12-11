#  (C) Catchoom Technologies S.L.
#  Licensed under the MIT license.
#  https://github.com/catchoom/craftar-python/blob/master/LICENSE
#  All warranties and liabilities are disclaimed.

"Provides functions for accessing the CraftAR's management API."

from craftar._common import _get_object_list, _get_object, _create_object, \
    _create_object_multipart, _update_object, _delete_object
from craftar import settings


# Collections


def get_collection_list(api_key, limit, offset):
    "Return a list of collections, paginated by @limit and @offset"
    return _get_object_list(api_key, "collection", limit, offset, filter=None)


def get_collection(api_key, uuid):
    "Return a collection, identified by @uuid"
    return _get_object(api_key, "collection", uuid)


def create_collection(api_key, name):
    "Create a collection with a given @name (must be unique)"
    data = {'name': name}
    return _create_object(api_key, "collection", data)


def update_collection(api_key, uuid, name=None):
    "Update the collection name, identified by @uuid"
    data = {}
    if name is not None:
        data["name"] = name
    return _update_object(api_key, "collection", uuid, data)


def delete_collection(api_key, uuid):
    "Delete a collection, identified by @uuid"
    return _delete_object(api_key, "collection", uuid)


# Items

def get_item_list(api_key, limit, offset, collection=None):
    """Return a list of items, paginated by @limit and @offset
    Filter by @collection"""
    return _get_object_list(api_key, "item", limit, offset, filter=collection)


def get_item(api_key, uuid):
    "Return an item, identified by @uuid"
    return _get_object(api_key, "item", uuid)


def create_item(api_key, collection, name, url=None, custom=None,
                trackable=None, content=None):
    """Create a collection with a given @name, belonging to @collection.
    The fields @url, @custom, @trackable and @content are optional."""
    collection = "/api/%s/collection/%s/" % (settings.MANAGEMENT_API_VERSION,
                                             collection)
    data = {
        'collection': collection,
        'name': name,
    }
    if url is not None:
        data['url'] = url
    if custom is not None:
        data['custom'] = custom
    if trackable is not None:
        data['trackable'] = trackable
    if content is not None:
        data['content'] = content

    return _create_object(api_key, "item", data)


def update_item(api_key, uuid, name=None, url=None, custom=None,
                trackable=None, content=None):
    "Update an item, identified by @uuid"
    data = {}
    if name is not None:
        data["name"] = name
    if url is not None:
        data["url"] = url
    if custom is not None:
        data["custom"] = custom
    if trackable is not None:
        data['trackable'] = trackable
    if content is not None:
        data['content'] = content
    return _update_object(api_key, "item", uuid, data)


def delete_item(api_key, uuid):
    "Delete an item, identified by @uuid"
    return _delete_object(api_key, "item", uuid)


# Images

def get_image_list(api_key, limit, offset, item=None):
    """Return a list of images, paginated by @limit and @offset
    Filter by @item"""
    return _get_object_list(api_key, "image", limit, offset, filter=item)


def get_image(api_key, uuid):
    "Return an image, identified by @uuid"
    return _get_object(api_key, "image", uuid)


def create_image(api_key, item, filename):
    "Create an image from a @filename, belongs to @item"
    files = {'file': open(filename, 'rb')}
    item = "/api/%s/item/%s/" % (settings.MANAGEMENT_API_VERSION, item)
    data = {'item': item}
    return _create_object_multipart(api_key, "image", files, data)


def delete_image(api_key, uuid):
    "Delete an image, identified by @uuid"
    return _delete_object(api_key, "image", uuid)


# Tokens

def get_token_list(api_key, limit, offset, collection=None):
    """Return a list of tokens, paginated by @limit and @offset.
    Filter by @collection"""
    return _get_object_list(api_key, "token", limit, offset,
                            filter=collection)


def create_token(api_key, collection):
    "Create a token, belongs to @collection"
    collection = "/api/%s/collection/%s/" % (settings.MANAGEMENT_API_VERSION,
                                             collection)
    data = {'collection': collection}
    return _create_object(api_key, "token", data)


def delete_token(api_key, token):
    "Delete a token, identified by @token"
    return _delete_object(api_key, "token", token)


# Media objects

def get_media_list(api_key, limit, offset):
    """Return a list of media objects, paginated by @limit and @offset"""
    return _get_object_list(api_key, "media", limit, offset)


def get_media(api_key, uuid):
    "Return a media object, identified by @uuid"
    return _get_object(api_key, "image", uuid)


def create_media(api_key, item, filename):
    "Create a media object from a @filename, belongs to @item"
    files = {'file': open(filename, 'rb')}
    item = "/api/%s/item/%s/" % (settings.MANAGEMENT_API_VERSION, item)
    data = {'item': item}
    return _create_object_multipart(api_key, "image", files, data)


def delete_media(api_key, uuid):
    "Delete an image, identified by @uuid"
    return _delete_object(api_key, "image", uuid)
