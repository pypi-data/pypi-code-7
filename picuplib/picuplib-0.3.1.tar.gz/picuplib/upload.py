# -*- coding:utf8 -*-
######################## BEGIN LICENSE BLOCK ########################
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA
######################### END LICENSE BLOCK #########################
"""
This module handels the entire upload and some argument and response checking
"""

from __future__ import unicode_literals, print_function

from requests import post
from os.path import splitext, basename
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor


from picuplib.checks import (check_resize, check_rotation, check_noexif,
                             check_response, check_if_redirect)
from picuplib.globals import API_URL, USER_AGENT

class Upload(object):
    """
    Class based wrapper for uploading.
    It stores the apikey and default settings for resize, rotation
    and the noexif parameter.

    :param str apikey: Apikey needed for Autentication on picflash.
    :param str resize: Either 'og' or an allowed resolution in the following\
        format '80x80'(optional)
    :param str|degree rotation: The picture will be rotated by this Value. \
        Allowed values are 00, 90, 180, 270.(optional)
    :param boolean noexif: set to True when exif data should be purged.\
        (optional)

    :ivar str resize:
    :ivar str rotation:
    :ivar boolean noexif: If true exif data will be deleted
    """

    def __init__(self, apikey, resize='og', rotation='00', noexif=False):
        self._apikey = apikey
        self._resize = resize
        self._rotation = rotation
        self._noexif = noexif

    @property
    def resize(self):
        """getter for _resize"""
        return self._resize

    @resize.setter
    def resize(self, value):
        """setter for _resize"""
        check_resize(value)
        self._resize = value

    @property
    def rotation(self):
        """getter for _rotation"""
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        """setter for rotation"""
        check_rotation(value)
        self._rotation = value

    @property
    def noexif(self):
        """getter for _noexif"""
        return self._noexif

    @noexif.setter
    def noexif(self, value):
        """setter for _noexif"""
        check_noexif(value)
        self._noexif = value

    def upload(self, picture, resize=None, rotation=None, noexif=None):
        """
        wraps upload function

        :param str picture: Path to picture
        :param str resize: Either 'og' or an allowed resolution in the \
            folowing format: '80x80'(optional)
        :param str|degree rotation: The picture will be rotated by this Value. \
            Allowed values are 00, 90, 180, 270.(optional)
        :param boolean noexif: set to True when exif data should be purged.\
            (optional)

        """
        if not resize:
            resize = self._resize
        if not rotation:
            rotation = self._rotation
        if not noexif:
            noexif = self._noexif

        return upload(self._apikey, picture, resize, rotation, noexif)

    def remote_upload(self, picture_url, resize=None,
                      rotation=None, noexif=None):
        """
        wraps remote_upload funktion

        :param str picture_url: URL to picture allowd Protocols are: ftp,\
            http, https
        :param str resize: Either 'og' or an allowed resolution in the \
            folowing format: '80x80'(optional)
        :param str|degree rotation: The picture will be rotated by this Value. \
            Allowed values are 00, 90, 180, 270.(optional)
        :param boolean noexif: set to True when exif data should be purged.\
            (optional)

        """
        if not resize:
            resize = self._resize
        if not rotation:
            rotation = self._rotation
        if not noexif:
            noexif = self._noexif

        return remote_upload(self._apikey, picture_url,
                             resize, rotation, noexif)

def punify_filename(filename):
    """
    small hackisch workaround for unicode problems with the picflash api
    """
    path, extension = splitext(filename)
    return path.encode('punycode').decode('utf8') + extension


def upload(apikey, picture, resize='og', rotation='00', noexif=False,
           callback=None):
    """
    prepares post for regular upload

    :param str picture: Path to picture
    :param str resize: Either 'og' or an allowed resolution in the \
        folowing format: '80x80'(optional)
    :param str|degree rotation: The picture will be rotated by this Value. \
        Allowed values are 00, 90, 180, 270.(optional)
    :param boolean noexif: set to True when exif data should be purged.\
        (optional)

    """
    check_rotation(rotation)
    check_resize(resize)

    post_data = compose_post(apikey, resize, rotation, noexif)

    with open(picture, 'rb') as file_obj:
        post_data['Datei[]'] = (punify_filename(basename(picture)), file_obj)

        return do_upload(post_data, callback)

def remote_upload(apikey, picture_url, resize='og',
                  rotation='00', noexif=False):
    """
    prepares post for remote upload

    :param str picture_url: URL to picture allowd Protocols are: ftp,
        http, https
    :param str resize: Either 'og' or an allowed resolution in the \
        folowing format: '80x80'(optional)
    :param str|degree rotation: The picture will be rotated by this Value. \
        Allowed values are 00, 90, 180, 270.(optional)
    :param boolean noexif: set to True when exif data should be purged.\
        (optional)

    """
    check_rotation(rotation)
    check_resize(resize)
    url = check_if_redirect(picture_url)
    if url:
        picture_url = resolve_redirect(url)

    post_data = compose_post(apikey, resize, rotation, noexif)
    post_data['url[]'] = ('', picture_url)

    return do_upload(post_data)

def resolve_redirect(url):
    """
    recursively resolves redirects
    """
    new_url = check_if_redirect(url)
    if new_url:
        return resolve_redirect(new_url)
    return url


def compose_post(apikey, resize, rotation, noexif):
    """
    composes basic post requests
    """
    check_rotation(rotation)
    check_resize(resize)

    post_data = {
        'formatliste': ('', resize),
        'userdrehung': ('', rotation),
        'apikey': ('', apikey)
        }

    if noexif:
        post_data['noexif'] = ('', '')

    return post_data

def do_upload(post_data, callback=None):
    """
    does the actual upload also sets and generates the user agent string
    """

    encoder = MultipartEncoder(post_data)
    monitor = MultipartEncoderMonitor(encoder, callback)



    headers = {'User-Agent': USER_AGENT, 'Content-Type': monitor.content_type}
    response = post(API_URL, data=monitor, headers=headers)
    check_response(response)

    return response.json()[0]

