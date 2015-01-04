# coding: utf-8

import requests

import exceptions as exc


class API:
    JSON = 'json'
    XML = 'xml'
    HTML = 'html'

    urls = {
        'dictionaries': 'dictionaries',
        'dictionary': 'dictionaries/{dictCode}',
        'entry': 'dictionaries/{dictCode}/entries/{entryId}',
        'nearby_entries':
            'dictionaries/{dictCode}/entries/{entryId}/nearbyentries',
        'entry_pronunciations':
            'dictionaries/{dictCode}/entries/{entryId}/pronunciations',
        'related_entries':
            'dictionaries/{dictCode}/entries/{entryId}/relatedentries',
        'search': 'dictionaries/{dictCode}/search',
        'did_you_mean': 'dictionaries/{dictCode}/search/didyoumean',
        'search_first': 'dictionaries/{dictCode}/search/first'
    }

    def __init__(self, base_url, access_key, response_format=JSON):
        self._base_url = base_url

        assert response_format in (self.JSON, self.XML)
        self._headers = {
            'content-type': 'application/' + response_format,
            'accessKey': access_key
        }

    def dictionaries(self):
        """
        http://dictionary-api.cambridge.org/index.php/help/specification#getDictionaries

        :return:
        """
        return self._get(self.urls['dictionaries'])


    def dictionary(self, code):
        """
        http://dictionary-api.cambridge.org/index.php/help/specification#getDictionary

        :param code:
        :return:
        """
        return self._get(self.urls['dictionary'].format(
            **{'dictCode': code}
        ))

    def entry(self, code, entry_id):
        """
        http://dictionary-api.cambridge.org/index.php/help/specification#getEntry

        :param code:
        :return:
        """
        return self._get(self.urls['entry'].format(
            **{'dictCode': code, 'entryId': entry_id}
        ))

    def nearby_entries(self, code, entry_id):
        """
        http://dictionary-api.cambridge.org/index.php/help/specification#getNearbyEntries

        :param code:
        :param entry_id:
        :return:
        """
        return self._get(self.urls['nearby_entries'].format(
            **{'dictCode': code, 'entryId': entry_id}
        ))

    def entry_pronunciations(self, code, entry_id):
        """
        http://dictionary-api.cambridge.org/index.php/help/specification#getEntryPronunciations

        :param code:
        :param entry_id:
        :return:
        """
        return self._get(self.urls['entry_pronunciations'].format(
            **{'dictCode': code, 'entryId': entry_id}
        ))

    def related_entries(self, code, entry_id):
        """

        :param code:
        :param entry_id:
        :return:
        """
        return self._get(self.urls['related_entries'].format(
            **{'dictCode': code, 'entryId': entry_id}
        ))

    def search(self, code, word, size=10, page=1):
        """
        http://dictionary-api.cambridge.org/index.php/help/specification#search

        :param code:
        :param word:
        :param size:
        :param page:
        :return:
        """
        data = {
            'q': word,
            'pagesize': size,
            'pageindex': page
        }
        return self._get(self.urls['search'].format(
            **{'dictCode': code}
        ), params=data)

    def did_you_mean(self, code, word, size=10):
        """
        http://dictionary-api.cambridge.org/index.php/help/specification#didYouMean

        :param code:
        :param word:
        :param size:
        :return:
        """
        data = {
            'q': word,
            'entrynumber': size,
        }
        return self._get(self.urls['did_you_mean'].format(
            **{'dictCode': code}
        ), params=data)

    def search_first(self, code, word, format_body=XML):
        """
        http://dictionary-api.cambridge.org/index.php/help/specification#searchFirst

        :param code:
        :param word:
        :param format_body:
        :return:
        """
        assert format_body in (self.XML, self.HTML)
        data = {
            'q': word,
            'format': format_body
        }
        return self._get(self.urls['search_first'].format(
            **{'dictCode': code}
        ), params=data)

    def _get(self, url, **kwargs):
        res = requests.get('{0}/{1}'.format(self._base_url, url),
                           headers=self._headers, **kwargs)
        return self._process_result(res)

    @staticmethod
    def _process_result(result):
        data = result.json()
        if result.status_code == 404:
            e = getattr(exc, data['errorCode'], exc.InternalError)
            raise e(data['errorCode'], data['errorMessage'])
        elif result.status_code == 500:
            raise exc.InternalError(
                data['errorCode'], data['errorMessage']
            )

        return data


__all__ = [API, ]