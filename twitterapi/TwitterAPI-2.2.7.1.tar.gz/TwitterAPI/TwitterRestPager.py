__author__ = "Jonas Geduldig"
__date__ = "June 8, 2013"
__license__ = "MIT"

import time


class TwitterRestPager(object):

    """Continuous (stream-like) pagination of response from Twitter REST API resource.

    :param api: An authenticated TwitterAPI object
    :param resource: String with the resource path (ex. search/tweets)
    :param params: Dictionary of resource parameters
    """

    def __init__(self, api, resource, params=None):
        self.api = api
        self.resource = resource
        self.params = params

    def get_iterator(self, wait=5, new_tweets=False):
        """Iterate response from Twitter REST API resource.  Resource is called
        in a loop to retrieve consecutive pages of results.

        :param wait: Integer number (default=5) of seconds wait between requests.
                     Depending on the resource, appropriate values are 5 or 60 seconds.
        :param new_tweets: Boolean determining the search direction.
                           False (default) retrieves old results.
                           True retrieves current results.

        :returns: JSON objects containing statuses, errors or other return info.
        """
        elapsed = 0
        while True:
            # get one page of results
            start = time.time()
            r = self.api.request(self.resource, self.params)
            it = r.get_iterator()
            if new_tweets:
                it = reversed(list(it))

            # yield each item in the page
            id = None
            for item in it:
                if 'id' in item:
                    id = item['id']
                yield item

			# bail when no more older results
            if id is None and not new_tweets:
            	break

            # sleep before getting another page of results
            elapsed = time.time() - start
            pause = wait - elapsed if elapsed < wait else 0
            time.sleep(pause)

            # use the first id to limit the next batch of newer tweets, or
            # use the last id to limit the next batch of older tweets
            if id is None:
            	continue
            elif new_tweets:
                self.params['since_id'] = str(id)
            else:
                self.params['max_id'] = str(id - 1)
