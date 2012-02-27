from flask import abort
from libshowoff import Paginator
import os, re

def _paginated_overview(app, album, page, endpoint='admin.list', template='grid'):
    files = os.listdir(os.path.join(app.config['ALBUMS_DIR'], album))

    ext = re.compile(".jpg$", re.IGNORECASE)
    files = filter(ext.search, files)

    if len(files) == 0:
        abort(404)

    files.sort()

    return Paginator(album, files, app.config['THUMBNAILS_PER_PAGE'], page, endpoint, template)

