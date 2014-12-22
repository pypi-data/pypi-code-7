"This is for testing HTTP-POSTing data using requests with either dicts or lists."

import json

import pytest

from relayr.resources import Device


class TestHttpPostData(object):
    "Test HTTP post requests with different types of data payloads."
    # http://curl.haxx.se/docs/httpscripting.html

    def test_perform_request(self, fix_registered):
        "Test building cURL calls."
        token = fix_registered.testset1['token']
        from relayr import Client
        c = Client(token=token)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer 3A1owTXfLKRew0s.BF-4qhEdXQTHgDr4',
            'User-Agent': 'io.relayr.sdk.python/0.2.1 (Darwin-10.8.0; i386-64bit; CPython-2.7.6)'
        }
        res = c.api.perform_request('get', 'https://api.relayr.io/devices/a3386628-61a8-4a80-9a42-1bd3c64c46a5/cmd/led', 
            data={'cmd': 1},
            headers=headers)
        # import pdb; pdb.set_trace();

    def test_build_curl_0(self, fix_registered):
        "Test building cURL calls."
        token = fix_registered.testset1['token']
        from relayr.api import build_curl_call
        res = build_curl_call('post', 'http://foo.com')
        assert res == 'curl -X POST http://foo.com'
        res = build_curl_call('post', 'http://foo.com', headers={'foo': 'bar', 'bar': 'foo'})
        assert res == 'curl -X POST http://foo.com -H "foo: bar" -H "bar: foo"'
        res = build_curl_call('post', 'http://foo.com', data={'foo': 'bar', 'bar': 'foo'})
        assert res == 'curl -X POST http://foo.com --data foo=bar&bar=foo'
        res = build_curl_call('post', 'http://foo.com', data=json.dumps([{'foo': 'bar'}]))
        assert res == 'curl -X POST http://foo.com --data \'[{"foo": "bar"}]\''

    def _test_post_dict(self, fix_registered):
        "Test building a cURL call."
        token = fix_registered.testset1['token']
        from relayr import Client
        c = Client(token=token)
        dev.send_command('led', data)

    def _test_post_list(self, fix_registered):
        "Post list as JSON."
        token = fix_registered.testset1['token']
        from datetime import datetime
        from relayr import Client
        c = Client(token=token)
        messages = [
            {
                "timestamp": datetime.now().isoformat(),
                "message": "testing xyz",
                "connection": { "internet": True}
            },
            {
                "timestamp": datetime.now().isoformat(),
                "message": "testing xyz",
                "connection": { "internet": True}
            },
        ]
        res = c.api.post_client_log(messages)
