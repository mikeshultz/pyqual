""" Various items we'll need later """
import psycopg2
from psycopg2 import extras as pg_extras

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

class Updated(object): pass
class Inserted(object): pass

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