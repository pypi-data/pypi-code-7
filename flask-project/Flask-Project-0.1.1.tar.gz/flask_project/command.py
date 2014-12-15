# coding=utf-8
"""
Flask Project

Usage:
  flask-project new <template> <project>
  flask-project new <project>
  flask-project -h | --help
  flask-project -v | --version

Options:
  -h, --help          Help information.
  -v, --version       Show version.
"""
from __future__ import unicode_literals

import os
import sys
import codecs
from distutils.dir_util import copy_tree
from uuid import uuid4
from docopt import docopt
from functools import partial
from importing import path_for_import
import shutil
from .utils import generate_site_name, generate_site_brand
from . import log

logger = log.get_logger(__name__)


def do_vars_replace(config_paths, variables={}):
    for config_path in config_paths:
        with codecs.open(config_path, "r", "utf-8") as f:
            data = f.read()
        with codecs.open(config_path, "w", "utf-8") as f:
            for key, val in variables:
                data = data.replace("%(" + key + ")s", val())
            f.write(data)


def create_project(project_name, template_name="default"):
    """
    Copies the contents of the templates/<template_name> directory to
    <project_name> directory.
    """
    logger.info("try create %s project." % template_name)
    # Ensure the given directory name doesn't clash with an existing
    # Python package/module.
    try:
        __import__(project_name)
    except ImportError:
        pass
    else:
        logger.error("'%s' conflicts with an existing Python module" % project_name)
        sys.exit(1)

    package_name = "flask_project.templates"
    try:
        __import__(package_name)
    except ImportError:
        logger.error("Could not import package '%s'" % package_name)
        sys.exit(1)

    project_path = os.path.join(os.getcwd(), project_name)
    template_path = os.path.join(path_for_import(package_name), template_name)
    if os.path.isdir(project_path):
        logger.error("%s template already exists." % project_name)
        sys.exit(1)
    if not os.path.isdir(template_path):
        logger.error("%s template not exists." % template_name)
        sys.exit(1)
    logger.info("copying tree...")
    copy_tree(template_path, project_path)
    logger.info("done copy tree.")

    # do variable replace.
    variables = [
        ('SECRET_KEY', lambda: "%s" % uuid4()),
        ('PROJECT_NAME', lambda: project_name),
        ('SITE_NAME', partial(generate_site_name, project_name)),
        ('SITE_BRAND', partial(generate_site_brand, project_name)),
    ]
    config_paths = [os.path.join(project_path, path)
                    for path in ["config/__init__.py", "README.md"]]
    logger.info("replacing variables...")
    do_vars_replace(config_paths, variables)
    logger.info("done replacing variables.")

    # Clean up pyc files.
    for (root, dirs, files) in os.walk(project_path, False):
        for f in files:
            try:
                if f.endswith(".pyc"):
                    os.remove(os.path.join(root, f))
            except:
                pass


def main():
    import flask_project
    args = docopt(__doc__, version="Flask-Project {0}".format(flask_project.__version__))
    template_name = args.get('<template>') or 'default'
    project_name = args.get('<project>')
    try:
        create_project(project_name, template_name)
    except Exception as e:
        logger.error(e)
        project_path = os.path.join(os.getcwd(), project_name)
        shutil.rmtree(project_path)


if __name__ == "__main__":
    main()
