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

from flask import Blueprint, current_app, render_template, send_from_directory, url_for, redirect, jsonify, request
from libshowoff import Show, get_exif
from .lib.image import _image_rotate, image_rotate_exif, image_retrieve
from .lib.page import _paginated_overview

import os, re

admin = Blueprint('admin', __name__, template_folder='templates')

def render_themed(template, **options):
    template_path = os.path.join(current_app.config['THEME'], template)
    return render_template(template_path, **options)

@admin.route('/static/<path:filename>')
def static_files(filename):
    """Send static files such as style sheets, JavaScript, etc."""
    static_path = os.path.join(admin.root_path, 'templates', current_app.config['THEME'], 'static')
    return send_from_directory(static_path, filename)

@admin.route('/<album>/image/<filename>/<int:size>/')
def show_image(album, filename, size=None):
    return image_retrieve(album, filename, size)

@admin.route('/<album>/image/<filename>/full/')
def show_image_full(album, filename):
    return image_retrieve(album, filename)

@admin.route('/<album>/show/<filename>')
def image_page(album, filename):
    show = Show(album)
    exif_array = get_exif(album, filename)
    return render_themed('image.html', album=album, filename=filename,
                           exif=exif_array, show=show)

@admin.route('/<album>/rotate_exif/')
def rotate_url():
    # dummy
    pass

@admin.route('/<album>/list/<template>/<int:page>/')
@admin.route('/<album>/list/<int:page>/')
def list(album, page, template='grid'):
    show = Show(album)
    ext = re.compile(".jpg$", re.IGNORECASE)

    all_files = os.listdir(os.path.join(current_app.config['ALBUMS_DIR'], album))
    all_files = filter(ext.search, all_files)
    all_files.sort()

    p = _paginated_overview(album, page, 'admin.list', template)
    return render_themed(template + '.html', album=album,
                         show=show, files=p.entries, paginator=p, page=page,
                         all_files=all_files)

@admin.route('/<album>/')
def show_album(album):
    return list(album, 1)

@admin.route('/')
def show_index():
    dir_list = os.listdir(current_app.config['ALBUMS_DIR'])
    album_list = [os.path.basename(album) for album in dir_list]
    album_list.sort(reverse=True)
    return render_themed('index.html', albums=album_list)

@admin.route('/<album>/rotate/<int:steps>/<filename>/')
def image_rotate(album, filename, steps=1):
    _image_rotate(album, filename, steps)
    return jsonify(result='OK')

@admin.route('/<album>/rotate_exif/<filename>/')
def exif_rotate_image(album, filename):
    image_rotate_exif(album, filename)
    return jsonify(result='OK')

@admin.route('/<album>/add_image_to_show/<filename>/')
def add_image_to_show(album, filename):
    """Add an image to the show"""
    show = Show(album)
    if show.add_image(filename):
        return jsonify(result='OK')
    return jsonify(result='Failed')

@admin.route('/<album>/remove_image_from_show/<filename>/')
def remove_image_from_show(album, filename):
    """Remove an image from the show"""
    show = Show(album)
    if show.remove_image(filename):
        return jsonify(result='OK')
    return jsonify(result='Failed')

@admin.route('/<album>/sort_by_exifdate/')
def sort_show_by_exifdate(album):
    """Sort the show by exif datetime """
    show = Show(album)
    show.sort_by_exif_datetime()
    return redirect(request.referrer or url_for('.index'))

@admin.route('/<album>/edit_users/')
def show_edit_users(album):
    show = Show(album)
    users = show.data['users']
    return render_themed('edit_users.html', album=album, show=show, users=users)

@admin.route('/<album>/add_all/')
def add_all_images_to_show(album):
    show = Show(album)
    show.add_all_images()
    return redirect(request.referrer or url_for('.index'))

@admin.route('/<album>/set/<setting>/<value>/')
def show_change_setting(album, setting, value):
    show = Show(album)
    if (show.change_setting(setting, value) and show.save()):
        return jsonify(result='OK')
    else:
        return jsonify(result='Failed')

@admin.route('/<album>/change_password/', methods=['POST'])
def show_change_password(album):
    if request.method == 'POST':
        show = Show(album)
        username = request.form['username']
        password = request.form['password']
        show.set_user(username, current_app.config['SECRET_KEY'], password)
        if (show.save()):
            return redirect(request.referrer or url_for('.index'))
        else:
            return jsonify(result='Failed')

@admin.route('/<album>/remove_user/<username>/')
def show_remove_user(album, username):
    show = Show(album)
    show.remove_user(username)
    if (show.save()):
        return redirect(request.referrer or url_for('.index'))
    else:
        return jsonify(result='Failed')

