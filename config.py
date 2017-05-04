from os import environ as env

DEBUG = True
TITLE = env.get('GALLERY_TITLE') 
FRONTEND_HOST = '0.0.0.0'
FRONTEND_PORT = 5050
FRONTEND_BASEURL = 'http://photo'
FRONTEND_PREFIX = '/gallery'
FRONTEND_FCGI_SOCKET = '/var/lib/showoff/frontend.sock'
ADMIN_HOST = '0.0.0.0'
ADMIN_PORT = 5051
ADMIN_BASEURL = 'http://photo'
ADMIN_PREFIX = '/admin'
ADMIN_FCGI_SOCKET = '/var/lib/showoff/admin.sock'
THUMBNAIL_SIZE = 400
GRID_SIZE = 200
ADMIN_THUMBNAIL_SIZE = 400
THUMBNAILS_PER_PAGE = 40
THUMBNAILS_PER_SMALL_LIST = 8
ADMIN_THUMBNAILS_PER_PAGE = 12
ADMIN_GRID_ITEMS_PER_PAGE = 50
FRONTEND_GRID_ITEMS_PER_PAGE = 50
IMAGE_SIZE = 800
ALLOWED_SIZES = [ 75, 200, 400, 500, 640, 800, 1024, 1600, 'full' ]
THEME = 'v2'
ADMIN_THEME = 'v2'
CACHE_DIR = '/var/lib/showoff/cache'
EDITS_DIR = '/var/lib/showoff/edits'
SHOWS_DIR = '/var/lib/showoff/shows'
ALBUMS_DIR = env.get('ALBUMS_DIR')
SECRET_KEY = env.get('SECRET_KEY')
FRONTEND_LIST_TEMPLATES = ['list', 'list_small', 'grid', 'galleria']

