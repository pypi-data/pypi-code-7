import re
import json

from django.conf.urls import patterns, include, url

from tastypie.api import Api
from tastypie.serializers import Serializer
from tastypie.authorization import DjangoAuthorization
from tastypie.authentication import SessionAuthentication


class UsersApi(Api):

    def __init__(self):
        super(UsersApi, self).__init__(api_name=None)

    @property
    def urls(self):
        """
        Override Api.urls to ignore ``api_name`` from resources urls.
        """
        pattern_list = [
            url(r'^$', self.wrap_view('top_level'), name='api_top_level'),
        ]

        for name in sorted(self._registry.keys()):
            self._registry[name].api_name = self.api_name
            pattern_list.append((r'', include(self._registry[name].urls)))

        urlpatterns = self.prepend_urls()

        urlpatterns += patterns(
            '',
            *pattern_list
        )

        return urlpatterns


# Copyrights: https://django-tastypie.readthedocs.org/en/latest/cookbook.html#camelcase-json-serialization  # noqa
class JsonSerializer(Serializer):
    formats = ['json']
    content_types = {
        'json': 'application/json',
    }

    def to_json(self, data, options=None):
        # Changes underscore_separated names to camelCase names to go from
        # python convention to javacsript convention
        data = self.to_simple(data, options)

        def underscoreToCamel(match):
            return match.group()[0] + match.group()[2].upper()

        def camelize(data):
            if isinstance(data, dict):
                new_dict = {}
                for key, value in data.items():
                    new_key = re.sub(r"[a-z]_[a-z]", underscoreToCamel, key)
                    new_dict[new_key] = camelize(value)
                return new_dict
            if isinstance(data, (list, tuple)):
                for i in range(len(data)):
                    data[i] = camelize(data[i])
                return data
            return data

        camelized_data = camelize(data)

        return json.dumps(camelized_data, sort_keys=True)

    def from_json(self, content):
        # Changes camelCase names to underscore_separated names to go from
        # javascript convention to python convention
        data = json.loads(content)

        def camelToUnderscore(match):
            return match.group()[0] + "_" + match.group()[1].lower()

        def underscorize(data):
            if isinstance(data, dict):
                new_dict = {}
                for key, value in data.items():
                    new_key = re.sub(r"[a-z][A-Z]", camelToUnderscore, key)
                    new_dict[new_key] = underscorize(value)
                return new_dict
            if isinstance(data, (list, tuple)):
                for i in range(len(data)):
                    data[i] = underscorize(data[i])
                return data
            return data

        underscored_data = underscorize(data)

        return underscored_data


class CommonMeta:
    excludes = ['id']

    max_limit = None

    always_return_data = True

    list_allowed_methods = ['get', 'post']
    detail_allowed_methods = ['get', 'put', 'delete']

    serializer = JsonSerializer()

    authentication = SessionAuthentication()
    authorization = DjangoAuthorization()
