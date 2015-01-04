# coding: utf-8

import os
import pytest
from camdict.util import parse

import exceptions as exc

from api import API


assert os.environ['access-key']

api = API(
    base_url='https://dictionary.cambridge.org/api/v1',
    access_key=os.environ['access-key'],
    response_format='json'
)


def test_dictionaries():
    data = api.dictionaries()

    assert isinstance(data, list)
    assert len(data) > 0


def test_dictionary():
    data = api.dictionary('british')

    assert isinstance(data, dict)
    assert len(data) > 0


def test_wrong_dictionary():
    with pytest.raises(exc.InvalidDictionary):
        api.dictionary('russian')


def test_entry():
    data = api.entry('british', 'hello')
    assert isinstance(data, dict)
    assert data['entryId'] == 'hello'


def test_wrong_entry_id():
    with pytest.raises(exc.InvalidEntryId):
        api.entry('british', 'wrong_entry_id')


def test_nearby_entry():
    data = api.nearby_entries('british', 'hello')
    assert isinstance(data, dict)
    assert data['nearbyFollowingEntries']
    assert data['nearbyPrecedingEntries']


def test_entry_pronunciations():
    data = api.entry_pronunciations('british', 'hello')
    assert isinstance(data, list)


def test_related_entries():
    data = api.related_entries('british', 'hello')
    assert isinstance(data, dict)
    assert data['relatedEntries']


def test_search():
    data = api.search('british', 'hello')

    assert isinstance(data, dict)

    assert data.get('results')
    assert isinstance(data['results'], list)
    assert len(data['results']) > 0


def test_search_wrong_page():
    with pytest.raises(exc.PageNotFound):
        api.search('british', 'hello', page=42)


def test_did_you_mean():
    data = api.did_you_mean('british', 'hellot')

    assert data.get('suggestions')
    assert isinstance(data['suggestions'], list)
    assert len(data['suggestions']) > 0


def test_search_first():
    data = api.search_first('british', 'test')
    assert isinstance(data, dict)
    assert data.get('entryContent')


def test_wrong_test_search_first():
    with pytest.raises(exc.NoResults):
        api.search_first('british', 'hellohello')


def test_match():
    data = api.search_first('british', 'sensation')
    data = parse(data)
    assert isinstance(data, list)
    for value in data:
        assert isinstance(value, dict)
        assert value.get('audio')
        assert value.get('pos')
        assert value.get('transcription')
        assert value.get('definition')


def test_complex_match():
    data = api.search_first('english-russian', 'come up')
    data = parse(data)
    assert isinstance(data, list)
    assert len(data) == 1

    value, = data
    assert isinstance(value, dict)
    assert value.get('audio')
    assert value.get('pos')
    assert value.get('transcription')
    assert value.get('definition')
