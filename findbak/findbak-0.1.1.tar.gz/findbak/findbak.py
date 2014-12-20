#coding: utf-8
from configobj import ConfigObj
from opster import command
import gzip
import json
import os.path
import time

HOME = os.getenv('USERPROFILE') or os.getenv('HOME')
CONF_PATH = os.path.join(HOME, '.findbakrc')

def write_template_config():
    conf = ConfigObj(
        CONF_PATH,
        create_empty=True,
        write_empty_values=True
    )

    conf['directories'] = ['/mnt/hdd0/plex', '/mnt/hdd1/plex']
    conf['keep_days'] = 180

    conf.write()

def get_conf():
    if os.path.exists(CONF_PATH):
        return ConfigObj(CONF_PATH)
    else:
        write_template_config()
        print("Wrote example config to {0}".format(CONF_PATH))
        exit(0)

CONF = get_conf()

@command()
def main():
    backups = []
    gzpath = os.path.expanduser('~/.findbak.json.gz')
    if os.path.exists(gzpath):
        with gzip.open(gzpath) as fh:
            for backup in json.loads(fh.read()):
                if backup['timestamp'] > time.time()-60*60*24*int(CONF['keep_days']):
                    backups.append(backup)
    backup = {
        'timestamp': time.time(),
        'files': [],
    }
    for dirpath in CONF['directories']:
        for root, dirs, files in os.walk(dirpath):
            for filepath in files:
                backup['files'].append(root + filepath)

    backups.append(backup)
    with gzip.open(gzpath, 'w') as fh:
        fh.write(json.dumps(backups))
