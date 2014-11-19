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
class AnnotationInfo:
    """
    
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually."""


    def __init__(self):
        self.swaggerTypes = {
            'guid': 'str',
            'documentGuid': 'str',
            'layerId': 'int',
            'sessionGuid': 'str',
            'creatorGuid': 'str',
            'creatorName': 'str',
            'creatorEmail': 'str',
            'box': 'Rectangle',
            'pageNumber': 'int',
            'annotationPosition': 'Point',
            'range': 'Range',
            'svgPath': 'str',
            'type': 'str',
            'access': 'str',
            'replies': 'list[AnnotationReplyInfo]',
            'createdOn': 'int',
            'fontColor': 'int',
            'penColor': 'int',
            'penWidth': 'int',
            'penStyle': 'int',
            'backgroundColor': 'int',
            'fieldText': 'str',
            'fontFamily': 'str',
            'fontSize': 'float'

        }


        self.guid = None # str
        self.documentGuid = None # str
        self.layerId = None # int
        self.sessionGuid = None # str
        self.creatorGuid = None # str
        self.creatorName = None # str
        self.creatorEmail = None # str
        self.box = None # Rectangle
        self.pageNumber = None # int
        self.annotationPosition = None # Point
        self.range = None # Range
        self.svgPath = None # str
        self.type = None # str
        self.access = None # str
        self.replies = None # list[AnnotationReplyInfo]
        self.createdOn = None # int
        self.fontColor = None # int
        self.penColor = None # int
        self.penWidth = None # int
        self.penStyle = None # int
        self.backgroundColor = None # int
        self.fieldText = None # str
        self.fontFamily = None # str
        self.fontSize = None # float
        
