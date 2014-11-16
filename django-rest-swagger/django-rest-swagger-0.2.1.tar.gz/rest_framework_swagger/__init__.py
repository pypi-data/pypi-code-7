VERSION = '0.2.1'

DEFAULT_SWAGGER_SETTINGS = {
    'exclude_namespaces': [],
    'api_version': '',
    'api_path': '/',
    'api_key': '',
    'enabled_methods': ['get', 'post', 'put', 'patch', 'delete'],
    'is_authenticated': False,
    'is_superuser': False,
    'permission_denied_handler': None,
    'template_path': 'rest_framework_swagger/index.html',
}

try:
    from django.conf import settings
    SWAGGER_SETTINGS = getattr(settings, 'SWAGGER_SETTINGS', DEFAULT_SWAGGER_SETTINGS)

    for key, value in DEFAULT_SWAGGER_SETTINGS.items():
        if key not in SWAGGER_SETTINGS:
            SWAGGER_SETTINGS[key] = value

except:
    SWAGGER_SETTINGS = DEFAULT_SWAGGER_SETTINGS
