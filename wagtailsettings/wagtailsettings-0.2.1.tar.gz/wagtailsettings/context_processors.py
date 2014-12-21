from django.db.models.loading import get_model


class SettingsProxy(dict):
    def __init__(self):
        self.cache = {}

    def __getattr__(self, app_label):
        if app_label not in self.cache:
            self.cache[app_label] = SettingModuleProxy(app_label)
        return self.cache[app_label]


class SettingModuleProxy(object):
    def __init__(self, app_label):
        self.app_label = app_label
        self.cache = {}

    def __getattr__(self, model_name):
        model_name = model_name.lower()
        if model_name not in self.cache:
            Model = get_model(self.app_label, model_name)
            self.cache[model_name] = Model.objects.first()
        return self.cache[model_name]


def settings(request):
    return {'settings': SettingsProxy()}
