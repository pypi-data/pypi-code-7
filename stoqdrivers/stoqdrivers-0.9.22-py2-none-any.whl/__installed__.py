# Generated by setup.py do not modify
import os
import sys
prefix = 'sys.prefix'
if hasattr(sys, 'frozen'):
    pos = __file__.find('library.zip')
    prefix = os.path.dirname(__file__[:pos-1])
elif not os.path.exists(prefix):
    prefix = sys.prefix
revision = 0
resources = {}
resources['locale'] = os.path.join(prefix, "share", "locale")
global_resources = {}
global_resources['conf'] = os.path.join(prefix, "share", "stoqdrivers", "conf")
