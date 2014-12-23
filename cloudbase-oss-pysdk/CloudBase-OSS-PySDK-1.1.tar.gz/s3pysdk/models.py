#!/usr/bin/env python
#
#
# @author <a href="hoang281283@gmail.com">Minh Hoang TO</a>
# @date: 12/22/14
#
#
# ==============================================================

class Bucket:
    def __init__(self, name, owner, shared):
        self.name = name
        self.owner = owner
        self.shared = shared


class File:
    def __init__(self, bucket, file_path, download_link, direct_link):
        self.bucket = bucket
        self.file_path = file_path
        self.download_link = download_link
        self.direct_link = direct_link


class Multipart:
    def __init__(self, id, bucket, file_path, number_of_parts):
        self.id = id
        self.bucket = bucket
        self.file_path = file_path
        self.number_of_parts = number_of_parts


class Part:
    def __init__(self, id, multipart_id, part_index, length):
        self.id = id
        self.multipart_id = multipart_id
        self.part_index = part_index
        self.length = length


class DownloadLink:
    def __init__(self, link):
        self.download_link = link


class ApiError:
    def __init__(self, error):
        self.error = error
