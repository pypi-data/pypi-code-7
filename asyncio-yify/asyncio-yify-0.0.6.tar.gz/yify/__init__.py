import asyncio

import aiohttp
from lxml import etree

base_url = 'http://www.yify-torrent.org'

# use semaphore to limit the number of coroutines
sem = asyncio.Semaphore(15)


@asyncio.coroutine
def get_one(url):
    '''Get informations of the specific movie.'''
    # get page content by asyncio
    res = yield from aiohttp.request('GET', url)
    content = yield from res.text()

    movie = {}

    # use lxml to find the informations we want
    root = etree.HTML(content)

    # get movie poster
    movie['poster_large'] =\
        root.xpath('//div[@class="cover"]/img')[0].attrib['src']

    # get movie details
    for li in root.xpath('//div[@class="inattr"]//li'):
        # strip space for each text segments
        texts = list(text.strip() for text in li.itertext())

        # use first segment as key
        # lowercase, remove : and replace space with underscore
        key = texts[0].lower().replace(':', '').replace(' ', '_')

        # others as value, and join all as one string
        value = ' '.join(texts[1:]).strip()
        movie[key] = value

        # get imdb link if key is imdb_rating
        if key == 'imdb_rating':
            movie['imdb'] = li.xpath('./a')[0].attrib['href']

    attrs = root.xpath('//div[@class="outattr"]/div[@class="attr"]')
    # get trailer
    movie['trailer'] = attrs[1].xpath('./a')[0].attrib['href']
    # get magnet
    movie['magnet'] = attrs[2].xpath('./a')[0].attrib['href']

    # get screenshots
    imgs = root.xpath('//div[@class="scrshot"]//img')
    movie['screenshot'] = [i.attrib['src'] for i in imgs]

    # get plot
    movie['plot'] = root.xpath('//div[@class="info"]/p')[0].text

    return movie


@asyncio.coroutine
def get_movies(kind, page, search=None):
    '''Get all movies by specifing kind.'''
    # use semaphore to limit the number of coroutines
    with (yield from sem):
        url = get_url(kind, page, search)
        # check url is None
        if url is None:
            return []

        # get page content by asyncio
        res = yield from aiohttp.request('GET', url)
        content = yield from res.text()

        movies = []

        # use lxml to find the informations we want
        root = etree.HTML(content)
        # every movie is inside a div with class mv
        for mv in root.xpath('//div[@class="mv"]'):
            a = mv.xpath('./h3')[0].xpath('./a')[0]
            # get movie title
            title = a.text
            # get yify link
            link = base_url + a.attrib['href']

            # find movie poster image
            poster =\
                mv.xpath('.//div[@class="movie-image"]//img')[0].attrib['src']

            # put movie data into dictionary
            movie = {
                'title': title,
                'link': link,
                'poster_small': poster,
            }

            # find movie informations like genre, qualit, etc
            for li in mv.xpath('.//li'):
                # strip space for each text segments
                texts = list(text.strip() for text in li.itertext())

                # use first segment as key
                # lowercase, remove : and replace space with underscore
                key = texts[0].lower().replace(':', '').replace(' ', '_')

                # others as value, and join all as one string
                value = ' '.join(texts[1:]).strip()
                movie[key] = value

            # append movie into movies
            movies.append(movie)

        # get informations from the movie's yify link
        for movie in movies:
            detail = yield from get_one(movie['link'])
            movie.update(detail)

        return movies


def get_url(kind, page, search=None):
    '''Use kind to generate different url.'''
    kind = kind.lower()
    if kind == 'search' and search is not None:
        return '{}/search/{}/t-{}/'.format(base_url, search, page)
    elif kind in ['latest', 'popular']:
        return '{}/{}.html'.format(base_url, kind)


@asyncio.coroutine
def latest(page=1):
    '''Show latest movies.'''
    return get_movies('latest', page)


@asyncio.coroutine
def popular(page=1):
    '''Show popular movies.'''
    return get_movies('popular', page)


@asyncio.coroutine
def search(keyword, page=1):
    '''Search movies.'''
    return get_movies('search', page, keyword)


@asyncio.coroutine
def test():
    '''Get ten pages of movies.'''
    for f in asyncio.as_completed([popular(i) for i in range(1, 3)]):
        movies = yield from f
        for movie in movies:
            print(movie['rating'], movie['title'])


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())

if __name__ == '__main__':
    main()
