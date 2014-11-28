import flask
import string
import math


def dashify(text):
    result = text[0].lower()
    for c in text[1:]:
        if c in string.ascii_lowercase:
            result = result + c
        else:
            result = result + '-' + c.lower()
    return result


class Paginator:
    def __init__(self, iterable, page, perpage=20, ajax_perpage=20, pages=None):
        if page < 1:
            flask.abort(404)

        # INIT
        self.iterable = iterable
        self.page = page
        if perpage:
            self.perpage = perpage
            self.ajax = False
        else:
            self.perpage = ajax_perpage
            self.ajax = True
        try:
            self.total = iterable.count()
        except (TypeError, AttributeError):
            self.total = len(iterable)
        self.pages = int(math.ceil(self.total / float(self.perpage))) if pages is None else pages

        # EVALUATE
        start_index = (page - 1) * self.perpage
        end_index = page * self.perpage

        try:
            self.models = list(iterable.skip(start_index).limit(self.perpage))
        except (TypeError, AttributeError):
            self.models = iterable[start_index:end_index]
        if not self.models and page != 1:
            flask.abort(404)

        # CAN BE SET TO FALSE TO HIDE PAGINATION BUT BE ABLE TO ITERATE (AT AJAX CALL)
        self.show = True


    @property
    def has_prev(self):
        return self.page > 1


    @property
    def has_next(self):
        return self.page < self.pages


    def __iter__(self, around_edge=2, around_current=2):
        last = 0 # equals to p - 1, except ... cases
        for p in range(1, self.pages + 1):
            in_left_edge = p <= around_edge
            in_right_edge = p > self.pages - around_edge
            in_around_current = self.page - around_current - 1 < p < self.page + around_current + 1
            if in_left_edge or in_around_current or in_right_edge:
                if last + 1 != p:
                    yield None
                yield p
                last = p


    def iter_pages(self):
        return iter(self)


__all__ = (
    'dashify',
    'Paginator'
)
