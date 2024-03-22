# from typing import Any, Dict, List
from psycopg2 import connect as pg_connect, ProgrammingError, InterfaceError
# from psycopg2.extras import RealDictCursor
from pyodbc import connect as odbc_connect
# from flask import g
import os
import logging

_logger = logging.getLogger(__name__)


class DB:
    host = os.environ['PGDB_HOST'] or '127.0.0.1'
    port = os.environ['PGDB_PORT'] or '5432'
    database = os.environ['PGDB_NAME'] or None
    user = os.environ['PGDB_USER'] or None
    password = os.environ['PGDB_PASS'] or None
    odbc_driver = os.environ['PGDB_ODBC_DRIVER'] or None
    connection = None
    cursor = None

    def __init__(self, host=None, port=None, database=None, user=None, password=None, **kwargs):
        if host is not None:
            self.host = host
        if port is not None:
            self.port = port
        if database is not None:
            self.database = database
        if user is not None:
            self.user = user
        if password is not None:
            self.password = password
        if not all([self.host, self.port, self.database, self.user, self.password]):
            raise InterfaceError("Invalid database connection, please set all envvars before using DB")
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)
        # connect to db
        self.connect()

    def connect(self):
        pass


class DBPsycopg(DB):
    """
    Реалізація інтерфейсу БД для psycopg2
    """
    def connect(self):
        self.connection = pg_connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )
        self.cursor = self.connection.cursor()


class DBOdbc(DB):
    """
    Реалізація інтерфейсу БД для ODBC
    """
    def __init__(self, **kwargs):
        if 'odbc_driver' in kwargs:
            self.odbc_driver = kwargs['odbc_driver']
        if not self.odbc_driver:
            raise InterfaceError("Invalid database connection, please define odbc_driver before using DB")
        super().__init__(**kwargs)

    def connect(self):
        conn_str = (
            f"DRIVER={self.odbc_driver};"
            f"DATABASE={self.database};"
            f"UID={self.user};"
            f"PWD={self.password};"
            f"SERVER={self.host};"
            f"PORT={self.port};"
        )
        self.connection = odbc_connect(conn_str)
        self.cursor = self.connection.cursor()


connection_classes = {
    'ODBC': DBOdbc,
    'Psycopg': DBPsycopg
}

