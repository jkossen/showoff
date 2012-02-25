#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Showoff - Webbased photo album software

Copyright (c) 2010-2011 by Jochem Kossen <jochem.kossen@gmail.com>

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

This is the admin application code for showoff.

"""

from flask import Flask, render_template, send_from_directory, abort, url_for, redirect, json, jsonify, request
from controllers import PageController, ImageController
from werkzeug import cached_property
from libshowoff import Show, Paginator, supported_exiftags, clear_cache, update_cache, update_exif, is_edited, get_edit_or_original, get_exif, rotate_image
from ExifTags import TAGS

import os, re, Image

app = Flask(__name__, static_path=None, template_folder='templates/admin')
app.config.from_pyfile('config.py')
app.config.from_envvar('SHOWOFF_ADMIN_CONFIG', silent=True)

def get_route(function):
    """Return complete route based on configuration and routes"""
    return '/%s%s' % (app.config['ADMIN_PREFIX'],
                      app.config['ADMIN_ROUTES'][function])

def themed(template):
    """Return path to template in configured theme"""
    return os.path.join(app.config['THEME'], template)

def _paginated_overview(album, page, endpoint='list', template='grid'):
    controller = PageController(app)
    show = Show(app, album)
    files = os.listdir(os.path.join(app.config['ALBUMS_DIR'], album))

    ext = re.compile(".jpg$", re.IGNORECASE)
    files = filter(ext.search, files)

    if len(files) == 0:
        abort(404)

    files.sort()

    return controller.act('paginated_overview', album=album, show=show, page=page,
                          files=files, endpoint=endpoint, template=template)

def _rotate_image(album, filename, steps=1):
    rotate_image(app, album, filename, steps)
    for size in app.config['ALLOWED_SIZES']:
        if size != 'full':
            clear_cache(app, album, filename, size)

@app.template_filter('exif_table')
def get_exif_table(exif):
    table = '<table>'
    for line in exif:
        table = table + '<tr><td>' + line.replace('|', '</td><td>') + '</td></tr>'
    table = table + '</table>'
    return table

@app.route(get_route('static_files'))
def static_files(filename):
    """Send static files such as style sheets, JavaScript, etc."""
    static_path = os.path.join(app.root_path, 'templates', 'admin',
                               app.config['THEME'], 'static')
    return send_from_directory(static_path, filename)

@app.route(get_route('show_image'))
def show_image(album, filename, size=None):
    controller = ImageController(app)
    return controller.act('get', album, filename, size)

@app.route(get_route('show_image_full'))
def show_image_full(album, filename):
    return show_image(album, filename)

@app.route(get_route('image_page'))
def image_page(album, filename):
    controller = PageController(app)
    return controller.act('image_info', album, filename)

@app.route(get_route('rotate_url'))
def rotate_url():
    # dummy
    pass

@app.route(get_route('list_templated'))
@app.route(get_route('list'))
def list(album, page, template='grid'):
    return _paginated_overview(album, page, 'list', template)

@app.route(get_route('show_album'))
def show_album(album):
    return list(album, 1)

@app.route(get_route('index'))
def show_index():
    dir_list = os.listdir(app.config['ALBUMS_DIR'])
    album_list = [os.path.basename(album) for album in dir_list]
    album_list.sort(reverse=True)
    return render_template(themed('index.html'), albums=album_list)

@app.route(get_route('image_rotate'))
def image_rotate(album, filename, steps=1):
    _rotate_image(album, filename, steps)
    return jsonify(result='OK')

@app.route(get_route('exif_rotate_image'))
def exif_rotate_image(album, filename):
    orientation_steps = { 3: 2, 6: 1, 8: 3 }
    if not is_edited(app, album, filename):
        img = Image.open(os.path.join(app.config['ALBUMS_DIR'], album, filename))
        exif = img._getexif()
        ret = {}
        for tag, value in exif.items():
            decoded = TAGS.get(tag, tag)
            ret[decoded] = value
        if ret.has_key('Orientation'):
            orientation = int(ret['Orientation'])
            if orientation_steps.has_key(orientation):
                _rotate_image(album, filename, orientation_steps[orientation])
    return jsonify(result='OK')

@app.route(get_route('add_image_to_show'))
def add_image_to_show(album, filename):
    """Add an image to the show"""
    show = Show(app, album)
    if show.add_image(filename):
        return jsonify(result='OK')
    return jsonify(result='Failed')

@app.route(get_route('remove_image_from_show'))
def remove_image_from_show(album, filename):
    """Remove an image from the show"""
    show = Show(app, album)
    if show.remove_image(filename):
        return jsonify(result='OK')
    return jsonify(result='Failed')

@app.route(get_route('sort_show_by_exifdate'))
def sort_show_by_exifdate(album):
    """Sort the show by exif datetime """
    show = Show(app, album)
    show.sort_by_exif_datetime()
    return redirect(request.referrer or url_for('index'))

@app.route(get_route('show_edit_users'))
def show_edit_users(album):
    show = Show(app, album)
    users = show.data['users']
    return render_template(themed('edit_users.html'), album=album, show=show, users=users)

@app.route(get_route('add_all_images_to_show'))
def add_all_images_to_show(album):
    show = Show(app, album)
    show.add_all_images()
    return redirect(request.referrer or url_for('index'))

@app.route(get_route('show_change_setting'))
def show_change_setting(album, setting, value):
    show = Show(app, album)
    if (show.change_setting(setting, value) and show.save()):
        return jsonify(result='OK')
    else:
        return jsonify(result='Failed')

@app.route(get_route('show_change_password'), methods=['POST'])
def show_change_password(album):
    if request.method == 'POST':
        show = Show(app, album)
        username = request.form['username']
        password = request.form['password']
        show.set_user(username, app.config['SECRET_KEY'], password)
        if (show.save()):
            return redirect(request.referrer or url_for('index'))
        else:
            return jsonify(result='Failed')

@app.route(get_route('show_remove_user'))
def show_remove_user(album, username):
    show = Show(app, album)
    show.remove_user(username)
    if (show.save()):
        return redirect(request.referrer or url_for('index'))
    else:
        return jsonify(result='Failed')

if __name__ == '__main__':
    app.run(host=app.config['ADMIN_HOST'], port=app.config['ADMIN_PORT'])

