#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

application_name = 'snipe'
version = '0.0.1'

filepath_user = os.environ['HOME'] + '/.' + application_name
filepath_dump = os.environ['HOME'] + '/.' + application_name + '.dump'

note_max_limit = 50
note_default_tag = 'Snipe'

sandbox = False

evernote_url = 'https://www.evernote.com'
if sandbox:
    evernote_url = 'https://sandbox.evernote.com'
token_geturl = evernote_url + '/api/DeveloperToken.action'

