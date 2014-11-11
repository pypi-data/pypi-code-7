__author__ = 'Eric'

import subprocess
import argparse
import os
import shutil
import csv
import sys
import math
import json
from collections import defaultdict
from copy import deepcopy
sys.path.append(os.getcwd())
#from Ity.Couriers import SaliencyCourier
from Ity.Tokenizers import RegexTokenizer as RegT
#from Ity.Taggers import SaliencyTagger
from Ity.Formatters import SaliencyFormatter
from Ity.Formatters import MalletLineGraphFormatter
from Ity import metadata_root, corpus_root, data_root

def runSalTM(args):
    #courier = SaliencyCourier(args.corpus_name)
    tokenizer = RegT(case_sensitive=False, preserve_original_strs=True)
    #tagger = SaliencyTagger
    formatter = SaliencyFormatter(template='partial.html')
    lgFormatter = MalletLineGraphFormatter(template='partial.svg')

    # Make and name necessary directories
    if args.corpus_path:
        if os.path.isdir(args.corpus_path):
            corpus_dir = args.corpus_path
        else:
            print 'Invalid corpus_path %s. Argument is not a directory.' % args.corpus_path
            exit(1)
    else:
        corpus_dir = os.path.join(corpus_root, args.corpus_name)
    if args.model_name is None:
        args.model_name = args.corpus_name
    createDir(os.path.join(metadata_root, args.model_name), False)
    malletDir = os.path.join(metadata_root, args.model_name, 'Mallet')
    createDir(malletDir, args.forceOverwrite)

    # Read and parse the corpus
    print 'Reading corpus...'
    malletCorpusDir = os.path.join(malletDir, 'Corpus')
    createDir(malletCorpusDir, args.forceOverwrite)
    #tokens = {} # tokens[textName] -> tokens from tokenizer
    textList = os.listdir(corpus_dir)
    numTexts = len(textList)
    for i in range(len(textList)):
        textName = textList[i]
        msg = '\rReading text %d of %d: %s...' % (i+1, numTexts, textName)
        print msg,
        sys.stdout.flush()
        # Get the string from file and tokenize it
        textStr = ''
        with open(os.path.join(corpus_dir, textName), 'rb') as inF:
            for line in inF:
                textStr += line
        textStr = textStr.decode('utf-8', 'ignore')
        tokens = tokenizer.tokenize(textStr)

        # Get the words out for the topic modeler to deal with
        words = []
        for token in tokens:
            if token[RegT.INDEXES['TYPE']] == RegT.TYPES['WORD']:
                words.append(token[RegT.INDEXES['STRS']][0]) # Banking on there only being one word per token in this context

        if args.chunkSize is not None:
            numChunks = int(len(words)/args.chunkSize) + 1
            i = 0
            while i < numChunks:
                strForMallet = ' '.join(words[i*args.chunkSize:(i+1)*args.chunkSize])
                with open(os.path.join(malletCorpusDir, textName + '__' + str(i).zfill(6)), 'wb') as outF: # TODO: what if 6 isn't big enough?
                    outF.write(strForMallet.encode('utf-8'))
                i += 1
        else:
            # Join the words to create a Mallet-readable string and output to disk
            strForMallet = ' '.join(words)
            with open(os.path.join(malletCorpusDir, textName), 'wb') as outF:
                outF.write(strForMallet.encode('utf-8'))
    print 'Done reading.'

    # Import corpus with Mallet
    print 'Importing corpus to Mallet...'
    malletCorpusFile = os.path.join(malletDir, args.model_name + '.mallet')
    callStr = 'mallet import-dir --input %s --output %s --keep-sequence --token-regex "[^\p{Space}]*"' \
              % (malletDir, malletCorpusFile)
    if args.malletStopwords:
        callStr += ' --remove-stopwords'
        if args.extraStopwords is not None:
            callStr += ' --extra-stopwords %s' % os.path.join(data_root, 'Stopwords', args.extraStopwords)
    elif args.extraStopwords is not None:
        callStr += '--stoplist-file %s' % os.path.join(data_root, 'Stopwords', args.extraStopwords)
    print callStr
    returncode = subprocess.call(callStr, shell=True)
    if returncode != 0:
        print 'mallet operation failed. May need to be installed on machine.'
        exit(1)
    print 'Done importing.'

    # Run model with Mallet
    print 'Training topics with Mallet...'
    malletOutputDir = os.path.join(malletDir, 'Output')
    createDir(malletOutputDir, args.forceOverwrite)
    def getParamPath(paramName):
        return os.path.join(malletOutputDir, paramName)
    callStr = 'mallet train-topics --input %s' % malletCorpusFile
    # Modeling parameters
    if args.numTopics is not None:
        callStr += ' --num-topics %d' % args.numTopics
    if args.numIterations is not None:
        callStr += ' --num-iterations %d' % args.numIterations
    if args.alpha is not None:
        callStr += ' --alpha %f' % args.alpha
    if args.beta is not None:
        callStr += ' --beta %f' % args.beta
    if args.randomSeed is not None:
        callStr += ' --random-seed %d' % args.randomSeed
    if args.optimizeInterval is not None:
        callStr += ' --optimize-interval %d' % args.optimizeInterval
    if args.optimizeBurnIn is not None:
        callStr += ' --optimize-burn-in %d' % args.optimizeBurnIn
    # Command-line output
    if args.showTopicsInterval is not None:
        callStr += ' --show-topics-interval %d' % args.showTopicsInterval
    # Output files
    if args.outputAll or args.outputSerendip or args.outputDocTopics:
        callStr += ' --output-doc-topics %s' % getParamPath('docTopics')
    if args.outputAll or args.outputTopicKeys:
        callStr += ' --output-topic-keys %s' % getParamPath('topicKeys')
    if args.outputAll or args.outputSerendip or args.outputState:
        callStr += ' --output-state %s' % getParamPath('finalState.gz')
    if args.outputAll or args.outputModel:
        callStr += ' --output-model %s' % getParamPath('finalModel')
    if args.outputAll or args.outputTopicWordWeights:
        callStr += ' --topic-word-weights-file %s' % getParamPath('topicWordWeights')
    if args.outputAll or args.outputSerendip or args.outputWordTopicCounts:
        callStr += ' --word-topic-counts-file %s' % getParamPath('wordTopicCounts')
    # Now call the damn thing
    print callStr
    returncode = subprocess.call(callStr, shell=True)
    if returncode != 0:
        print 'mallet operation failed. May need to be installed on machine.'
        exit(1)
    print 'Done training.'

    # If we're creating Serendip files, convert Mallet files
    if args.outputAll or args.outputSerendip:
        serendipDir = os.path.join(metadata_root, args.model_name, 'TopicModel') #TODO: these directories should really be labeled "Serendip"
        createDir(serendipDir, args.forceOverwrite)

        print 'Building theta...'
        buildThetaAndMeta(os.path.join(malletOutputDir, 'docTopics'), \
                          os.path.join(serendipDir, 'theta.csv'), \
                          os.path.join(serendipDir, 'metadata.csv'), \
                          args.chunkSize, args)

        print 'Building topics dir...'
        rankBins = buildTopicCSVs(os.path.join(malletOutputDir, 'wordTopicCounts'), \
                                    serendipDir, \
                                    args.numTopics, \
                                    args.numRankingBins, \
                                    args.outputAll or args.outputFullCorpusDist, \
                                    args.forceOverwrite)

        # Unzip, tag, and format the finalState
        print 'Tagging finalState...'
        returncode = subprocess.call('gzip -d %s' % os.path.join(malletOutputDir, 'finalState.gz'), shell=True)
        if returncode != 0:
            print 'gzip operation failed. May need to be installed on machine.'
            exit(1)
        htmlDir = os.path.join(serendipDir, 'HTML')
        createDir(htmlDir, args.forceOverwrite)

        # Function to sparsify a summed area table, getting rid of a bunch of intermediate lines.
        # sat is the summed area table to be sparsified, roughNumLines is the ROUGH number of lines to be returned
        def sparsifySAT(sat, roughNumLines):
            if len(sat) <= roughNumLines:
                return sat
            else:
                step = len(sat) / roughNumLines
                sparseSAT = []
                i = 0
                while i < len(sat):
                    sparseSAT.append(sat[i])
                    i += step
                if i - step != len(sat) - 1:
                    sparseSAT.append(sat[-1])
                return sparseSAT

        # Helper function tokenizes file, applies given tags, and spits out .html file.
        # Seperated in case I end up making a Tagger and also so for try/catch block below.
        def tagFile(name, tags):
            textStr = ''
            with open(os.path.join(corpus_dir, name), 'rb') as inF:
                for line in inF:
                    textStr += line
            textStr = textStr.decode('utf-8', 'ignore')
            currTokens = tokenizer.tokenize(textStr)
            # Build tag_map with tokens and tags
            rules = {}
            tag_maps = []
            freqBins = []
            igBins = []
            salBins = []
            lgSAT = [0 for i in range(len(currTokens))]
            currSATline = defaultdict(lambda: [0,0,0,0]) # [count, freq, ig, sal]
            tagIndex = 0
            pageIndex = -1
            if args.htmlPageSize is None:
                currPageSize = len(currTokens)
            else:
                currPageSize = args.htmlPageSize
            for tokenIndex in range(len(currTokens)):
                if tokenIndex % currPageSize == 0:
                    tag_maps.append([ -1 for j in range(currPageSize) ])
                    freqBins.append([ -1 for j in range(currPageSize) ])
                    igBins.append([ -1 for j in range(currPageSize) ])
                    salBins.append([ -1 for j in range(currPageSize) ])
                    pageIndex += 1
                token = currTokens[tokenIndex]
                if token[RegT.INDEXES['TYPE']] == RegT.TYPES['WORD']:
                    if tagIndex < len(tags) and token[RegT.INDEXES['STRS']][0] == tags[tagIndex][0]:
                        tag_maps[pageIndex][tokenIndex%currPageSize] = tags[tagIndex][1]
                        topic = int(tags[tagIndex][1])
                        word = tags[tagIndex][0].encode('utf-8')
                        rule_name = 'topic_%d' % topic
                        if rule_name in rules:
                            rules[rule_name]['num_tags'] += 1
                            rules[rule_name]['num_included_tokens'] += 1
                        else:
                            rules[rule_name] = {
                                'name': rule_name,
                                'full_name': rule_name,
                                'num_tags': 1,
                                'num_included_tokens': 1
                            }
                        wordRankBins = rankBins[topic][word]
                        freqBins[pageIndex][tokenIndex%currPageSize], \
                            igBins[pageIndex][tokenIndex%currPageSize], \
                            salBins[pageIndex][tokenIndex%currPageSize] = wordRankBins
                        satUpdate = [1, \
                                     1 + args.numRankingBins - wordRankBins[0], \
                                     1 + args.numRankingBins - wordRankBins[1],
                                     1 + args.numRankingBins - wordRankBins[2]]
                        currSATline[topic] = map(sum, zip(currSATline[topic], satUpdate))
                        tagIndex += 1
                lgSAT[tokenIndex] = deepcopy(currSATline)
            if tagIndex != len(tags):
                raise Exception('Error: not all of tags read. file %s' % name)
            # Format the document with tag_maps
            nameSansExtension = name[:-4]
            currHTMLdir = os.path.join(htmlDir, nameSansExtension)
            createDir(currHTMLdir, args.forceOverwrite)
            for i in range(pageIndex + 1):
                htmlStr = formatter.format(tags=tag_maps[i],
                                           tokens=currTokens[i*currPageSize:(i+1)*currPageSize],
                                           freqBins=freqBins[i],
                                           igBins=igBins[i],
                                           salBins=salBins[i])
                with open(os.path.join(currHTMLdir, 'page%d.html' % i), 'wb') as htmlF:
                    htmlF.write(htmlStr.encode('utf-8'))
            # Format the line graph
            svgs = lgFormatter.format(summed_area_table=lgSAT, \
                                      rankTypes=['count','freq','ig','sal'], \
                                      numPages=len(tag_maps), \
                                      text_name=nameSansExtension, pixel_size=500)
            for type in svgs:
                with open(os.path.join(currHTMLdir, '%s.svg' % type), 'wb') as svgF:
                    svgF.write(svgs[type].encode('utf-8'))
            # Write rules to json file
            with open(os.path.join(currHTMLdir, 'rules.json'), 'wb') as jsonF:
                jsonF.write(json.dumps(rules))
            if args.outputSAT:
                with open(os.path.join(currHTMLdir, 'sat.json'), 'wb') as satF:
                    satF.write(json.dumps(lgSAT))
                with open(os.path.join(currHTMLdir, 'sparsesat.json'), 'wb') as satF:
                    satF.write(json.dumps(sparsifySAT(lgSAT, 2000)))

        # Helper function that helps when dealing with chunked files
        def getBasename(filename):
            baseWithChunkNum = os.path.basename(filename)
            if args.chunkSize is None:
                return baseWithChunkNum
            else:
                return baseWithChunkNum[:baseWithChunkNum.find('__')]

        # Read through all the lines of the finalState.
        # Whenever we get a complete file, tag and format it.
        # Once we gzip -d finalState.gz, we'll get a file that looks like this, starting on line 4:
        # doc source pos typeindex type topic
        with open(os.path.join(malletOutputDir, 'finalState'), 'rb') as stateF:
            # Eat first three lines (which aren't useful to us yet)
            stateF.next()
            stateF.next()
            stateF.next()
            # Kick off loop
            currLine = stateF.next().decode('utf-8','ignore').split()
            currDocNum = 0
            currDocName = getBasename(currLine[1])
            currTags = []
            while True:
                msg = '\rTagging document %d...' % (currDocNum + 1)
                print msg,
                sys.stdout.flush()

                if getBasename(currLine[1]) == currDocName:
                    currTags.append((currLine[4], int(currLine[5])))
                else:
                    # Deal with currDoc
                    tagFile(currDocName, currTags)
                    # Update things for next doc
                    currDocNum += 1
                    currDocName = getBasename(currLine[1])
                    currTags = [currLine[4:]]
                try:
                    currLine = stateF.next().decode('utf-8','ignore').split()
                except StopIteration:
                    tagFile(currDocName, currTags)
                    break
        print 'Done tagging.'

# This function takes a given docTopic file output from Mallet and turns it into theta.csv and metadata.csv
# docTopic file has lines of this form:
# docNum filename topic proportion topic proportion topic proportion ...
# TODO: remove the middle man. theta is no better than docTopic. Update Serendip for this.
# TODO: bug. This doesn't take into account the fact that the last chunk might be smaller than the rest when normalizing.
def buildThetaAndMeta(docTopicPath, thetaPath, metaPath, chunkSize, args):
    with open(docTopicPath, 'rb') as dtFile:
        with open(thetaPath, 'wb') as tFile:
            with open(metaPath, 'wb') as mFile:
                # Prep csv writers
                thetaWriter = csv.writer(tFile)
                metaWriter = csv.writer(mFile)
                # Prep metadata.csv
                metaWriter.writerow(['id','filename'])
                metaWriter.writerow(['int','str'])
                # If we're not chunking, this is pretty straightforward
                if chunkSize is None:
                    # Loop through docTopics file, adding lines to theta and metadata
                    firstLine = True
                    for line in dtFile:
                        if firstLine:
                            firstLine = False
                        else:
                            line = line.split()
                            sparseLine = []
                            for i in range(2, len(line), 2):
                                if float(line[i+1]) > .001:
                                    sparseLine += line[i:i+2]
                            thetaWriter.writerow(sparseLine) # Take out docNum and filename for theta
                            metaWriter.writerow([line[0], os.path.basename(line[1])]) # Just include docNum and filename for metadata
                # If we are chunking, then we need to combine and normalize the rows for each file
                else:
                    def writeFileLine(docNum, basename, thetaLine, numChunks, thetaWriter, metaWriter):
                        # normalize the row
                        for topic in thetaLine:
                            thetaLine[topic] /= numChunks
                        # write it
                        row = []
                        for topic in thetaLine:
                            row.append(topic)
                            row.append(thetaLine[topic])
                        thetaWriter.writerow(row)
                        metaWriter.writerow([docNum, os.path.basename(basename)]) # TODO: make sure it corresponds with metadata
                    currDocNum = -1
                    firstLine = True
                    currBasename = ''
                    currThetaline = {}
                    numMiniFiles = 0
                    for line in dtFile:
                        if firstLine:
                            firstLine = False
                        else:
                            line = line.split()
                            name = line[1]
                            basename = name[:name.find('__')]
                            # If we're starting a new file, finish the last one
                            if basename != currBasename:
                                if currBasename != '':
                                    writeFileLine(currDocNum, currBasename, currThetaline, numMiniFiles, thetaWriter, metaWriter)
                                # update for next row
                                currDocNum += 1
                                currBasename = basename
                                numMiniFiles = 0
                                currThetaline = {}
                            for i in range(2, len(line), 2):
                                line[i] = int(line[i])
                                line[i+1] = float(line[i+1])
                                if line[i+1] > .001:
                                    if line[i] in currThetaline:
                                        currThetaline[line[i]] += line[i+1]
                                    else:
                                        currThetaline[line[i]] = line[i+1]
                            numMiniFiles += 1
                    writeFileLine(currDocNum, currBasename, currThetaline, numMiniFiles, thetaWriter, metaWriter)

# This function takes a given wordTopicCounts file output from Mallet and turns it into topic_#.csv files.
# The wordTopicCounts file has lines of this form:
# typeIndex type topic#:count topic#:count topic#:count ...
#TODO: word distributions
def buildTopicCSVs(wordTopicCountsPath, topicDirPath, numTopics, numRankingBins, outputFullCorpusDist, forceOverwrite=False):
    # Read the wordTopicCounts file
    with open(wordTopicCountsPath, 'rb') as wtcF:
        topicDists = [ [] for i in range(numTopics) ] # Distributions across vocab for each topic
        p_topic = [ 0.0 for i in range(numTopics) ] # probability of each topic
        p_topicGivenWord = [ {} for i in range(numTopics) ] # probability of each topic given word
        p_word = [] # probability of each word across whole corpus
        totWordCount = 0.0 # Used to normalize p_topic
        for line in wtcF:
            line = line.split()
            word = line[1]
            countPairs = line[2:] # These are the topic#:count pairs
            thisWordCount = 0.0 # Used to normalize p_topicGivenWord
            topicsWithThisWord = []
            for countPair in countPairs:
                topic, count = map(int, countPair.split(':'))
                topicDists[topic].append([word, count])
                p_topic[topic] += count
                p_topicGivenWord[topic][word] = count
                topicsWithThisWord.append(topic)
                totWordCount += count
                thisWordCount += count
            # Normalize p_topicGivenWord
            for topic in topicsWithThisWord:
                p_topicGivenWord[topic][word] /= thisWordCount
            # Add word to corpus distribution
            p_word.append([word, thisWordCount])
        # Normalize p_topic
        for topic in range(numTopics):
            p_topic[topic] /= totWordCount
        # Normalize p_word
        for i in range(len(p_word)):
            p_word[i][1] /= totWordCount

    # Sort and normalize topicDists
    for topic in range(numTopics):
        topicDists[topic].sort(key=lambda x: x[1], reverse=True)
        tot = 0.0
        for i in range(len(topicDists[topic])):
            tot += topicDists[topic][i][1]
        for i in range(len(topicDists[topic])):
            topicDists[topic][i][1] /= tot
    # Sort p_word
    p_word.sort(key=lambda x:x[1], reverse=True)

    # Calculate and sort information gain lists
    igLists = [ [] for i in range(numTopics) ]
    igDicts = [ {} for i in range(numTopics) ]
    for topic in range(numTopics):
        p_t = p_topic[topic]
        totIG = 0.0
        for word, freq in topicDists[topic]:
            try:
                p_tGw = p_topicGivenWord[topic][word]
            except KeyError:
                p_tGw = 0.0
            if p_tGw == 0:
                iG = math.log(1 / (1-p_t))
            elif p_tGw == 1:
                iG = math.log(1 / p_t)
            else:
                iG = p_tGw * math.log(p_tGw / p_t) + (1-p_tGw) * math.log((1-p_tGw) / (1-p_t))
            igLists[topic].append([word, iG])
            igDicts[topic][word] = iG
            totIG += iG
        igLists[topic].sort(key=lambda x: x[1], reverse=True)
        # Normalizing, if only b/c binning is easy if everything sums to 1
        for i in range(len(igLists[topic])):
            igLists[topic][i][1] /= totIG

    # Calculate and sort saliency lists
    salLists = [ [] for i in range(numTopics) ]
    for topic in range(numTopics):
        totSal = 0.0
        for word, freq in topicDists[topic]:
            try:
                sal = freq * igDicts[topic][word]
                salLists[topic].append([word, sal])
                totSal += sal
            except KeyError:
                pass
        salLists[topic].sort(key=lambda x: x[1], reverse=True)
        # Normalizing, if only b/c binning is easy if everything sums to 1
        for i in range(len(salLists[topic])):
            salLists[topic][i][1] /= totSal

    # Output ranking lists to proper directories
    freqPath = os.path.join(topicDirPath, 'topics_freq')
    createDir(freqPath, forceOverwrite)
    igPath = os.path.join(topicDirPath, 'topics_ig')
    createDir(igPath, forceOverwrite)
    salPath = os.path.join(topicDirPath, 'topics_sal')
    createDir(salPath, forceOverwrite)
    for topic in range(numTopics):
        filename = 'topic_%d.csv' % topic
        with open(os.path.join(freqPath, filename), 'wb') as freqF:
            freqWriter = csv.writer(freqF)
            for freqPair in topicDists[topic]:
                freqWriter.writerow(freqPair)
        with open(os.path.join(igPath, filename), 'wb') as igF:
            igWriter = csv.writer(igF)
            for igPair in igLists[topic]:
                igWriter.writerow(igPair)
        with open(os.path.join(salPath, filename), 'wb') as salF:
            salWriter = csv.writer(salF)
            for salPair in salLists[topic]:
                salWriter.writerow(salPair)

    # Output full corpus distribution
    if outputFullCorpusDist:
        with open(os.path.join(topicDirPath, 'corpus_dist.csv'), 'wb') as distF:
                distWriter = csv.writer(distF)
                for pair in p_word:
                    distWriter.writerow(pair)

    # Create ranking bins
    rankBins = [ {} for i in range(numTopics) ]
    for topic in range(numTopics):
        # frequency bins
        currFreqTot = 0.0
        currBin = 1
        for word, freq in topicDists[topic]:
            if currFreqTot > currBin * (1.0 / numRankingBins):
                currBin += 1
            rankBins[topic][word] = [currBin, 0, 0]
            currFreqTot += freq
        # info gain bins
        currIgTot = 0.0
        currBin = 1
        for word, ig in igLists[topic]:
            if currIgTot > currBin * (1.0 / numRankingBins):
                currBin += 1
            rankBins[topic][word][1] = currBin
            currIgTot += ig
        # saliency bins
        currSalTot = 0.0
        currBin = 1
        for word, sal in salLists[topic]:
            if currSalTot > currBin * (1.0 / numRankingBins):
                currBin += 1
            rankBins[topic][word][2] = currBin
            currSalTot += sal

    # Return rankBins to be used in HTML tagging
    return rankBins

# Helper function that creates new directories, overwriting old ones if necessary and desired.
def createDir(name, force=False):
    if os.path.exists(name):
        if force:
            shutil.rmtree(name)
        else:
            response = raw_input('%s already exists. Do you wish to overwrite it? (y/n) ' % name)
            if response.lower() == 'y' or response.lower() == 'yes':
                shutil.rmtree(name)
            elif response.lower() == 'n' or response.lower() == 'no':
                print 'Modeler aborted.'
                exit(0)
            else:
                print 'Response not understood.'
                print 'Modeler aborted.'
                exit(1)
    os.mkdir(name)

#if __name__=="__main__":
def main():
    parser = argparse.ArgumentParser(description='A Mallet-based topic modeler for Serendip')

    parser.add_argument('--corpus_name', help='name of the corpus', required=True)
    parser.add_argument('--model_name', help='name of the model')
    parser.add_argument('--corpus_path', help='full path to corpus (if not located in VEP_Core Corpora directory)')
    parser.add_argument('-f', '--forceOverwrite', help='force overwriting of previous corpus/model', action='store_true')

    parsingGroup = parser.add_argument_group('Corpus parsing parameters')
    parsingGroup.add_argument('-mS', '--malletStopwords', help='ignore standard Mallet stopwords', action='store_true')
    parsingGroup.add_argument('-eS', '--extraStopwords', help='file of extra stopwords to be ignored')
    parsingGroup.add_argument('--chunkSize', help='number of tokens per chunk (no chunking if left empty)', type=int)

    modelingGroup = parser.add_argument_group('LDA modeling parameters')
    modelingGroup.add_argument('-n', '--numTopics', help='number of topics to infer', type=int)
    modelingGroup.add_argument('-i', '--numIterations', help='number of iterations run by modeler', type=int)
    modelingGroup.add_argument('-a', '--alpha', help='alpha parameter for model', type=float)
    modelingGroup.add_argument('-b', '--beta', help='beta parameter for model', type=float)
    modelingGroup.add_argument('-r', '--randomSeed', help='starting seed for model iterations', type=int)
    modelingGroup.add_argument('-oI', '--optimizeInterval', help='iterations between parameter optimizations', type=int)
    modelingGroup.add_argument('-oBI', '--optimizeBurnIn', help='iterations before first parameter optimization', type=int)

    feedbackGroup = parser.add_argument_group('Command-line feedback parameters')
    feedbackGroup.add_argument('-sTI', '--showTopicsInterval', help='iterations between showing topics', type=int)

    outputGroup = parser.add_argument_group('Modeling output parameters')
    outputGroup.add_argument('-oDT', '--outputDocTopics', help='output the doc-topic proportions', action='store_true')
    outputGroup.add_argument('-oTK', '--outputTopicKeys', help='output file of simple topic representations', action='store_true')
    outputGroup.add_argument('-oS', '--outputState', help='output full final state of Gibbs sampling (g-zipped)', action='store_true')
    outputGroup.add_argument('-oM', '--outputModel', help='output full final model', action='store_true')
    outputGroup.add_argument('-oTWW', '--outputTopicWordWeights', help='output topic-word-weights file', action='store_true')
    outputGroup.add_argument('-oWTC', '--outputWordTopicCounts', help='output word-topic-counts file', action='store_true')
    outputGroup.add_argument('-oFCD', '--outputFullCorpusDist', help='output full corpus distribution of vocabulary', action='store_true')
    outputGroup.add_argument('--outputSerendip', help='output files needed by Serendip', action='store_true')
    outputGroup.add_argument('--outputAll', help='output all potential files', action='store_true')
    outputGroup.add_argument('--numRankingBins', help='number of bins in which to divide words for color-coding', type=int, default=5)
    outputGroup.add_argument('--htmlPageSize', help='number of tokens per page of html. default is no pagination', type=int, default=1000)
    outputGroup.add_argument('-oSAT', '--outputSAT', help='output .json version of summed area table', action='store_true')

    parser.set_defaults(func=runSalTM)
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()