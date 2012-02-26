#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Showoff - Webbased photo album software

Copyright (c) 2010 by Jochem Kossen <jochem.kossen@gmail.com>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

   1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
   2. Redistributions in binary form must reproduce the above
   copyright notice, this list of conditions and the following
   disclaimer in the documentation and/or other materials provided
   with the distribution.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

This is the frontend application code for showoff. It's only used for
viewing content, not manipulation.

"""

from flask import Blueprint, current_app, Flask, abort, render_template, send_from_directory, request, redirect, session, url_for
from controllers import AuthenticationController, PageController, ImageController
from functools import wraps
from libshowoff import Show
from forms import LoginForm
import os

frontend = Blueprint('frontend', __name__, template_folder='templates')

def get_show(album, page, endpoint, template):
    controller = PageController(current_app)
    return controller.act('get_show', album=album, page=page,
                          endpoint=endpoint, template=template)

def get_nonpaginated_show(album, template):
    controller = PageController(current_app)
    return controller.act('get_nonpaginated_show', album=album,
                          template=template)

def render_themed(template, **options):
    template_path = os.path.join(current_app.config['THEME'], template)
    return render_template(template_path, **options)

def login_required(f):
    @wraps(f)
    def decorated_function(album, *args, **kwargs):
        show = Show(current_app, album)
        if show.need_authentication():
            session['next_url'] = request.url
            return redirect(url_for('frontend.login', album=album))
        return f(album, *args, **kwargs)
    return decorated_function

#@app.template_filter('exif_table')
def get_exif_table(exif):
    table = '<table>'
    for line in exif:
        table = table + '<tr><td>' + line.replace('|', '</td><td>') + '</td></tr>'
    table = table + '</table>'
    return table

@frontend.route('/login/<album>', methods=['GET', 'POST'])
def login(album):
    if request.method == 'POST':
        if AuthenticationController(current_app).act('login', album=album):
            if session.has_key('next_url') and session['next_url'] is not None and session['next_url'] != url_for('frontend.login', album=album):
                next_url = session['next_url']
                session.pop('next_url', None)
                return redirect(next_url)
            return redirect(url_for('frontend.show_album', album=album))
    return render_themed('login.html', album=album, form=LoginForm())

@frontend.route('/static_files/<path:filename>')
def static_files(filename):
    """Send static files such as style sheets, JavaScript, etc."""
    static_path = os.path.join(frontend.root_path, 'templates', current_app.config['THEME'], 'static')
    return send_from_directory(static_path, filename)

@frontend.route('/image/<album>/<filename>/<size>/')
@login_required
def get_image(album, filename, size=None):
    controller = ImageController(current_app)
    return controller.act('get', album, filename, size)

@frontend.route('/page/<album>/<filename>.html')
@login_required
def image_page(album, filename):
    controller = PageController(current_app)
    return controller.act('image_info', album, filename)

@frontend.route('/list/<album>/<template>/<int:page>.html')
@frontend.route('/list/<album>/<int:page>.html')
@login_required
def list(album, page, template='list'):
    if template in current_app.config['FRONTEND_LIST_TEMPLATES']:
        return get_show(album, page, 'frontend.list', template)
    else:
        abort(404)

@frontend.route('/fullshow/<album>/<template>.html')
@login_required
def show_nonpaginated(album, template='grid_full'):
    return get_nonpaginated_show(album, template)

@frontend.route('/slideshow/<album>/<int:page>.html')
@login_required
def show_slideshow(album, page):
    controller = PageController(current_app)
    return controller.act('slideshow', album, page, 'show_slideshow',
                          'slideshow.html')

@frontend.route('/<album>.html')
@login_required
def show_album(album):
    """Render first page of album"""
    return list(album, 1)

@frontend.route('/')
def show_index():
    controller = PageController(current_app)
    return controller.act('index')

