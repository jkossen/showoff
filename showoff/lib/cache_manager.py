# -*- coding: utf-8 -*-
"""
    showoff.lib.cache_manager
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2010-2014 by Jochem Kossen.
    :license: BSD, see LICENSE.txt for more details.
"""

from showoff.lib import ExifManager
from showoff.lib.exceptions import UnsupportedImageSizeError
from PIL import Image
import os


class CacheManager(object):
    """Handle caching for a given image"""

    def __init__(self, image, config):
        """Constructor

           Args:
             image (image): showoff image object
             config (dict): configuration dictionary
        """
        self.image = image
        self.config = config

    def _get_folderpath(self, size):
        """Get folder path of given size (without filename)

           Args:
             size (int): size of image in pixels

           Returns:
              string containing folder path
        """
        if size == 'full':
            return self.image.orig_dir

        return os.path.join(self.config['CACHE_DIR'],
                            self.image.album,
                            str(size))

    def _get_filepath(self, size):
        """Get full path to cached file of given size

           Args:
             size (int): size of image in pixels

           Returns:
              string containing full image path
        """
        return os.path.join(self._get_folderpath(size), self.image.filename)

    def get(self, size):
        """Get tuple with folder and filename for given size

           Args:
             size (int): size of image in pixels

           Raises:
             UnsupportedImageSizeError if size is not in ALLOWED_SIZES

           Returns:
             folder, filename
        """
        if size not in self.config['ALLOWED_SIZES']:
            raise UnsupportedImageSizeError

        if size == 'full':
            return self.image.orig_dir, self.image.filename

        if not os.path.exists(self._get_filepath(size)):
            self.create(size)

        return self._get_folderpath(size), self.image.filename

    def create(self, size):
        """Generate new cache files for given size

           Args:
             size (int): size of image in pixels

           Raises:
             UnsupportedImageSizeError if size is not in ALLOWED_SIZES

           Returns:
             self
        """
        if size not in self.config['ALLOWED_SIZES']:
            raise UnsupportedImageSizeError

        fpath = self._get_filepath(size)

        if not os.path.exists(fpath):
            adir = os.path.join(self.config['CACHE_DIR'],
                                self.image.album)
            if not os.path.exists(adir):
                os.mkdir(adir)

            tdir = os.path.join(adir, str(int(size)))
            if not os.path.exists(tdir):
                os.mkdir(tdir)

        img = Image.open(self.image.get_fullsize_path())
        img.thumbnail((int(size), int(size)), Image.ANTIALIAS)
        img.save(fpath, 'JPEG')

        self.event_manager.trigger("CACHE_REFRESH")

        return self

    def delete(self, size=None):
        """Remove cached files for given size, or all if size is None

           Args:
             size (int): size of image in pixels
        """
        if size == 'full':
            return self

        if size is None:
            for size in self.config['ALLOWED_SIZES']:
                self.delete(size)
        else:
            fpath = self._get_filepath(size)
            if os.path.exists(fpath):
                os.unlink(fpath)

        return self
