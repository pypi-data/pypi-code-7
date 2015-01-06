# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="ramdani"
__date__ ="$Jan 5, 2015 10:20:03 PM$"

from bs4 import BeautifulSoup
import urllib3
import re

class ReadibilityPlus:

    def __init__(self, url=None):
        self.url = url
        self.soup = BeautifulSoup(self.read_url())

    def set_url(self, url):
        self.url = url

    def set_tag_article(self, tag):
        self.tag = tag

    def set_tag_image(self, tag_image):
        self.tag_image = tag_image

    def get_image(self):
        result = self.soup.find('div',self.tag_image)
        if result != None:
            return result.img['src']
        else:
            return False

    def get_other_images(self):
        results = self.soup.find_all(text=re.compile('png'))
        print results
        buffers = [r['src'] for r in results]
        return buffers

    def get_content(self,clean=True):
        result = self.soup.find('div',self.tag)
        if result != None:
            if clean == True:
                return self.set_boundary(result)
            else:
                return result
        else:
            return False

    def set_boundary(self,text):

        text = text.get_text().split(".")
        paragraph = ''
        for t in text:
            buffer = "<p>%s.</p>" % (t)
            paragraph = "%s%s" % (paragraph, buffer)

        return paragraph

    def read_url(self):
        http = urllib3.PoolManager()
        r = http.request('GET', self.url)
        if r.status == 200:
            return r.data
        else:
            return False

rp = ReadibilityPlus('http://nasional.news.viva.co.id/news/read/575071-tiga-korban-airasia-ditemukan-masih-duduk-di-kursi-pesawat')
rp.set_tag_article({'class':'content'})
rp.set_tag_image({'class':'thumbcontainer'})
print rp.get_content(True)
print rp.get_image()
#print rp.get_other_images()
