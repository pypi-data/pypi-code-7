#!/usr/bin/env python
# -*- coding: utf-8 -*-


#from .newspaper import Article, build
import sys
from urls import Link
import requests
from newspaper.article import Article
# import BeautifulSoup

class Page(object):
    def __init__(self, item):
        if item is not None:
            try:
                self.origin = item['origin']
            except KeyError:
                self.origin = "crawl"  
            try:
                self.source_url = item['source_url']
            except KeyError:
                self.source_url = None            
            self.url = item["url"]
            self.code = 0
            self.depth = item['depth']
            self.link = Link(self.url, self.origin, self.depth, self.source_url)
            self.status = self.link.status
            self.links = []
        else:
            self.status = False
    def control(self):
        print "Relative", self.url, self.link.url, self.link.relative
        return self.status

    def log(self, debug = False):
        if debug:
            print self.status, self.msg, self.code 
        return {"url":self.url, "status": self.status, "msg": self.msg, "code": self.code}    
    
    def fetch(self):
        try:
            # req = requests.get((self.url), headers = headers ,allow_redirects=True, proxies=None, timeout=5)
            req = requests.get(self.url, allow_redirects=True, timeout=5)
            req.raise_for_status()
            try:
                self.html = req.text
                self.msg = "Ok"
                self.code = 200
                self.status = True
                if 'text/html' not in req.headers['content-type']:
                    self.msg ="Control: Content type is not TEXT/HTML"
                    self.code = 404
                    self.status = False
                    return False
            #Error on ressource or on server
                elif req.status_code in range(400,520):
                    self.code = req.status_code
                    self.msg = "Control: Request error on connexion no ressources or not able to reach server"
                    self.status = False
                    return False
                else:
                    return True

            except Exception as e:
                self.msg = "Requests: answer was not understood %s" %e
                self.code = 400
                self.status = False
                return False

        except Exception as e:
            self.msg = "Requests Error: "+str(e)
            self.code = 500
            self.status = False
            return False
    
    def parse(self, query):
        
        article = Article(self.url)
        if article is not None and article.status is not False:
            try:
                if article.parse(self.html):
                    # if article.text == "":
                    #     print article.text[0:500], article.html[0:500]
                    #     self.code = 700
                    #     self.msg = "Article Parse: Text is empty"
                    #     self.status = False
                    #     return False
                    if article.is_relevant(query) is False:
                        self.code = 800
                        self.msg = "Article Query: not relevant"
                        self.status = False
                        return False
                    else:
                        self.title = article.title
                        self.text = article.text
                        self.links = self.next_links(article.links)
                        self.html = article.html
                        return True
                else:
                    self.msg = article.msg
                    self.code = article.code
                    self.status = False
                    return False
            except Exception as e:
                self.msg = "Article Parse: Error %s" %str(e)
                self.code = 700
                self.status = False
                return False

    def next_links(self, links):
        return [n for n in links if n != self.url and n!= self.source_url]
        
    def export(self):
        return {"url":self.url,
                 "url_info":self.link.json(), 
                 "title": self.title, 
                 "text":self.text,
                 #"html":self.html,
                 "links":self.links,
                 }

    def clean_outlinks(self, urllist, depth, source_url):
        for n in set(urllist):
            if n != None and n != "" and n != "#" and n != "/":
                l = Link(n, origin="crawl", depth = depth+1, source_url= source_url)
                if l.status is True:
                    yield {"url":l.url, "depth":l.depth, "source_url": l.source_url}

    def put_to_seeds(project_db):
        print "Putting", len(project_db.sources.distinct("url")), "urls"
        for n in project_db.sources.find():
            if n not in project_db.queue.find({"url":n}):
                if n["status"][-1] is not False:
                    project_db.queue.insert({"url":n, "depth":0})
