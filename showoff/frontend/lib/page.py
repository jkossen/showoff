from flask import current_app, render_template, abort, session
from showoff.lib import Show, Paginator, get_exif
import os, re

def render_themed(template, **options):
    template_path = os.path.join(current_app.config['THEME'], template)
    return render_template(template_path, **options)

def get_paginator(album, page, endpoint, template):
    show = Show(album)

    if len(show.data['files']) == 0:
        abort(404)

    files = show.data['files']

    if show.get_setting('reverse') == 'yes':
        files.reverse()

    p = Paginator(album, files, current_app.config['THUMBNAILS_PER_PAGE'], page, endpoint, template)
    return p

