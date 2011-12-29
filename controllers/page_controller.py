from controller import Controller
from flask import render_template, abort, session
from libshowoff import Show, Paginator
import os, re

class PageController(Controller):
    def render_themed(self, template, **options):
        template_path = os.path.join(self.app.config['THEME'], template)
        return render_template(template_path, **options)

    def image_info(self, album, filename, template='image.html'):
        show = Show(self.app, album)
        exifdir = os.path.join(self.app.config['CACHE_DIR'], album, 'exif')
        f = open(os.path.join(exifdir, filename + '.exif'))
        exif_array = f.readlines()
        f.close()

        return self.render_themed(template, album=album, filename=filename,
                                  exif=exif_array, show=show)

    def paginated_overview(self, album, page, files, endpoint, template):
        ext = re.compile(".jpg$", re.IGNORECASE)
        all_files = os.listdir(os.path.join(self.app.config['ALBUMS_DIR'], album))
        all_files = filter(ext.search, all_files)
        all_files.sort()

        p = Paginator(album, files, self.app.config['THUMBNAILS_PER_PAGE'], page, endpoint, template)
        return self.render_themed(template + '.html', album=album,
                                  files=p.entries, paginator=p, page=page,
                                  all_files=all_files)

    def get_show(self, album, page, endpoint, template):
        show = Show(self.app, album)

        if len(show.data['files']) == 0:
            abort(404)

        files = show.data['files']
        return self.paginated_overview(album, page, files, endpoint, template)

    def get_nonpaginated_show(self, album, template):
        show = Show(self.app, album)

        if len(show.data['files']) == 0:
            abort(404)

        files = show.data['files']

        return self.render_themed(template + '.html', album=album, files=files)

    def slideshow(self, album, page, endpoint, template='slideshow.html'):
        files = None
        show = Show(self.app, album)

        if len(show.data['files']) == 0:
            abort(404)

        ext = re.compile(".jpg$", re.IGNORECASE)
        files = filter(ext.search, show.data['files'])

        p = Paginator(album, files, self.app.config['THUMBNAILS_PER_PAGE'], page, endpoint, template)
        return self.render_themed(template, album=album, files=p.entries, paginator=p, page=page)

    def index(self, template='index.html'):
        dir_list = os.listdir(self.app.config['ALBUMS_DIR'])
        full_album_list = [ os.path.basename(album) for album in dir_list ]
        shows = {}

        for album in full_album_list:
            show = Show(self.app, album)
            if show.is_enabled():
                shows[album] = show

        album_list = shows.keys()
        album_list.sort(reverse=True)

        return self.render_themed(template, albums=album_list, shows=shows)

