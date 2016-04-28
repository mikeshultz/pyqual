#!/usr/bin/python
""" Installer for pyqual """

import sys
# Check version first
if sys.version_info[0] != 3:
    sys.exit('Requires Python 3.4')
if sys.version_info[1] < 4:
    sys.exit('Requires Python 3.4')

import subprocess
try:
    from setuptools import setup
    from setuptools import Command
except:
    from distutils.core import setup
    from distutils.core import Command
from pyqual import settings

commands = {}

try:
    import psycopg2

    class BaseData(Command):
        description = "Install base data."
        user_options = [
            ('host=', 'h', "DB Host"),
            ('port=', 'o', "DB Port"),
            ('name=', 'n', "DB Name"),
            ('user=', 'u', "DB Username"),
            ('password=', 'p', "DB Password"),
        ]

        def initialize_options(self):
            self.host = 'localhost'
            self.port = 5432
            self.name = 'pyqual'
            self.user = 'pyqual'
            self.password = ''

        def finalize_options(self):
            pass

        def run(self):
            """Run base_data.sql using psql."""

            cmd = [
                "psql", 
                "--host=%s" % self.host,
                "--username=%s" % self.user,
                "--port=%s" % self.port,
                "--file=setup/base_data.sql",
                "--dbname=%s" % self.name
            ]
            #print cmd
            subprocess.call(cmd)

    commands['basedata'] = BaseData
except ImportError:
    print("Warning! To run basedata command, psycopg2 must be installed!")

""" TODO:
    - create necessay folders and files for the daemon.  For instance
      the PID location and log files.
      mkdir /var/run/pyqual
      touch /var/log/pyqal.log /var/log/pqweb.log
      touch /var/run/pyqual/pqweb.pid /var/run/pyqual/pyqual.pid
"""

setup(
    name =              'pyqual',
    version =           settings.VERSION,
    author =            'Mike Shultz',
    author_email =      'mike@mikeshultz.com',
    packages =          ['pyqual', 'config'],
    scripts =           ['bin/pqrun.py','bin/pqmessage.py','bin/pqweb.py','bin/pqdaemon.py'],
    url =               'http://github.com/mikeshultz/pyqual',
    license =           'LICENSE.txt',
    description =       'A python database QA app.',
    long_description =  open('README.rst').read(),
    install_requires =  open('requirements.txt').read().split('\n'),
    cmdclass =          commands,
    package_data={
        'pyqual':       [
            'templates/*.html', 
            'static/b/js/*',
            'static/b/fonts/*',
            'static/b/css/*',
            'static/css/codemirror.css',
            'static/css/pyqual.css',
            'static/css/font-awesome.css',
            'static/font/fontawesome-webfont.ttf',
            'static/font/fontawesome-webfont.woff',
            'static/font/fontawesome-webfont.svg',
            'static/font/fontawesome-webfont.eot',
            'static/img/*.png',
            'static/js/jquery.textarea.js',
            'static/js/jquery.validate.js',
            'static/js/jquery.validate.min.js',
            'static/js/additional-methods.js',
            'static/js/additional-methods.min.js',
            'static/js/jquery-2.2.3.min.js',
            'static/js/jquery.tablesorter.js',
            'static/js/codemirror.js',
            'static/js/codemirror/*.js',
            'static/js/pyqual.js',
            'static/ts/addons/pager/jquery.tablesorter.pager.js',
            'static/ts/addons/pager/jquery.tablesorter.pager.css',
            'static/ts/jquery.tablesorter.js',
            'static/ts/jquery.tablesorter.min.js',
            'static/ts/jquery.metadata.js',
        ],
        'config':       [
            'pyqual.ini',
        ]
    },
)