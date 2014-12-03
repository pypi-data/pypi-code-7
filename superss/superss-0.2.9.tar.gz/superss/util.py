from datetime import datetime 
from HTMLParser import HTMLParser
import re
import pytz 
import jsonpath_rw as jsonpath
from bs4 import BeautifulSoup
import logging

logging.basicConfig()
logger = logging.getLogger("superss")

# html stripping
class MLStripper(HTMLParser):
  def __init__(self):
    self.reset()
    self.fed = []

  def handle_data(self, d):
    self.fed.append(d)

  def get_data(self):
    return ''.join(self.fed)

def strip_tags(html):
  """
  string tags and clean text from html.
  """
  s = MLStripper()
  s.feed(html)
  raw_text = s.get_data()
  raw_text = re.sub(r'\n|\t|\r', ' ', raw_text)
  return re.sub('\s+', ' ', raw_text).strip()

def utc_now():
  dt = datetime.utcnow()
  return dt.replace(tzinfo=pytz.utc)

# time obj -> datetime
def parse_datetime(t):
  
  return datetime(
    year = t.tm_year,
    month = t.tm_mon,
    day = t.tm_mday,
    hour = t.tm_hour,
    minute = t.tm_min,
    second = t.tm_sec,
    tzinfo = pytz.utc
  )

def get_jsonpath(obj, path, null=[]):
  """
  from https://pypi.python.org/pypi/jsonpath-rw/1.3.0
  parse a dict with jsonpath:
  usage:
  d = {'a' : [{'a':'b'}]}
  get_jsonpath(d, 'a[0].a')
  ['b']
  """
  jp = jsonpath.parse(path)
  res = [m.value for m in jp.find(obj)]
  if len(res) == 0:
    return null
  else:
    return res

def imgs_from_html(html):
  """
  Get the `src` attribute from `img` tags.
  """
  soup = BeautifulSoup(html)
  imgs = []
  for el in soup.find_all('img'):
    src = el.attrs.get('src', None)
    if src:
      imgs.append(src)

  return list(set(imgs))
