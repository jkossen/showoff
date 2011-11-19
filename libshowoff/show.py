from authentication import validate_password
import os, json

class Show(object):
    def __init__(self, app, album):
        self.app = app
        self.album = album
        self.show_dir = os.path.join(app.config['SHOWS_DIR'], album)
        self.show_file = os.path.join(self.show_dir, 'show.json')
        self.data = {'files': [], 'settings': {}, 'users': {}}
        self.valid_settings = [
            'require_authentication',
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
        self.data['users'][username] = encrypt_password(seed, password)

    def remove_user(self, username):
        self.data['users'].pop(username)

    def need_authentication(self):
        if (self.get_setting('require_authentication') == 'yes'):
            if session.get('username') and (session.get('album') == self.album):
                return False
            else:
                return True
        return False

    def check_auth(self, username, seed, password):
        if username in self.data['users']:
            return validate_password(seed, password, self.data['users'][username])
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
            datetime = get_exif_datetime(self.app, self.album, filename)
            filenames.append((datetime, filename))
        self.data['files'] = [v for (k, v) in sorted(filenames)]
        return self.save()

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

