#!/usr/bin/python
import time, os
from daemonize import Daemonize

import pqweb, pqrun, pqmessage

pid = os.fork()
children = 0

class PqWebDaemon:
    def __init__(self):
        """ Run pqweb """
        self.stdin_path = '/dev/null'
        self.stdout_path = '/var/log/pqweb.log'
        self.stderr_path = '/var/log/pqweb.log'
        self.pidfile_path =  '/var/run/pyqual/pqweb.pid'
        self.pidfile_timeout = 5
    def run(self):
        pqweb.main() 

class MainDaemon():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/var/log/pyqual.log'
        self.stderr_path = '/var/log/pyqual.log'
        self.pidfile_path =  '/var/run/pyqual/pyqual.pid'
        self.pidfile_timeout = 5

        self.web_pid = None
        self.web_children = 0

    def run(self):
        while True:
            print("Running pqrun and pqmessage.")
            pqrun.main()
            pqmessage.main()
            time.sleep(60 * 5)


if pid == 0 and children <= 1:
    app = MainDaemon()
    daemon = Daemonize(app="pyqual", pid=app.pidfile_path, action=app.run)
    daemon.start()
elif children > 1:
    os._exit(0)
else:
    web = PqWebDaemon()
    daemon = Daemonize(app="pyqual-web", pid=web.pidfile_path, action=web.run)
    daemon.start()
    os._exit(0)