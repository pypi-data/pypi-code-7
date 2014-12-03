from enum import Enum


class CollectionType(Enum):
    COUNTING = 'counting'
    BLOG = 'liveblog'
    CHAT = 'livechat'
    COMMENTS = 'livecomments'
    RATINGS = 'ratings'
    REVIEWS = 'reviews'
    SIDENOTES = 'sidenotes'

    def __init__(self, ctype):
        self.type = ctype
        
    def __str__(self):
        return self.type