from flask import abort

class Controller(object):
    app = None
    def __init__(self, app):
        self.app = app

    def act(self, action, *args, **kwargs):
        try:
            func = getattr(self, action)
            return func(*args, **kwargs)
        except AttributeError:
            # this makes debugging a bit harder ;-)
            abort(404)

