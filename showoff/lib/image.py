import os


class Image(object):
    def __init__(self, album, filename, config):
        self.album = album
        self.filename = filename
        self.config = config

    def _get_folder(self, kind):
        return os.path.join(self.config[kind + '_DIR'], self.album)

    @property
    def orig_dir(self):
        return self._get_folder('ALBUMS')

    @property
    def orig_file(self):
        return os.path.join(self.orig_dir, self.filename)

    @property
    def edit_dir(self):
        return self._get_folder('EDITS')

    @property
    def edit_file(self):
        return os.path.join(self.edit_dir, self.filename)

    @property
    def exif_dir(self):
        return os.path.join(self._get_folder('CACHE'), 'exif')

    @property
    def exif_file(self):
        return os.path.join(self.exif_dir, self.filename + '.exif')

    def is_edited(self):
        if os.path.exists(self.edit_file):
            return True
        else:
            return False

    def get_edit_or_original_dir(self):
        if self.is_edited():
            return self.edit_dir
        else:
            return self.orig_dir

    def get_fullsize_path(self):
        return os.path.join(
            self.get_edit_or_original_dir(),
            self.filename
        )
