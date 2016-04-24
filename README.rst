================================================================================
 Pyqual - A python database quality assurance app
================================================================================
:Info: See <http://github.com/mikeshultz/pyqual> for basic info.
:Author: Mike Shultz <mike@mikeshultz.com>
:Date: $Date: 2016-04-23 14:20:00 -0700 (Sat, 32 Apr 2016) $
:Revision: $Revision: 2.0.0 $
:Description: A python database QA app
:License: MIT License <http://opensource.org/licenses/MIT>
:Copyright: Copyright 2016 Mike Shultz

.. image:: http://www.quantifiedcode.com/api/v1/project/f9240e0e06db42a09eb4c47f8785d04e/badge.svg
   :target: http://www.quantifiedcode.com/app/project/f9240e0e06db42a09eb4c47f8785d04e
   :alt: QC Code Review

Introduction
================================================================================
Pyqual is a data quality assurance(QA) application. Its intention is to provide
a system in which users can setup tests to run against a PostgreSQL database.
Tests generally are for checking to make sure your data is sane and to key you
into problems that need to be fixed.

For instance, a sample test that comes with the base data for pyqual checks to 
make sure there is at least one superuser setup.  If there is not one, there 
would be a problem and it would make pyqual unusable.  This then will notify the
test owner of the problem so it can be fixed.

Pyqual provides the ability to run simple TRUE/FALSE SQL tests, as well as more 
complex tests that can use Python to do more complex checks with the data 
returned by the test query.  You can also store data from the test for later 
use.  For instance, you could have the test return the result of all Pyqual 
users for later use.

Python Dependencies
-------------------
See requirements.txt

Setup
================================================================================

1) Run ``sudo python setup.py install``
2) *Optionally* get the base data into your database with ``python setup.py basedata --name=[dbname] --user=[username]``
3) Create ``/etc/pyqual/pyqual.ini`` or ``~/.config/pyqual.ini`` with the configuration files outlined in Configuration_
4) Run the Pyqual daemon with ``pqdaemon.py start``
5) Try the web interface, which is default at http://localhost:8081/ and the first user added to the DB has a username of 'admin' and a password of 'pyqual'.

Configuration
================================================================================
Pyqual configuration is layed out in an ini format with each parameter inside sections.  All configuration options should be under the correct section.  The following is an example configuration with all available parameters.

Configuration should be stored in ``/etc/pyqual/pyqual.ini`` and/or ``~/.config/pyqualini``.  The latter takes precidence if it exists.

::

    [pyqual]
    ; password salt that should be set to a random string of characters
    salt = 95f6cdeac6b2121b61b0e5b208fc3466

    [database]
    ; hostname or IP of the database server
    host = localhost
    ; name of the database
    name = pyqual
    ; user to connect as
    user = pyqual
    ; password
    pass = 
    ; the TCP port we are connecting to
    port = 5432

    [email]
    ; whether or not to send E-mail notifications[on/off]
    notifications = on
    ; the address that will appear as the sender
    sender = pyqual@example.com
    ; the server we will be sending through/as
    smtp_host = 

    [web]
    ; IP address to bind the Web server too
    host = 127.0.0.1
    ; and it's TCP port
    port = 8081

    [tests]
    ; python modules that are okay to import in pyqual tests
    ; !! WARNING: Be cautious about what to allow as some modules such as os and sys
    ; may give access to the underlying OS
    import_whitelist = re,datetime

Building Tests
================================================================================
Pyqual currently has two types of tests.  SQL Only, and SQL+Python.  For 
SQL-only tests to pass, the query should return ``TRUE``.  If using Python, the 
variable ``results`` should be set to ``True``.

SQL Only Tests
--------------
An SQL test is the simplest and the purpose is to return TRUE from the query if 
everything is okay.

For instance, one of the sample tests that come with Pyqual checks to make sure
there is at least one test in the database.::

    SELECT TRUE FROM pq_test LIMIT 1;

This would simply be considered passed if at least one row is returned and is 
TRUE.

SQL + Python Tests
------------------

More complex tests can be made using Python to parse and play with the returned
data from the query.  One of the sample tests mentioned before checks to see if
there's at least one super user.::

    SELECT COUNT(user_id) AS count FROM pq_user JOIN pq_user_permission perm USING (user_id) WHERE permission_id = 3;

This test could be run as SQL only in this case, but for a demonstration of 
using Python, we check the count returned to make sure it's greater than 0.::

    if data[0]['count'] > 0:
        result = True

Storing Test Result Data
------------------------

Pyqual also allows you to store result data in the logs(and have it sent in 
notification E-mails).  So, for instance, if you wanted to be sent(or just store 
it in the log table) the list of all of the super users(if they exist), you can
store it in ``resultData`` in your Python test.::

    SELECT user_id, username FROM pq_user JOIN pq_user_permission perm USING (user_id) WHERE permission_id = 3;

::

    if len(data) > 0:
        result = True
        resultData['users'] = []
        for row in data:
            resultData['users'].append(row['username'])

Then the list will be stored in the log as the actual list of strings and be
E-mailed as a pretty printed string.

Problems or Questions
================================================================================
If you have problems or want to report a bug, please use the Github issue 
tracker at https://github.com/mikeshultz/pyqual/issues

If you have any questions, feel free to E-mail me at the address listed at the 
top of this README.
