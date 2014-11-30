class Pagination(object):
    def __init__(self, query, page=0, per_page=10):
        self.items = query[page * per_page:(page + 1) * per_page]
