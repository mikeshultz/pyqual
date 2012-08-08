=====================================================
 Pyqual - A python database quality assurance app
=====================================================
:Info: See <http://wiki.mikeshultz.com/Pyqual> for basic info.
:Author: Mike Shultz <mike@mikeshultz.com>
:Date: $Date: 2012-08-07 21:33:00 -0700 (Tue, 7 Aug 2012) $
:Revision: $Revision: 0 $
:Description: A python database QA app
:License: MIT License <http://opensource.org/licenses/MIT>
:Copyright: Copyright 2012 Mike Shultz

Setup
=====================================================
To set up pyqual, follow these simple steps:

1) Install dependencies using PIP by running ``pip install -r requirements.txt``
2) Edit settings.py to set your database settings
3) To populate your database with base data and structure, run the SQL in setup/base_data.sql
4) Try out the web interface by running ``python pyqual/web.py``.  The first uer added to the DB has a username of 'admin' and a password of 'pyqual'.

You should be all set from here!

Running Tests
=====================================================
To run the tests, pyqual/run_tests.py should be run.  For a permanent solution, adding it to your crontab would be best, but it can be run manually whenever you need it instead.  All output(unless there's an unexpected error) should be logged into the pq_log table in your database.

E-mail Notifications
=====================================================
Coming soon.

TODO
=====================================================
+ Add log listing to Web interface.
+ Add stdout log messages to run_tests.py along with a log file option
