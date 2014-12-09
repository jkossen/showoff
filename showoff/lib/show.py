# -*- coding: utf-8 -*-
"""
    showoff.lib.show
    ~~~~~~~~~~~~~~~~

    :copyright: (c) 2010-2014 by Jochem Kossen.
    :license: BSD, see LICENSE.txt for more details.
"""

from showoff.lib import hash_password
from showoff.lib import validate_password
from showoff.lib import Image
from showoff.lib import ExifManager
from showoff.lib.exceptions import UnknownFileError
from showoff.lib.exceptions import UnsupportedSettingError
import os
import re
import json


class Show(object):
    """A Show represents the list of published images from an album"""

    def __init__(self, album, config, session):
        """Constructor

           Args:
             album (string): name of the album
             config (dict): configuration dictionary
             session (dict): http session dictionary
        """

        self.session = session
        self.album = album
        self.album_dir = os.path.join(config['ALBUMS_DIR'], album)
        self.show_dir = os.path.join(config['SHOWS_DIR'], album)
        self.show_file = os.path.join(self.show_dir, 'show.json')
        self.data = {'files': [], 'settings': {}, 'users': {}}
        self.valid_settings = [
            'require_authentication',
            'reverse',
        ]

        self.load()

    def __repr__(self):
        return '<Show for album %s>' % (self.album)

    def __iter__(self):
        return iter(self.data['files'])

    @property
    def nr_of_items(self):
        """Number of items in show"""
        return len(self.data['files'])

    @property
    def is_enabled(self):
        """Check if show is enabled"""
        return self.nr_of_items > 0

    @property
    def need_authentication(self):
        """Check if show requires a user session

           Returns:
             True if show requires user session, False otherwise
        """
        if self.get_setting('require_authentication') != 'no':
            if 'username' in self.session and 'album' in self.session and \
                    self.session['album'] == self.album:
                return False
            return True
        return False

    def _ensure_file_exists(self, filename):
        """Check if album contains image

           Args:
             filename (string): filename of the image

           Raises:
             UnknownFileError: if file does not exist in album
        """
        if filename not in os.listdir(self.album_dir):
            raise UnknownFileError

    def set_user(self, username, seed, password):
        """Add user to show, or change the password for an existing user

           Args:
             username (string): username
             seed (string): seed to use for encrypting the password
             password (string): the plaintext password to be encrypted

           Returns:
             self
        """
        self.data['users'][username] = hash_password(seed, password)
        return self

    def remove_user(self, username):
        """Remove user from show

           Args: username (string): username

           Returns:
             self
        """
        self.data['users'].pop(username)
        return self

    def check_auth(self, username, seed, password):
        """Validate if username and password match

           Args:
             username (string): username
             seed (string): seed used for encrypting the password
             password (string): the plaintext password

           Returns:
             True if successful, False otherwise
        """
        if username in self.data['users']:
            return validate_password(seed, password,
                                     self.data['users'][username])
        return False

    def change_setting(self, setting, value):
        """Change value of setting

           Args:
             setting (string): name of setting
             value (string): new value of setting

           Returns:
             self
        """
        if setting in self.valid_settings:
            self.data['settings'][setting] = value

        return self

    def get_setting(self, setting):
        """Get value of setting

           Args:
             setting (string): name of setting

           Returns:
             value of setting

           Raises:
             UnsupportedSettingError if setting is not supported
        """
        if setting in self.data['settings']:
            return self.data['settings'][setting]
        else:
            raise UnsupportedSettingError

    def load(self):
        """Load the show data

           Returns:
             self
        """
        if os.path.exists(self.show_file):
            with open(self.show_file) as infile:
                self.data.update(json.load(infile))
        return self

    def toggle_image(self, filename):
        """Toggle if image is part of show

           Returns:
             self
        """
        self._ensure_file_exists(filename)

        if filename in self.data['files']:
            self.data['files'].remove(filename)
        else:
            self.data['files'].append(filename)

        return self

    def add_image(self, filename):
        """Add image from album to show

           Returns:
             self
        """
        self._ensure_file_exists(filename)

        if filename not in self.data['files']:
            self.data['files'].append(filename)

        return self

    def remove_image(self, filename):
        """Remove image from show (not from album)

           Returns:
             self
        """
        self._ensure_file_exists(filename)

        if filename in self.data['files']:
            self.data['files'].remove(filename)

        return self

    def sort_by_filename(self):
        """Sort the show contents by date retrieved from EXIF data

           Returns:
             self
        """
        self.data['files'].sort()

        return self

    def sort_by_exif_datetime(self):
        """Sort the show contents by filename

           Returns:
             self
        """
        filenames = []

        for filename in self.data['files']:
            image = Image(self.album, filename)
            exif_manager = ExifManager(image)
            datetime = exif_manager.get_exif_datetime()
            filenames.append((datetime, filename))

        self.data['files'] = [filename
                              for (datetime, filename)
                              in sorted(filenames)]

        return self

    def add_all_images(self):
        """Add all images in album to the show

           Returns:
             self
        """
        files = os.listdir(self.album_dir)

        # only list .jpg, .png, .gif, and .bmp files
        ext = re.compile(".(jpg|png|gif|bmp)$", re.IGNORECASE)
        files = [f for f in files if ext.search(f)]
        files.sort()

        for filename in files:
            self.add_image(filename)

        return self

    def save(self):
        """Save the show to disk"""
        if not os.path.exists(self.show_dir):
            os.mkdir(self.show_dir)

        with open(self.show_file, 'w') as outfile:
            outfile.write(json.dumps(self.data))
