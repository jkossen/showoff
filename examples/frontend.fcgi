#!/usr/bin/env python
from flup.server.fcgi import WSGIServer
from run_frontend import app

WSGIServer(app, bindAddress=app.config['VIEWER_FCGI_SOCKET']).run()
