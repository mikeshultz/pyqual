""" Here we'll run all the tests """
import re, psycopg2
import settings
from utils import DB

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
        self.compiledCode = compile(self._codeString, 'script', 'exec')
    def getCode(self):
        return self._codeString
    code = property(getCode, setCode)

    def run(self, variables = { 'result': None, }):
        exec self.compiledCode in variables
        self.result = variables['result']

""" Meat
"""
if __name__ == '__main__':
    db = DB()
    cur = db.connect(settings.DSN)
    testDb = DB()
    testCur = testDb.connect(settings.DSN)

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

    for test in cur.fetchall():
        # update lastrun
        cur.execute("""UPDATE pq_test SET lastrun = now() WHERE test_id = %s""", (test['test_id'], ))
        try:
            testCur.execute(test['sql'])
        except psycopg2.ProgrammingError, e:
            message = 'Test failed due to an SQL error: %s' % e.pgerror
            cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message) VALUES (3,%s,%s);""", (test['test_id'], message, ) )
        
        if test['test_type_id'] == 1: # SQL only
            for row in testCur.fetchall():
                if row[0] != True:
                    cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message) VALUES (1,%s,'Test failed!');""", (test['test_id'], ) )
        else:
            if testCur.rowcount > 0:
                data = testCur.fetchall()
            else:
                data = None
            try:
                t = TestPythonWrapper(test['test_id'])
                t.code = test['python']
                t.run({ 'data': data, })
            except RunDenied, e:
                cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message) VALUES (3,%s,'Test not run for security reasons.');""", (test['test_id'], ) )
            except:
                cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message) VALUES (3,%s,'Test failed for unknown reasons. Check for previous error.');""", (test['test_id'], ) )
            finally:
                if t.result != True:
                    cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message) VALUES (1,%s,'Test failed!');""", (test['test_id'], ) )
                if t.logs:
                    for l in t.logs:
                        cur.execute("""INSERT INTO pq_log (log_type_id, test_id, message) VALUES (%s,%s,%s);""", (l[0], test['test_id'], l[1]))

            db.commit()

    testDb.disconnect()
    db.disconnect()