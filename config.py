DEBUG = True
TITLE = 'Photo albums'
VIEWER_HOST = '192.168.1.3'
VIEWER_PORT = 5050
VIEWER_BASEURL = 'http://showoff'
VIEWER_PREFIX = 'showoff/'
VIEWER_FCGI_SOCKET = '/var/lib/showoff/viewer.sock'
ADMIN_HOST = '192.168.1.3'
ADMIN_PORT = 5051
ADMIN_BASEURL = 'http://showoff'
ADMIN_PREFIX = 'showoff_admin/'
ADMIN_FCGI_SOCKET = '/var/lib/showoff/admin.sock'
THUMBNAIL_SIZE = 75
GRID_SIZE = 200
ADMIN_THUMBNAIL_SIZE = 400
THUMBNAILS_PER_PAGE = 12
THUMBNAILS_PER_SMALL_LIST = 8
ADMIN_THUMBNAILS_PER_PAGE = 12
ADMIN_GRID_ITEMS_PER_PAGE = 50
IMAGE_SIZE = 800
ALLOWED_SIZES = [ 75, 200, 400, 500, 640, 800, 1024, 1600, 'full' ]
THEME = 'default'
CACHE_DIR = '/home/jochem/showoff/data/cache'
EDITS_DIR = '/home/jochem/showoff/data/edits'
SHOWS_DIR = '/home/jochem/showoff/data/shows'
SECRET_KEY = 'CHANGE_THIS'

ALBUMS_DIR = '/home/jochem/Pictures/fotos'

# Routes to the view functions in the viewer
VIEWER_ROUTES = {
    'static_files': 'static_files/<path:filename>',
    'show_image': '<album>/image/<int:size>/<filename>',
    'show_image_full': '<album>/image/full/<filename>',
    'image_page': '<album>/show/<filename>.html',
    'list': '<album>/list/<int:page>.html',
    'grid': '<album>/grid/',
    'list_small': '<album>/list_small/<int:page>.html',
    'album': '<album>.html',
    'show_galleria': '<album>/galleria/<int:page>.html',
    'show_slideshow': '<album>/slideshow/<int:page>.html',
    'index': '',
    }

# Routes to the view functions in the viewer
ADMIN_ROUTES = {
    'static_files': 'static_files/<path:filename>',
    'show_image': '<album>/image/<filename>/<int:size>/',
    'show_image_full': '<album>/image/<filename>/full/',
    'image_page': '<album>/show/<filename>/',
    'grid': '<album>/grid/<int:page>/',
    'list': '<album>/list/<int:page>/',
    'list_show': '<album>/list_show/<int:page>/',
    'show_album': '<album>/',
    'rotate_url': '<album>/rotate_exif/',
    'exif_rotate_image': '<album>/rotate_exif/<filename>/',
    'rotate_image': '<album>/rotate/<int:steps>/<filename>/',
    'show_galleria': '<album>/galleria/<int:page>/',
    'add_image_to_show': '<album>/add_image_to_show/<filename>/',
    'remove_image_from_show': '<album>/remove_image_from_show/<filename>/',
    'add_all_images_to_show': '<album>/add_all/',
    'sort_show_by_exifdate': '<album>/sort_by_exifdate/',
    'index': '',
    }
