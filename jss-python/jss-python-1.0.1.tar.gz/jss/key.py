# -*- coding: utf-8 -*-  
'''
Created on 2013-7-23

@author: root
'''
from jss import commonconstants
from jss.util import error_handler, file_MD5, generate_all_task_slices, \
    Thread_Upload_Part, bucket_name_check, object_name_check
import base64
import hashlib
import hmac
import httplib
import json
import jss
import md5
import os
import string
import time
import urllib

class Key(object):
    '''
    classdocs
    '''
    def __init__(self, bucket=None, name=None):
        '''
        Constructor
        '''
        self.bucket = bucket
        self.name = name
        self.content_type = commonconstants.DEFAULT_CONTENT_TYPE
        self.content_disposition = None
        self.date = None
        self.etag = None
        self.content_length = None
        
    def download(self, headers=None, local_file_path=None):
        """
        download file from JSS
        :type bucket_name :string
        :param  bucket_name:the name of bucket 
        :type headers:dict
        :param  headers:Additional headers to pass along with the request to
            JSS. 
        :type local_file_path:string 
        :param local_file_path:the path of the  file which you want to save.    
        """
        fp = open(local_file_path, 'wb')
        res = self.bucket.jss_client.make_request(method='GET', bucket_name=self.bucket.name, object_name=self.name, headers=headers)
        if res.status / 100 > 2:
            error_handler(res)
        else:
            while True:
                data = res.read(commonconstants.DEFAULT_BUFFER_SIZE)
                if len(data) != 0:
                    fp.write(data)
                else:
                    break
            fp.flush()    
            fp.close() 
            
    def download_flow(self, headers=None):
        res = self.bucket.jss_client.make_request(method='GET', bucket_name=self.bucket.name, object_name=self.name, headers=headers)
        if res.status / 100 > 2:
            error_handler(res)
        return res 
    
    def upload(self, headers=None, local_file_path=None, compute_MD5=True):
        """
        :type :bucket_name:string
        :param :bucket_name:the bucket you file want to put
        :type :object_name:string
        :param :object_name:the key of the file you want to upload
        :type: headers:dict
        :param: headers:Additional headers to pass along with the request to
            JSS. 
        :type local_file_path:string 
        :param local_file_path:the path of the  file which you want to upload.
        """
        bucket_name_check(self.bucket.name)
        object_name_check(self.name)
        fq = open(local_file_path, 'r')
        fq.seek(os.SEEK_SET, os.SEEK_END)
        filesize = fq.tell()
        fq.seek(os.SEEK_SET)
        suffix = local_file_path.split('.')[-1]      
        if not headers:
            headers = {}
        headers['Content-Length'] = filesize
        if compute_MD5:
            fp = open(local_file_path)
            md5_value = file_MD5(fp)
            headers['Content-MD5'] = md5_value
            fp.close()   #new add this time
          
        if '.' + suffix in self.bucket.jss_client.map:
            headers['Content-Type'] = self.bucket.jss_client.map['.' + suffix]
        else:
            headers['Content-Type'] = commonconstants.DEFAULT_CONTENT_TYPE
       # httplib.HTTPConnection("%s:%d")
        self.bucket.jss_client.open_connection_to_put('PUT', self.bucket.name, self.name, headers)
        fq.seek(os.SEEK_SET)
        l = fq.read(commonconstants.DEFAULT_SEND_SIZE)
        while len(l) > 0:
            self.bucket.jss_client.send(l)
            l = fq.read(commonconstants.DEFAULT_SEND_SIZE)
        response = self.bucket.jss_client.pool.getresponse()
        #print response.status
        if response.status / 100 > 2:
            error_handler(response)
        else:
            fq.close()    # new  add this time
            return response
  
    def upload_flow(self,headers=None,data=None,compute_MD5=True):
        bucket_name_check(self.bucket.name)
        object_name_check(self.name)
        if not headers:
            headers = {}
        headers['Content-Length'] = len(data)
        if compute_MD5:
            m = md5.new()
            m.update(data)
            headers['Content-MD5'] = m.hexdigest()
        headers['Content-Type'] = commonconstants.DEFAULT_CONTENT_TYPE
        # httplib.HTTPConnection("%s:%d")
        self.bucket.jss_client.open_connection_to_put('PUT', self.bucket.name, self.name, headers)
        offset=0
        total_size = len(data)
        while offset < total_size:
            read_bytes = data[offset:offset + commonconstants.DEFAULT_SEND_SIZE]
            offset += commonconstants.DEFAULT_SEND_SIZE
            self.bucket.jss_client.send(read_bytes)
        response = self.bucket.jss_client.pool.getresponse()
    #print response.status
        if response.status / 100 > 2:
            error_handler(response)
        else:
            return response       
 
    def upload_fp(self, headers=None, fp=None):
        bucket_name_check(self.bucket.name)
        object_name_check(self.name)
        fp.seek(os.SEEK_SET, os.SEEK_END)
        filesize = fp.tell()
        fp.seek(os.SEEK_SET)    
        if not headers:
            headers = {}
        headers['Content-Length'] = filesize
        headers['Content-Type'] = commonconstants.DEFAULT_CONTENT_TYPE
       # httplib.HTTPConnection("%s:%d")
        self.bucket.jss_client.open_connection_to_put('PUT', self.bucket.name, self.name, headers)
        l = fp.read(commonconstants.DEFAULT_SEND_SIZE)
        while len(l) > 0:
            self.bucket.jss_client.send(l)
            l = fp.read(commonconstants.DEFAULT_SEND_SIZE)
        response = self.bucket.jss_client.pool.getresponse()
        #print response.status
        if response.status / 100 > 2:
            error_handler(response)
        else:
            return response  
        
    def download_part(self, headers=None, start_pos=0, end_pos=None, local_file_path=None):
 
        if not headers:
            headers = {}
        if end_pos:
            headers['Range'] = 'Bytes=' + str(start_pos) + '-' + str(end_pos)
        else:
            headers['Range'] = 'Bytes=' + str(start_pos) + '-'   
        fp = open(local_file_path, 'awb')
        if start_pos>0:
            fp.seek(start_pos-1)
        else:
            fp.seek(start_pos)
        res = self.bucket.jss_client.make_request(method='GET', bucket_name=self.bucket.name, object_name=self.name, headers=headers)
        if res.status / 100 != 2:
            error_handler(res)
        else:
            while True:
                data = res.read(commonconstants.DEFAULT_BUFFER_SIZE)
                if len(data) != 0:
                    fp.write(data)
                else:
                    break
        fp.flush()    
        fp.close() 
        return res
        
    def multi_part_down(self,headers=None,local_file_path=None,part_size=None):
        
        myself=self.bucket.get_key(self.name)
        if part_size<0:
            raise Exception("Part_size can not < 0")
        if myself.content_length<0:
            raise Exception("object length can not <0")
        if string.atoi(myself.content_length)<part_size:
            self.download(None,local_file_path)
        else:
            start_pos=0
            end_pos=part_size
            while end_pos<string.atoi(myself.content_length):
                retry_times=0
                while retry_times<commonconstants.DEFAULT_RETRY_COUNT:
                    try:
                        res=self.download_part(headers=headers,start_pos=start_pos,end_pos=end_pos,local_file_path=local_file_path)
                        if res.status/100==2:
                            break
                    except:
                        retry_times = retry_times + 1
                        time.sleep(1)
                if retry_times>=commonconstants.DEFAULT_RETRY_COUNT:
                    raise  Exception("Bigger than the default  retry time")
                start_pos=end_pos+1
                end_pos=end_pos+part_size
                if end_pos>=string.atoi(myself.content_length):
                    self.download_part(headers=headers,start_pos=start_pos,end_pos=None,local_file_path=local_file_path)
                    break
        
    def download_part_flow(self, headers=None, start_pos=0, end_pos=None):
         
        if not headers:
            headers = {}
        if end_pos:
            headers['Range'] = 'Bytes=' + str(start_pos) + '-' + str(end_pos)
        else:
            headers['Range'] = 'Bytes=' + str(start_pos) + '-'   
        res = self.bucket.jss_client.make_request(method='GET', bucket_name=self.bucket.name, object_name=self.name, headers=headers)
        if res.status / 100 != 2:
            error_handler(res)
        else:
            return res
        
       
    def generate_url(self, method, headers=None, param=None):
        url = "http://%s:%s/%s/%s" % (self.bucket.jss_client.host, self.bucket.jss_client.port, self.bucket.name, self.name)
        l = []
        if not param:
            param = {}
            param['AccessKey'] = self.bucket.jss_client.access_key
            path = self._build_path_base(self.bucket.name, self.name)
            param['Signature'] = self._presignalture(method, path, headers)
        if  headers:
           if 'Expires' in headers:
               param['Expires'] = int(headers['Expires']) + int(time.time())
           else:
               param['Expires'] = commonconstants.DEFAULT_EXPIRE_TIME + int(time.time())
        else:
            param['Expires'] = commonconstants.DEFAULT_EXPIRE_TIME + int(time.time())
            
        for k, v in param.items():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            if v is not None and v != '':
                l.append('%s=%s' % (urllib.quote(k), urllib.quote(str(v))))
        if len(l):
            url = url + '?' + '&'.join(l)
        return url
    
    def _build_path_base(self, bucket_name, object_name, query_args=None):
        path_base = '/'
        if bucket_name:
            path_base += "%s" % bucket_name
        if object_name:
            path_base += "/%s" % object_name
        if query_args:
            path_base += '?' + query_args
        #print path_base    
        return path_base
       
   
    def _presignalture(self, method, url_resource, headers):
        if  headers:
            if 'Content-MD5' in headers:
                content_md5 = headers.get('Content-MD5')
            else:
                content_md5 = ''
            if 'Content-Type' in headers:
                content_type = headers.get('Content-Type')
            else:
                content_type = ''
            if 'Expires' in headers:
                expires = int(headers.get('Expires')) + int(time.time())
                    
        else:
            content_md5 = ''
            content_type = ''
            expires = commonconstants.DEFAULT_EXPIRE_TIME + int(time.time())
        
        string_to_sign = method + \
                         "\n" + content_md5 + \
                         "\n" + content_type + \
                         "\n" + str(expires) + \
                         "\n" + url_resource
        signature = base64.encodestring(hmac.new(str(self.bucket.jss_client.secret_key), \
            string_to_sign, hashlib.sha1).digest()).strip()
        
        return signature
    
    def init_multi_upload(self, headers=None):
        if not headers:
            headers = {}
        if not 'Content-Type' in headers:
            headers['Content-Type'] = commonconstants.DEFAULT_CONTENT_TYPE
        subresource = 'uploads'    
        response = self.bucket.jss_client.make_request('POST', self.bucket.name, self.name, headers, '', subresource, subresource)
        if response.status / 100 != 2:
            error_handler(response)
        data = response.read()    
        pre_upload = json.loads(data)
        return pre_upload
        
    def upload_part(self, headers=None, data=None, part_number=None, upload_id=None):
        param = {}
        param['partNumber'] = part_number 
        param['uploadId'] = upload_id
        l = []
        query_param = ''
        # subresource = 'uploads'
        if  not headers:
            headers = {}
        headers['Content-Length'] = str(len(data))
        for k, v in param.items():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            if v is not None and v != '':
                l.append('%s=%s' % (urllib.quote(k), urllib.quote(str(v))))
        if len(l):
            query_param = '&'.join(l)
 
        self.bucket.jss_client.open_connection_to_put(method='PUT', bucket_name=self.bucket.name, object_name=self.name, headers=headers, query_args=query_param, subresource=query_param)
        self.bucket.jss_client.send(data)
        response = self.bucket.jss_client.pool.getresponse()
        return response
        
    def upload_part_fp(self, data=None, part_number=None, upload_id=None):
        param = {}
        param['partNumber'] = part_number 
        param['uploadId'] = upload_id
        l = []
        query_param = ''
        # subresource = 'uploads'
        headers = {}
        headers['Content-Length'] = str(len(data))
        for k, v in param.items():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            if v is not None and v != '':
                l.append('%s=%s' % (urllib.quote(k), urllib.quote(str(v))))
        if len(l):
            query_param = '&'.join(l)
 
        self.bucket.jss_client.open_connection_to_put(method='PUT', bucket_name=self.bucket.name, object_name=self.name, headers=headers, query_args=query_param, subresource=query_param)
        self.bucket.jss_client.send(data)
        response = self.bucket.jss_client.pool.getresponse()
        return response
    
    def upload_part_from_pos(self, headers=None, local_file_path=None, offset=None, part_size=None, part_number=None, upload_id=None):
        
        fp = open(local_file_path, 'r')
        param = {}
        param['partNumber'] = part_number 
        param['uploadId'] = upload_id
        l = []
        query_param = ''
        # subresource = 'uploads'
        headers={}
        headers['Content-Length'] = part_size
        for k, v in param.items():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            if v is not None and v != '':
                l.append('%s=%s' % (urllib.quote(k), urllib.quote(str(v))))
        if len(l):
            query_param = '&'.join(l)
        fp.seek(os.SEEK_SET, os.SEEK_END)
        filesize = fp.tell()
        if offset > filesize:
            fp.seek(os.SEEK_SET, os.SEEK_END)
        else:
            fp.seek(os.SEEK_SET)
            fp.seek(offset)
        left_len = part_size
        self.bucket.jss_client.open_connection_to_put(method='PUT', bucket_name=self.bucket.name, object_name=self.name, headers=headers, query_args=query_param, subresource=query_param)
        while True:
            if left_len <= 0:
                break
            elif left_len < commonconstants.DEFAULT_SEND_SIZE:
                buff_content = fp.read(left_len)
            else:
                buff_content = fp.read(commonconstants.DEFAULT_SEND_SIZE)

            if len(buff_content) > 0:
                self.bucket.jss_client.send(buff_content)
 
            left_len = left_len - len(buff_content)
        fp.close()
        return self.bucket.jss_client.pool.getresponse()
    
    def multi_upload(self, headers=None, local_file_path=None, part_size=commonconstants.DEFAULT_PART_SIZE):
        bucket_name_check(self.bucket.name)
        object_name_check(self.name)
        pre_upload = self.init_multi_upload() 
        fp = open(local_file_path, 'rb')
        m = md5.new()
        file_size = os.path.getsize(local_file_path)
        num_part = file_size / part_size
        if file_size % part_size != 0:
            num_part = num_part + 1
        for i in range(num_part):
            retry_times=0
            data_content=fp.read(part_size)
            m.update(data_content)
            while retry_times<commonconstants.DEFAULT_RETRY_COUNT:
                response = self.upload_part(headers, data_content, i + 1, pre_upload['UploadId'])
                if response.status/100==2:
                    break
                else:
                    retry_times=retry_times+1   
                    time.sleep(1)
            if retry_times>=commonconstants.DEFAULT_RETRY_COUNT:
                raise Exception("-2, after retry %s, failed, multi upload part failed!" % retry_times)
        result = self.get_uploaded_parts(None, pre_upload['UploadId'])
        part_submit_json = self._generate_part_json(result)
        data=self.complete_multi_upload(None, pre_upload['UploadId'], json.dumps(part_submit_json))
        fp.close()
        
        return data,m.hexdigest()
    
    def multi_upload_fp(self,headers=None,fp=None,part_size=commonconstants.DEFAULT_PART_SIZE):
        bucket_name_check(self.bucket.name)
        object_name_check(self.name)
        fp.seek(os.SEEK_SET, os.SEEK_END)
        file_size = fp.tell()
        fp.seek(os.SEEK_SET) 
        m = md5.new()
        pre_upload = self.init_multi_upload()
        num_part = file_size / part_size
        if file_size % part_size != 0:
            num_part = num_part + 1
        for i in range(num_part):
            retry_times=0
            data_content=fp.read(part_size)
            m.update(data_content)
            while retry_times<commonconstants.DEFAULT_RETRY_COUNT:
                response = self.upload_part(headers, data_content, i + 1, pre_upload['UploadId'])
                if response.status/100==2:
                    break
                else:
                    retry_times=retry_times+1
            if retry_times>=commonconstants.DEFAULT_RETRY_COUNT:
                raise Exception("-2, after retry %s, failed, multi upload part failed!" % retry_times) 
        result = self.get_uploaded_parts(None, pre_upload['UploadId'])
        part_submit_json = self._generate_part_json(result)
        data=self.complete_multi_upload(None, pre_upload['UploadId'], json.dumps(part_submit_json))
        fp.close() 
        return data,m.hexdigest()
    
    def multi_upload_fp_with_size(self,headers=None,fp=None,size=None,part_size=commonconstants.DEFAULT_PART_SIZE):
        bucket_name_check(self.bucket.name)
        object_name_check(self.name)
        m = md5.new()
        pre_upload = self.init_multi_upload()
        num_part = size / part_size
        if size % part_size != 0:
            num_part = num_part + 1
        for i in range(num_part):
            retry_times=0
            data_content=fp.read(part_size)
            m.update(data_content)
            while retry_times<commonconstants.DEFAULT_RETRY_COUNT:
                response = self.upload_part(headers, data_content, i + 1, pre_upload['UploadId'])
                if response.status/100==2:
                    break
                else:
                    retry_times=retry_times+1
            if retry_times>=commonconstants.DEFAULT_RETRY_COUNT:
                raise Exception("-2, after retry %s, failed, multi upload part failed!" % retry_times) 
        result = self.get_uploaded_parts(None, pre_upload['UploadId'])
        part_submit_json = self._generate_part_json(result)
        data=self.complete_multi_upload(None, pre_upload['UploadId'], json.dumps(part_submit_json))
        fp.close() 
        return data,m.hexdigest()
       
    def multi_thread_upload(self, headers=None, local_file_path=None, part_size=commonconstants.DEFAULT_PART_SIZE,
                             num_thread=10, max_part=10000,timeout=None):
        bucket_name_check(self.bucket.name)
        object_name_check(self.name)
        pre_upload = self.init_multi_upload()
        task_queue = generate_all_task_slices(file_name=local_file_path, part_size=part_size, max_part=max_part)
        thread_list = []
        for i in range(num_thread):
            jss_client = jss.connection.JssClient(access_key=self.bucket.jss_client.access_key, secret_key=self.bucket.jss_client.secret_key,
                         host=self.bucket.jss_client.host, port=self.bucket.jss_client.port,timeout=timeout)
            thread_curr = Thread_Upload_Part(jss_client=jss_client, bucket_name=self.bucket.name, object_name=self.name, upload_id=pre_upload['UploadId'], all_task_slices=task_queue)
            thread_list.append(thread_curr)
            thread_curr.start()
        for item in thread_list:
            item.join()
        result = self.get_uploaded_parts(None, pre_upload['UploadId'])
        part_submit_json = self._generate_part_json(result)
        data=self.complete_multi_upload(None, pre_upload['UploadId'], json.dumps(part_submit_json))
        return data
    

    
    def complete_multi_upload(self, headers=None, upload_id=None, data=None):
        
        if not headers:
            headers = {}
        subresource = 'uploads'
        query_param = urllib.quote('uploadId') + '=' + urllib.quote(upload_id)
        response = self.bucket.jss_client.make_request(method='POST', bucket_name=self.bucket.name, object_name=self.name, headers=headers, data=data, query_args=query_param, subresource=query_param)
        #print response.status
        if response.status / 100 != 2:
            error_handler(response)
        while True:
            data = response.read()
            if len(data) != 0:
                message=json.loads(data)
                if message['ETag']=="We encountered an internal error. Please try again.":
                    raise Exception("merge the object error")
                return data
            
    def get_uploaded_parts(self, headers=None, upload_id=None, max_parts=None, part_number_marker=None):  
          
        if not headers:
            headers = {}
        subresource = 'uploads'
        param = {}
        l = []
        query_param = ''
        if upload_id:
            param['uploadId'] = upload_id
        if max_parts:
            param['max-parts'] = max_parts
        if part_number_marker:
            param['part-number-marker'] = part_number_marker   
        for k, v in param.items():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            if v is not None and v != '':
                l.append('%s=%s' % (urllib.quote(k), urllib.quote(str(v))))
        if len(l):
            query_param = '&'.join(l)    
        response = self.bucket.jss_client.make_request(method='GET', bucket_name=self.bucket.name, object_name=self.name, headers=headers, data='', query_args=query_param, subresource=query_param)
        if response.status / 100 != 2:
            error_handler(response)
        data = response.read()
        result = json.loads(data)
        return result
    
        
    def _generate_part_json(self, uploaded_part):
        
        result = {}
        #print json.dumps(uploaded_part)
        part_content = []
        if uploaded_part:
            for memb in uploaded_part['Part']:
                curr = {}
                curr['PartNumber'] = memb['PartNumber']
                curr['ETag'] = memb['ETag']
                part_content.append(curr)
        result['Part'] = part_content
        return result
    
    def cancel_multipart_uploaded(self, headers=None, upload_id=None):
        param = {}
        l = []
        query_param=''
        if upload_id:
            param['uploadId'] = upload_id
        for k, v in param.items():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            if v is not None and v != '':
                l.append('%s=%s' % (urllib.quote(k), urllib.quote(str(v))))
        if len(l):
            query_param = '&'.join(l) 
        response = self.bucket.jss_client.make_request(method='DELETE', bucket_name=self.bucket.name, object_name=self.name, headers=headers, data='', query_args=query_param, subresource=query_param)
       
        if response.status / 100 != 2:
            error_handler(response)
        return response
    
               
        
