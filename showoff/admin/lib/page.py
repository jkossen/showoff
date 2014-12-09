from flask import abort, current_app, session
from showoff.lib import Paginator, Show
import os, re

def _paginated_overview(album, page, endpoint='admin.list', template='grid'):
    show = Show(album, current_app.config, session)
    files = os.listdir(os.path.join(current_app.config['ALBUMS_DIR'], album))

    ext = re.compile(".(jpg|png|gif|bmp)$", re.IGNORECASE)
    files = [f for f in files if ext.search(f)]

    if len(files) == 0:
        abort(404)

    files.sort()

    if show.get_setting('reverse') == 'yes':
        files.reverse()

    try:
        return Paginator(album, files, current_app.config['THUMBNAILS_PER_PAGE'], page, endpoint, template)
    except:
        abort(404)
