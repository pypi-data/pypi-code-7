#!/usr/bin/env python

import sys
import os
from pathlib import Path

vimix_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(vimix_dir)

DARKGREEN = '\033[32m'
GREEN = '\033[92m'

def vimix(project, prefix='vim-', suffix=''):
    root_dir = prefix + project + suffix
    base_dirs = {d: os.path.join(os.getcwd(), root_dir, d) for d in ['autoload', 'doc', 'plugin']}
    _make_dirs(base_dirs)
    _make_readme(root_dir)
    _make_gitignore(root_dir)
    _make_doc(project, base_dirs['doc'])
    _make_plugin(project, base_dirs['plugin'])
    _make_autoload(project, base_dirs['autoload'])

def _make_dirs(base_dirs):
    [os.makedirs(d) for d in base_dirs.values()]

def _make_readme(root):
    print(DARKGREEN+'*creating', GREEN+'README.md')
    os.makedirs(os.path.join(root, 'README.md'))

def _make_gitignore(root):
    print(DARKGREEN+'*creating', GREEN+'.gitignore')
    os.makedirs(os.path.join(root, '.gitignore'))

def _make_doc(project, doc_path):
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'doc.txt')

    with open(template_path, 'r') as f:
        template = ''.join(f.readlines()).format(plugin_name=project, borderline='='*78)

    with open(os.path.join(doc_path, project+'.txt'), 'w') as f:
        print(DARKGREEN+'*creating', GREEN+'doc/{plugin_name}.txt'.format(plugin_name=project))
        f.write(template)

def _make_plugin(project, plugin_path):
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'plugin.txt')

    with open(template_path, 'r') as f:
        template = ''.join(f.readlines()).format(plugin_name=project)

    with open(os.path.join(plugin_path, project+'.vim'), 'w') as f:
        print(DARKGREEN+'*creating', GREEN+'plugin/{plugin_name}.vim'.format(plugin_name=project))
        f.write(template)

def _make_autoload(project, autoload_path):
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'autoload.txt')

    with open(template_path, 'r') as f:
        template = ''.join(f.readlines())

    with open(os.path.join(autoload_path, project+'.vim'), 'w') as f:
        print(DARKGREEN+'*creating', GREEN+'autoload/{plugin_name}.vim'.format(plugin_name=project))
        f.write(template)
