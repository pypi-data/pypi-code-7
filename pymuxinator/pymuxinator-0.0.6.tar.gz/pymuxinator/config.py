import os
import fnmatch
import yaml

from jinja2 import Template
from pymuxinator import exceptions

root = os.path.expanduser("~") + u'/.pymuxinator'


def list_all():
    matches = []

    for l_root, dirnames, filenames in os.walk(root):
      for filename in fnmatch.filter(filenames, u'*.yml'):
          matches.append(os.path.join(l_root, filename))

    return matches


def project_path(project_name):
    project_name = project_name + u'.yml'

    for project in list_all():
        if project_name in project:
            return project

    raise exceptions.ProjectNotFoundError


def load(project_name):
    path = project_path(project_name)

    with open(path, 'r') as config_file:
        try:
            return yaml.load(config_file)
        except Exception as e:
            raise exceptions.ConfigParseError(path)

def load_template(template_name):
    path = '%s/templates/%s.template' % (os.path.dirname(__file__), template_name)

    with open(path) as template:
        return Template(template.read())

    return template_name

def get_env_var(var_name, default=None):
    return os.environ.get(var_name, default)
