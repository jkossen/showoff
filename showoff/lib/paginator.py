from flask import abort, url_for
from werkzeug import cached_property

class Paginator(object):
    def __init__(self, album, items, per_page, page, endpoint, template):
        self.album = album
        self.items = items
        self.per_page = per_page
        self.page = page
        self.endpoint = endpoint
        self.template = template

        if (self.page > self.pages or self.page < 1):
            abort(404)

    @cached_property
    def count(self):
        return len(self.items)

    @cached_property
    def entries(self):
        offset = (self.page - 1) * self.per_page
        end = offset + self.per_page
        return self.items[offset:end]

    has_previous = property(lambda x: x.page > 1)
    has_next = property(lambda x: x.page < x.pages)
    previous = property(lambda x: url_for(x.endpoint, album=x.album, page=x.page - 1, template=x.template))
    next = property(lambda x: url_for(x.endpoint, album=x.album, page=x.page + 1, template=x.template))
    first = property(lambda x: url_for(x.endpoint, album=x.album, page=1, template=x.template))
    last = property(lambda x: url_for(x.endpoint, album=x.album, page=x.pages, template=x.template))
    pages = property(lambda x: max(0, x.count - 1) // x.per_page + 1)
