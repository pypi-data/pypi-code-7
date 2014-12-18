import json
import urllib
from requests import get, post, put, delete
from mxit import settings
from mxit.exceptions import MxitAPIException


class BaseService():
    def __init__(self, oauth):
        self.oauth = oauth


class MessagingService(BaseService):
    def send_message(self, app_mxit_id, target_user_ids, message='', contains_markup=True,
                     spool=None, spool_timeout=None, links=None, scope='message/send'):
        """
        Send a message (from a Mxit app) to a list of Mxit users
        """

        data = {
            'From': app_mxit_id,
            'To': ",".join(target_user_ids),
            'Body': message,
            'ContainsMarkup': contains_markup
        }

        if spool:
            data['Spool'] = spool
        if spool_timeout:
            data['SpoolTimeOut'] = spool_timeout
        if links:
            data['Links'] = links

        return _post(
            token=self.oauth.get_app_token(scope),
            uri='/message/send',
            data=data
        )

    def send_user_to_user_message(self, from_user_id, target_user_ids, message='', contains_markup=True,
                                  scope='message/user'):
        """
        Send a message (from a Mxit user) to a list of Mxit users
        """
        return _post(
            token=self.oauth.get_user_token(scope),
            uri='/message/send',
            data={
                'From': from_user_id,
                'To': ",".join(target_user_ids),
                'Body': message,
                'ContainsMarkup': contains_markup
            }
        )

    def create_redirect_link(self, create_temporary_contact, target_service, text,
                             add_to_back_history=None, parameters=None):
        data = {
            'CreateTemporaryContact': create_temporary_contact,
            'TargetService': target_service,
            'Text': text
        }
        if add_to_back_history:
            data['AddToBackHistory'] = add_to_back_history;
        if parameters:
            data['Parameters'] = parameters;
        return data


class UserService(BaseService):
    def get_user_id(self, mxit_id, scope='profile/public'):
        """
        Retrieve the Mxit user's internal "user ID"
        No user authentication required
        """
        user_id = _get(
            token=self.oauth.get_app_token(scope),
            uri='/user/lookup/' + urllib.quote(mxit_id)
        )

        if user_id.startswith('"') and user_id.endswith('"'):
            user_id = user_id[1:-1]

        return user_id

    def get_status(self, mxit_id, scope='profile/public'):
        """
        Retrieve the Mxit user's current status
        No user authentication required
        """
        status = _get(
            token=self.oauth.get_app_token(scope),
            uri='/user/public/statusmessage/' + urllib.quote(mxit_id)
        )

        if status.startswith('"') and status.endswith('"'):
            status = status[1:-1]

        return status

    def set_status(self, message, scope='status/write'):
        """
        Set the Mxit user's status
        User authentication required with the following scope: 'status/write'
        """
        return _put(
            token=self.oauth.get_user_token(scope),
            uri='/user/statusmessage',
            data=message
        )

    def get_display_name(self, mxit_id, scope='profile/public'):
        """
        Retrieve the Mxit user's display name
        No user authentication required
        """
        display_name = _get(
            token=self.oauth.get_app_token(scope),
            uri='/user/public/displayname/' + urllib.quote(mxit_id)
        )

        if display_name.startswith('"') and display_name.endswith('"'):
            display_name = display_name[1:-1]

        return display_name

    def get_avatar(self, mxit_id, output_file_path=None, scope='profile/public'):
        """
        Retrieve the Mxit user's avatar
        No user authentication required
        """
        data = _get(
            token=self.oauth.get_app_token(scope),
            uri='/user/public/avatar/' + urllib.quote(mxit_id)
        )

        if output_file_path:
            with open(output_file_path, 'w') as f:
                f.write(data)
        else:
            return data

    def set_avatar(self, data=None, input_file_path=None, scope='avatar/write',
                   content_type='application/octet-stream'):
        """
        Set the Mxit user's avatar
        User authentication required with the following scope: 'avatar/write'
        """
        if input_file_path:
            with open(input_file_path, 'rb') as f:
                data = f.read()

        if not data:
            raise ValueError('Either the data of an image file or the path to an image file must be provided')

        return _post(
            token=self.oauth.get_user_token(scope),
            uri='/user/avatar',
            data=data,
            content_type=content_type,
        )

    def delete_avatar(self, scope='avatar/write'):
        """
        Delete the Mxit user's avatar
        User authentication required with the following scope: 'avatar/write'
        """
        return _delete(
            token=self.oauth.get_user_token(scope),
            uri='/user/avatar'
        )

    def get_basic_profile(self, user_id, scope='profile/public'):
        """
        Retrieve the Mxit user's basic profile
        No user authentication required
        """
        profile = _get(
            token=self.oauth.get_app_token(scope),
            uri='/user/profile/' + urllib.quote(user_id)
        )

        try:
            return json.loads(profile)
        except:
            raise MxitAPIException('Error parsing profile data')

    def get_full_profile(self, scope='profile/private'):
        """
        Retrieve the Mxit user's full profile
        User authentication required with the following scope: 'profile/private'
        """
        profile = _get(
            token=self.oauth.get_user_token(scope),
            uri='/user/profile'
        )

        try:
            return json.loads(profile)
        except:
            raise MxitAPIException('Error parsing profile data')

    def update_profile(self, about_me=None, display_name=None, email=None, first_name=None, gender=None, last_name=None,
                       mobile_number=None, relationship_status=None, title=None, where_am_i=None,
                       scope='profile/write'):
        """
        Update the Mxit user's profile
        User authentication required with the following scope: 'profile/write'
        """

        data = {}
        if about_me:
            data['AboutMe'] = about_me
        if display_name:
            data['DisplayName'] = display_name
        if email:
            data['Email'] = email
        if first_name:
            data['FirstName'] = first_name
        if gender:
            data['Gender'] = gender
        if last_name:
            data['LastName'] = last_name
        if mobile_number:
            data['MobileNumber'] = mobile_number
        if relationship_status:
            data['RelationshipStatus'] = relationship_status
        if title:
            data['Title'] = title
        if where_am_i:
            data['WhereAmI'] = where_am_i

        if data:
            _put(
                token=self.oauth.get_user_token(scope),
                uri='/user/profile',
                data=data
            )

    def add_contact(self, contact_id, scope='contact/invite'):
        """
        Add a contact
        contact_id can either be the mxit ID of a service or a Mxit user
        User authentication required with the following scope: 'contact/invite'
        """
        return _put(
            token=self.oauth.get_user_token(scope),
            uri='/user/socialgraph/contact/' + urllib.quote(contact_id)
        )

    def get_contact_list(self, list_filter, skip=None, count=None, scope='graph/read'):
        """
        Retrieve the Mxit user's full contact list
        User authentication required with the following scope: 'graph/read'
        """
        params = {
            'filter': list_filter
        }
        if skip:
            params['skip'] = skip
        if count:
            params['count'] = count

        contact_list = _get(
            token=self.oauth.get_user_token(scope),
            uri='/user/socialgraph/contactlist?' + urllib.urlencode(params)
        )

        try:
            return json.loads(contact_list)
        except:
            raise MxitAPIException('Error parsing contact_list data')

    def get_friend_suggestions(self, scope='graph/read'):
        """
        Retrieve the Mxit user's full profile
        User authentication required with the following scope: 'graph/read'
        """
        suggestions = _get(
            token=self.oauth.get_user_token(scope),
            uri='/user/socialgraph/suggestions'
        )

        try:
            return json.loads(suggestions)
        except:
            raise MxitAPIException('Error parsing suggestions data')

    def get_gallery_folder_list(self, scope='content/read'):
        """
        Retrieve a list of the Mxit user's gallery folders
        User authentication required with the following scope: 'content/read'
        """
        folder_list = _get(
            token=self.oauth.get_user_token(scope),
            uri='/user/media'
        )
        try:
            return json.loads(folder_list)
        except:
            raise MxitAPIException('Error parsing gallery folder list')

    def create_gallery_folder(self, folder_name, scope='content/write'):
        """
        Create a new folder in the Mxit user's gallery
        User authentication required with the following scope: 'content/write'
        """
        return _post(
            token=self.oauth.get_user_token(scope),
            uri='/user/media/' + urllib.quote(folder_name)
        )

    def delete_gallery_folder(self, folder_name, scope='content/write'):
        """
        Delete a folder in the Mxit user's gallery
        User authentication required with the following scope: 'content/write'
        """
        return _delete(
            token=self.oauth.get_user_token(scope),
            uri='/user/media/' + urllib.quote(folder_name)
        )

    def rename_gallery_folder(self, old_folder_name, new_folder_name, scope='content/write'):
        """
        Rename a folder in the Mxit user's gallery
        User authentication required with the following scope: 'content/write'
        """
        return _put(
            token=self.oauth.get_user_token(scope),
            uri='/user/media/' + urllib.quote(old_folder_name),
            data=new_folder_name
        )

    def delete_gallery_file(self, file_id, scope='content/write'):
        """
        Delete a file in the Mxit user's gallery
        User authentication required with the following scope: 'content/write'
        """
        return _delete(
            token=self.oauth.get_user_token(scope),
            uri='/user/media/file/' + urllib.quote(file_id)
        )

    def rename_gallery_file(self, file_id, new_file_name, scope='content/write'):
        """
        Rename a file in the Mxit user's gallery
        User authentication required with the following scope: 'content/write'
        """
        return _put(
            token=self.oauth.get_user_token(scope),
            uri='/user/media/file/' + urllib.quote(file_id),
            data=new_file_name
        )

    def upload_gallery_file(self, folder_name, file_name, data=None, input_file_path=None,
                            prevent_share=False, content_type="image/png", scope='content/write'):
        """
        Upload a file to a folder in the Mxit user's gallery
        User authentication required with the following scope: 'content/write'
        """
        if input_file_path:
            with open(input_file_path, 'rb') as f:
                data = f.read()

        if not data:
            raise ValueError('Either the data of a file or the path to a file must be provided')

        params = {
            'fileName': file_name,
            'preventShare': 'true' if prevent_share else 'false',
        }

        return _post(
            token=self.oauth.get_user_token(scope),
            uri='/user/media/file/' + urllib.quote(folder_name) + '?' + urllib.urlencode(params),
            data=data,
            content_type=content_type,
        )

    def get_gallery_item_list(self, folder_name, skip=None, count=None, scope='content/read'):
        """
        Get the item listing in a given folder in the Mxit user's gallery
        User authentication required with the following scope: 'content/read'
        """

        params = {}
        if skip:
            params['skip'] = skip
        if count:
            params['count'] = count

        qs = '?' + urllib.urlencode(params) if params else ''

        folder_item_list = _get(
            token=self.oauth.get_user_token(scope),
            uri='/user/media/list/' + urllib.quote(folder_name) + qs
        )
        try:
            return json.loads(folder_item_list)
        except:
            raise MxitAPIException('Error parsing gallery folder list')

    def get_gallery_file(self, file_id, output_file_path=None, scope='content/read'):
        """
        Get a file in the Mxit user's gallery
        User authentication required with the following scope: 'content/read'
        """
        data = _get(
            token=self.oauth.get_user_token(scope),
            uri='/user/media/content/' + urllib.quote(file_id)
        )

        if output_file_path:
            with open(output_file_path, 'w') as f:
                f.write(data)
        else:
            return data

    def upload_file_and_send_file_offer(self, file_name, user_id, data=None, input_file_path=None,
                                        content_type='application/octet-stream', auto_open=False,
                                        prevent_share=False, scope='content/send'):
        """
        Upload a file of any type to store and return a FileId once file offer has been sent.
        No user authentication required
        """
        if input_file_path:
            with open(input_file_path, 'rb') as f:
                data = f.read()

        if not data:
            raise ValueError('Either the data of a file or the path to a file must be provided')

        params = {
            'fileName': file_name,
            'userId': user_id,
            'autoOpen': 'true' if auto_open else 'false',
            'preventShare': 'true' if prevent_share else 'false',
        }

        return _post(
            token=self.oauth.get_app_token(scope),
            uri='/user/media/file/send?' + urllib.urlencode(params),
            data=data,
            content_type=content_type
        )

    def send_file_offer(self, file_id, user_id, auto_open=False, scope='content/send'):
        """
        Send an offer to a user for content to be downloaded.
        User authentication required with the following scope: 'content/write'
        """

        params = {
            'UserId': user_id,
            'autoOpen': 'true' if auto_open else 'false'
        }

        return _post(
            token=self.oauth.get_app_token(scope),
            uri='/user/media/file/send/' + urllib.quote(file_id) + '?' + urllib.urlencode(params)
        )

    def get_cover_image(self, output_file_path=None, scope='profile/public'):
        """
        Retrieve the Mxit user's cover image
        No user authentication required
        """
        data = _get(
            token=self.oauth.get_user_token(scope),
            uri='/user/cover'
        )

        if output_file_path:
            with open(output_file_path, 'w') as f:
                f.write(data)
        else:
            return data

    def set_cover_image(self, data=None, input_file_path=None, scope='avatar/write',
                        content_type='application/octet-stream'):
        """
        Set the Mxit user's cover image
        User authentication required with the following scope: 'avatar/write' (cover image and avatars are treated the same)
        """
        if input_file_path:
            with open(input_file_path, 'rb') as f:
                data = f.read()

        if not data:
            raise ValueError('Either the data of an image file or the path to an image file must be provided')

        return _post(
            token=self.oauth.get_user_token(scope),
            uri='/user/cover',
            data=data,
            content_type=content_type,
            )


# Helpers

CONTACT_LIST_FILTER = {
    'all': '@All',
    'friends': '@Friends',
    'apps': '@Apps',
    'invites': '@Invites',
    'connections': '@Connections',
    'rejected': '@Rejected',
    'pending': '@Pending',
    'deleted': '@Deleted',
    'blocked': '@Blocked',
}


def _get(token, uri, content_type='application/json', api_endpoint=settings.API_ENDPOINT):
    headers = {
        'Content-Type': content_type,
        'Accept': content_type,
        'Authorization': 'Bearer ' + token
    }

    r = get(api_endpoint + uri, headers=headers)

    response = ''
    for chunk in r.iter_content():
        response += chunk

    if r.status_code != 200:
        raise MxitAPIException("Unexpected HTTP Status: %s" % r.status_code,
                               {'response': response, 'code': r.status_code})

    return response


def _post(token, uri, data={}, content_type='application/json', api_endpoint=settings.API_ENDPOINT):
    headers = {
        'Content-Type': content_type,
        'Accept': content_type,
        'Authorization': 'Bearer ' + token
    }

    if 'json' in content_type:
        data = json.dumps(data)

    r = post(api_endpoint + uri, data=data, headers=headers)

    response = ''
    for chunk in r.iter_content():
        response += chunk

    if r.status_code != 200:
        raise MxitAPIException("Unexpected HTTP Status: %s" % r.status_code,
                               {'response': response, 'code': r.status_code})

    return response


def _put(token, uri, data={}, content_type='application/json', api_endpoint=settings.API_ENDPOINT):
    headers = {
        'Content-Type': content_type,
        'Accept': content_type,
        'Authorization': 'Bearer ' + token
    }

    if 'json' in content_type:
        data = json.dumps(data)

    r = put(api_endpoint + uri, data=data, headers=headers)

    response = ''
    for chunk in r.iter_content():
        response += chunk

    if r.status_code != 200:
        raise MxitAPIException("Unexpected HTTP Status: %s" % r.status_code,
                               {'response': response, 'code': r.status_code})

    return response


def _delete(token, uri, content_type='application/json', api_endpoint=settings.API_ENDPOINT):
    headers = {
        'Content-Type': content_type,
        'Accept': content_type,
        'Authorization': 'Bearer ' + token
    }

    r = delete(api_endpoint + uri, headers=headers)

    response = ''
    for chunk in r.iter_content():
        response += chunk

    if r.status_code != 200:
        raise MxitAPIException("Unexpected HTTP Status: %s" % r.status_code,
                               {'response': response, 'code': r.status_code})

    return response
