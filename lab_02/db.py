# from typing import Any, Dict, List
# from flask import g
from psycopg2 import connect as pg_connect, ProgrammingError, InterfaceError
from psycopg2.extras import RealDictCursor as PostgresDictCursor
from pymysql import connect as my_connect
from pymysql.cursors import DictCursor as MySQLDictCursor
import os
import logging

_logger = logging.getLogger(__name__)


class DB:
    host = os.environ['DB_HOST'] or '127.0.0.1'
    port = os.environ.get('DB_PORT', None)
    database = os.environ['DB_NAME'] or None
    user = os.environ['DB_USER'] or None
    password = os.environ['DB_PASS'] or None
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
        pass

    def load(self, query: str, params: tuple = None) -> dict:
        self.cursor.execute(query, params)
        result = self.cursor.fetchall()
        if result:
            return {
                'headers': list(dict(result[0]).keys()),
                'data': [dict(row) for row in result]
            }
        return {}


class Postgres(DB):
    """
    Реалізація інтерфейсу БД для Postgres
    """
    port = os.environ.get('DB_PORT', 5432)

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


class MySQL(DB):
    """
    Реалізація інтерфейсу БД для MySQL
    """
    port = os.environ.get('DB_PORT', 3306)

    def connect(self):
        self.connection = my_connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
            cursorclass=MySQLDictCursor
        )
        self.cursor = self.connection.cursor()


database_classes = {
    'Postgres': Postgres,
    'MySQL': MySQL,
}

