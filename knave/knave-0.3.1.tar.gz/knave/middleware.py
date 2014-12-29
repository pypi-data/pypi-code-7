# Copyright 2014 Oliver Cope
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

import sys
from . import predicates

noop = lambda: None


def unauthorized_response(environ, start_response):
        s = "<html><body>Access is denied</body></html>"
        start_response("401 unauthorized",
                        [("Content-Type", "text/html"),
                            ("Content-Length", str(len(s)))],
                        sys.exc_info())
        return [s]


def KnaveMiddleware(app, acl, unauthorized_response=unauthorized_response):

    def knave_middleware(environ, start_response):
        acl.bind_to(environ)
        try:
            result = app(environ, start_response)
            close = getattr(result, 'close', noop)
            try:
                for item in result:
                    yield item
            finally:
                close()
        except predicates.Unauthorized:
            # Ensure start_response gets the required exc_info argument
            def start_response(status, headers, exc_info=sys.exc_info(),
                               saved_start_response=start_response):
                return saved_start_response(status, headers, exc_info)
            result = unauthorized_response(environ, start_response)
            close = getattr(result, 'close', noop)
            try:
                for item in result:
                    yield item
            finally:
                close()
    return knave_middleware
