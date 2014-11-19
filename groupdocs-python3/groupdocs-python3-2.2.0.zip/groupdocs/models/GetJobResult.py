#!/usr/bin/env python
"""
Copyright 2012 GroupDocs.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
class GetJobResult:
    """
    
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually."""


    def __init__(self):
        self.swaggerTypes = {
            'id': 'float',
            'out_formats': 'list[str]',
            'actions': 'str',
            'status': 'str',
            'email_results': 'bool',
            'priority': 'float',
            'url_only': 'bool',
            'documents': 'JobDocumentsEntry',
            'requested_time': 'int',
            'scheduled_time': 'int',
            'guid': 'str',
            'name': 'str',
            'callback_url': 'str',
            'type': 'str'

        }


        self.id = None # float
        self.out_formats = None # list[str]
        self.actions = None # str
        self.status = None # str
        self.email_results = None # bool
        self.priority = None # float
        self.url_only = None # bool
        self.documents = None # JobDocumentsEntry
        self.requested_time = None # int
        self.scheduled_time = None # int
        self.guid = None # str
        self.name = None # str
        self.callback_url = None # str
        self.type = None # str
        
