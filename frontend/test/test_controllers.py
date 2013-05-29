from .. import controllers
from flask import Flask
import py

class TestControllers(object):
    def setup_method(self, method):
        self.app = Flask(__name__)
        self.app.register_blueprint(controllers.frontend)
        self.app.config.update({
                'ALBUMS_DIR' : str(py.test.ensuretemp('albums')),
                'THEME' : 'default',
                })

    def test_show_index(self):
        with self.app.test_client() as c:
            resp = c.get('/')
            assert resp.status_code == 200
            print resp.data

