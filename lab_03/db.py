from psycopg2 import connect as pg_connect, ProgrammingError, InterfaceError
from psycopg2.extras import RealDictCursor as PostgresDictCursor
import os
import logging

_logger = logging.getLogger(__name__)


class Postgres:
    host = os.environ.get('POSTGRES_HOST', '127.0.0.1')
    port = os.environ.get('POSTGRES_PORT', 5432)
    database = os.environ['POSTGRES_DB'] or None
    user = os.environ['POSTGRES_USER'] or None
    password = os.environ['POSTGRES_PASSWORD'] or None
    connection = None
    cursor = None

    def __init__(self, host=None, port=None, database=None, user=None, password=None, **kwargs):
        if host is not None:
            self.host = host
        if port is not None:
            self.port = int(port)
        if database is not None:
            self.database = database
        if user is not None:
            self.user = user
        if password is not None:
            self.password = password
        if not all([self.host, self.port, self.database, self.user, self.password]):
            raise InterfaceError("Invalid database connection credentials, please set all envvars before using DB")
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)
        # connect to db
        self.connect()

    def connect(self):
        self.connection = pg_connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
            cursor_factory=PostgresDictCursor
        )
        self.cursor = self.connection.cursor()

    def get_table(self, query: str, params: tuple = None) -> dict:
        self.cursor.execute(query, params)
        result = self.cursor.fetchall()
        if result:
            return {
                'headers': list(dict(result[0]).keys()),
                'data': [dict(row) for row in result]
            }
        return {}

    def get_one(self, query: str, params: tuple = None) -> dict:
        self.cursor.execute(query, params)
        result = self.cursor.fetchone()
        if result:
            _logger.info(f"GET_Q: {result}")
            return dict(result)
        return {}
