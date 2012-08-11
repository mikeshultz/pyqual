import os, math, cherrypy, psycopg2
from psycopg2 import extras as pg_extras

from auth import Auth, LoginPage
from utils import DB, Updated, Inserted

import settings

""" Setup
"""
cherrypy.config.update(settings.CP_CONFIG)

""" Init
"""
auth = Auth(DB)
cherrypy.tools.is_authenticated = cherrypy.Tool("on_start_resource", auth.is_authenticated)

""" Views
"""
#@cherrypy.expose
@cherrypy.tools.json_out()
class Test:
    exposed = True
    def GET(self, test_id = None):
        """ Return JSON detail of a test
        """
        db = DB()
        cur = db.connect(settings.DSN)

        def multiple(self):
            """ Return JSON of tests in the DB
            """
            cur.execute("""SELECT
                                test_id, 
                                t.name, 
                                lastrun, 
                                schedule_id, 
                                s.name AS schedule_name, 
                                database_id,
                                d.name AS database_name
                                FROM pq_test t
                                LEFT JOIN pq_schedule s USING (schedule_id)
                                LEFT JOIN pq_database d USING (database_id)
                                ORDER BY lastrun, test_id;""")

            tests = []
            for test in cur.fetchall():
                try:
                    lastrun = test['lastrun'].isoformat()
                except AttributeError:
                    lastrun = None
                t = {
                    'test_id':          test['test_id'],
                    'name':             test['name'],
                    'lastrun':          lastrun,
                    'schedule_id':      test['schedule_id'],
                    'schedule_name':    test['schedule_name'],
                    'database_id':      test['database_id'],
                    'database_name':    test['database_name'],
                }
                tests.append(t)

            return tests

        def single(self):

            cur.execute("""SELECT
                                test_id, 
                                t.name, 
                                lastrun, 
                                schedule_id, 
                                database_id,
                                test_type_id,
                                sql,
                                python
                                FROM pq_test t
                                LEFT JOIN pq_schedule s USING (schedule_id)
                                LEFT JOIN pq_database d USING (database_id)
                                WHERE test_id = %s
                                ORDER BY lastrun;""", test_id)

            if cur.rowcount > 0:
                test = cur.fetchone()
                try:
                    lastrun = test['lastrun'].isoformat()
                except AttributeError:
                    lastrun = None
                t = {
                    'test_id':          test['test_id'],
                    'name':             test['name'],
                    'lastrun':          lastrun,
                    'schedule_id':      test['schedule_id'],
                    'database_id':      test['database_id'],
                    'test_type_id':     test['test_type_id'],
                    'sql':              test['sql'],
                    'python':           test['python']
                }
            else:
                raise cherrypy.HTTPError(404) 

            db.disconnect()
            return t

        if test_id:
            return single(self)
        else:
            return multiple(self)
            
    def POST(
        self, 
        test_id = None, 
        name = None, 
        schedule_id = None, 
        database_id = None, 
        test_type_id = None, 
        sql = None, 
        python = None):
        """ Insert/update a test
        """

        # do
        action = None
        db = DB()
        cur = db.connect(settings.DSN)

        #cur.execute("""SELECT TRUE AS exist FROM pq_test WHERE test_id = %s""" % test_id)
        #res = cur.fetchone()
        #if res['exist']:
        if test_id:
            cur.execute(
                """UPDATE pq_test 
                    SET 
                        name = %s,
                        schedule_id = %s,
                        database_id = %s,
                        test_type_id = %s,
                        sql = %s,
                        python = %s
                    WHERE test_id = %s;""", 
                    (name, schedule_id, database_id, test_type_id, sql, python, test_id)
            )
            action = Updated()
        else:
            cur.execute(
                """INSERT INTO pq_test (name, schedule_id, database_id, test_type_id, sql, python) VALUES (%s,%s,%s,%s,%s,%s);""",
                (name, schedule_id, database_id, test_type_id, sql, python)
            )
            action = Inserted()

        if cur.rowcount > 0:
            db.commit()
            db.disconnect()
            if type(action) == type(Updated()):
                return { 'result': 'success', 'message': 'Test updated successfully.'}
            elif type(action) == type(Inserted()):
                return { 'result': 'success', 'message': 'Test added successfully.'}
            else:
                return { 'result': 'failure', 'message': 'Something was successful?  Add/update reported successful, but we have no idea what happened.'}
        else:
            db.rollback()
            db.disconnect()
            return { 
                'result': 'failure',
                'message': 'Add/update failed.'
            }

    def DELETE(self, test_id):
        """ Delete a test """

        db = DB()
        cur = db.connect(settings.DSN)

        cur.execute("""DELETE FROM pq_test WHERE test_id = %s""", (test_id, ))
        if cur.rowcount == 1:
            db.commit()
            db.disconnect()
            return { 
                'result': 'success',
                'message': 'Test deleted successfully.',
            }
        elif cur.rowcount > 1:
            db.rollback()
            db.disconnect()
            return {
                'result': 'failure',
                'message': 'Delete failed.  Attempt was made to delete more than one record.'
            }
        else:
            db.rollback()
            db.disconnect()
            return { 
                'result': 'failed',
                'message': 'Test delete failed.',
            }

@cherrypy.tools.json_out()
class Database:
    exposed = True
    def GET(self, database_id = None):
        def multiple(self):
            """ Return JSON of known databases
            """
            db = DB()
            cur = db.connect(settings.DSN)
            cur.execute("SELECT database_id, name, username, password, port, hostname, active FROM pq_database ORDER BY name, hostname;")

            dbs = []
            for dbase in cur.fetchall():
                d = {
                    'database_id':  dbase['database_id'],
                    'name':         dbase['name'],
                    'username':     dbase['username'],
                    'password':     dbase['password'],
                    'port':         dbase['port'],
                    'hostname':     dbase['hostname'],
                    'active':       dbase['active'],
                }
                dbs.append(d)

            db.disconnect()

            return dbs

        def single(self, database_id):
            """ Return JSON of known databases
            """
            db = DB()
            cur = db.connect(settings.DSN)
            cur.execute("SELECT database_id, name, username, password, port, hostname, active FROM pq_database WHERE database_id = %s ORDER BY name, hostname;", (database_id, ))
            dbase = cur.fetchone()
            db.disconnect()

            return {
                'database_id':  dbase['database_id'],
                'name':         dbase['name'],
                'username':     dbase['username'],
                'password':     dbase['password'],
                'port':         dbase['port'],
                'hostname':     dbase['hostname'],
                'active':       dbase['active'],
            }

        if database_id:
            return single(self, database_id)
        else:
            return multiple(self)

    def POST(
        self,
        name,
        username,
        password,
        hostname,
        database_id = None,
        port = 5432,
        active = True
    ):
         # do
        action = None
        db = DB()
        cur = db.connect(settings.DSN)

        if database_id:
            cur.execute(
                """UPDATE pq_database 
                    SET 
                        name = %s,
                        username = %s,
                        password = %s,
                        port = %s,
                        hostname = %s,
                        active = %s
                    WHERE database_id = %s;""", 
                    (name, username, password, port, hostname, active, database_id)
            )
            action = Updated()
        else:
            cur.execute(
                """INSERT INTO pq_database (name, username, password, port, hostname, active) VALUES (%s,%s,%s,%s,%s,%s);""",
                (name, username, password, port, hostname, active)
            )
            action = Inserted()

        if cur.rowcount > 0:
            db.commit()
            db.disconnect()
            if type(action) == type(Updated()):
                return { 'result': 'success', 'message': 'Database updated successfully.'}
            elif type(action) == type(Inserted()):
                return { 'result': 'success', 'message': 'Database added successfully.'}
            else:
                return { 'result': 'failure', 'message': 'Something was successful?  Add/update reported successful, but we have no idea what happened.'}
        else:
            db.rollback()
            db.disconnect()
            return { 
                'result': 'failure',
                'message': 'Add/update failed.'
            }

    def DELETE(self, database_id):
        """ Delete a database entry """

        db = DB()
        cur = db.connect(settings.DSN)

        cur.execute("""DELETE FROM pq_database WHERE database_id = %s""", (database_id, ))
        if cur.rowcount > 0:
            db.commit()
            db.disconnect()
            return { 
                'result': 'success',
                'message': 'Database deleted successfully.',
            }
        elif cur.rowcount > 1:
            db.rollback()
            db.disconnect()
            return {
                'result': 'failure',
                'message': 'Delete failed.  Attempt was made to delete more than one record.'
            }
        else:
            db.rollback()
            db.disconnect()
            return { 
                'result': 'failed',
                'message': 'Database delete failed.',
            }

@cherrypy.tools.json_out()
class UserCheck:
    exposed = True
    def GET(self, username):
        """ Check if a username is unique/unused
        """
        db = DB()
        cur = db.connect(settings.DSN)
        cur.execute("SELECT true FROM pq_user WHERE username = %s", (username, ))
        if cur.rowcount > 0:
            return { 'available': False, }
        else:
            return { 'available': True, }

@cherrypy.tools.json_out()
class User:
    exposed = True
    def GET(self, user_id = None):
        """ Return JSON of users
        """
        def multiple(self):
            db = DB()
            cur = db.connect(settings.DSN)
            cur.execute("SELECT user_id, username, email FROM pq_user ORDER BY username;")

            users = []
            for user in cur.fetchall():
                u = {
                    'user_id':      user['user_id'],
                    'username':     user['username'],
                    'email':        user['email']
                }
                users.append(u)

            db.disconnect()

            return users

        def single(self, user_id):
            db = DB()
            cur = db.connect(settings.DSN)
            cur.execute("SELECT user_id, username, email FROM pq_user WHERE user_id = %s ORDER BY username;", (user_id, ))
            user = cur.fetchone()
            db.disconnect()

            return {
                'user_id':      user['user_id'],
                'username':     user['username'],
                'email':        user['email']
            }

        if user_id:
            return single(self, user_id)
        else:
            return multiple(self)

    def POST(
        self,
        username,
        password,
        email,
        user_id = None
    ):
         # do
        action = None
        db = DB()
        cur = db.connect(settings.DSN)

        if user_id:
            cur.execute(
                """UPDATE pq_user 
                    SET 
                        username = %s,
                        password = %s,
                        email = %s
                    WHERE user_id = %s;""", 
                    (username, password, email, user_id)
            )
            action = Updated()
        else:
            cur.execute(
                """INSERT INTO pq_user (username, password, email) VALUES (%s,%s,%s);""",
                (username, password, email)
            )
            action = Inserted()

        if cur.rowcount > 0:
            db.commit()
            db.disconnect()
            if type(action) == type(Updated()):
                return { 'result': 'success', 'message': 'User updated successfully.'}
            elif type(action) == type(Inserted()):
                return { 'result': 'success', 'message': 'User added successfully.'}
            else:
                return { 'result': 'failure', 'message': 'Something was successful?  Add/update reported successful, but we have no idea what happened.'}
        else:
            db.rollback()
            db.disconnect()
            return { 
                'result': 'failure',
                'message': 'Add/update failed.'
            }

    def DELETE(self, user_id):
        """ Delete a user """

        db = DB()
        cur = db.connect(settings.DSN)

        cur.execute("""DELETE FROM pq_user WHERE user_id = %s""", (user_id, ))
        if cur.rowcount > 0:
            db.commit()
            db.disconnect()
            return { 
                'result': 'success',
                'message': 'User deleted successfully.',
            }
        elif cur.rowcount > 1:
            db.rollback()
            db.disconnect()
            return {
                'result': 'failure',
                'message': 'Delete failed.  Attempt was made to delete more than one record.'
            }
        else:
            db.rollback()
            db.disconnect()
            return { 
                'result': 'failed',
                'message': 'User delete failed.',
            }

@cherrypy.tools.json_out()
class TestType:
    exposed = True
    def GET(self):
        """ Return JSON of test types
        """
        db = DB()
        cur = db.connect(settings.DSN)
        cur.execute("SELECT test_type_id, name FROM pq_test_type ORDER BY name;")

        types = []
        for type in cur.fetchall():
            t = {
                'test_type_id':     type['test_type_id'],
                'name':             type['name']
            }
            types.append(t)

        db.disconnect()

        return types

@cherrypy.tools.json_out()
class Schedule:
    exposed = True
    def GET(self):
        """ Return JSON of schedules
        """
        db = DB()
        cur = db.connect(settings.DSN)
        cur.execute("SELECT schedule_id, name FROM pq_schedule ORDER BY name;")

        schedules = []
        for schedule in cur.fetchall():
            s = {
                'schedule_id':      schedule['schedule_id'],
                'name':             schedule['name']
            }
            schedules.append(s)

        db.disconnect()

        return schedules

@cherrypy.tools.json_out()
class Log:
    exposed = True
    def GET(self, page = None, total = 100):
        """ Return JSON of logs
        """
        db = DB()
        cur = db.connect(settings.DSN)
        cur.execute("SELECT count(log_id) FROM pq_log;")
        row = cur.fetchone()
        log_count = row[0]
        pages = math.ceil(log_count / int(total))
        pages = int(math.ceil(float(log_count) / float(total)))
        try:
            offset = (int(page) * int(total)) - int(total)
        except TypeError:
            offset = 0
        cur.execute("""SELECT 
                            log_id, 
                            lt.log_type_id,
                            lt.name AS log_type, 
                            test_id, 
                            t.name AS test_name, 
                            message, 
                            stamp, 
                            notify 
                        FROM 
                            pq_log l 
                            JOIN pq_log_type lt USING (log_type_id) 
                            JOIN pq_test t USING (test_id)
                        ORDER BY stamp DESC 
                        LIMIT %s OFFSET %s""", (total, offset, ))
        
        results = {
            'meta': {
                'totalLogs': log_count,
                'pages': pages,
            },
            'logs': [],
        }
        
        for log in cur.fetchall():
            l = {
                'log_id': log['log_id'],
                'log_type': log['log_type'],
                'log_type_id': log['log_type_id'],
                'test_id': log['test_id'],
                'test_name': log['test_name'],
                'message': log['message'],
                'stamp': log['stamp'].isoformat(),
                'notify': log['notify'],
            }
            results['logs'].append(l)

        db.disconnect()

        return results

class JSON(object): 
    def GET(self):
        raise HTTPError(404)

class Static(object):
    def GET(self):
        return ''

class Index(object):
    exposed = True
    @cherrypy.tools.is_authenticated()
    def GET(self):
        """ Main page
        """
        f = open(settings.APP_ROOT + '/templates/main.html')
        return f.read()

class Pyqual:
    exposed = True
    pyqual = Index()
    j = JSON()
    j.test = Test()
    j.database = Database()
    j.test_type = TestType()
    j.schedule = Schedule()
    j.user = User()
    j.check_user = UserCheck()
    j.log = Log()
    login = LoginPage(auth)

    def GET(self):
        raise cherrypy.HTTPRedirect('/pyqual')



cherrypy.quickstart(Pyqual(), '', settings.CP_CONFIG)