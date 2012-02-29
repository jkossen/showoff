#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Showoff - Webbased photo album software

Copyright (c) 2010-2012 by Jochem Kossen <jochem@jkossen.nl>

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
"""

from flask import Blueprint, current_app, Flask, abort, render_template, send_from_directory, request, redirect, session, url_for
from showoff.lib import Show
from .lib.authentication import login_required, authenticate
from .lib.page import get_paginator, render_themed
from .lib.image import image_retrieve
from forms import LoginForm
import os

frontend = Blueprint('frontend', __name__, template_folder='templates')

@frontend.route('/login/<album>', methods=['GET', 'POST'])
def login(album):
    if request.method == 'POST':
        if authenticate(album):
            if session.has_key('next_url') and session['next_url'] is not None and session['next_url'] != url_for('.login', album=album):
                next_url = session['next_url']
                session.pop('next_url', None)
                return redirect(next_url)
            return redirect(url_for('.show_album', album=album))
    return render_themed('login.html', album=album, form=LoginForm())

@frontend.route('/static_files/<path:filename>')
def static_files(filename):
    """Send static files such as style sheets, JavaScript, etc."""
    static_path = os.path.join(frontend.root_path, 'templates', current_app.config['THEME'], 'static')
    return send_from_directory(static_path, filename)

@frontend.route('/image/<album>/<filename>/<size>/')
@login_required
def get_image(album, filename, size=None):
    return image_retrieve(album, filename, size)

@frontend.route('/page/<album>/<filename>.html')
@login_required
def image_page(album, filename):
    show = Show(album)
    exifdir = safe_join(current_app.config['CACHE_DIR'], os.path.join(album, 'exif'))
    exif_array = get_exif(album, filename)

    return render_themed(template, album=album, filename=filename,
                         exif=exif_array, show=show)

@frontend.route('/list/<album>/<template>/<int:page>.html')
@frontend.route('/list/<album>/<int:page>.html')
@login_required
def list(album, page, template='list'):
    if template in current_app.config['FRONTEND_LIST_TEMPLATES']:
        show = Show(album)
        paginator = get_paginator(album, page, 'frontend.list', template)
        return render_themed(template + '.html', album=album,
                             show=show, files=paginator.entries, paginator=paginator, page=page)
    else:
        abort(404)

@frontend.route('/fullshow/<album>/<template>.html')
@login_required
def show_nonpaginated(album, template='grid_full'):
    show = Show(album)

    if len(show.data['files']) == 0:
        abort(404)

    files = show.data['files']
    return render_themed(template + '.html', album=album, files=files)

@frontend.route('/slideshow/<album>/<int:page>.html')
@login_required
def show_slideshow(album, page):
    paginator = get_paginator(album, page, 'frontend.show_slideshow', 'slideshow.html')
    return render_themed('slideshow.html', album=album, files=p.entries, paginator=p, page=page)

@frontend.route('/<album>.html')
@login_required
def show_album(album):
    """Render first page of album"""
    return list(album, 1)

@frontend.route('/')
def show_index():
    dir_list = os.listdir(current_app.config['ALBUMS_DIR'])
    full_album_list = [ os.path.basename(album) for album in dir_list ]
    shows = {}

    for album in full_album_list:
        show = Show(album)
        if show.is_enabled():
            shows[album] = show

    album_list = shows.keys()
    album_list.sort(reverse=True)

    return render_themed('index.html', albums=album_list, shows=shows)
