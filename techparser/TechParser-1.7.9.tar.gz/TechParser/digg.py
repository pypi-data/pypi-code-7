#!/usr/bin/env python
# -*- coding: utf-8 -*-

from TechParser import parser

def get_articles():
	return parser.get_articles_from_rss('http://digg.com/rss/top.rss', 'digg')
