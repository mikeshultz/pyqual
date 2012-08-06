import os, cherrypy

DB_HOST = 'localhost'
DB_NAME = 'pyqual'
DB_USER = 'mike'
DB_PASS = ''
DB_PORT = 5432
DSN = "dbname=%s user=%s password=%s port=%s host=%s" % (DB_NAME, DB_USER, DB_PASS, DB_PORT, DB_HOST)

SALT = ''

APP_ROOT = os.path.dirname(os.path.realpath(__file__))

# Config for CherryPy
CP_CONFIG = {
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(APP_ROOT, 'static'),
    },
}
