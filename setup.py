import subprocess
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
    pass

setup(
    name =              'PyQual',
    version =           settings.VERSION,
    author =            'Mike Shultz',
    author_email =      'mike@mikeshultz.com',
    packages =          ['pyqual'],
    scripts =           ['bin/pqrun.py','bin/pqmessage.py','bin/pqweb.py'],
    url =               'http://github.com/mikeshultz/pyqual',
    license =           'LICENSE.txt',
    description =       'A python database QA app.',
    long_description =  open('README.rst').read(),
    install_requires =  open('requirements.txt').read().split('\n'),
    cmdclass =          commands,
)