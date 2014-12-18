from urllib.parse import urlencode

import httplib2
import json

class HttpPublisher:

    def __init__(self, url):
        self.url = url
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json;version=0.1'
        }

    def publish(self, data):
        h = httplib2.Http()
        resp, content = h.request(
                            self.url,
                            method='POST',
                            body=json.dumps({'hit': data}),
                            headers=self.headers
                        )

        return content.decode('utf-8')
