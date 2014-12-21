import asyncio

import aiohttp
from lxml import etree

base_url = 'http://www.yify-torrent.org'

# use semaphore to limit the number of coroutines
sem = asyncio.Semaphore(10)


def parse_movies(content):
    movies = []

    # use lxml to find the informations we want
    root = etree.HTML(content)
    # every movie is inside a div with class mv
    for mv in root.xpath('//div[@class="mv"]'):
        # find movie title and yify link
        h3 = mv.xpath('./h3')
        a = h3[0].xpath('./a')[0]
        title = a.text
        link = base_url + a.attrib['href']

        # find movie poster image
        poster = mv.xpath('.//div[@class="movie-image"]//img')[0].attrib['src']

        # find movie informations like genre, quality...
        infos = {}
        for li in mv.xpath('.//li'):
            texts = list(li.itertext())
            # remove : for first item, and convert string to lowercase
            texts[0] = texts[0].replace(':', '').lower()
            # use first item as key, others as value
            infos[texts[0]] = ' '.join(texts[1:])

        # split rating with /, then get first part and turn it into float
        infos['rating'] = float(infos['rating'].split('/')[0])

        # put movie data into dictionary
        movie = {
            'title': title,
            'link': link,
            'poster': poster,
        }
        movie.update(infos)
        # append movie into movies
        movies.append(movie)

    return movies


def get_url(kind, page, search=None):
    '''Use kind to generate different url.'''
    kind = kind.lower()
    if kind == 'search' and search is not None:
        return '{}/search/{}/t-{}/'.format(base_url, search, page)
    elif kind in ['latest', 'popular']:
        return '{}/{}.html'.format(base_url, kind)


@asyncio.coroutine
def get_movies(kind, page, search=None):
    with (yield from sem):
        url = get_url(kind, page, search)

        # check url is None
        if url is None:
            return []

        # get page content by asyncio
        res = yield from aiohttp.request('GET', url)
        content = yield from res.text()

        # let the parse begin
        movies = parse_movies(content)
        return movies


@asyncio.coroutine
def latest(page):
    '''Show latest movies.'''
    return get_movies('latest', page)


@asyncio.coroutine
def popular(page):
    '''Show popular movies.'''
    return get_movies('popular', page)


@asyncio.coroutine
def search(keyword, page):
    '''Search movies.'''
    return get_movies('search', page, keyword)


def main():
    loop = asyncio.get_event_loop()
    f = asyncio.wait([popular(i) for i in range(1, 46)])
    loop.run_until_complete(f)
    # loop.run_until_complete(search('equalizer', 1))

if __name__ == '__main__':
    main()
