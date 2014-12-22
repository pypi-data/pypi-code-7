#!/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import shutil

from dockerfly import settings

db_dir = settings.default_db_dir
dbs = settings.dbs

def init_db(func):
    def init_db_wrapper(*args, **kwargs):
        if not os.path.exists(db_dir):
            os.mkdir(db_dir)
        for db in dbs:
            if not os.path.exists(db):
                with open(db, 'w') as db_file:
                    json.dump([], db_file, indent=4)
        return func(*args, **kwargs)
    return init_db_wrapper

@init_db
def update_db(content, db_name):
    db_file = os.path.join(db_dir, db_name)
    lock_file = db_file + '.lock'
    while True:
        if os.path.exists(lock_file):
            time.sleep(0.1)
        else:
            break

    #lock update op
    open(lock_file, 'a').close()
    with open(db_file, 'w') as db:
        json.dump(content, db, indent=4)
    os.remove(lock_file)

@init_db
def get_db(db_name):
    db_file = os.path.join(db_dir, db_name)
    with open(db_file, 'r') as db:
        return json.load(db)

def del_db(db_name):
    db_file = os.path.join(db_dir, db_name)
    if os.path.exists(db_file):
        os.remove(db_file)
