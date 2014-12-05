#encoding=utf-8
import time
import hashlib
import random
import urllib
#import json
import requests


class Messenger(object):

    def __init__(self, channel, secret_key,
                 host='http://weteam.toraysoft.com'):
        self.channel = channel
        self.secret_key = secret_key
        self.host = host

    def notify(self, content, msg_type='text'):
        timestamp = str(time.time())
        nonce = str(random.randint(9999, 99999))
        sign = hashlib.sha1('&'.join([str(self.channel), self.secret_key,
                                      timestamp, nonce])).hexdigest()
        params = {'timestamp': timestamp,
                  'nonce': nonce,
                  'channel': self.channel,
                  'sign': sign}

        url = self.host + '/messenger/notify/' + '?' + urllib.urlencode(params)
        data = {'msg_type': msg_type, 'content': content}
        rsp = requests.post(url, json=data)

        if rsp.status_code != 200:
            return {'errno': 5999, 'message': 'server error'}
        return rsp.json()

    def send_text(self, content):
        return self.notify(content)

    def send_image(self, image_url):
        return self.notify(image_url, 'image')

    def send_voice(self, voice_url):
        return self.notify(voice_url, 'voice')

    def send_file(self, file_url):
        return self.notify(file_url, 'file')

    def send_video(self, video_url, title, description):
        return self.notify(
            {'media_url': video_url, 'title': title,
             'description': description}, 'video')

    def send_news(self, title, description, url, picurl):
        return self.notify(
            {'title': title, 'description': description,
             'url': url, 'picurl': picurl}, 'news')
