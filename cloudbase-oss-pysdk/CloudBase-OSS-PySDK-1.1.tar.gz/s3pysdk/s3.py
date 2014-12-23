#!/usr/bin/env python
#
#
# @author <a href="hoang281283@gmail.com">Minh Hoang TO</a>
# @date: 12/22/14
#
#
# ==============================================================

from upload import SingleUploadAPI, MultipartUploadAPI
from bucket import BucketAPI

'''
params argument in following methods is expected to be a dictionary holding
S3 API authentication input. Ex:

params = {'signature':'...', 'access_key_id':'...', 'access_key_value':'...', 'random_data':'...'}

'''


def single_upload_api(params):
    return SingleUploadAPI(params)


def multipart_upload_api(params):
    return MultipartUploadAPI(params)


def bucket_api(params):
    return BucketAPI(params)
