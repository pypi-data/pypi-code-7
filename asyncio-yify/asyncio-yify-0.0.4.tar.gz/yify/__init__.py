import asyncio

import aiohttp
from lxml import etree

base_url = 'http://www.yify-torrent.org'

# use semaphore to limit the number of coroutines
sem = asyncio.Semaphore(10)


@asyncio.coroutine
def get_movie(url):
    # get movie page
    res = yield from aiohttp.request('GET', url)
    content = yield from res.text()

    root = etree.HTML(content)

    datas = {}

    # get movie poster
    datas['poster_large'] = root.xpath('//div[@class="cover"]/img')[0].attrib['src']

    # get movie details
    for li in root.xpath('//div[@class="inattr"]//li'):
        texts = list(text.lower().strip().replace(' ', '_') for text in li.itertext())
        key = texts[0].replace(':', '')
        value = ' '.join(texts[1:]).strip()

        # get imdb link
        if key == 'imdb_rating':
            datas['imdb'] = li.xpath('./a')[0].attrib['href']

    attrs = root.xpath('//div[@class="outattr"]/div[@class="attr"]')
    # get trailer
    datas['trailer'] = attrs[1].xpath('./a')[0].attrib['href']
    # get magnet
    datas['magnet'] = attrs[2].xpath('./a')[0].attrib['href']

    # get screenshots
    imgs = root.xpath('//div[@class="scrshot"]//img')
    datas['screenshot'] = [i.attrib['src'] for i in imgs]

    # get plot
    datas['plot'] = root.xpath('//div[@class="info"]/p')[0].text

    return datas


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
                texts = list(text.lower().strip().replace(' ', '_') for text in li.itertext())
                # remove : for first item, and convert string to lowercase
                texts[0] = texts[0].replace(':', '').lower()
                # use first item as key, others as value
                infos[texts[0]] = ' '.join(texts[1:])

            # put movie data into dictionary
            movie = {
                'title': title,
                'link': link,
                'poster_small': poster,
            }
            movie.update(infos)

            # append movie into movies
            movies.append(movie)

        # get details of each movie by calling get_movie
        for movie in movies:
            info = yield from get_movie(movie['link'])

            # update movie dictionary with info
            movie.update(infos)

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
    # get first ten pages of movies
    for f in asyncio.as_completed([popular(i) for i in range(1, 11)]):
        movies = yield from f
        for movie in movies:
            print(movie['rating'], movie['title'])


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())

if __name__ == '__main__':
    main()
