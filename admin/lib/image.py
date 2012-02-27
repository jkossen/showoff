from flask import send_from_directory
from libshowoff import is_edited, clear_cache, update_cache, update_exif, rotate_image
from ExifTags import TAGS
import os, Image

def _image_rotate(app, album, filename, steps=1):
    rotate_image(app, album, filename, steps)
    for size in app.config['ALLOWED_SIZES']:
        if size != 'full':
            clear_cache(admin, album, filename, size)

def image_rotate_exif(app, album, filename):
    orientation_steps = { 3: 2, 6: 1, 8: 3 }
    if not is_edited(app, album, filename):
        img = Image.open(os.path.join(app.config['ALBUMS_DIR'], album, filename))
        exif = img._getexif()
        ret = {}
        for tag, value in exif.items():
            decoded = TAGS.get(tag, tag)
            ret[decoded] = value
        if ret.has_key('Orientation'):
            orientation = int(ret['Orientation'])
            if orientation_steps.has_key(orientation):
                _image_rotate(app, album, filename, orientation_steps[orientation])

def image_retrieve(app, album, filename, size=None):
    if size == None or size == 'full':
        return send_from_directory(get_edit_or_original(app, album, filename), filename)

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

