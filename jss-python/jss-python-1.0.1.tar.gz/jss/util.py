# -*- coding: utf-8 -*-  
'''
Created on 2013-5-29

@author: sunyanhao
'''

from jss import commonconstants
from jss.exception import StorageError
from threading import Thread
import Queue
import json
import md5
import os
import re

def  error_handler(response):
     body = response.read()
     try:
        body_json = json.loads(body, 'UTF-8')
        raise StorageError(response.status, response.reason,
                       body_json['code'], body_json['message'], body_json['resource'], body_json['requestId'])
     except:
          raise Exception("OtherException:"+body)
     
def file_MD5(fp):
    '''Returns an md5 hash for an object with read() method.'''
    m = md5.new()
    while True:
        data = fp.read(commonconstants.DEFAULT_BUFFER_SIZE)
        if not data:
            break
        m.update(data)
    return m.hexdigest()

class Thread_Upload_Part(Thread):
    
    def __init__(self, jss_client=None, thread_headers=None, bucket_name=None, object_name=None, upload_id=None, all_task_slices=None):
        Thread.__init__(self)
        self.jss_client = jss_client
        self.bucket_name = bucket_name
        self.object_name = object_name
        self.all_task_slices = all_task_slices
        self.thread_headers = thread_headers
        self.upload_id = upload_id
        
    def run(self):
        while True:
            if self.all_task_slices.qsize() <= 0:
                break
            else:
                task_slice = self.all_task_slices.get()
                file_name = task_slice['file_name']
                offset = task_slice['offset']
                part_size = task_slice['part_size']
                part_num = task_slice['part_num']
                retry_times=0
                while retry_times<commonconstants.DEFAULT_RETRY_COUNT:
                    thread_key = self.jss_client.bucket(self.bucket_name).object(self.object_name)
                    response=thread_key.upload_part_from_pos(self, local_file_path=file_name, offset=offset, part_size=part_size, part_number=part_num, upload_id=self.upload_id)
                    if response.status/100==2:
                        break
                    else:
                        retry_times=retry_times+1
                        
# class  Thread_Upload_Part_fp(Thread):
#     def __init__(self, jss_client=None, thread_headers=None, bucket_name=None, object_name=None, upload_id=None, all_task_slices=None):
#         Thread.__init__(self)
#         self.jss_client = jss_client
#         self.bucket_name = bucket_name
#         self.object_name = object_name
#         self.all_task_slices = all_task_slices
#         self.thread_headers = thread_headers
#         self.upload_id = upload_id
#         self.data=None
#         
#         
#     def run(self):
#         while True:
#                 task_slice = self.all_task_slices.get()
#                 self.data = task_slice['data']
#                 print self.data
#                 part_num = task_slice['part_num']
#                 thread_key = self.jss_client.bucket(self.bucket_name).object(self.object_name)
#                 thread_key.upload_part_fp(self,data=self.data, part_number=part_num, upload_id=self.upload_id)
                
# class Thread_generate_task_slice(Thread):
#     def __init__(self, fp=None,all_task_slices=None, part_size=None, max_part=10000):
#         Thread.__init__(self)
#         self.fp = fp
#         self.part_size = part_size
#         self.max_part = max_part
#         self.all_task_slices=all_task_slices
#     def run(self):
#         self.fp.seek(os.SEEK_SET, os.SEEK_END)
#         file_size = self.fp.tell()
#         self.fp.seek(os.SEEK_SET) 
#         if self.part_size <= 0:
#             raise Exception('part_size must greater than 0')
#         if file_size <= 0:
#             raise Exception('can not upload empty file!')
#         if file_size < self.part_size:
#             task_slice = {}
#             data=self.fp.read()
#             task_slice['data'] = data
#             task_slice['part_num'] = 1
#             self.all_task_slices.put(task_slice)
#         else:
#             left_size = file_size
#             current_offset = 0
#             part_num = 1
#             while left_size > 0:
#                 if left_size >= self.part_size:
#                     task_slice = {}
#                     data=self.fp.read(self.part_size)
#                     task_slice['part_num'] = part_num
#                     task_slice['data'] = data
#                     self.all_task_slices.put(task_slice)
#                     current_offset = current_offset + self.part_size
#                     left_size = file_size - current_offset
#                     part_num = part_num + 1
#                 else:
#                     task_slice = {}
#                     data=self.fp.read(left_size)
#                     task_slice['data'] = data
#                     task_slice['part_num'] = part_num
#                     self.all_task_slices.put(task_slice)
#                     break
        
        
def generate_all_task_slices(file_name=None, part_size=None, max_part=10000):
    all_task_slices = Queue.Queue(0)
    file_size = os.path.getsize(file_name)
    if part_size <= 0:
        raise Exception('part_size must greater than 0')
    if file_size <= 0:
        raise Exception('can not upload empty file!')
    if file_size < part_size:
        task_slice = {}
        task_slice['offset'] = 0
        task_slice['part_size'] = file_size
        task_slice['part_num'] = 1
        task_slice['file_name']
        all_task_slices.put(task_slice)
    else:
        if file_size > part_size * max_part:
            raise Exception('the part_size is set to small,please reset it ')
        else:
            left_size = file_size
            current_offset = 0
            part_num = 1
            while left_size > 0:
                if left_size >= part_size:
                    task_slice = {}
                    task_slice['offset'] = current_offset
                    task_slice['part_size'] = part_size
                    task_slice['part_num'] = part_num
                    task_slice['file_name'] = file_name
                    all_task_slices.put(task_slice)
                    current_offset = current_offset + part_size
                    left_size = file_size - current_offset
                    part_num = part_num + 1
                else:
                    task_slice = {}
                    task_slice['offset'] = current_offset
                    task_slice['part_size'] = left_size
                    task_slice['part_num'] = part_num
                    task_slice['file_name'] = file_name
                    all_task_slices.put(task_slice)
                    break
    return all_task_slices

def bucket_name_check(bucket_name):
    pattern = re.compile("^[a-z0-9][a-z0-9\\.\\-]{1,61}[a-z0-9]$")
    if bucket_name.find('..')!=-1:
        raise Exception('bucket_name contain invalid character')
    if bucket_name.find('.-')!=-1:
        raise Exception('bucket_name contain invalid character')
    if bucket_name.find('--')!=-1:
        raise Exception('bucket_name contain invalid character')
    if bucket_name.find('-.')!=-1:
        raise Exception('bucket_name contain invalid character')    
    str_match = pattern.match(bucket_name)
    if str_match:
        pass
    else:  
        raise Exception('bucket_name contain invalid character')
   
    
def object_name_check(object_name):
    patt = re.compile(u"^[^\/][\w\u4e00-\u9fa5\\\/\.\-]{1,100}")
    mh=patt.match(object_name.decode('UTF-8'))
    if mh:
        pass
    else:  
        raise Exception('object_name contain invalid character')
    


        
        


