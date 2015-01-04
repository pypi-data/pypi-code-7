# coding: utf-8
from xml.etree import ElementTree


def _get_audio(el):
    return (el.attrib['region'],
            [(lambda inner_el: inner_el.attrib['src'])(source_el) for source_el
             in el])


def _get_definitions(elements):
    return [(el.find('definition/info/lvl').text,
             u' '.join(el.find('definition/def').itertext()),
             getattr(el.find('definition/trans'), 'text', None),
             [u' '.join(e.itertext()) for e in el.findall('examp')])
            for el in elements]


def _get_transcription(el):
    if el is not None and el.text:
        return u'/{0}/'.format(el.text)
    else:
        return u''


def _process_word(el):
    definition_path = 'sense-block/def-block'
    if el.find('header/info/posgram'):
        pos_path = 'header/info/posgram/pos'
        trans_path = 'header/info/pron/ipa'
        audio_path = 'header/info/audio'
    else:
        pos_path = 'header/info/anc/header/pos'
        trans_path = 'header/info/anc/info/pron/ipa'
        audio_path = 'header/info/anc/info/audio'

    return {'pos': getattr(el.find(pos_path), 'text', ''),
            'transcription': _get_transcription(el.find(trans_path)),
            'audio': [_get_audio(audio) for audio in
                      el.findall(audio_path)],
            'definition': _get_definitions(
                el.findall(definition_path))}


def _word_processing(root):
    elements = root.findall('pos-block')
    if elements:
        return [_process_word(el) for el in elements]
    else:
        return [_process_word(root)]


def parse(data):
    """

    :param data:
    :return:
    """
    return _word_processing(
        ElementTree.fromstring(data['entryContent'].encode('utf-8'))
    )


__all__ = [parse, ]