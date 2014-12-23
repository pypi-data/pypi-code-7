#!/usr/bin/env python
#
#
# @author <a href="hoang281283@gmail.com">Minh Hoang TO</a>
# @date: 12/22/14
#
#
# ==============================================================

import json

from connection import ApiCaller
from models import Multipart, Part, DownloadLink, ApiError


def parts_unmars(res):
    if res.status_code == 200:
        obj = json.loads(res.text)
        if obj['parts'] is not None:
            parts = []
            for p in obj['parts']:
                parts.append(Part(p['id'], p['multipartId'], p['partIndex'], p['length']))
            return parts

    return ApiError(res.text)


def part_unmars(res):
    if res.status_code == 200:
        obj = json.loads(res.text)
        if obj['id'] is not None:
            return Part(obj['id'], obj['multipart'], obj['partIndex'], obj['length'])

    return ApiError(res.text)


def multipart_unmars(res):
    if res.status_code == 200:
        obj = json.loads(res.text)
        if obj['id'] is not None:
            return Multipart(obj['id'], obj['bucket'], obj['filePath'], obj['numberOfParts'])

    return ApiError(res.text)


def download_link_unmars(res):
    if res.status_code == 200:
        obj = json.loads(res.text)
        if obj['downloadLink'] is not None:
            return DownloadLink(obj['downloadLink'])

    return ApiError(res.text)


class SingleUploadAPI(ApiCaller):
    def upload(self, bucket, file_path, payload):
        headers = {'Content-Type': 'application/octet-stream'}
        return self.do_put_to_obj("/upload/" + bucket + "/" + file_path,
                                  payload,
                                  headers,
                                  unmarshaller=download_link_unmars)


class MultipartUploadAPI(ApiCaller):
    def init_multipart(self, bucket, file_path, number_of_parts):
        return self.do_post_to_obj(
            "/multipart/initiate/" + bucket + "/" + file_path + "?numberOfParts=" + number_of_parts,
            None,
            unmarshaller=multipart_unmars)

    def part_upload(self, multipart_id, payload, index):
        headers = {'Content-Type': 'application/octet-stream'}
        return self.do_put_to_obj("/multipart/" + multipart_id + "/part_upload?partIndex=" + index,
                                  payload,
                                  headers,
                                  unmarshaller=part_unmars)

    def list_parts(self, multipart_id):
        return self.do_get_to_obj("/multipart/" + multipart_id + "/parts", unmarshaller=parts_unmars)

    def complete(self, multipart_id):
        return self.do_post_to_obj("/multipart/" + multipart_id + "/complete",
                                   None,
                                   unmarshaller=download_link_unmars)

