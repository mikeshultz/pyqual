import cherrypy, hashlib, json, functools
from datetime import datetime
from binascii import a2b_qp

import settings

class Auth:
    """ Authentication handling """
    def __init__(self, db):
        self.db = db()
        self.cur = self.db.connect(settings.DSN)
        self.session_id = -1
        self.user_id = -1
        self.username = ''
        self.password = ''

        self._startHash()
        self._authenticated = False

        self.check()

    def __del__(self):
        self.db.disconnect()

    def _startHash(self):
        self.hashObj = hashlib.sha256()
        if settings.SALT:
            self.hash.update(a2b_qp(settings.SALT))

    def _setCookie(self):
        cherrypy.response.cookie['session'] = self.session_id
        cherrypy.response.cookie['session']['expires'] = 7200 # 2 hours

    def _getCookie(self):
        sessionCookie = cherrypy.request.cookie.get('session')
        if sessionCookie:
            self.session_id = sessionCookie.value
        else:
            self.session_id = -1
        return self.session_id

    def check(self):
        if self._getCookie():

            self.cur.execute("""SELECT user_session_id, user_id FROM pq_user_session WHERE session_update + interval '2 hours' < now() AND user_session_id = %s;""", (self.session_id, ))
            if self.cur.rowcount > 0:
                session = self.cur.fetchone()
                self.cur.execute("""UPDATE pq_user_session SET session_update = now() WHERE session_id = %s""", (session['session_id'], ))
                self.db.commit()
                self._authenticated = True
                return True
            else:
                return False
        else:
            return False

    def hash(self, password):
        self.hashObj = hashlib.sha256()
        self.hashObj.update(a2b_qp(password))
        return self.hashObj.hexdigest()

    def login(self, username, password):
        hash = self.hash(password)
        self.cur.execute("""SELECT user_id FROM pq_user WHERE username = %s AND password = %s;""", (username, hash, ))
        if self.cur.rowcount > 0:
            res = self.cur.fetchone()
            self.user_id = res['user_id']
            self._authenticated = True

            # cleanup while we're here
            self.cur.execute("""DELETE FROM pq_user_session WHERE user_id = %s AND session_update + interval '2 hours' < now()""", (self.user_id, ))
            # Add the session
            self.cur.execute("""INSERT INTO pq_user_session (user_id, session_start) VALUES (%s, %s);""", (self.user_id, datetime.now(), ))
            self.db.commit()

    def is_authenticated(self, no_redirect = False, debug = False):
        if not self._authenticated:
            if no_redirect:
                raise cherrypy.HTTPError(401, "You must be logged in.")
            else:
                raise cherrypy.HTTPRedirect('/login')

class LoginPage:
    exposed = True
    def __init__(self, auth):
        self.auth = auth
    def GET(self):
        if self.auth._authenticated:
            raise cherrypy.HTTPRedirect('/')
        else:
            f = open(settings.APP_ROOT + '/templates/login.html')
            return f.read()
    def POST(self, username, password):
        self.auth.login(username, password)
        if self.auth._authenticated:
            self.auth._setCookie()
            if cherrypy.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                cherrypy.response.headers['Content-Type'] = 'application/json'
                return json.dumps({
                    'result': 'success',
                    'message': 'Logged in successfully!'
                })
            else:
                raise cherrypy.HTTPRedirect('/')
        else:
            if cherrypy.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                cherrypy.response.headers['Content-Type'] = 'application/json'
                return json.dumps({
                    'result': 'failure',
                    'message': 'Username or password is incorrect.'
                })
            else:
                raise cherrypy.HTTPRedirect('/login')
