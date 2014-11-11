# coding=utf-8
__author__ = 'kohlmannj'

import os
import glob
import json
import codecs
import HTMLParser
import zipfile
import re
from flask import render_template, request, Response, current_app, url_for, redirect, jsonify
from Ity import corpus_root, metadata_root, Utilities
from Ity.Tokenizers import RegexTokenizer
from Ity.Taggers import TopicModelTagger
from Ity.Formatters import HTMLFormatter, LineGraphFormatter
import CorpusViewer

tokenizer = RegexTokenizer(
    case_sensitive=True
)
formatters = dict(
    HTML=HTMLFormatter(),
    LineGraph=LineGraphFormatter()
)
text_data = {}
corpus_courier = None
corpora = Utilities.get_corpora()
html_parser = HTMLParser.HTMLParser()

def index():
    return render_template(
        "text/index.html"
    )

def mallet_view_by_name(corpus_name, text_name):
    html_root = os.path.join(metadata_root, corpus_name, 'TopicModel', 'HTML')
    if os.path.exists(html_root + '.zip'):
        with zipfile.ZipFile(html_root + '.zip') as zf:
            htmlFiles = [ e for e in zf.namelist() if re.match('HTML/%s/(\S*).html' % text_name, e) is not None]
            if len(htmlFiles) != 0:
                pages = []
                for i in range(len(htmlFiles)):
                    with zf.open('HTML/%s/page%d.html' % (text_name, i)) as textF:
                        pages.append(textF.read().decode('utf-8'))
                with zf.open('HTML/%s/rules.json' % text_name) as jsonF:
                    rules = json.loads(jsonF.read())
            else:
                return
    else:
        if text_name in os.listdir(html_root):
            currHTMLdir = os.path.join(html_root, text_name)
            pages = []
            htmlFiles = glob.glob(os.path.join(currHTMLdir, '*.html'))
            for i in range(len(htmlFiles)):
                filename = os.path.join(currHTMLdir, 'page%d.html' % i)
                with open(filename, 'rb') as textF:
                    pages.append(textF.read().decode('utf-8'))
            with open(os.path.join(currHTMLdir, 'rules.json'), 'rb') as jsonF:
                rules = json.loads(jsonF.read())
        else:
            return
    tot_tags = 0.0
    for rule_name in rules:
        tot_tags += rules[rule_name]['num_tags']
    return render_template(
        "text/malletIndex.html",
        title=u"%s/%s" % (corpus_name, text_name),
        corpus_name=corpus_name,
        text_name=text_name,
        pages=pages,
        rules=rules,
        tot_tags=tot_tags
    )

def get_mallet_line_graph(corpus_name, text_name, ranking_type):
    html_root = os.path.join(metadata_root, corpus_name, 'TopicModel', 'HTML')
    if os.path.exists(html_root + '.zip'):
        try:
            with zipfile.ZipFile(html_root + '.zip') as zf:
                with zf.open('HTML/%s/%s.svg' % (text_name, ranking_type)) as svgF:
                    return svgF.read().decode('utf-8')
        except KeyError:
            return
    else:
        if text_name in os.listdir(html_root):
            currHTMLdir = os.path.join(html_root, text_name)
            with open(os.path.join(currHTMLdir, '%s.svg' % ranking_type), 'rb') as svgF:
                return svgF.read().decode('utf-8')