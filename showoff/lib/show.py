from flask import current_app, session
from authentication import hash_password, validate_password
import os
import re
import json
from PIL import ExifTags, Image
from .exif import get_exif_datetime


class Show(object):
    def __init__(self, album):
        self.album = album
        self.show_dir = os.path.join(current_app.config['SHOWS_DIR'], album)
        self.show_file = os.path.join(self.show_dir, 'show.json')
        self.data = {'files': [], 'settings': {}, 'users': {}}
        self.valid_settings = [
            'require_authentication',
            'reverse',
        ]

        self.load()

    def nr_of_items(self):
        return len(self.data['files'])

    def is_enabled(self):
        return self.nr_of_items() > 0

    def add_image(self, filename):
        if filename not in self.data['files']:
            self.data['files'].append(filename)
            return self.save()
        return True

    def remove_image(self, filename):
        if filename in self.data['files']:
            self.data['files'].remove(filename)
            return self.save()
        return True

    def set_user(self, username, seed, password):
        self.data['users'][username] = hash_password(seed, password)

    def remove_user(self, username):
        self.data['users'].pop(username)

    def need_authentication(self):
        if (self.get_setting('require_authentication') != 'no'):
            if 'username' in session and 'album' in session and \
                    session['album'] == self.album:
                return False
            return True
        return False

    def check_auth(self, username, seed, password):
        if username in self.data['users']:
            return validate_password(seed, password,
                                     self.data['users'][username])
        return False

    def change_setting(self, setting, value):
        if setting in self.valid_settings:
            self.data['settings'][setting] = value
            return True
        else:
            return False

    def get_setting(self, setting):
        if setting in self.data['settings']:
            return self.data['settings'][setting]
        else:
            return False

    def load(self):
        if os.path.exists(self.show_file):
            fp = open(self.show_file, 'r')
            self.data.update(json.load(fp))

    def sort_by_exif_datetime(self):
        filenames = []
        for filename in self.data['files']:
            datetime = get_exif_datetime(current_app, self.album, filename)
            filenames.append((datetime, filename))
        self.data['files'] = [v for (k, v) in sorted(filenames)]
        return self.save()

    def add_all_images(self):
        """Add all images in album to the show"""
        files = os.listdir(os.path.join(current_app.config['ALBUMS_DIR'],
                                        self.album))

        # only list .jpg, .png, .gif, and .bmp files
        ext = re.compile(".(jpg|png|gif|bmp)$", re.IGNORECASE)
        files = filter(ext.search, files)
        files.sort()

        for filename in files:
            self.add_image(filename)

    def save(self):
        try:
            if not os.path.exists(self.show_dir):
                os.mkdir(self.show_dir)
            fp = open(self.show_file, 'w')
            js = json.dumps(self.data)
            fp.write(js)
            fp.close()
            return True
        except:
            return False
