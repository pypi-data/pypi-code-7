from django.conf import settings
from django.core.cache import cache
import urllib2
import urllib
import django.utils.simplejson as json
from django.template import defaultfilters


fql_url = 'https://api.facebook.com/method/fql.query'
cache_expires = getattr(settings, 'CACHE_EXPIRES', 30)


def get_fql_result(fql):
    cachename = 'fbgallery_cache_' + defaultfilters.slugify(fql)
    data = None
    if cache_expires > 0:
        data = cache.get(cachename)
    if data is None:
        options = {
            'query': fql,
            'format': 'json',
        }
        f = urllib2.urlopen(urllib2.Request(fql_url, urllib.urlencode(options)))
        response = f.read()
        f.close()
        data = json.loads(response)
        if cache_expires > 0:
            cache.set(cachename, data, cache_expires*60)
    return data


def display_album(album_id):
    """Display a facebook album

    First check that the album id belongs to the page id specified
    """
    fb_id = settings.FB_PAGE_ID
    fql = "select aid, name from album where owner=%s and aid='%s'" % (fb_id, album_id)
    valid_album = get_fql_result(fql)
    if valid_album:
        fql = "select pid, src, src_small, src_big, caption from photo where aid = '%s'  order by created desc" % album_id
        album = get_fql_result(fql)
        #album_detail = [item for item in valid_album]
        return album
