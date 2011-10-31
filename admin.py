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

This is the admin application code for showoff.

"""
# }}}

# IMPORTS {{{
from flask import Flask, render_template, send_from_directory, abort, url_for, redirect, json, jsonify, request
from werkzeug import cached_property
from libshowoff import Show, Paginator, supported_exiftags, clear_cache, update_cache, update_exif, is_edited, get_edit_or_original, get_exif
from ExifTags import TAGS

import os, re, Image
# }}}

# APP INITIALIZATION {{{
app = Flask(__name__, static_path=None)
app.config.from_pyfile('config.py')
app.config.from_envvar('SHOWOFF_ADMIN_CONFIG', silent=True)
# }}}

# HELPER FUNCTIONS {{{

# get_route {{{
def get_route(function):
    """Return complete route based on configuration and routes"""
    return '/%s%s' % (app.config['ADMIN_PREFIX'],
                      app.config['ADMIN_ROUTES'][function])
# }}}

# themed {{{
def themed(template):
    """Return path to template in configured theme"""
    return os.path.join('admin', app.config['THEME'], template)
# }}}

# }}}

# TEMPLATE TAGS {{{

# get_exif_table {{{
@app.template_filter('exif_table')
def get_exif_table(exif):
    table = '<table>'
    for line in exif:
        table = table + '<tr><td>' + line.replace('|', '</td><td>') + '</td></tr>'
    table = table + '</table>'
    return table
# }}}

# }}}

# ADMIN VIEWS {{{

# static files {{{
@app.route(get_route('static_files'))
def static_files(filename):
    """Send static files such as style sheets, JavaScript, etc."""
    static_path = os.path.join(app.root_path, 'templates', 'admin',
                               app.config['THEME'], 'static')
    return send_from_directory(static_path, filename)
# }}}

# show_image {{{
@app.route(get_route('show_image'))
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
# }}}

# show_image_full {{{
@app.route(get_route('show_image_full'))
def show_image_full(album, filename):
    return show_image(album, filename)
# }}}

# image_page {{{
@app.route(get_route('image_page'))
def image_page(album, filename):
    show = Show(app, album)
    if len(show.data['files']) == 0:
        abort(404)
    exifdir = os.path.join(app.config['CACHE_DIR'], album, 'exif')
    f = open(os.path.join(exifdir, filename + '.exif'))
    exif_array = f.readlines()
    f.close()

    exif = get_exif(app, album, filename)

    return render_template(themed('image.html'), album=album, filename=filename, exif=exif_array, show=show, exif2=exif)
# }}}

@app.route(get_route('rotate_url'))
def rotate_url():
    # dummy
    pass

# list {{{
@app.route(get_route('list'))
def list(album, page):
    files = os.listdir(os.path.join(app.config['ALBUMS_DIR'], album))
    show = Show(app, album)

    # only list .jpg files
    ext = re.compile(".jpg$", re.IGNORECASE)
    files = filter(ext.search, files)

    files.sort()
    p = Paginator(album, files, app.config['ADMIN_THUMBNAILS_PER_PAGE'], page, 'list')
    return render_template(themed('list.html'), album=album, files=p.entries, paginator=p, show=show, all_files=files)
# }}}

# list_show {{{
@app.route(get_route('list_show'))
def list_show(album, page):
    show = Show(app, album)

    if len(show.data['files']) == 0:
        abort(404)

    p = Paginator(album, show.data['files'], app.config['ADMIN_THUMBNAILS_PER_PAGE'], page, 'list_show')
    return render_template(themed('list.html'), album=album, files=p.entries, paginator=p, show=show)
# }}}

# show_album {{{
@app.route(get_route('show_album'))
def show_album(album):
    """Render first page of album"""
    return grid(album)
# }}}

# show_index {{{
@app.route(get_route('index'))
def show_index():
    """Render frontpage"""
    dir_list = os.listdir(app.config['ALBUMS_DIR'])
    album_list = [ os.path.basename(album) for album in dir_list ]
    album_list.sort(reverse=True)
    return render_template(themed('index.html'), albums=album_list)
# }}}

def _rotate_image(album, filename, steps=1):
    if steps < 1:
        steps = 1
    if steps > 3:
        steps = 3

    imgfile = os.path.join(get_edit_or_original(app, album, filename), filename)
    img = Image.open(imgfile)
    img = img.rotate(steps * -90)
    efile = os.path.join(app.config['EDITS_DIR'], album, filename)
    if not os.path.exists(os.path.join(app.config['EDITS_DIR'], album)):
        os.mkdir(os.path.join(app.config['EDITS_DIR'], album))
    img.save(efile, "JPEG")
    for size in app.config['ALLOWED_SIZES']:
        if size != 'full':
            clear_cache(app, album, filename, size)

# rotate_image {{{
@app.route(get_route('rotate_image'))
def rotate_image(album, filename, steps=1):
    print album + " " + filename
    #return redirect(request.referrer or url_for('index'))
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
# }}}

# add_image_to_show {{{
@app.route(get_route('add_image_to_show'))
def add_image_to_show(album, filename):
    """Add an image to the show"""
    show = Show(app, album)
    if show.add_image(filename):
        return jsonify(result='OK')
    return jsonify(result='Failed')
# }}}

# remove_image_from_show {{{
@app.route(get_route('remove_image_from_show'))
def remove_image_from_show(album, filename):
    """Remove an image from the show"""
    show = Show(app, album)
    if show.remove_image(filename):
        return jsonify(result='OK')
    return jsonify(result='Failed')
# }}}

# sort_show_by_exifdate {{{
@app.route(get_route('sort_show_by_exifdate'))
def sort_show_by_exifdate(album):
    """Sort the show by exif datetime """
    show = Show(app, album)
    show.sort_by_exif_datetime()
    return redirect(request.referrer or url_for('index'))
# }}}

@app.route(get_route('grid'))
def grid(album, page=1):
    files = os.listdir(os.path.join(app.config['ALBUMS_DIR'], album))
    show = Show(app, album)
    ext = re.compile(".jpg$", re.IGNORECASE)
    files = filter(ext.search, files)

    files.sort()
    p = Paginator(album, files, app.config['ADMIN_GRID_ITEMS_PER_PAGE'], page, 'grid')
    return render_template(themed('grid.html'), album=album, files=p.entries,
                           paginator=p, show=show)

# add_all_images_to_show {{{
@app.route(get_route('add_all_images_to_show'))
def add_all_images_to_show(album):
    """Add all images in album to the show"""
    files = os.listdir(os.path.join(app.config['ALBUMS_DIR'], album))
    show = Show(app, album)

    # only list .jpg files
    ext = re.compile(".jpg$", re.IGNORECASE)
    files = filter(ext.search, files)
    files.sort()

    for filename in files:
        show.add_image(filename)

    return redirect(request.referrer or url_for('index'))
# }}}
# }}}

# MAIN RUN LOOP {{{
if __name__ == '__main__':
    app.run(host=app.config['ADMIN_HOST'], port=app.config['ADMIN_PORT'])
# }}}

