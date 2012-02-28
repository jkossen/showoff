from flask import current_app, render_template, abort, request, session
from libshowoff import Show
from frontend.forms import LoginForm
import os

def authenticate(album):
    """Check user credentials and initialize session"""
    show = Show(album)

    if request.method == 'POST':
        form = LoginForm(request.form)
        if form.validate():
            if show.check_auth(request.form['username'], current_app.config['SECRET_KEY'], request.form['password']):
                next_url = None
                if session.has_key('next_url'):
                    next_url = session['next_url']

                session.clear()

                session['username'] = request.form['username']
                session['album'] = album

                if next_url is not None:
                    session['next_url'] = next_url

                return True
    return False

