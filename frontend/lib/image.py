from flask import send_from_directory
from libshowoff import update_cache, update_exif, get_edit_or_original
import os

def image_retrieve(app, album, filename, size=None):
    if size == None or size == 'full':
        return send_from_directory(get_edit_or_original(app, album, filename), filename)
    else:
        adir = os.path.join(app.config['CACHE_DIR'], album)

        if not os.path.exists(adir):
            os.mkdir(adir)

        tdir = os.path.join(adir, str(int(size)))
        if not os.path.exists(os.path.join(tdir, os.path.basename(filename))):
            update_cache(app, album, filename, int(size))

        exifdir = os.path.join(app.config['CACHE_DIR'], album, 'exif')
        exiffile = os.path.join(exifdir, os.path.basename(filename) + '.exif')

        if not os.path.exists(exiffile):
            update_exif(app, album, filename)

        return send_from_directory(tdir, filename)
