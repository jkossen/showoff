from flask import current_app, send_from_directory, safe_join
from showoff.lib import update_cache, update_exif, get_edit_or_original
import os

def image_retrieve(album, filename, size=None):
    if size == None or size == 'full':
        return send_from_directory(get_edit_or_original(current_app, album, filename), filename)
    else:
        adir = safe_join(current_app.config['CACHE_DIR'], album)

        if not os.path.exists(adir):
            os.mkdir(adir)

        tdir = os.path.join(adir, str(int(size)))
        if not os.path.exists(os.path.join(tdir, os.path.basename(filename))):
            update_cache(current_app, album, filename, int(size))

        exifdir = safe_join(current_app.config['CACHE_DIR'], os.path.join(album, 'exif'))
        exiffile = safe_join(exifdir, os.path.basename(filename)) + '.exif'

        if not os.path.exists(exiffile):
            update_exif(current_app, album, filename)

        return send_from_directory(tdir, filename)
