#!/usr/bin/python
import time, os
from daemon import runner

import pqweb, pqrun, pqmessage

pid = os.fork()
children = 0
print 'pid: %s' % pid
# TODO: add logging

class PqWebDaemon:
    def __init__(self):
        """ Run pqweb """
        self.stdin_path = '/dev/null'
        self.stdout_path = '/var/log/pqweb.log'
        self.stderr_path = '/var/log/pqweb.log'
        self.pidfile_path =  '/var/run/pqweb.pid'
        self.pidfile_timeout = 5
    def run(self):
        pqweb.main()

def run_web():
    """ Run the pqweb daemon """
    web = PqWebDaemon()
    web_daemon_runner = runner.DaemonRunner(web)
    web_daemon_runner.do_action()
    #pqweb.main()    

class MainDaemon():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/var/log/pyqual.log'
        self.stderr_path = '/var/log/pyqual.log'
        self.pidfile_path =  '/var/run/pyqual.pid'
        self.pidfile_timeout = 5

        self.web_pid = None
        self.web_children = 0

    def run(self):
        while True:
            print "Running pqrun and pqmessage."
            pqrun.main()
            pqmessage.main()
            time.sleep(60)

if pid == 0 and children <= 1:
    app = MainDaemon()
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.do_action()
elif children > 1:
    os._exit(0)
else:
    web = PqWebDaemon()
    web_daemon_runner = runner.DaemonRunner(web)
    web_daemon_runner.do_action()
    os._exit(0)