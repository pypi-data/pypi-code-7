import os
import codecs
import distutils

from jinja2 import Environment, FileSystemLoader

from racconto.settings_manager import SettingsManager as SETTINGS

class Generator:

    jinja_env = None

    @classmethod
    def setup_jinja_environment(cls, templates_path):
        """Load save the jinja2 environment
        """
        cls.jinja_env = Environment(loader=FileSystemLoader(templates_path))

    @classmethod
    def generate(cls, content_object, directory):
        """Generates a file from content_object
        in the specified directory using the jinja environment.
        content_object - instance of Post or Page
        directory - name of directory to save generated file
        """
        template = cls.jinja_env.get_template(content_object.template)
        output = template.render(content_object.template_parameters)
        # Create the directories if they don't exist already
        path = "%s/%s" % (directory, content_object.filepath)
        if not os.path.exists(path):
            os.makedirs(path)

        full_path = "%s/%s" % (path, 'index.html')
        f = codecs.open(full_path, 'w+', 'utf-8')
        f.write(output)
        f.close()

    @classmethod
    def generate_index_file(cls, directory_path, template_name, **template_arguments):
        """
        Generates a index.html with template (rendered with template_arguments)
        inside directory_path.
        """
        template = cls.jinja_env.get_template(template_name)
        path = "%s/%s" % (directory_path, "index.html")
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        f = codecs.open(path, 'w+', 'utf-8')
        f.write(template.render(**template_arguments))
