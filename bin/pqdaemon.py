#!/usr/bin/python
""" Daemon to run all parts of pyqual.  """

import time, os

from pyqual import runner
import pqweb, pqrun, pqmessage

__author__ = "Mike Shultz"
__copyright__ = "Copyright 2016, Mike Shultz"
__credits__ = ["Mike Shultz"]
__license__ = "MIT"
__version__ = "2.0.0"
__maintainer__ = "Mike Shultz"
__email__ = "mike@mikeshultz.com"
__status__ = "Production"

pid = os.fork()
print('fork #%s' % pid)
children = 0

class PqWebDaemon:
    def __init__(self):
        """ Run pqweb """
        self.stdin_path = '/dev/null'
        self.stdout_path = '/var/log/pqweb.log'
        self.stderr_path = '/var/log/pqweb_error.log'
        self.pidfile_path =  '/var/run/pyqual/pqweb.pid'
        self.pidfile_timeout = 5
    def run(self):
        pqweb.main() 

class MainDaemon:
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/var/log/pyqual.log'
        self.stderr_path = '/var/log/pyqual_error.log'
        self.pidfile_path =  '/var/run/pyqual/pyqual.pid'
        self.pidfile_timeout = 5

        self.web_pid = None
        self.web_children = 0

    def run(self):
        while True:
            #print("Running pqrun and pqmessage.")
            pqrun.main()
            pqmessage.main()
            time.sleep(60 * 5)


if pid == 0 and children <= 1:
    """ Second fork for the main app processes """

    app = MainDaemon()
    run = runner.DaemonRunner(app)
    run.do_action()
    #with daemon.DaemonContext(
    #        files_preserve=[app.stdout_path, app.stdin_path, app.pidfile_path],
    #        pidfile=app.pidfile_path,
    #        stdout=app.stdout_path,
    #        stderr=app.stderr_path,
    #        ):
    #    app.run()
    
elif children > 1:
    """ Just in case, we don't want any more forks """

    os._exit(0)

else:
    """ First for the Web interface """

    web = PqWebDaemon()
    run = runner.DaemonRunner(web)
    run.do_action()
    #with daemon.DaemonContext(
    #        files_preserve=[web.stdout_path, web.stdin_path, web.pidfile_path],
    #        pidfile=web.pidfile_path,
    #        stdout=web.stdout_path,
    #        stderr=web.stderr_path,
    #        ):
    #    web.run()

    os._exit(0)