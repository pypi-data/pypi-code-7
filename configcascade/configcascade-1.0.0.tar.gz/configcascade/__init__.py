import yaml
from os.path import realpath, dirname, isabs
import abc


class Settings:
    def __init__(self, file_loader, mergeable_elements=None):
        """
        @type file_loader: FileLoader
        @type mergeable_elements: list, tuple
        """
        self._file_loader = file_loader

        if mergeable_elements is None:
            mergeable_elements = []

        if "imports" not in mergeable_elements:
            mergeable_elements.append("imports")

        self._mergeable_elements = mergeable_elements

    def compile(self, config_file):
        config_dir = dirname(realpath(config_file))

        settings = self._file_loader.load(config_file)
        settings = self._import_elements(settings, config_dir)

        return settings

    def _import_elements(self, settings, working_dir):
        if 'imports' in settings and len(settings['imports']) > 0:
            import_file = settings['imports'].pop()
            if not isabs(import_file):
                import_file = realpath('%s/%s' % (working_dir, import_file))
            imported_settings = self._file_loader.load(import_file)
            settings = self._overwrite_unmergeable_elements(settings, imported_settings)
            settings = self._merge_elements(settings, imported_settings)
            return self._import_elements(settings, dirname(import_file))
        else:
            return settings

    def _overwrite_unmergeable_elements(self, settings, imported_settings):
        for element_key, element_value in imported_settings.items():
            if element_key not in self._mergeable_elements and element_key not in settings:
                settings[element_key] = element_value
        return settings

    def _merge_elements(self, settings, imported_settings):
        for mergeable_element in self._mergeable_elements:
            settings = self._merge_element(settings, imported_settings, mergeable_element)

        return settings

    @staticmethod
    def _merge_element(settings, imported_settings, key):
        if key in imported_settings:
            if key in settings:
                if isinstance(settings[key], dict):
                    settings[key] = dict(list(imported_settings[key].items()) + list(settings[key].items()))
                if isinstance(settings[key], list):
                    settings[key] = imported_settings[key] + settings[key]
            else:
                settings[key] = imported_settings[key]

        return settings


class FileLoader:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def load(self, file_path):
        """
        @param file_path:
        @return dict
        """


class YamlFileLoader(FileLoader):
    def load(self, file_path):
    #def _settings_yml_loader(file_path):
        """ @type file_path: str """
        settings_stream = open(file_path, "r")
        settings_generator = yaml.load_all(settings_stream)

        app_settings = {}
        for app_settings_ in settings_generator:
            for key, value in app_settings_.items():
                app_settings[key] = value

        return app_settings
