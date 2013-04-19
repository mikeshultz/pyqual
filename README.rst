================================================================================
 Pyqual - A python database quality assurance app
================================================================================
:Info: See <http://wiki.mikeshultz.com/Pyqual> for basic info.
:Author: Mike Shultz <mike@mikeshultz.com>
:Date: $Date: 2012-09-02 18:28:00 -0700 (Sun, 02 Sep 2012) $
:Revision: $Revision: 1.0 $
:Description: A python database QA app
:License: MIT License <http://opensource.org/licenses/MIT>
:Copyright: Copyright 2012 Mike Shultz

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

Requirements
================================================================================
- Python 2.7
- distutils or setuptools if using setup.py

Python Dependencies
-------------------
See requirements.txt

Setup
================================================================================

Using setup.py
--------------
1) Install requirements ``sudo pip install -r requirements.txt``
2) Run ``sudo python setup.py install``
3) Get the base data into your database with ``python setup.py basedata --name=[dbname] --user=[username]``
4) Edit site-packages/pyqual/settings.py to set your database settings
5) Run the Pyqual daemon with ``pqdaemon.py start``
6) Try the web interface, which is default at http://localhost:8081/ and the first user added to the DB has a username of 'admin' and a password of 'pyqual'.

Using pip
---------
1) Run ``pip install -e .`` in the pyqual directory
2) Get the base data into the database with ``psql -f setup/base_data.sql [dbname]``
3) Edit settings.py to configure your DB connection settings
4) Run the Pyqual daemon with ``pqdaemon.py start``
5) Try the web interface, which is default at http://localhost:8081/ and the first user added to the DB has a username of 'admin' and a password of 'pyqual'.

Manual Installation
-------------------
To set up pyqual, follow these simple steps:

1) Install dependencies using PIP by running ``pip install -r requirements.txt``
2) Edit pyqual/settings.py to set your database settings
3) To populate your database with base data and structure, run the SQL in setup/base_data.sql
4) Run the Pyqual daemon with ``pqdaemon.py start``
5) Try the web interface, which is default at http://localhost:8081/ and the first user added to the DB has a username of 'admin' and a password of 'pyqual'.

You should be all set from here!

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

TODO
================================================================================
n/t

Problems or Questions
================================================================================
If you have problems or want to report a bug, please use the Github issue 
tracker at https://github.com/mikeshultz/pyqual/issues

If you have any questions, feel free to E-mail me at the address listed at the 
top of this README.
