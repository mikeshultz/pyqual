""" 
    WARNING

    All user configuration should be defined in the INI files 
    located at /etc/pyqual/pyqual.ini or ~/.config/pyqual.ini.

    Change any of the following at your own risk!
"""
import os, configparser
try:
    import cherrypy
    nocherry = False
except ImportError:
    nocherry = True

VERSION = '1.0.5'

config = configparser.ConfigParser()
config.read([
    'config/pyqual.ini',
    '/etc/pyqual/pyqual.ini',
    os.path.expanduser('~/.config/pyqual.ini')
])

# Control database connection settings
DSN = "dbname=%s user=%s password=%s port=%s host=%s" % (
    config['database']['name'],
    config['database']['user'],
    config['database']['pass'],
    config['database']['port'],
    config['database']['host']
)

# Web interface IP and port to bind to
WEB_HOST = config['web']['host']
WEB_PORT = config['web']['port']

# Password salt.  NOTE: If you lose this, all passwords will be lost!
SALT = config['pyqual']['salt']

# Should notification E-mails be sent out?
EMAIL_NOTIFY = config['email']['notifications']
EMAIL_SENDER = config['email']['sender']
EMAIL_SENDING_HOST = config['email']['smtp_host']

# Modules that you don't mind being imported by tests
# Be careful what you allow here, enabling modules like sys or os will 
# give test writers access to the whole operating system
IMPORT_WHITELIST = config['tests']['import_whitelist'].split(',')


### !!!
# Do not alter the below settings unless you know what you're doing!
### !!!
APP_ROOT = os.path.dirname(os.path.realpath(__file__))

# Config for CherryPy
if not nocherry:
    CP_CONFIG = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(APP_ROOT, 'static'),
        },
    }
