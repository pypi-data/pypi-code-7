# coding=utf-8
__author__ = 'ealexand'

import json
import csv
import os
import sys
from flask import Blueprint, render_template, abort, current_app, jsonify, request

vep_core_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')
sys.path.append(vep_core_dir)
sys.path.append(os.path.join(vep_core_dir, "Serendip"))
sys.path.append(os.path.join(vep_core_dir, "Ity"))
from Ity import metadata_root, Utilities
#from Ity.Couriers import TopicModelCorpusCourier
from Ity.Taggers import TopicModelTagger

import numpy
import MikeTM

# *CorpusCourier classes, keyed by the corpus_name.
corpus_couriers = {}
corpora = Utilities.get_corpora()
models = Utilities.get_models()

def _parse_list_from_get_value(get_value_name):
    get_value = request.args.get(get_value_name)
    if get_value is None or get_value == "":
        get_value_list = []
    else:
        get_value_list = get_value.split(",")
    return get_value_list


'''def _get_corpus_courier(corpus_name):
    try:
        courier = corpus_couriers[corpus_name]
    except KeyError:
        # Haven't seen this corpus before.
        courier = TopicModelCorpusCourier(corpus_name=corpus_name)
        # Reuse this courier later.
        corpus_couriers[corpus_name] = courier
    return courier'''


def index():
    return view_by_name("foo")


def view_by_name(corpus_name):
    # Create a TopicModelCorpusCourier for this corpus_name; we'll need it!
    # corpus_couriers[corpus_name] = TopicModelCorpusCourier(corpus_name=corpus_name)
    return render_template(
        "corpus/index.html",
        script="app",
        # Examples
        title=corpus_name + " (Matrix View)",
        corpus_name=corpus_name,
        corpora=corpora,
        models=models
    )


def mesoview(corpus_name):
    # Create a TopicModelCorpusCourier for this corpus_name; we'll need it!
    # corpus_couriers[corpus_name] = TopicModelCorpusCourier(corpus_name=corpus_name)
    # Create a TopicModelTagger just to get the tags! This is behavior specific to TopicModelTagger.
    tagger = TopicModelTagger(corpus_name=corpus_name)
    # Get which texts we want to show.
    # TODO: Decide what the default is. Every text or no text?
    included_text_names = _parse_list_from_get_value("included_text_names")
    # Include every text instead if we're given zero text names to include.
    if len(included_text_names) == 0 and corpus_name in corpora:
        included_text_names = corpora[corpus_name]
    # Also, get whichever topics should be enabled.
    included_tag_keys = _parse_list_from_get_value("included_tag_keys")
    # Getting colors, as done in TextViewer.py. (This seems silly...)
    colors = json.dumps([ramp[0] for ramp in current_app.config["COLORS"]["seq_single_hue_ramps_5"]])
    # Elsewhere, in JavaScript land:
    # flask_util.url_for("corpus_mesoview", { corpus_name: "Foo", included_text_names: text_names});
    return render_template(
        "corpus/meso.html",
        title=corpus_name + " (Meso View)",
        corpus_name=corpus_name,
        tags=[tagger.tags, []],
        included_tag_keys=included_tag_keys,
        included_text_names=included_text_names,
        colors=colors,
        corpora=corpora
    )


def get_metadata(corpus_name):
    metadataCSV = os.path.join(metadata_root, corpus_name + '/TopicModel/metadata.csv')
    if not os.path.exists(metadataCSV):
        metadataCSV = os.path.join(metadata_root, corpus_name.split("/")[0] + '/TopicModel/metadata.csv')
    metadata = []
    with open(metadataCSV, 'rb') as f:
        reader = csv.reader(f)
        rowNum = 0
        for row in reader:
            if rowNum == 0:
                colNames = row
            elif rowNum == 1:
                dataTypes = row
            else:
                temp = {}
                for i in range(len(row)):
                    temp[colNames[i]] = row[i]
                    # TODO: Remove the need for this!
                #### TEMPORARY ANNOYING CACHE HACK ####
                #### DO WE HAVE CACHE FILES FOR THIS TEXT?!?!?!1one!?!1eleven ####
                filename_cache_path = os.path.join(
                    metadata_root,
                    corpus_name,
                    "TopicModel",
                    "Serendip",
                    os.path.splitext(
                        # Word of advice: don't change the column name in these CSV files.
                        os.path.basename(temp["filename"])
                    )[0]
                )
                #### ONLY APPEND IF WE HAVE CACHE DATA FOR THIS FILE ####
                # if (
                #     not current_app.config["TOPICMODEL_STATIC_CACHE"] or
                #     (current_app.config["TOPICMODEL_STATIC_CACHE"] and os.path.exists(filename_cache_path))
                # ):
                if os.path.exists(filename_cache_path) or True:
                    metadata.append(temp)
                    #### END HACKS ####
            rowNum += 1
    try:
        return jsonify({'metadata': metadata, 'fieldNames': colNames, 'dataTypes': dataTypes})
    except UnicodeDecodeError:
        for i in range(len(metadata)):
            try:
                jsonify({'metadata': metadata[i]})
            except UnicodeDecodeError:
                print 'UnicodeDecodeError on metadata row %d' % i
                print metadata[i]
                raise


def get_theta(corpus_name):
    includedMetadataIndices = getIncludedMetadata(corpus_name)
    thetaCSV = os.path.join(metadata_root, corpus_name + '/TopicModel/theta.csv')
    if not os.path.exists(thetaCSV):
        thetaCSV = os.path.join(metadata_root, corpus_name.split("/")[0] + '/TopicModel/theta.csv')
    theta = []
    topicProps = {}
    with open(thetaCSV, 'rb') as f:
        reader = csv.reader(f)
        currDoc = 0
        currIndex = 0 # This is only incremented if we actually include the doc
        maxTopic = 0
        for row in reader:
            if currDoc in includedMetadataIndices:
                theta.append({})
                for i in range(0, len(row), 2):
                    topicNum = int(row[i])
                    prop = float(row[i+1])
                    theta[currIndex][topicNum] = prop
                    maxTopic = max(maxTopic, topicNum)
                    if topicNum in topicProps:
                        topicProps[topicNum].append(prop)
                    else:
                        topicProps[topicNum] = [prop]
                currIndex += 1
            currDoc += 1

    topicMetadataList = [{} for i in range(maxTopic+1)]
    for i in range(maxTopic+1):
        if i in topicProps:
            currTopicList = topicProps[i]
            topicMetadataList[i]['numDocs'] = len(currTopicList)
            topicMetadataList[i]['min'] = numpy.min(currTopicList)
            topicMetadataList[i]['max'] = numpy.max(currTopicList)
            topicMetadataList[i]['median'] = numpy.median(currTopicList)
            topicMetadataList[i]['mean'] = numpy.mean(currTopicList)
            topicMetadataList[i]['variance'] = numpy.var(currTopicList)
            topicMetadataList[i]['range'] = topicMetadataList[i]['max'] - topicMetadataList[i]['min']
            #topicMetadataList[i]['outliers'] = 0 #TODO: fill this in
            #topicMetadataList[i]['uniformity'] = 0 #TODO: fill this in
        else:
            topicMetadataList[i] = {
                'numDocs': 0,
                'min': 0,
                'max': 0,
                'median': 0,
                'mean': 0,
                'variance': 0,
                'range': 0
            }
    topicMetadataFields = ['min','max','median','mean','variance','range','numDocs']#,'outliers','uniformity']

    returnDict = {}
    returnDict['theta'] = theta
    returnDict['numDocs'] = len(theta)
    returnDict['numTopics'] = maxTopic + 1
    returnDict['topicMetadata'] = topicMetadataList
    returnDict['topicMetadataFields'] = topicMetadataFields

    try:
        topicNameFile = os.path.join(metadata_root, corpus_name + '/TopicModel/topicNames.csv')
        with open(topicNameFile, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                topicNames = row
                break
        returnDict['colList'] = topicNames
    except IOError:
        pass

    try:
        groupFilePath = os.path.join(metadata_root, corpus_name, 'TopicModel', 'docGroups.csv')
        groups = {}
        with open(groupFilePath, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                groups[row[0]] = map(int, row[1:])
        returnDict['docGroups'] = groups
    except IOError:
        returnDict['docGroups'] = {}

    try:
        groupFilePath = os.path.join(metadata_root, corpus_name, 'TopicModel', 'topicGroups.csv')
        groups = {}
        with open(groupFilePath, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                groups[row[0]] = map(int, row[1:])
        returnDict['topicGroups'] = groups
    except IOError:
        returnDict['topicGroups'] = {}

    return jsonify(returnDict)


def getIncludedMetadata(corpus_name):
    metadataCSV = os.path.join(metadata_root, corpus_name, 'TopicModel', 'metadata.csv')
    if not os.path.exists(metadataCSV):
        metadataCSV = os.path.join(metadata_root, corpus_name.split("/")[0], 'TopicModel', 'metadata.csv')
    includedMetadataIndices = []
    with open(metadataCSV, 'rb') as f:
        reader = csv.reader(f)
        rowNum = 0
        for row in reader:
            if rowNum == 0:
                colNames = row
            elif rowNum == 1:
                dataTypes = row
            else:
                temp = {}
                for i in range(len(row)):
                    temp[colNames[i]] = row[i]
                    # TODO: Remove the need for this!
                #### TEMPORARY ANNOYING CACHE HACK ####
                #### DO WE HAVE CACHE FILES FOR THIS TEXT?!?!?!1one!?!1eleven ####
                filename_cache_path = os.path.join(
                    metadata_root,
                    corpus_name,
                    "TopicModel",
                    "Serendip",
                    os.path.splitext(
                        # Word of advice: don't change the column name in these CSV files.
                        os.path.basename(temp["filename"])
                    )[0]
                )
                #### ONLY APPEND IF WE HAVE CACHE DATA FOR THIS FILE ####
                if os.path.exists(filename_cache_path) or True:
                    includedMetadataIndices.append(rowNum - 2)
                    #### END HACKS ####
            rowNum += 1
    return includedMetadataIndices


def get_topic(corpus_name, topic_num, num_words, ranking_type='freq'):
    num_words = int(num_words)
    topicCSV = os.path.join(metadata_root, corpus_name + '/TopicModel/topics_%s/topic_%s.csv' % (ranking_type, topic_num))
    if not os.path.exists(topicCSV):
        topicCSV = os.path.join(metadata_root, corpus_name.split("/")[0] + '/TopicModel/topics_%s/topic_%s.csv' % (ranking_type, topic_num))
    wordList = [0 for i in range(num_words) ]
    propList = [0 for i in range(num_words) ]
    with open(topicCSV, 'rb') as f:
        reader = csv.reader(f)
        wordNum = 0
        for row in reader:
            if wordNum >= num_words:
                break
            wordList[wordNum] = row[0]
            propList[wordNum] = float(row[1])
            wordNum += 1
    return jsonify({'wordList':wordList, 'propList':propList})


def get_topic_names(corpus_name):
    try:
        topicNameFile = os.path.join(metadata_root, corpus_name + '/TopicModel/topicNames.csv')
        with open(topicNameFile, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                topicNames = row
                break
        return jsonify({'topicNames':topicNames})
    except IOError:
        return jsonify({})


def set_topic_name(corpus_name, topic_num, topic_name, num_topics):
    topic_num = int(topic_num)
    num_topics = int(num_topics)
    topicNameFile = os.path.join(metadata_root, corpus_name + '/TopicModel/topicNames.csv')
    try:
        with open(topicNameFile, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                topicNames = row
                break
    except IOError:
        topicNames = ['Topic %d' % i for i in range(num_topics)]

    topicNames[topic_num] = topic_name
    with open(topicNameFile, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(topicNames)
    return jsonify({'topicNames':topicNames})


def set_group_name(corpus_name, group_file, group_name, group):
    # First, load any pre-existing groups to compare
    groups = {}
    groupFilePath = os.path.join(metadata_root, corpus_name, 'TopicModel', group_file)
    try:
        with open(groupFilePath, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                groups[row[0]] = row[1:]
    except IOError:
        pass

    groups[group_name] = map(int, group.split(','))
    with open(groupFilePath, 'wb') as f:
        writer = csv.writer(f)
        for groupName in groups:
            writer.writerow([groupName] + groups[groupName]);
    return jsonify({'groups':groups})


def get_groups(corpus_name, group_file):
    try:
        groupFilePath = os.path.join(metadata_root, corpus_name, 'TopicModel', group_file)
        groups = {}
        with open(groupFilePath, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                groups[row[0]] = map(int, row[1:])
        return jsonify({'groups':groups})
    except IOError:
        return jsonify({})

def getAnovaOrder(corpus_name, fieldName, debug=False):
    try:
        mtm = MikeTM.TopicModel(metadata_root, corpus_name)
        anovaOrder = mtm.anovaColsRanks(fieldName)
        if debug:
            return anovaOrder
        else:
            return jsonify({'anovaOrder':[str(v) for v in anovaOrder]})
    except KeyError:
        print 'KeyError while getting ANOVA order. Probably from bad metadata field name. Check capitalization?'
        return jsonify({'anovaOrder':[]})

def getContrastOrder(corpus_name, fieldName, group1, group2=[], debug=False):
    group1 = group1.split(',')
    if group2=='matrix' or group2=='[ALL]':
        group2 = []
    else:
        group2 = group2.split(',')
    mtm = MikeTM.TopicModel(metadata_root, corpus_name)
    contrastOrder = mtm.contrastColsRanks(fieldName, group1, group2)
    if debug:
        return contrastOrder
    else:
        return jsonify({'contrastOrder':[str(v) for v in contrastOrder]})

if __name__=='__main__':
    print getAnovaOrder('ShakespeareChunkedOptimized_50','Genre',debug=True)
    print getContrastOrder('ShakespeareChunkedOptimized_50','Genre','comedy',debug=True)
    print getContrastOrder('ShakespeareChunkedOptimized_50','Genre','tragedy','history',debug=True)
    print getContrastOrder('ShakespeareChunkedOptimized_50','Genre','romance',debug=True)
    print getContrastOrder('ShakespeareChunkedOptimized_50','Genre',['comedy','tragedy'],debug=True)