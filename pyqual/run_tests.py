""" Here we'll run all the tests """
import sys, argparse, re, psycopg2, pickle
import settings
from utils import DB
from test_header import test_header

""" Helpers
"""
class RunDenied(Exception): pass

class TestPythonWrapper(object):
    def __init__(self, test_id, codeString = None):
        self._codeString = ''
        if codeString:
            self.setCode(codeString)
        self.compiledCode = None
        self.linesRemoved = 0
        self.result = None
        self.resultData = None
        self.logs = []
        self.test_id = test_id
    def _cleanCode(self, string = None):
        if string:
            self.setCode(string)

        self.removeLines = [
            re.compile('[^\s]*(from\s+)*import\s+'),    # no importing allowed
            re.compile('^[\s]*print[\(\s]+'),           # no stdout
        ]
        self.stopScript = [
            re.compile('\s*exec(file)*[\(\s]+'),    # no use of exec allowed
            re.compile('file\s*\('),                # file()
            re.compile('open\s*\('),                # file()
        ]
        listScript = self._codeString.splitlines()
        i = 0
        for line in listScript:
            for r in self.removeLines:
                if r.search(line):
                    self.linesRemoved += 1
                    del listScript[i]
                    self.logs.append((2, 'Line %s was deleted from python for test(%s) for security reasons.' % (i, self.test_id)))
            for s in self.stopScript:
                if s.search(line):
                    raise RunDenied()
            i += 1
        self._codeString = '\n'.join(listScript)
    
    def setCode(self, string):
        self._codeString = string
        self._cleanCode()
        self.compiledCode = compile(test_header + self._codeString, 'script', 'exec')
    def getCode(self):
        return self._codeString
    code = property(getCode, setCode)

    def run(self, variables = { 'result': None, }):
        exec self.compiledCode in variables
        self.result = variables['result']
        self.resultData = variables['resultData']

""" Meat
"""
if __name__ == '__main__':
    """ Handle cli arguments """
    parser = argparse.ArgumentParser(description='Run pyqual tests logging results to the DB.')
    parser.add_argument(
        '-d', '--debug', 
        action='store_true',
        default=False,
        help='Output debug statements to stdout'
    )
    args = parser.parse_args()

    db = DB()
    cur = db.connect(settings.DSN)

    """  schedule_id |  name   
        -------------+---------
                   1 | Hourly
                   2 | Daily
                   3 | Weekly
                   4 | Monthly
    """
    cur.execute("""SELECT 
                    test_id, 
                    test.name,
                    sql,
                    python,
                    test_type_id,
                    database_id,
                    db.name AS database_name,
                    db.username AS database_username,
                    db.password AS database_password,
                    db.port AS database_port,
                    db.hostname AS database_hostname
                    FROM
                        pq_test test
                        JOIN pq_database db USING (database_id)
                    WHERE
                        db.active IS TRUE
                        AND CASE WHEN lastrun IS NOT NULL THEN
                            CASE schedule_id
                                WHEN 1 THEN INTERVAL '1 hour' <= now() - lastrun
                                WHEN 2 THEN INTERVAL '1 day' <= now() - lastrun
                                WHEN 3 THEN INTERVAL '1 week' <= now() - lastrun
                                WHEN 4 THEN INTERVAL '1 month' <= now() - lastrun
                                ELSE FALSE
                            END
                        ELSE TRUE
                        END
                    ORDER BY db.database_id""")

    if cur.rowcount == 0:
        if args.debug:
            print 'Debug: No tests to run at this time.'
    for test in cur.fetchall():
        if args.debug:
            print 'Debug: Running test #%s' % test.get('test_id')
        testCur = None
        try:
            if args.debug:
                print 'Debug: Connecting to target DB %s on %s' % (test.get('database_name'), test.get('database_hostname'))
            # connect to target DB 
            testDSN = "dbname=%s user=%s password=%s port=%s host=%s" % (
                test['database_name'], 
                test['database_username'], 
                test['database_password'], 
                test['database_port'] or 5432, 
                test['database_hostname']
            )
            testDb = DB()
            testCur = testDb.connect(testDSN)
            if args.debug:
                print 'Debug: Connection successful'
        except psycopg2.OperationalError, e:
            if args.debug:
                print 'Debug: Connection failed!'
            errMessage = e.pgerror or e or 'Unknown Error'
            message = 'Test failed due to an SQL or connection error: %s' % errMessage
            cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message) VALUES (3,%s,%s);""", (test['test_id'], message, ) )
            db.commit()

        if testCur:
            # update lastrun
            cur.execute("""UPDATE pq_test SET lastrun = now() WHERE test_id = %s""", (test['test_id'], ))
            try:
                if args.debug:
                    print 'Debug: Running test query'
                testCur.execute(test['sql'])
            except psycopg2.ProgrammingError, e:
                if args.debug:
                    print 'Debug: Query failed due to an SQL error.'
                message = 'Test failed due to an SQL error: %s' % e.pgerror
                cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message) VALUES (3,%s,%s);""", (test['test_id'], message, ) )
                db.commit()

            if testCur.rowcount > 0:
                if test['test_type_id'] == 1: # SQL only
                    if args.debug:
                        print 'Debug: Test is SQL only'
                    if testCur.rowcount == 1:
                        row = testCur.fetchone()
                        if row[0] != True:
                            if args.debug:
                                print 'Debug: Test failed! (170)'
                            cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message) VALUES (1,%s,'Test failed!');""", (test['test_id'], ) )
                            db.commit()
                        else:
                            if args.debug:
                                print 'Debug: Test passed'
                            cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message) VALUES (1,%s,'Test passed!');""", (test['test_id'], ))
                            db.commit()
                    else:
                        if args.debug:
                            print 'Debug: Test failed because the query returned multiple rows'
                        cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message) VALUES (1,%s,'Test failed! The query returned more than one row.');""", (test['test_id'], ) )
                        db.commit()
                elif test['test_type_id'] == 2: # + python
                    if args.debug:
                        print 'Debug: Test is SQL+Python'
                    data = testCur.fetchall()
                    try:
                        if args.debug:
                            print 'Debug: Initializing python test'
                        t = TestPythonWrapper(test['test_id'])
                        if args.debug:
                            print 'Debug: Setting python test code'
                        t.code = test['python']
                        if args.debug:
                            print 'Debug: Running python test'
                        t.run({ 'data': data, })
                    except RunDenied, e:
                        if args.debug:
                            print 'Debug: Python test not run for security reasons'
                        cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message) VALUES (3,%s,'Test not run for security reasons.');""", (test['test_id'], ) )
                        db.commit()
                    except Exception as e:
                        message = 'Python test failed to run for uknown reason. Check for previous error: %s: %s' % (type(e), e.args)
                        if args.debug:
                            print 'Debug: %s' % message
                        cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message) VALUES (3,%s,%s);""", (test['test_id'], message, ) )
                        db.commit()
                    finally:
                        if t.result == True:
                            if args.debug:
                                print 'Debug: Test passed'
                            cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message, result_data) VALUES (1,%s,'Test passed!',%s);""", (test['test_id'], pickle.dumps(t.resultData) ) )
                            db.commit()
                        else:
                            if args.debug:
                                print 'Debug: Test failed! (208)'
                            cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message, result_data) VALUES (1,%s,'Test failed!',%s);""", (test['test_id'], pickle.dumps(t.resultData) ) )
                            db.commit()
                        if t.logs:
                            for l in t.logs:
                                print 'data! ',
                                print t.resultData
                                cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message, result_data) VALUES (%s,%s,%s,%s);""", (l[0], test['test_id'], l[1], pickle.dumps(t.resultData)))
                else:
                    if args.debug:
                        print "Debug: Unknown test type. Don't know what to do"
                    cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message) VALUES (3,%s,'Test failed because it's an unknown test type.);""", (test['test_id'], ) )
                    db.commit()
            else:
                if args.debug:
                    print 'Debug: Nothing returned by the query'
                cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message) VALUES (1,%s,'Test failed! Nothing was returned by the query.');""", (test['test_id'], ) )
                db.commit()

            testDb.disconnect()
        else:
            if args.debug:
                print 'Debug: No database cursor to deal with!'
    db.disconnect()