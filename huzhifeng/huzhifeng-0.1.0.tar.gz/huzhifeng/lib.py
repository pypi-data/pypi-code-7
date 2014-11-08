#!/usr/bin/env python
# -*- coding: utf-8 -*-

# huzhifeng's Python Lib

import json
import requests
import wget

def format_filename(fname):
    invalid_chars = '/\:*?"<>|'
    filename = ''
    for c in fname:
        filename = filename + ('-' if c in invalid_chars else c)

    return filename

def pdfcrowd(url, file_path):
    post_url = 'http://pdfcrowd.com/form/json/convert/uri/'
    headers = {
        'Host': 'pdfcrowd.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'
    }
    payload = {
        'noCache': '1414481239318',
        'src': url,
        'conversion_source': 'uri'
    }
    try:
        r = requests.post(post_url, data=payload, headers=headers)
    except:
        print 'Exception: requests.post(%s), url=%s' % (post_url, url)
        return False
    if not r or r.status_code != 200:
        print 'requests.post(%s) failed, url=%s' % (post_url, url)
        return False

    data = r.text
    obj = json.loads(data)
    if not all(key in obj for key in ('status', 'uri')):
        print 'Invalid response obj=%s' % (obj)
        return False
    status = obj['status']
    if status != 'ok':
        print 'status=%s' % (status)
    download_url = 'http://pdfcrowd.com%s' % (obj['uri'])

    if wget.download(download_url, out=file_path):
        print ''
        return True
    else:
        return False

def pdfmyurl(url, file_path):
    post_url = 'http://pdfmyurl.com/index.php'
    headers = {
        'Host': 'pdfmyurl.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36',
        'Cookie': 'NB_SRVID=srv29695; _ga=GA1.2.826873587.1414482384; _gat=1',
        'Cache-Control': 'max-age=0',
        'Origin': 'http://pdfmyurl.com',
        'Referer': 'http://pdfmyurl.com/',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    payload = {
        'url': url
    }
    try:
        r = requests.post(post_url, data=payload, headers=headers)
    except:
        print 'Exception: requests.post(%s), url=%s' % (post_url, url)
        return False
    if not r or r.status_code != 200:
        print 'requests.post(%s) failed, url=%s' % (post_url, url)
        return False

    with open(file_path, 'wb') as f:
        f.write(r.content)

    return True
