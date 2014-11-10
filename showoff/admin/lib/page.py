from flask import abort, current_app
from showoff.lib import Paginator
import os, re

def _paginated_overview(album, page, endpoint='admin.list', template='grid'):
    files = os.listdir(os.path.join(current_app.config['ALBUMS_DIR'], album))

    ext = re.compile(".(jpg|png)$", re.IGNORECASE)
    files = filter(ext.search, files)

    if len(files) == 0:
        abort(404)

    files.sort()

    return Paginator(album, files, current_app.config['THUMBNAILS_PER_PAGE'], page, endpoint, template)

