import codecs
from datetime import datetime
import markdown2 as m
import yaml

from racconto.models import Post, Page

from racconto.settings_manager import SettingsManager as SETTINGS

class MissingYAMLFrontMatterError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class RaccontoParser():

    def parse(self, filepath):
        """Parses markdown content to html files.
        If file doesn't have a YAML Front Matter it
        stops parsing and returns None
        """
        try:
            config, content = self._config_and_content_reader(filepath)
        except MissingYAMLFrontMatterError:
            print "File at '%s' is missing a YAML Front Matter config" % filepath
            return None

        return self._parse_file(filepath, config, content)

    def _config_and_content_reader(self, filepath):
        """Reads config and content from file """
        config_separator = SETTINGS.get('CONFIG_SEPARATOR')
        f = codecs.open(filepath, 'r', 'utf-8')
        lines = f.readlines()
        f.close()

        raw_data = {"config": "", "content": "", "reading_config": False }

        for index, line in enumerate(lines):
            # File must start with YAML Front Matter
            if index == 0 and not line.startswith(config_separator):
                raise MissingYAMLFrontMatterError("File must start with YAML Front Matter")

            if line.startswith(config_separator):
                raw_data["reading_config"] = not raw_data["reading_config"]
                continue
            if raw_data["reading_config"]:
                raw_data["config"] += line
            else:
                raw_data["content"] += line

        if raw_data["reading_config"]:
          raise MissingYAMLFrontMatterError("Reached EOF before YAML Front Matter ended")

        # Parse config and content
        config = yaml.load(raw_data["config"])
        extras = SETTINGS.get('MARKDOWN_EXTRAS')
        content = m.markdown(raw_data["content"], extras=extras)

        return config, content

    def _parse_file(self, filepath, config, content):
        """Determines what type of content this is from filename
        and then calls the appropriate object creator method
        """
        filename = filepath.split('/')[-1:][0]
        possible_date = " ".join(filename.split('-')[0:3])
        try:
            date = datetime.strptime(possible_date, "%Y %m %d")
            return self._create_post(filepath, config, content, date)
        except ValueError:
            return self._create_page(filepath, config, content)

    def _create_post(self, filepath, config, content, date):
        """Creates a Post from file data
        """
        template = config.get("template", SETTINGS.get('POST_TEMPLATE'))
        return Post({
                "title": config["title"],
                "body":  content,
                "template": template,
                "date": date,
                "filepath": filepath,
                "config": config,
                })

    def _create_page(self, filepath, config, content):
        """Creates a Page from file data
        """
        template = config.get("template", SETTINGS.get('PAGE_TEMPLATE'))
        return Page({
                "title": config["title"],
                "body": content,
                "template": template,
                "filepath": filepath,
                "config": config,
                })
