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

This is the admin adminlication code for showoff.

"""

from flask import Blueprint, current_app, Flask, render_template, send_from_directory, abort, url_for, redirect, json, jsonify, request
from controllers import PageController, ImageController
from libshowoff import Show, Paginator, supported_exiftags, clear_cache, update_cache, update_exif, is_edited, get_edit_or_original, get_exif, rotate_image
from ExifTags import TAGS

import os, re, Image

admin = Blueprint('admin', __name__, template_folder='templates')

def themed(template):
    """Return path to template in configured theme"""
    return os.path.join(current_app.config.get('THEME'), template)

def _paginated_overview(album, page, endpoint='admin.list', template='grid'):
    controller = PageController(current_app)
    show = Show(current_app, album)
    files = os.listdir(os.path.join(current_app.config['ALBUMS_DIR'], album))

    ext = re.compile(".jpg$", re.IGNORECASE)
    files = filter(ext.search, files)

    if len(files) == 0:
        abort(404)

    files.sort()

    return controller.act('paginated_overview', album=album, show=show, page=page,
                          files=files, endpoint=endpoint, template=template)

def _rotate_image(album, filename, steps=1):
    rotate_image(admin, album, filename, steps)
    for size in current_app.config['ALLOWED_SIZES']:
        if size != 'full':
            clear_cache(admin, album, filename, size)

#@current_app.template_filter('exif_table')
def get_exif_table(exif):
    table = '<table>'
    for line in exif:
        table = table + '<tr><td>' + line.replace('|', '</td><td>') + '</td></tr>'
    table = table + '</table>'
    return table

@admin.route('/static/<path:filename>')
def static_files(filename):
    """Send static files such as style sheets, JavaScript, etc."""
    static_path = os.path.join(admin.root_path, 'templates', current_app.config['THEME'], 'static')
    return send_from_directory(static_path, filename)

@admin.route('/<album>/image/<filename>/<int:size>/')
def show_image(album, filename, size=None):
    controller = ImageController(current_app)
    return controller.act('get', album, filename, size)

@admin.route('/<album>/image/<filename>/full/')
def show_image_full(album, filename):
    return show_image(album, filename)

@admin.route('/<album>/show/<filename>')
def image_page(album, filename):
    controller = PageController(current_app)
    return controller.act('image_info', album, filename)

@admin.route('/<album>/rotate_exif/')
def rotate_url():
    # dummy
    pass

@admin.route('/<album>/list/<template>/<int:page>/')
@admin.route('<album>/list/<int:page>/')
def list(album, page, template='grid'):
    return _paginated_overview(album, page, 'admin.list', template)

@admin.route('/<album>/')
def show_album(album):
    return list(album, 1)

@admin.route('/')
def show_index():
    dir_list = os.listdir(current_app.config['ALBUMS_DIR'])
    album_list = [os.path.basename(album) for album in dir_list]
    album_list.sort(reverse=True)
    return render_template(themed('index.html'), albums=album_list)

@admin.route('/<album>/rotate/<int:steps>/<filename>/')
def image_rotate(album, filename, steps=1):
    _rotate_image(album, filename, steps)
    return jsonify(result='OK')

@admin.route('/<album>/rotate_exif/<filename>/')
def exif_rotate_image(album, filename):
    orientation_steps = { 3: 2, 6: 1, 8: 3 }
    if not is_edited(admin, album, filename):
        img = Image.open(os.path.join(current_app.config['ALBUMS_DIR'], album, filename))
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

@admin.route('/<album>/add_image_to_show/<filename>/')
def add_image_to_show(album, filename):
    """Add an image to the show"""
    show = Show(current_app, album)
    if show.add_image(filename):
        return jsonify(result='OK')
    return jsonify(result='Failed')

@admin.route('/<album>/remove_image_from_show/<filename>/')
def remove_image_from_show(album, filename):
    """Remove an image from the show"""
    show = Show(current_app, album)
    if show.remove_image(filename):
        return jsonify(result='OK')
    return jsonify(result='Failed')

@admin.route('/<album>/sort_by_exifdate/')
def sort_show_by_exifdate(album):
    """Sort the show by exif datetime """
    show = Show(current_app, album)
    show.sort_by_exif_datetime()
    return redirect(request.referrer or url_for('index'))

@admin.route('/<album>/edit_users/')
def show_edit_users(album):
    show = Show(current_app, album)
    users = show.data['users']
    return render_template(themed('edit_users.html'), album=album, show=show, users=users)

@admin.route('/<album>/add_all/')
def add_all_images_to_show(album):
    show = Show(current_app, album)
    show.add_all_images()
    return redirect(request.referrer or url_for('index'))

@admin.route('/<album>/set/<setting>/<value>/')
def show_change_setting(album, setting, value):
    show = Show(current_app, album)
    if (show.change_setting(setting, value) and show.save()):
        return jsonify(result='OK')
    else:
        return jsonify(result='Failed')

@admin.route('/<album>/change_password/', methods=['POST'])
def show_change_password(album):
    if request.method == 'POST':
        show = Show(current_app, album)
        username = request.form['username']
        password = request.form['password']
        show.set_user(username, current_app.config['SECRET_KEY'], password)
        if (show.save()):
            return redirect(request.referrer or url_for('index'))
        else:
            return jsonify(result='Failed')

@admin.route('/<album>/remove_user/<username>/')
def show_remove_user(album, username):
    show = Show(current_app, album)
    show.remove_user(username)
    if (show.save()):
        return redirect(request.referrer or url_for('index'))
    else:
        return jsonify(result='Failed')

#if __name__ == '__main__':
#    admin.run(host=current_app.config['ADMIN_HOST'], port=current_app.config['ADMIN_PORT'])

