# The MIT License (MIT)
#
# Copyright (c) 2014 Carlos de Alfonso (caralla@upv.es)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import xmlrpclib
import time

class Lock:
    def __init__(self, XMLRPC_SERVER, lock_name):
        self._proxy = xmlrpclib.ServerProxy(XMLRPC_SERVER)
        self._lockname = lock_name
        self._lock_id = None

    def lock_wait(self):
        if self._lock_id is None:
            return False
        
        lock_got = False
        while not lock_got:
            success, got = self._proxy.get_lock(self._lockname, self._lock_id)
            lock_got = success and got
            if not lock_got:
                time.sleep(1)
        
        return True
    
    def lock_release(self, retries = 10):
        if self._lock_id is None:
            return False

        
        while retries > 0:
            success, released = self._proxy.release_lock(self._lockname, self._lock_id)
            if success and released:
                self._lock_id = None
                return True

            time.sleep(1)
            retries -= 1

        return False
    
    def lock_query(self, info = "", retries = 10):
        while retries > 0:
            success, lock_id = self._proxy.query_lock(self._lockname, info)
            if success:
                self._lock_id = lock_id
                return True
            
            time.sleep(1)
            retries -= 1
            
        return False
