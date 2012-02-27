from flask import render_template, abort, session
from libshowoff import Show, Paginator, get_exif
import os, re

def image_info(app, album, filename, template='image.html'):
    show = Show(app, album)
    exifdir = os.path.join(app.config['CACHE_DIR'], album, 'exif')
    exif_array = get_exif(app, album, filename)

    return render_themed(app, template, album=album, filename=filename,
                         exif=exif_array, show=show)

def render_themed(app, template, **options):
    template_path = os.path.join(app.config['THEME'], template)
    return render_template(template_path, **options)

def get_nonpaginated_show(app, album, template):
    show = Show(app, album)

    if len(show.data['files']) == 0:
        abort(404)

    files = show.data['files']
    return render_themed(template + '.html', album=album, files=files)

def paginated_overview(app, album, show, page, files, endpoint, template):
    ext = re.compile(".jpg$", re.IGNORECASE)
    all_files = os.listdir(os.path.join(app.config['ALBUMS_DIR'], album))
    all_files = filter(ext.search, all_files)
    all_files.sort()

    p = Paginator(album, files, app.config['THUMBNAILS_PER_PAGE'], page, endpoint, template)
    return render_themed(app, template + '.html', album=album,
                         show=show, files=p.entries, paginator=p, page=page,
                         all_files=all_files)

def get_show(app, album, page, endpoint, template):
    show = Show(app, album)

    if len(show.data['files']) == 0:
        abort(404)

    files = show.data['files']
    return paginated_overview(app, album, show, page, files, endpoint, template)

def slideshow(app, album, page, endpoint, template='slideshow.html'):
    files = None
    show = Show(app, album)

    if len(show.data['files']) == 0:
        abort(404)

    ext = re.compile(".jpg$", re.IGNORECASE)
    files = filter(ext.search, show.data['files'])

    p = Paginator(album, files, app.config['THUMBNAILS_PER_PAGE'], page, endpoint, template)
    return render_themed(template, album=album, files=p.entries, paginator=p, page=page)


