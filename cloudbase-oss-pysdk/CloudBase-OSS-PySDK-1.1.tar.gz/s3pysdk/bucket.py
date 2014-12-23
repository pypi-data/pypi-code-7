#!/usr/bin/env python
#
#
# @author <a href="hoang281283@gmail.com">Minh Hoang TO</a>
# @date: 12/22/14
#
#
# ==============================================================

from models import Bucket, File, ApiError
from connection import ApiCaller
import json


def buckets_unmars(res):
    if res.status_code == 200:
        obj = json.loads(res.text)
        if obj['buckets'] is not None:
            buckets = []
            for b in obj['buckets']:
                buckets.append(Bucket(b['name'], b['owner'], b['shared']))
            return buckets

    return ApiError(res.text)


def files_unmars(res):
    if res.status_code == 200:
        obj = json.loads(res.text)
        if obj['files'] is not None:
            files = []
            for f in obj['files']:
                files.append(File(f['bucket'], f['path'], f['downloadLink'], f['directLink']))
            return files

    return ApiError(res.text)


class BucketAPI(ApiCaller):
    def list_buckets(self):
        return self.do_get_to_obj("/buckets", unmarshaller=buckets_unmars)

    def create_bucket(self, name):
        return self.do_post("/buckets/" + name)

    def delete_bucket(self, name):
        return self.do_delete("/buckets/" + name)

    def list_files(self, bucket, folder="/"):
        return self.do_get_to_obj("/buckets/" + bucket + "?folder=" + folder, unmarshaller=files_unmars)

    def delete_file(self, bucket, path):
        return self.do_delete("/buckets/" + bucket + "/" + path)

