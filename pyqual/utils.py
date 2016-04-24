""" Various items we'll need later """

import re, psycopg2, dns.resolver, pickle
from psycopg2 import extras as pg_extras

__author__ = "Mike Shultz"
__copyright__ = "Copyright 2016, Mike Shultz"
__credits__ = ["Mike Shultz"]
__license__ = "MIT"
__version__ = "2.0.0"
__maintainer__ = "Mike Shultz"
__email__ = "mike@mikeshultz.com"
__status__ = "Production"

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

class Updated(object): pass
class Inserted(object): pass

def _cast_pickle(data, cur):
    if data is None: return None
    return pickle.loads(str(psycopg2.BINARY(data, cur)))

psycopg2.extensions.register_type(
    psycopg2.extensions.new_type(
        psycopg2.BINARY.values, 'BINARY-PICKLE', _cast_pickle
    )
)

class DB:
    """ Simple DB wrapper
    """
    def __init__(self, dsn = None):
        self.dsn = ''
        self.connection = None
        self.cursor = None

        if dsn:
            self.connect(dsn)

    def connect(self, dsn):
        """ Connect to a DB and return a cursor
        """
        self.connection = psycopg2.connect(dsn)
        self.cursor = self.connection.cursor(cursor_factory=pg_extras.DictCursor)
        return self.cursor

    def commit(self, *args, **kwargs):
        return self.connection.commit(*args, **kwargs)

    def rollback(self, *args, **kwargs):
        return self.connection.commit(*args, **kwargs)

    def disconnect(self):
        self.cursor.close()
        self.connection.close()

class DNS:
    """ Get the primary mail server for an E-mail address """
    @staticmethod
    def getPrimaryMX(domain):
        primary = (None, 99999)
        try:
            answers = dns.resolver.query(domain, 'MX')
            for r in answers:
                if r.preference < primary[1]:
                    primary = (r.exchange, r.preference)
            return primary[0]
        except dns.resolver.NoAnswer as e:
            return None

    """ Get the primary MX server for an E-mail address """
    @staticmethod
    def getPrimaryMXFromEmail(email):
        #matches = re.match('@([A-Za-z0-9\.-]+$)', email)
        matches = re.search(r'@[A-Za-z.-]+$', email, re.MULTILINE)
        theMatch = matches.group().lstrip('@')
        if matches:
            return DNS.getPrimaryMX(theMatch)
        else:
            return None
