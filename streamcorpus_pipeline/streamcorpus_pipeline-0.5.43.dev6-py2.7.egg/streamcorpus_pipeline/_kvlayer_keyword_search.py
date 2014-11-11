'''rudimentary keyword search indexing build on top of `kvlayer`

.. This software is released under an MIT/X11 open source license.
   Copyright 2012-2014 Diffeo, Inc.
'''
from __future__ import absolute_import
from collections import Counter
import logging
import struct
import uuid

import streamcorpus
from streamcorpus_pipeline._kvlayer_table_names import table_name, \
    epoch_ticks_to_uuid, HASH_TF_SID, HASH_KEYWORD
from yakonfig import ConfigurationError

logger = logging.getLogger(__name__)

INDEXING_DEPENDENCIES_FAILED = None
try:
    from backports import lzma
    from sklearn.feature_extraction.text import CountVectorizer
    from many_stop_words import get_stop_words
    import mmh3

except ImportError, exc:
    INDEXING_DEPENDENCIES_FAILED = str(exc)

## used in manipulating 128-bit doc_id hashes into two 64-bit Q ints
max_int64 = 0xFFFFFFFFFFFFFFFF
min_int64 = 0x0000000000000000

### This defines the keyword index keys
## big-endian preserves sorting order
## i = 4-byte signed int
## B = unsigned byte int (character)
## Q = unsigned 8-byte int
### see below for what goes in these fields
reverse_index_packing = '>iBQi'

def keywords(si, analyzer, hash_to_word):
    '''yields packed keys for kvlayer that form a keyword index on
    StreamItems. This uses murmur3 hash of the individual tokens
    generated by sklearn's `CountVectorizer` tokenization and
    filtering based on `many_stop_words`

    Also constructs the hash-->word mapping that inverts the murmur3
    hash, which gets stored as a separate table.

    '''
    if not si.stream_id:
        raise Exception('si.stream_id missing: %r' % si)
    if not si.body:
        logger.warn('no so.body on %s' % si.stream_id)
        return
    if not si.body.clean_visible:
        logger.warn('no so.body.clean_visible on %s' % si.stream_id)
        return
    if not si.stream_time.epoch_ticks:
        raise Exception('si.stream_time.epoch_ticks missing: %s' % si.stream_id)
    if not si.doc_id and len(si.doc_id) == 32:
        raise Exception('si.doc_id does not look like an md5 hash: %r' % si.doc_id)
    epoch_ticks = int(si.stream_time.epoch_ticks)
    doc_id = int(si.doc_id, 16)
    ## split doc_id into two 8-byte things, we only use the first below
    doc_id_1, doc_id_2 = (doc_id >> 64) & max_int64, doc_id & max_int64
    for tok, count in Counter(analyzer(si.body.clean_visible)).items():
        tok_encoded = tok.encode('utf8')
        tok_hash = mmh3.hash(tok_encoded)
        ## put both tok_hash and tok in the key, so we get all
        ## meanings of a hash even if collisions occur
        hash_to_word[(tok_hash, tok_encoded)] = r''
        ## force count to fit within a single byte
        count = min(count, 2**8 - 1)
        ## from debugging https://diffeo.atlassian.net/browse/DIFFEO-804
        #if tok_hash == 2054597875:
        #    logger.info('*** keywords: %r %r %r %r %r', tok, tok_hash, count, doc_id_1, epoch_ticks)
        #    logger.info('*** %r', struct.pack(reverse_index_packing, tok_hash, count, doc_id_1, epoch_ticks))
        ## can drop doc_id_2 and still have 10**19 document space to
        ## avoid collisions; epoch_ticks last allows caller to select
        ## only the last document.
        ### this yields kvlayer-style tuple(key-tuple, value) with all
        ### the info in the key:
        yield (struct.pack(reverse_index_packing, tok_hash, count, doc_id_1, epoch_ticks),), r''


class keyword_indexer(object):
    '''Utility class used by `to_kvlayer` and `from_kvlayer` to implement
simple token-based search.

    '''

    @staticmethod
    def check_config(config, name):
        ## called by streamcorpus_pipeline._kvlayer.{to,from}_kvlayer.check_config
        if HASH_TF_SID in config['indexes'] and \
           HASH_KEYWORD not in config['indexes']:
                raise ConfigurationError(
                    '{} set but {} is not; need both or neither'
                    .format(HASH_TF_SID, HASH_KEYWORD))
        if HASH_KEYWORD in config['indexes']:
            if INDEXING_DEPENDENCIES_FAILED:
                raise ConfigurationError(
                    'indexing is not enabled: {}'
                    .format(INDEXING_DEPENDENCIES_FAILED))
            if HASH_TF_SID not in config['indexes']:
                raise ConfigurationError(
                    '{} set but {} is not; need both or neither'
                    .format(HASH_KEYWORD, HASH_TF_SID))

    def __init__(self, kvl):
        '''`kvl` is a kvlayer client that has been configured and had
        :method:`~kvlayer._abstract_client.setup_namespace` called.

        '''
        self.client = kvl
        self.analyzer = self.build_analyzer()

    @staticmethod
    def build_analyzer():
        '''builds an sklearn `CountVectorizer` using `many_stop_words`

        '''
        if INDEXING_DEPENDENCIES_FAILED:
            raise ConfigurationError('indexing is not enabled: {}'
                                     .format(INDEXING_DEPENDENCIES_FAILED))
        ## sensible defaults; could need configuration eventually
        cv = CountVectorizer(
            stop_words=get_stop_words(),
            strip_accents='unicode',
        )
        return cv.build_analyzer()

    def index(self, si):
        '''create both "word barrels" style keyword reverse index, and also a
        mapping from murmur3 hash value to the input strings.

        '''
        hash_to_word = dict()
        self.client.put(table_name(HASH_TF_SID),
                        *list(keywords(si, self.analyzer, hash_to_word)))
        self.client.put(table_name(HASH_KEYWORD),
                        *hash_to_word.items())


    def invert_hash(self, tok_hash):
        '''returns a list of all the Unicode strings that have been mapped to
    the `tok_hash` integer

        '''
        return [tok_encoded.decode('utf8') 
                for (_, tok_encoded) in 
                self.client.scan(table_name(HASH_KEYWORD), ((tok_hash,), (tok_hash + 1,)))]

    def search(self, query_string):
        '''queries the keyword index for `word` and yields
        :class:`~streamcorpus.StreamItem` objects that match sorted in
        order of number of times the document references the word.

        warning: this is a very rudimentary search capability

        An analyzer generated by `build_analyzer` is used to tokenize and
        filter the `query_string`.  This can remove tokens.  Results for
        each token are yielded separately, which is equivalent to
        combining the separate tokens in a Boolean OR query.

        '''
        for tok in self.analyzer(query_string):
            #import pdb; pdb.set_trace()
            ## build a range query around this token's hash
            tok_hash = mmh3.hash(tok.encode('utf8'))
            ## the [:2] is a local work around for https://diffeo.atlassian.net/browse/DIFFEO-804
            tok_start = struct.pack(reverse_index_packing[:2], tok_hash    )
            tok_end   = struct.pack(reverse_index_packing[:2], tok_hash + 1)
            #logger.info('%r --> %s' % (tok_hash, self.invert_hash(tok_hash)))
            #logger.info('from %r', tok_start)
            #logger.info('to   %r', tok_end)
            ## query the keyword index
            for (key,), _ in self.client.scan(table_name(HASH_TF_SID),
                                   ((tok_start,), (tok_end,))):
                _tok_hash, count, doc_id_1, epoch_ticks = struct.unpack(reverse_index_packing, key)
                #logger.info('found %d %d', _tok_hash, count)
                ## assert that logic around big-endianness preserving sort
                ## order worked:
                assert tok_start <= key <= tok_end
                assert tok_hash <= _tok_hash <= tok_hash + 1
                ## build a range query around this epoch_ticks-half_doc_id
                doc_id_max_int = (doc_id_1 << 64) | max_int64
                doc_id_min_int = (doc_id_1 << 64) | min_int64
                key1 = epoch_ticks_to_uuid(epoch_ticks)
                key2_max = uuid.UUID(int=doc_id_max_int)
                key2_min = uuid.UUID(int=doc_id_min_int)
                for _, xz_blob in self.client.scan(table_name(), ((key1, key2_min), (key1, key2_max))):
                    ## given the half-doc_id this could yield some false positives
                    thrift_blob = lzma.decompress(xz_blob)
                    yield streamcorpus.deserialize(thrift_blob)


