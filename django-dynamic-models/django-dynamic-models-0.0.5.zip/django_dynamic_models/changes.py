class AlreadyRegistered(Exception):
    pass

class ModelChange(object):
    """
    An ModelChange
    """

    def __init__(self):
        self._registry = {}
        
    def register(self, model_name, **changes):
        """
        Registers the given model(s) with the given admin class.
        The model(s) should be Model classes, not instances.
        If an admin class isn't given, it will use ModelAdmin (the default
        admin options). If keyword arguments are given -- e.g., list_display --
        they'll be applied as options to the admin class.
        If a model is already registered, this will raise AlreadyRegistered.
        If a model is abstract, this will raise ImproperlyConfigured.
        """
        if not model_name in self._registry:
            self._registry[model_name] = {}

        # Instantiate the admin class to save in the registry
        for change in changes.keys():
            if change in self._registry[model_name]:
                raise AlreadyRegistered('A model field change %s in the model %s is already registered' % (change, model_name))

        self._registry[model_name].update(changes)

    def has_model_changes(self, model_name):
        """
        Check if a model class is registered with this `ModelChange`.
        """

        return model_name in self._registry

    def is_registred(self, model_name, field_name):
        """
        Check if a model class is registered with this `ModelChange`.
        """

        if model_name in self._registry:
            return field_name in self._registry[model_name]

        return False

    def get_model_changes(self, model_name, app_label):
        """
        get model changes.
        """
        changes = {'__module__':'%s.models'%app_label,}

        if self.has_model_changes(model_name):
            changes.update(self._registry[model_name])
            
        return changes


    def get_changes(self):
        return self._registry

    def load(self, model_name, model_base_class, app_label):
        return type(model_name, (model_base_class,), self.get_model_changes(model_name, app_label)) 
# This global object represents the default admin site, for the common case.
# You can instantiate ModelChange in your own code to create a custom admin site.
change = ModelChange()
