#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from pageone import PageOne

import lauteur
from siegfried import (
  prepare_url, urls_from_html, is_article_url
  )

from libs import feedparser
from util import (
  get_jsonpath, strip_tags, parse_datetime, 
  imgs_from_html, utc_now, logger
  )

# JSONPATH CANDIDATES
URL_CANDIDATE_JSONPATH = [
  'id', 'feedburner_origlink', 'link', 'link[*].href'
]

# applies to feed AND individual entries.
DATE_CANDIDATE_JSONPATH = [
  'updated_parsed', 'published_parse'
]

AUTHOR_CANDIDATE_JSONPATH = [
  'author', 'author_detail.name', 'authors[*].name'
]

IMG_CANDIDATE_JSONPATH = [
  'media_content[*].url'
]

CONTENT_CANDIDATE_JSONPATH = [
  'content[*].value', 'summary'
]

TAG_CANDIDATE_JSONPATH = [
  'tags[*].label', 'tags[*].term'
]


# MAIN CLASS
class SupeRSSInitError(Exception):
  pass

class SupeRSS:
  """
  Strategy: 
  """
  
  def __init__(self, feed=None, homepage=None, **kwargs):

    # required arg
    self.feed = feed
    self.homepage = homepage
    self.concurrent = kwargs.get('concurrent', False)
    self.num_workers = kwargs.get('num_workers', 20)
    self.is_full_text = kwargs.get('is_full_text', True)

  def get_candidates(self, obj, jsonpath):
    """
    evaluate an object with jsonpath, 
    and get all unique vals / lists
    of values
    """
    candidates = set()
    for path in jsonpath:
      path_candidates = get_jsonpath(obj, path)

      if isinstance(path_candidates, list):
        for candidate in path_candidates:
          if candidate:
            candidates.add(candidate)

      elif isinstance(path_candidates, str):
        candidates.add(candidate)

    return list(candidates)


  def get_datetime(self, obj):
    """
    return earliest time of candidates or current time.
    """
    candidates = self.get_candidates(obj, DATE_CANDIDATE_JSONPATH)
    if len(candidates) > 0:
      return parse_datetime(sorted(candidates)[0])
    else:
      return utc_now()


  # get authors, using `lauteur` for parsing.
  def get_authors(self, entry):
    """
    return all candidates, and parse unique
    """
    
    authors = set()
    
    _authors = self.get_candidates(entry, AUTHOR_CANDIDATE_JSONPATH)
    for _a in _authors:
      for author in lauteur.from_string(_a):
        authors.add(author)

    return list(authors)


  # get images
  def get_imgs(self, entry):
    """

    """
    img_urls = self.get_candidates(entry, IMG_CANDIDATE_JSONPATH)
    return list(set(img_urls))
  

  def get_article_html(self, entry):
    """
    Get all article text candidates and check which one is the longest.
    """
    candidates = self.get_candidates(entry, CONTENT_CANDIDATE_JSONPATH)
    candidates.sort(key = len)
    if len(candidates):
      return candidates[-1]
    else:
      return ''
  

  def get_tags(self, entry):
    tags = self.get_candidates(entry, TAG_CANDIDATE_JSONPATH)
    return list(set([t for t in tags if t!= ""]))


  def get_url(self, entry):
    """
    Two strategies:
    1: check candidates for valid urls
    2: Open / Unshorten candidates
    3: If still none, default to first candidate
    """
    # defaults to orig_link -> id -> link
    # only if valid
    if 'feedburner_origlink' in entry: 
      if is_article_url(entry.feedburner_origlink):
        return prepare_url(entry.feedburner_origlink)
  
    if 'link' in entry:
      if is_article_url(entry.link):
        return prepare_url(entry.link)

    if 'id' in entry:
      if is_article_url(entry.id):                  
        return prepare_url(entry.id)

    # get potential candidates
    candidates = self.get_candidates(entry, URL_CANDIDATE_JSONPATH)

    # if no candidates, return an empty string
    if len(candidates) == 0:
      return None

    # test for valid urls:
    article_urls = list(set([
      u for u in candidates if is_article_url(u)
      ]))
    
    # if we have one or more, update entry_urls and return the first
    if len(article_urls) >= 1:
      return article_urls[0]

    # if we STILL haven't found anything, just
    # return the first candidate that looks like a url.
    return [c for c in candidates if c.startswith('http')][0]

  def get_links(self, article_html):
    return [prepare_url(u) for u in urls_from_html(article_html)]

  def parse_entry(self, entry):

    """
    Parse an entry. if not full text, extract the article
    by opening the page and merge the results.
    """
    article_html = self.get_article_html(entry)

    data = {
      'url':           self.get_url(entry),
      'article_html':  article_html,
      'text':          strip_tags(article_html),
      'title':         entry.title,
      'tags':          self.get_tags(entry),
      'authors':       self.get_authors(entry),
      'datetime':      self.get_datetime(entry),
      'img_urls':      self.get_imgs(article_html),
      'article_links': self.get_links(article_html),
      'article_imgs':  imgs_from_html(article_html)
    }

    return data

  # def merge_extracted_data(self, feed_data, extracted_data):
  #   d = feed_data.copy()

  #   try:
  #     # TODO: better merge heuristics
  #     d['article_html'] = extracted_data['article_html']
  #     d['text'] = extracted_data['text']

  #     # add lists together
  #     d['tags'] = list(set(feed_data['tags'] + extracted_data['tags']))
  #     d['authors'] = list(set(feed_data['authors'] + extracted_data['authors']))
  #     d['img_urls'] = list(set(feed_data['img_urls'] + extracted_data['img_urls']))
  #     d['article_links'] = list(set(feed_data['article_links'] + extracted_data['article_links']))
  #     d['article_imgs'] = list(set(feed_data['article_imgs'] + extracted_data['article_imgs']))
    
  #   except TypeError:
  #     pass
    
  #   return d 
  
  # def extract_and_merge(self, entry):
  #   """
  #   runner for non-full-text
  #   """
  #   p = Particle()
  #   extracted_data = p.extract(url=entry['url'])
  #   return self.merge_extracted_data(entry, extracted_data)

  def run_concurrent(self, func, iterator):

    # if self.concurrent:
    #   pool = Pool(self.num_workers)
    #   for result in pool.imap_unordered(func, iterator):
    #     yield result 

    # elif not self.concurrent:
    #   logger.warn('SupeRSS requires gevent run concurrently.')
    #   for item in iterator:
    #     yield func(item)

    # else:
    for item in iterator:
      yield func(item)

  def run_full_text(self):
    """
    parse feed and stream entries
    """
    f = feedparser.parse(self.feed)
    return self.run_concurrent(self.parse_entry, f.entries)

  # def run_non_full_text(self):
  #   """
  #   Parse feed, extract article test, merge
  #   """
  #   return self.run_concurrent(self.extract_and_merge, self.run_full_text())

  # def run_homepage(self):
  #   pg1 = PageOne(url=self.homepage)
  #   pt = Particle()
  #   return self.run_concurrent(pt.extract, pg1.articles())

  def run(self):
    """
    run different methods based on intialization parameters
    """
    return self.run_full_text()
    
    # if self.homepage is not None:
    #   return self.run_homepage()

    # else:
    #   if self.is_full_text:
    #     return self.run_full_text()

    #   else:
    #     return self.run_non_full_text()
