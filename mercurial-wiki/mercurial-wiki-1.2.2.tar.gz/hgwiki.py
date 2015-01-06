#! /usr/bin/env python
# -*- coding: utf-8 -*-

# hgwiki, Copyright (c) 2010, Jochen Breuer <brejoc@gmail.com>
#
# This file is part of hgwiki.
#
# hgwiki is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import with_statement

import os
import codecs
import thread

from multiprocessing import Process
from time import sleep

from bottle import TEMPLATE_PATH
from bottle import route, run, redirect, request, debug, static_file
from bottle import jinja2_template as template

import markdown2

from mercurial_wiki import util

#from mercurial_wiki.util import start_browser
#from mercurial_wiki.util import page_exists
#from mercurial_wiki.util import write_to_file
#from mercurial_wiki.util import commit_to_repo

__version__ = '1.1'

debug(False)
file_path = os.path.dirname(os.path.realpath(util.__file__))

REPO_DIR = os.getcwdu()
PAGES_DIR = ".hgwiki"
SERVER_PORT = 8001
SERVER_ADDRESS = "localhost"
TEMPLATE_PATH.append(os.path.join(file_path, 'views/'))



# Bottle routes

@route('/static/:filename')
def server_static(filename):
    return static_file(filename, root=os.path.join(file_path, 'static/'))

@route('/favicon.ico')
def favicon():
    return ""

@route('/')
def index_page():
    redirect('/start')


@route('/edit/:name')
def edit_page(name):
    content = ""
    action = "Create"
    if(util.page_exists(PAGES_DIR, name)):
        page = codecs.open(os.path.join(PAGES_DIR, name), 'r', 'utf8')
        content = ''.join(page.readlines())
        page.close()
        action = "Edit"
    return template('edit.html',
             name = name,
             content = content,
             action=action)


@route('/:name')
@route('/:name/')
def page(name):
    if(util.page_exists(PAGES_DIR, name)):
        page = open(os.path.join(PAGES_DIR, name), 'r')
        document = markdown2.markdown(
            unicode(''.join(page.readlines()), 'utf-8', 'ignore'))
        return template('page.html',
                 name=name,
                 content=document)
    elif(name == "start"):
        start_text = """\
##A Mercurial Wiki##

This is a wiki built on top of Mercurial. You can use the [markdown markup](https://github.com/trentm/python-markdown2) to layout your wiki pages. 

Start creating some content!"""
        util.write_to_file(REPO_DIR,
                      PAGES_DIR,
                      os.path.join(PAGES_DIR, name),
                      start_text)
        util.commit_to_repo(REPO_DIR, [os.path.join(PAGES_DIR, name), ], name)
        document = markdown2.markdown(start_text)
        return template('page.html',
                 name=name,
                 content=document)
    else:
        redirect('/edit/' + name)


@route('/:name', method='POST')
def update_page(name):
    util.write_to_file(REPO_DIR,
                  PAGES_DIR,
                  os.path.join(PAGES_DIR, name),
                  request.forms.get('content'))
    file_list = [os.path.join(PAGES_DIR, name)]
    util.commit_to_repo(REPO_DIR, file_list, name)
    redirect(name)


@route('/admin/ping', method='GET')
def ping():
    return "pong"


if __name__ == '__main__':
    bottle_process = None
    while bottle_process == None or bottle_process.is_alive() == False:
        bottle_process = \
                Process(target=run, args=(), \
                kwargs={ 'host': 'localhost', 'port': SERVER_PORT, 'reloader': False })
        bottle_process.start()
        SERVER_PORT+=1
        # giving the server time to start up
        sleep(1)
    
    # Removing last increment from loop
    SERVER_PORT-=1
    print("*"*34)
    print("\nListening on http://localhost:%s\n" % (SERVER_PORT, ))
    thread.start_new_thread(util.start_browser, (SERVER_PORT, ))
