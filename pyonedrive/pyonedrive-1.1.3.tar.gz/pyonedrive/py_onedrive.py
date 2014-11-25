""" minimal OneDrive API

"""

import requests


class OneDrive(object):
    """ OneDrive basic API providing helpers to ease query

    """

    def __init__(self, token, refresh_token, client_id, client_secret,
                 refresh_callback=None):
        self.token = token
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_callback = refresh_callback

    def __token_params(self, params):
        """ add an access_token to the params dict

        @param params: request's original params
        @return: the modified dict
        """
        if params:
            params['access_token'] = self.token
        else:
            params = {'access_token': self.token}
        return params

    def __bearer_headers(self):
        """ Generate an authorization header for a request

        """
        return {'Authorization': 'Bearer {token}'.format(token=self.token)}

    def __request(self, method, path, params=None, data=None, stream=False):
        """ Run a request on OneDrive APIs

        @param method: HTTP verb
        @param path: resource endpoint
        @param params: request's parameters
        @rtype: Response
        @return: API's response
        """
        url = 'https://apis.live.net/v5.0/%s' % path
        headers = None

        if method is 'get' or 'delete':
            params = self.__token_params(params)
        else:
            headers = self.__bearer_headers()

        response = self.__do_request(
            method, url, headers, params, data, stream
        )

        if response.status_code == 401:
            self.__refresh_token()
            if method is 'get' or 'delete':
                params = self.__token_params(params)
            else:
                headers = self.__bearer_headers()
            return self.__do_request(
                method, url, headers, params, data, stream
            )
        else:
            return response

    def __do_request(self, method, path, headers, params, data, stream):
        if stream:
            return requests.request(
                method, path, headers=headers, params=params, data=data,
                stream=True)
        else:
            return requests.request(
                method, path, headers=headers, params=params, data=data
            )

    def __refresh_token(self):
        """ Handles the refresh process and update with newly acquired values

        """
        refresh_data = {
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }

        response = requests.post('https://login.live.com/oauth20_token.srf',
                                 data=refresh_data).json()

        self.token = response['access_token']
        self.refresh_token = response['refresh_token']

        if self.refresh_callback:
            self.refresh_callback(self.token, self.refresh_token)

    def get_user_metadata(self):
        """ Retrieve all token's scope granted information about the user

        @rtype: Response
        @return: API's response
        """
        return self.__request('get', 'me')

    def get_user_picture(self):
        """ Retrieve the users picture (Byte Stream)

        @rtype: Response
        @return: API's response
        """
        return self.__request('get', 'me/picture')

    def get_root_folder(self):
        """ Retrieve the root folder's representation

        @rtype: Response
        @return: API's response
        """
        return self.__request('get', 'me/skydrive')

    def get_albums(self):
        """ Retrieve signed in user's albums

        @rtype: Response
        @return: API's response
        """
        return self.__request('get', 'me/albums')

    def get_shared_albums(self):
        """ Retrieve albums shared with the signed user

        @rtype: Response
        @return: API's response
        """
        return self.__request('get', 'me/skydrive/shared/albums')

    def get_folder_content_generator(self, folder_id, content_filter=None,
                                     count=20):
        """ Create a generator to browse a folder

        @param folder_id: the folder's to get content from ID
        @param content_filter: a certain content type to filter, can be
        'folders', 'albums', 'photos', 'videos', 'audio'
        @param count: number of item to get
        @return: A generator for folder items
        """
        request_params = {
            'limit': count
        }

        if content_filter:
            request_params['filter'] = content_filter

        resp = self.__request('get', '{id}/files'.format(id=folder_id),
                              params=request_params).json()

        while True:
            for content in resp['data']:
                yield content
            if not 'next' in resp['paging']:
                break
            resp = self.__request('get', resp['paging']['next'],
                                  params=request_params).json()

    def get_folder_content(self, folder_id, content_filter=None,
                           count=20, offset=0):
        """ Retrieve folder's content

        @param folder_id: folder's to get content from ID
        @param content_filter: a certain content type to filter, can be
        'folders', 'albums', 'photos', 'videos', 'audio'
        @param count: number of item to get
        @param offset: pagination offset
        @rtype: Response
        @return: API's response
        """
        request_params = {
            'limit': count,
            'offset': offset
        }

        if content_filter:
            request_params['filter'] = content_filter

        return self.__request('get', '{id}/files'.format(id=folder_id),
                              params=request_params)

    def get_shared_objects(self, content_filter=None, count=20, offset=0):
        """ Retrieve the list of objects shared with the signed user

        @param content_filter: a certain content type to filter, can be
        'folders', 'albums', 'photos', 'videos', 'audio'
        @param count: number of item to get
        @param offset: pagination offset
        @rtype: Response
        @return: API's response
        """
        request_params = {
            'limit': count,
            'offset': offset
        }

        if content_filter:
            request_params['filter'] = content_filter

        return self.__request('get', 'me/skydrive/shared',
                              params=request_params)

    def get_shared_folders(self, count=20, offset=0):
        """ Retrieve the list of folders shared with the signed user

        @param count: number of item to get
        @param offset: pagination offset
        @rtype: Response
        @return: API's response
        """
        return self.get_shared_objects(count=count, offset=offset,
                                       content_filter='folders')

    def get_most_recent(self):
        """ Retrieve the list of most recent media for the signed user

        @rtype: Response
        @return: API's response
        """
        return self.__request('get', 'me/skydrive/recent_docs')

    def get_usage_quota(self):
        """ Retrieve the used / available space ratio

        @rtype: Response
        @return: API's response
        """
        return self.__request('get', 'me/skydrive/quota')

    def get_shared_read_link(self, item_id):
        """ Generate a share link (read only) for the given item

        @param item_id: item's to share ID
        @rtype: Response
        @return: API's response
        """
        return self.__request('get', '{id}/shared_read_link'.format(id=item_id))

    def get_shared_edit_link(self, item_id):
        """ Generate a share link (read-write) for the given item

        @param item_id: item's to share ID
        @rtype: Response
        @return: API's response
        """
        return self.__request('get', '{id}/shared_edit_link'.format(
            id=item_id))

    def get_embed_link(self, item_id):
        """ Generate an embeddable iframe for the specified document

        @param item_id: item's to share ID
        @rtype: Response
        @return: API's response
        """
        return self.__request('get', '{id}/embed'.format(id=item_id))

    def get_preview(self, item_id, size='thumbnail'):
        """ Generate a preview image for the specified item

        @param item_id: the item's to preview id
        @param size: preview's type, can be 'thumbnail', 'small', 'album' or
        'normal'
        @rtype: Response
        @return: API's response
        """
        link = self.get_shared_read_link(item_id).json()['link']

        params = {
            'type': size,
            'url': link
        }

        return requests.request(
            'get',
            'https://apis.live.net/v5.0/skydrive/get_item_preview',
            params=params)

    def get_comments(self, item_id, count=20, offset=0):
        """ Retrieve a list of comment for the given item

        @param item_id: the item's to get comments from ID
        @param count: number of item to get
        @param offset: pagination offset
        @rtype: Response
        @return: API's response
        """
        request_params = {
            'limit': count,
            'offset': offset
        }
        return self.__request('get', '{id}/comments'.format(id=item_id),
                              params=request_params)

    def get_comments_generator(self, item_id, count=20):
        """ Create a generator to get comments from a specified item

        @param item_id: the item's to get related comments from
        @param count: number of comments to get
        @param offset: pagination offset
        @return: A generator for item's comments
        """
        request_params = {
            'limit': count
        }

        resp = self.__request('get', '{id}/comments'.format(id=item_id),
                              params=request_params).json()

        while True:
            for content in resp['data']:
                yield content
            if not 'next' in resp['paging']:
                break
            resp = self.__request('get', resp['paging']['next'],
                                  params=request_params).json()

    def get_tags(self, item_id, count=20, offset=0):
        """ Retrieve a list of tags for the given item

        @param item_id: the item's to get comments from ID
        @param count: number of item to get
        @param offset: pagination offset
        @rtype: Response
        @return: API's response
        """
        request_params = {
            'limit': count,
            'offset': offset
        }
        return self.__request('get', '{id}/tags'.format(id=item_id),
                              params=request_params)

    def get_tags_generator(self, item_id, count=20):
        """ Create a generator to get tags from a specified item

        @param item_id: the item's to get related tags from
        @param count: number of tags to get
        @param offset: pagination offset
        @return: A generator for item's tags
        """
        request_params = {
            'limit': count
        }

        resp = self.__request('get', '{id}/tags'.format(id=item_id),
                              params=request_params).json()

        while True:
            for content in resp['data']:
                yield content
            if not 'next' in resp['paging']:
                break
            resp = self.__request('get', resp['paging']['next'],
                                  params=request_params).json()

    def delete_item(self, item_id):
        """ Delete the requested item (file, folder, comment, etc)

        @param item_id: the item's to delete ID
        @rtype: Response
        @return: API's response
        """
        return self.__request('delete', '{id}'.format(id=item_id))

    def download_file(self, file_id):
        """ Download a file identified by its ID

        file's actual content as Bytes can be found under the content file of
        the Response, metadata are to be seeked into the headers field (file's
        name, length, content type)

        @param file_id: the file's to download ID
        @rtype: Response
        @return: API's response
        """
        return self.__request('get', '{id}/content'.format(id=file_id),
            stream=True)
