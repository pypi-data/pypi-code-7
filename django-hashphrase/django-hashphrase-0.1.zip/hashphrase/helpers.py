hashphrase_functions = None

class Hashlink(object):
    def __init__(self, *args, **kwargs):
        import datetime
        self.current_datetime_function = kwargs.get('current_datetime_function', datetime.datetime.now)
        super(Hashlink, self).__init__()

        self.function_map = dict(default_action=("hashphrase.views","default_action_on_error"),
            default_action2=("hashphrase.views","test_success"))


    def register(self, category_name, function):
        self.register_function(function.__module__,
                               function.__name__,
                               function.__doc__, category_name)

    def register_function(self, module, name, doc, category_name):
        """
        Register function at 'module' depth
        """
        if category_name in self.function_map:
            return

        self.function_map[category_name] = (module, name)

    def get_category_names(self):
        """
        """
        return self.function_map.keys()

    def get_module_and_function(self, category_name):
        return self.function_map.get(category_name, (None,None))


def init_package():
    from django.conf import settings
    from models import _import_from_string
    import datetime
    global hashphrase_functions
    if hasattr(settings, 'HASHPHRASE_CURRENT_DATETIME_FUNCTION'):
        current_datetime_function = _import_from_string(settings.HASHPHRASE_CURRENT_DATETIME_FUNCTION)
        if not current_datetime_function:
            current_datetime_function = datetime.datetime.now()
    else:
        current_datetime_function = datetime.datetime.now()
    hashphrase_functions = Hashlink(current_datetime_function=current_datetime_function)

    if hasattr(settings, 'HASHPHRASE_HANDLERS'):
        for func_str in settings.HASHPHRASE_HANDLERS:
            #trigger parsing so they registered
            _import_from_string(func_str, file_only=True)



def hashphrase_register(*setting_args, **setting_kwargs):
    """
    """
    no_args = False
    function = None
    if len(setting_args) == 1 \
        and not setting_kwargs \
        and callable(setting_args[0]):
        # We were called without args
        function = setting_args[0]
        no_args = True
        raise "Needs at least one parameter - category name"
    else:
        category_name = setting_args[0]
    def second_wrapper(function):
        from functools import wraps
        hashphrase_functions.register(category_name, function)
        @wraps(function)
        def third_wrapper(request, *args, **kwargs):
            return function(request, *args, **kwargs)
        return third_wrapper
    if no_args: #it's different with or without arguments
        return second_wrapper(function)
    else:
        return second_wrapper
