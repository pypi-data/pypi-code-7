#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2014 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Hervé BREDIN - http://herve.niderb.fr

from __future__ import unicode_literals


from preprocessing import TextPreProcessing
from gensim import corpora


class PreProcessedTranscription(object):

    def __init__(self, transcriptions, attribute='speech', preprocessing=None):
        super(PreProcessedTranscription, self).__init__()
        self.transcriptions = transcriptions
        self.attribute = attribute
        if preprocessing is None:
            preprocessing = TextPreProcessing()
        self.preprocessing = preprocessing

    def __iter__(self):
        for transcription in self.transcriptions:
            for _, _, data in transcription.ordered_edges_iter(data=True):
                if self.attribute not in data:
                    continue
                yield self.preprocessing(data[self.attribute])

transcript = gameOfThrones.get_resource_from_plugin('transcript', gameOfThrones.episodes[0])
preProcessedTranscription = PreProcessedTranscription([transcript])
dictionary = corpora.Dictionary(preProcessedTranscription)


class BOWCorpus(object):

    def __init__(self, transcriptionCorpus, dictionary):
        super(BOWCorpus, self).__init__()
        self.transcriptionCorpus = transcriptionCorpus
        self.dictionary = dictionary

    def __iter__(self):
        for document in self.transcriptionCorpus:
            yield self.dictionary.doc2bow(document)

bowCorpus = BOWCorpus(preProcessedTranscription, dictionary)


import sklearn.feature_extraction.text


def identity(x):
    return x

cv = sklearn.feature_extraction.text.CountVectorizer(tokenizer=identity,
                                                     analyzer=identity,
                                                     preprocessor=identity)

cv.fit(preProcessedTranscription)
counts = cv.transform(preProcessedTranscription)


tfidf = sklearn.feature_extraction.text.TfidfTransformer(
    norm=u'l2', use_idf=True, smooth_idf=True, sublinear_tf=True)
tfidf.fit(counts)

x = tfidf.transform(counts)
