#!/usr/bin/python2.5
#
# Copyright 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Web request dispatcher for the Google App Engine Pipeline API.

In a separate file from the core pipeline module to break circular dependencies.
"""

import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util as webapp_util

import pipeline


_APP = webapp.WSGIApplication(pipeline.create_handlers_map(), debug=True)


def _main():
  webapp_util.run_wsgi_app(_APP)


if __name__ == '__main__':
  _main()
