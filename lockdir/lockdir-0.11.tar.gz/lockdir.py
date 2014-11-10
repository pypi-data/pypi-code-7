#!/usr/bin/env python

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

import time
import os
import random
import sys

class LockDir(object):
    def __init__(self, parallelruns, secondswait, lockdir = "/tmp/lockdir.lock"):
        self._BEGINTIME=time.time()
        self._ELAPSED=0
        self._ACQUIREDLOCK=""
        self._ACQUIRED=False
        self._PARALLELRUNS=parallelruns
        self._MAXWAIT=secondswait
        self._LOCKDIR=lockdir
        
    def acquire_lock(self):
        while (self._ELAPSED < self._MAXWAIT) and (not self._ACQUIRED):
            for i in range(0, self._PARALLELRUNS):
                cur_path = "%s.%s" % (self._LOCKDIR, i)
                try:
                    os.mkdir(cur_path)
                    self._ACQUIREDLOCK = cur_path
                    self._ACQUIRED = True
                    break
                except:
                    pass
                
            if not self._ACQUIRED:
                time.sleep(random.randint(1,5))
                self._ELAPSED = time.time() - self._BEGINTIME

        return self._ACQUIRED

    def clean_lock(self):
        if self._ACQUIRED:
            try:
                os.rmdir(self._ACQUIREDLOCK)
            except:
                pass