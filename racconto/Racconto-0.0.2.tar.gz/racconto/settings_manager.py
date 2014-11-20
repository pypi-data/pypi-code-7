class SettingsManager(object):

    _default_settings = {
        'SITEDIR':  'site',
        'BLOGDIR': 'site',
        'CONTENTDIR': 'content',
        'TEMPLATEDIR': 'templates',
        'STATICDIR': 'static',

        'YEAR_TEMPLATE': 'year_archive.j2',
        'MONTH_TEMPLATE': 'month_archive.j2',
        'DAY_TEMPLATE': 'day_archive.j2',
        "POST_TEMPLATE": 'post.j2',
        "PAGE_TEMPLATE": 'page.j2',
        'BLOG_INDEX_TEMPLATE': 'index.j2',

        'IGNORE_PATTERNS': [],
        "CONFIG_SEPARATOR": '---',
        'FILTERS': {},
        'MARKDOWN_EXTRAS': ["fenced-code-blocks"],
        }

    settings = _default_settings.copy()

    @classmethod
    def override(cls, module):
        for key in cls._default_settings.iterkeys():
            cls.settings[key] = getattr(module, key, cls._default_settings[key])

    @classmethod
    def get(cls, key):
        return cls.settings[key]
