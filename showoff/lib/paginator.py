# -*- coding: utf-8 -*-
"""
    showoff.lib.paginator
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2010-2014 by Jochem Kossen.
    :license: BSD, see LICENSE.txt for more details.
"""

from showoff.lib.exceptions import NoSuchPageError


class Paginator(object):
    """Paginate given list of items"""

    def __init__(self, album, items, per_page, page, endpoint, template):
        """Constructor

           Args:
             album (string): name of the album
             items (list): list of all items
             per_page (integer): amount of items to show per page
             page (integer): number of requested page
             endpoint (string): base url for constructing the return url
             template (string): template to use

           Raises:
             NoSuchPageError if page does not exist
        """
        self.album = album
        self.items = items
        self.per_page = per_page
        self.page = page
        self.endpoint = endpoint
        self.template = template

        if self.page > self.pages or self.page < 1:
            raise NoSuchPageError

    @property
    def count(self):
        """Total number of items"""
        return len(self.items)

    @property
    def entries(self):
        """List of items for the requested page"""
        offset = (self.page - 1) * self.per_page
        end = offset + self.per_page
        return self.items[offset:end]

    def get_page(self, index):
        """Get a dict of page parameters for the given index"""
        return {
            "endpoint": self.endpoint,
            "album": self.album,
            "page": index,
            "template": self.template
        }

    has_previous = property(lambda x: x.page > 1)
    has_next = property(lambda x: x.page < x.pages)
    previous = property(lambda x: x.get_page(x.page - 1))
    next = property(lambda x: x.get_page(x.page + 1))
    first = property(lambda x: x.get_page(1))
    last = property(lambda x: x.get_page(x.pages))
    pages = property(lambda x: max(0, x.count - 1) // x.per_page + 1)
