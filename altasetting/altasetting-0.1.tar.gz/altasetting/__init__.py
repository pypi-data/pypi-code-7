from pyaml import yaml

class SettingsNode(object):
    def __init__(self, name=None, children=None, default=None):
        self.children = {"name": name}
        self.default = default
        if children is not None and hasattr(children, "items"):
            for child in children.items():
                def_ = None
                if default is not None:
                    def_ = getattr(default, child[0])
                self.children[child[0]] = SettingsNode(*child, default=def_)
        else:
            self.children = children

    def __getattr__(self, key):
        value = self.children
        try:
            value = self.children[key]
        except TypeError:
            pass
        except KeyError:
            if self.default is not None:
                value = self.default[key]
            else:
                value = None
        return value

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __repr__(self):
        ret = None
        if hasattr(self.children, "__iter__") and "name" in self.children:
            ret = "SettingsNode: %s" % self.children["name"]
        else:
            ret = self.children

        return str(ret)


class Settings(object):
    def __init__(self, settings_file, default_file):
        self.settings_file = settings_file
        self.default_file = default_file
        self._defaults = SettingsNode()
        self._settings = SettingsNode()

        self._load()

    def _load(self):
        settings = self._load_file(self.settings_file)
        defaults = self._load_file(self.default_file)
        self._defaults = SettingsNode("defaults", defaults)
        self._settings = SettingsNode("root", settings,
                                      default=self._defaults)

    def __getattr__(self, attr):
        return getattr(self._settings, attr)

    def _load_file(self, file_name):
        with open(file_name, 'r') as file_:
            settings = yaml.load(file_.read())

        return settings


if __name__ == '__main__':
    settings = Settings("/home/felipe/.touchandgo/settings.yaml",
                        "/home/felipe/devel/touchandgo/touchandgo/templates/settings.yaml")
    print settings.limits
    print settings.limits.download
    print settings.strategy.always_sequential


