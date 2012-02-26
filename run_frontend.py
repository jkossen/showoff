from flask import Flask
from frontend.views import frontend

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config.from_envvar('SHOWOFF_FRONTEND_CONFIG', silent=True)

app.register_blueprint(frontend, url_prefix='/showoff')

if __name__ == '__main__':
    app.run(host=app.config['FRONTEND_HOST'], port=app.config['FRONTEND_PORT'])

