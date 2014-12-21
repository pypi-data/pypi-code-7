from collections import defaultdict

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from django.conf.urls import patterns, url
from django.template.defaultfilters import slugify


class MasterSite(object):
    def __init__(self):
        self.pages = defaultdict(list)
        self.widgets = defaultdict(list)
        self.urls = ()
        self._menu = OrderedDict()

    @property
    def urlpatterns(self):
        self._menu = OrderedDict()
        urls = []

        for module, pages in self.pages.items():
            module = module.replace('.master', '')
            self._menu[module] = []
            module_name = slugify(module)

            for page in pages:
                page_name = slugify(page.name)
                page.slug = module_name + '-' + page_name
                pattern = r'^{module}/{page}'.format(module=module_name,
                                                     page=page_name)
                urls.append(url(pattern, page.as_view(), name=page.slug))

                self._menu[module].append({
                    'name': page.slug,
                    'label': page.label
                })

        return patterns(r'', *urls)

    def add_view(self, module_name, view):
        self.pages[module_name].append(view)

    def add_widget(self, module_name, widget):
        self.widgets[module_name].append(widget)

    def get_menu(self):
        if not self._menu:
            self.urlpatterns
        return self._menu

mastersite = MasterSite()
