# coding=utf-8
__author__ = 'kohlmannj'

from flask import jsonify, render_template
from Ity.Utilities import get_corpora as util_get_corpora
from Ity.Utilities import get_models as util_get_models
from Ity import metadata_root
import os
import glob
import csv


def get_corpora():
    available_corpora = util_get_corpora()
    # corpora_uris = {}
    # for corpus_name in available_corpora:
    #     corpora_uris[corpus_name] = url_for("corpus_view_by_name", corpus_name=corpus_name)
    return jsonify({"corpora": available_corpora})

def get_models():
    available_models = util_get_models()
    return jsonify({"models": available_models})

def _get_word_rankings(corpus_name, words, rankingType='sal'):
    topicDir = os.path.join(metadata_root, corpus_name, 'TopicModel', 'topics_%s' % rankingType)
    numTopics = len(glob.glob(os.path.join(topicDir, 'topic_*.csv')))
    rankings = {}
    for word in words:
        rankings[word] = [ -1 for i in range(numTopics) ]
    wordsPerTopic = [ 0 for i in range(numTopics) ]
    maxWordsPerTopic = 0
    for topic in range(numTopics):
        with open(os.path.join(topicDir, 'topic_%d.csv' % topic), 'rb') as topicF:
            topicReader = csv.reader(topicF)
            currRow = 0
            for row in topicReader:
                if row[0] in words:
                    rankings[row[0]][topic] = currRow
                currRow += 1
            wordsPerTopic[topic] = currRow
            maxWordsPerTopic = max(maxWordsPerTopic, currRow)
    return {'rankings': rankings, 'wordsPerTopic':wordsPerTopic, 'maxWordsPerTopic':maxWordsPerTopic}

def get_word_ranking(corpus_name, word, rankingType='sal'):
    topicDir = os.path.join(metadata_root, corpus_name, 'TopicModel', 'topics_%s' % rankingType)
    numTopics = len(glob.glob(os.path.join(topicDir, 'topic_*.csv')))
    ranking = [ -1 for i in range(numTopics) ]
    for topic in range(numTopics):
        with open(os.path.join(topicDir, 'topic_%d.csv' % topic), 'rb') as topicF:
            topicReader = csv.reader(topicF)
            currRow = 0
            for row in topicReader:
                if row[0]==word:
                    ranking[topic] = currRow
                currRow += 1
    return jsonify({'ranking': ranking})

def get_word_rankings_json(corpus_name, words, rankingType='sal'):
    words = words.split(',')
    return jsonify(_get_word_rankings(corpus_name, words, rankingType))

def wordRankings(corpus_name, wordColorPairs, rankingType='sal'):
    words = []
    colors = []
    if wordColorPairs != 'empty':
        for pair in wordColorPairs.split(','):
            word, color = pair.split(':')
            words.append(word)
            colors.append(color)
    wr = _get_word_rankings(corpus_name, words, rankingType)
    wr['words'] = words
    wr['colors'] = colors
    return render_template(
        'wordRankings.html',
        corpus_name=corpus_name,
        rankingsObject=wr,
        rankingType=rankingType
    )

def wordRankingsDefault(corpus_name):
    return wordRankings(corpus_name, 'empty', 'sal')