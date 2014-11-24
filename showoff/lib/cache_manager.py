from flask import current_app, send_from_directory
from showoff.lib.exif import ExifManager
from PIL import Image
import os


class CacheManager(object):
    def __init__(self, image):
        self.image = image

    def get_dir(self, size):
        return os.path.join(current_app.config['CACHE_DIR'],
                            self.image.album,
                            str(size))

    def get_path(self, size):
        return os.path.join(self.get_dir(size), self.image.filename)

    def remove_cached_file(self, size):
        fpath = self.get_path(size)
        if os.path.exists(fpath):
            os.unlink(fpath)

    def clear(self, size=None):
        if size is None:
            for size in current_app.config['ALLOWED_SIZES']:
                self.remove_cached_file(size)
        else:
            self.remove_cached_file(size)

    def update(self, size):
        fpath = self.get_path(size)

        if not os.path.exists(fpath):
            adir = os.path.join(current_app.config['CACHE_DIR'],
                                self.image.album)
            if not os.path.exists(adir):
                os.mkdir(adir)

            tdir = os.path.join(adir, str(int(size)))
            if not os.path.exists(tdir):
                os.mkdir(tdir)

        if not os.path.exists(self.image.exif_file):
            exif = ExifManager(self.image)
            exif.update()

        img = Image.open(self.image.get_fullsize_path())
        img.thumbnail((size, size), Image.ANTIALIAS)
        img.save(self.get_path(size), 'JPEG')

    def send(self, size):
        if size == 'full':
            return self.image.send()

        size = int(size)
        fpath = self.get_path(size)

        if not os.path.exists(fpath):
            self.update(size)

        return send_from_directory(self.get_dir(size), self.image.filename)
