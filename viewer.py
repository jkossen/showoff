#!/usr/bin/env python
# -*- coding: utf-8 -*-

# LICENSE {{{
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
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR#{{{# }}}
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

This is the viewer application code for showoff. It's only used for
viewing content, not manipulation.

"""
# }}}

# IMPORTS {{{
from flask import Flask, render_template, send_from_directory, abort, url_for, redirect, json
from libshowoff import Show, Paginator, supported_exiftags, update_cache, update_exif, get_edit_or_original
import os, re, Image
# }}}

# APP INITIALIZATION {{{
app = Flask(__name__, static_path=None)
app.config.from_pyfile('config.py')
app.config.from_envvar('SHOWOFF_VIEWER_CONFIG', silent=True)
# }}}

# HELPER FUNCTIONS {{{
def view(rule, **options):
    """ Decorator for views """
    complete_rule = '/%s%s' % (app.config['VIEWER_PREFIX'],
            app.config['VIEWER_ROUTES'][rule])

    def decorator(f):
        app.add_url_rule(complete_rule, None, f, **options)
        return f
    return decorator

def render_themed(template, **options):
    """ Render template from a configured subdir to implement themes """
    template_path = os.path.join('viewer', app.config['THEME'], template)
    return render_template(template_path, **options)

# }}}

# TEMPLATE TAGS {{{
@app.template_filter('exif_table')
def get_exif_table(exif):
    table = '<table>'
    for line in exif:
        table = table + '<tr><td>' + line.replace('|', '</td><td>') + '</td></tr>'
    table = table + '</table>'
    return table
# }}}

# VIEWER VIEWS {{{
@view('static_files')
def static_files(filename):
    """Send static files such as style sheets, JavaScript, etc."""
    static_path = os.path.join(app.root_path, 'templates', 'viewer',
                               app.config['THEME'], 'static')
    return send_from_directory(static_path, filename)

@view('show_image')
def show_image(album, filename, size=None):
    """Send static files such as style sheets, JavaScript, etc."""
    if size is not None:
        adir = os.path.join(app.config['CACHE_DIR'], album)
        if not os.path.exists(adir):
            os.mkdir(adir)
        tdir = os.path.join(adir, str(int(size)))
        if not os.path.exists(os.path.join(tdir, os.path.basename(filename))):
            update_cache(app, album, filename, size)

        exifdir = os.path.join(app.config['CACHE_DIR'], album, 'exif')
        exiffile = os.path.join(exifdir, os.path.basename(filename) + '.exif')
        if not os.path.exists(exiffile):
            update_exif(app, album, filename)

        return send_from_directory(tdir, filename)
    else:
        return send_from_directory(get_edit_or_original(app, album, filename), filename)

@view('show_image_full')
def show_image_full(album, filename):
    return show_image(album, filename)

@view('image_page')
def image_page(album, filename):
    exifdir = os.path.join(app.config['CACHE_DIR'], album, 'exif')
    f = open(os.path.join(exifdir, filename + '.exif'))
    exif_array = f.readlines()
    f.close()

    return render_themed('image.html', album=album, filename=filename, exif=exif_array)

@view('list')
def list(album, page):
    show = Show(app, album)
    if len(show.data['files']) == 0:
        abort(404)
    files = show.data['files']
    p = Paginator(album, files, app.config['THUMBNAILS_PER_PAGE'], page, 'list')
    return render_themed('list.html', album=album, files=p.entries, paginator=p, page=page)

@view('list_small')
def list_small(album, page):
    show = Show(app, album)
    if len(show.data['files']) == 0:
        abort(404)
    files = show.data['files']
    p = Paginator(album, files, app.config['THUMBNAILS_PER_SMALL_LIST'], page, 'list_small')
    return render_themed('list_small.html', album=album, files=p.entries, paginator=p, page=page)

@view('album')
def show_album(album):
    """Render first page of album"""
    return list(album, 1)

@view('show_galleria')
def show_galleria(album, page):
    """"""
    show = Show(app, album)
    if len(show.data['files']) == 0:
        abort(404)
    files = show.data['files']

    p = Paginator(album, files, app.config['THUMBNAILS_PER_PAGE'], page, 'show_galleria')
    return render_themed('galleria.html', album=album, files=p.entries, paginator=p)

@view('show_slideshow')
def show_slideshow(album, page):
    """"""
    show = Show(app, album)
    if len(show.data['files']) == 0:
        abort(404)
    files = show.data['files']

    # only list .jpg files
    ext = re.compile(".jpg$", re.IGNORECASE)
    files = filter(ext.search, files)

    p = Paginator(album, files, app.config['THUMBNAILS_PER_PAGE'], page, 'show_slideshow')
    return render_themed('slideshow.html', album=album, files=p.entries, paginator=p, page=page)

@view('index')
def show_index():
    """Render frontpage"""
    dir_list = os.listdir(app.config['ALBUMS_DIR'])
    full_album_list = [ os.path.basename(album) for album in dir_list ]
    shows = {}
    for album in full_album_list:
        show = Show(app, album)
        if show.is_enabled():
            shows[album] = show
    album_list = shows.keys()
    album_list.sort()
    return render_themed('index.html', albums=album_list, shows=shows)

# }}}

# MAIN RUN LOOP {{{
if __name__ == '__main__':
    app.run(host=app.config['VIEWER_HOST'], port=app.config['VIEWER_PORT'])
# }}}

