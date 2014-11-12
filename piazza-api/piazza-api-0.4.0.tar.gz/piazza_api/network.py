from collections import namedtuple

from .rpc import PiazzaRPC


################
# Feed Filters #
################

class FeedFilter(object):
    pass

class UnreadFilter(FeedFilter):
    """Filter through only posts with unread content in feed"""
    def __init__(self):
        pass

    def to_kwargs(self):
        return dict(updated=True)

class FollowingFilter(FeedFilter):
    """Filter through only posts that you are following in feed"""
    def __init__(self):
        pass

    def to_kwargs(self):
        return dict(following=True)

class FolderFilter(FeedFilter):
    """Filter only posts in ``folder_name`` in your feed

    :type folder_name: str
    :param folder_name: Name of folder to show posts from in feed
    """
    def __init__(self, folder_name):
        self.folder_name = folder_name

    def to_kwargs(self):
        return dict(folder=True, filter_folder=self.folder_name)


###########
# Network #
###########

class Network(object):
    """Abstraction for a Piazza "Network" (or class)

    :param network_id: ID of the network
    :param cookies: RequestsCookieJar containing cookies used for authentication
    """
    def __init__(self, network_id, cookies):
        self._nid = network_id
        self._rpc = PiazzaRPC(network_id=self._nid)
        self._rpc.cookies = cookies

        ff = namedtuple('FeedFilters', ['unread', 'following', 'folder'])
        self._feed_filters = ff(UnreadFilter, FollowingFilter, FolderFilter)

    @property
    def feed_filters(self):
        """namedtuple instance containing FeedFilter classes for easy access

        :rtype: namedtuple
        :returns: namedtuple with unread, following, and folder attributes
            mapping to filters
        """
        return self._feed_filters

    #########
    # Posts #
    #########

    def get_post(self, cid):
        """Get data from post `cid`

        :type  cid: str|int
        :param cid: This is the post ID to get
        :rtype: dict
        :returns: Dictionary with all data on the post
        """
        return self._rpc.content_get(cid=cid)

    def iter_all_posts(self, limit=None):
        """Get all posts visible to the current user

        This grabs you current feed and ids of all posts from it; each post
        is then individually fetched. This method does not go against
        a bulk endpoint; it retrieves each post individually, so a
        caution to the user when using this.

        :type limit: int|None
        :param limit: If given, will limit the number of posts to fetch
            before the generator is exhausted and raises StopIteration.
            No special consideration is given to `0`; provide `None` to
            retrieve all posts.
        :returns: An iterator which yields all posts which the current user
            can view
        :rtype: generator
        """
        feed = self.get_feed(limit=999999, offset=0)
        cids = [post['id'] for post in feed["feed"]]
        if limit is not None:
            cids = cids[:limit]
        for cid in cids:
            yield self.get_post(cid)

    #########
    # Users #
    #########

    def get_users(self, user_ids):
        """Get a listing of data for specific users ``user_ids`` in
        this network

        :type  user_ids: list of str
        :param user_ids: a list of user ids. These are the same
            ids that are returned by get_all_users.
        :returns: Python object containing returned data, a list
            of dicts containing user data.
        :rtype: list
        """
        return self._rpc.get_users(user_ids=user_ids)

    def iter_users(self, user_ids):
        """Same as ``Network.get_users``, but returns an iterable instead

        :rtype: listiterator
        """
        return iter(self.get_users(user_ids=user_ids))

    def get_all_users(self):
        """Get a listing of data for all users in this network

        :rtype: list
        :returns: Python object containing returned data, a list
            of dicts containing user data.
        """
        return self._rpc.get_all_users()

    def iter_all_users(self):
        """Same as ``Network.get_all_users``, but returns an iterable instead

        :rtype: listiterator
        """
        return iter(self.get_all_users())

    def add_students(self, student_emails):
        """Add students with ``student_emails`` to the network

        Piazza will email these students with instructions to
        activate their account.

        :type  student_emails: list of str
        :param student_emails: A listing of email addresses to enroll
            in the network (or class). This can be a list of length one.
        :rtype: list
        :returns: Python object containing returned data, a list
            of dicts of user data of all of the users in the network
            including the ones that were just added.
        """
        return self._rpc.add_students(student_emails=student_emails)

    def remove_users(self, user_ids):
        """Remove users with ``user_ids`` from this network

        :type  user_ids: list of str
        :param user_ids: a list of user ids. These are the same
            ids that are returned by get_all_users.
        :rtype: list
        :returns: Python object containing returned data, a list
            of dicts of user data of all of the users remaining in
            the network after users are removed.
        """
        return self._rpc.remove_users(user_ids=user_ids)

    ########
    # Feed #
    ########

    def get_feed(self, limit=100, offset=0):
        """Get your feed for this network

        Pagination for this can be achieved by using the ``limit`` and
        ``offset`` params

        :type limit: int
        :param limit: Number of posts from feed to get, starting from ``offset``
        :type offset: int
        :param offset: Offset starting from bottom of feed
        :rtype: dict
        :returns: Feed metadata, including list of posts in feed format; this
            means they are not the full posts but only in partial form as
            necessary to display them on the Piazza feed. For example, the
            returned dicts only have content snippets of posts rather
            than the full text.
        """
        return self._rpc.get_my_feed(limit=limit, offset=offset)

    def get_filtered_feed(self, feed_filter):
        """Get your feed containing only posts filtered by ``feed_filter``

        :type feed_filter: FeedFilter
        :param feed_filter: Must be an instance of either: UnreadFilter,
            FollowingFilter, or FolderFilter
        :rtype: dict
        """
        assert isinstance(feed_filter, (UnreadFilter, FollowingFilter,
                                        FolderFilter))
        return self._rpc.filter_feed(**feed_filter.to_kwargs())

    def search_feed(self, query):
        """Search for posts with ``query``, returned in feed format

        :type query: str
        :param query: The search query; should just be keywords for posts
            that you are looking for
        :rtype: dict
        """
        return self._rpc.search(query=query)

    ##############
    # Statistics #
    ##############

    def get_statistics(self):
        """Get statistics for class

        :rtype: dict
        :returns: Statistics for class that are viewable on the Statistics
            page on the Piazza web UI
        """
        return self._rpc.get_stats()
