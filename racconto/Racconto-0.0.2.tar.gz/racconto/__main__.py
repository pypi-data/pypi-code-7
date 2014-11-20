# -*- coding: utf-8 -*-
import argparse
import codecs
import os, glob, shutil

from racconto.parsers import *
from racconto.hooks.manager import HooksManager
from racconto.generator import Generator
from racconto.settings_manager import SettingsManager as SETTINGS

# Import settings from project where racconto is used
PROJECT_SETTINGS = None
try:
    import settings as PROJECT_SETTINGS
except ImportError, e:
    pass

def compile_site():
    if PROJECT_SETTINGS:
        SETTINGS.override(PROJECT_SETTINGS)

    # Setup template environment
    Generator.setup_jinja_environment(SETTINGS.get('TEMPLATEDIR'))
    for key, value in SETTINGS.get('FILTERS').items():
        Generator.jinja_env.filters[key] = value

    entries = glob.glob('./%s/*.md' % SETTINGS.get('CONTENTDIR'))
    posts, pages = [], []

    # Parse content
    parser = RaccontoParser()
    for f in entries:
        parsed_file = parser.parse(f)

        if parsed_file is None:
            continue

        if isinstance(parsed_file, Post):
            posts.append(parsed_file)
        elif isinstance(parsed_file, Page):
            pages.append(parsed_file)

    posts.sort() # Sort list of posts by date

    # Run before all hooks
    HooksManager.run_before_all_hooks(pages, posts)

    # Generate site
    for parsed_file in pages:
        HooksManager.run_before_each_hooks(parsed_file)
        Generator.generate(parsed_file, SETTINGS.get('SITEDIR'))
    for parsed_file in posts:
        HooksManager.run_before_each_hooks(parsed_file)
        Generator.generate(parsed_file, SETTINGS.get('BLOGDIR'))

    # Run after all hooks
    HooksManager.run_after_all_hooks(pages, posts)

    print "Done!"


def clean_site():
    if PROJECT_SETTINGS:
        SETTINGS.override(PROJECT_SETTINGS)

    shutil.rmtree(SETTINGS.get('SITEDIR'))
    os.makedirs(SETTINGS.get('SITEDIR'))
    print "Clean"

def create_directory_structure():
    project_root = os.getcwd()
    folders = [SETTINGS.get('CONTENTDIR'),
               SETTINGS.get('TEMPLATEDIR'),
               SETTINGS.get('SITEDIR'),
               SETTINGS.get('STATICDIR'),
               ]
    for folder in folders:
        path = "%s%s%s" % (project_root, os.sep, folder)
        if not os.path.exists(path):
            os.makedirs(path)

def main():
    parser = argparse.ArgumentParser(description="Racconto is a static website generator.")

    parser.add_argument('-c', '--create', action="store_true",
                       help="creates the basic directory structure for a racconto project")
    parser.add_argument('-g', '--generate', action="store_true",
                       help="generates the site")
    parser.add_argument('-C', '--clean', action="store_true",
                       help="cleans the site directory prior to generate. Used in conjuction with -g")

    args = parser.parse_args()

    if args.generate == True:
        if args.clean == True:
            clean_site()

        compile_site()
    elif args.create == True:
        create_directory_structure()
    elif args.clean == True:
        clean_site()

if __name__ == "__main__":
    main()
