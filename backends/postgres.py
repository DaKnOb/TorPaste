import psycopg2
from contextlib import contextmanager
from functools import wraps
from itertools import groupby
from operator import itemgetter
from os import environ

from backends.exceptions import ErrorException

_ENV_DATABASE_CONNECTION = 'TP_BACKEND_POSTGRES_DATABASE_CONNECTION'


class _Db(object):
    _paramstyle = None
    _connection = None

    @classmethod
    @contextmanager
    def _get_cursor(cls, commit):
        cursor = cls._connection.cursor()

        yield cursor

        if commit:
            cls._connection.commit()

    @classmethod
    def read_cursor(cls):
        return cls._get_cursor(commit=False)

    @classmethod
    def write_cursor(cls):
        return cls._get_cursor(commit=True)

    @classmethod
    def prepare_sql(cls, sql):
        return sql.replace('?', cls._paramstyle)

    @classmethod
    def connect(cls, connection, paramstyle):
        cls._connection = connection
        cls._paramstyle = paramstyle


def _getenv_required(key):
    try:
        return environ[key]
    except KeyError:
        raise ErrorException(
            'Required environment variable %s not set' % key)


def _wrap_postgres_exception(func):
    @wraps(func)
    def _adapt_exception_types(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except psycopg2.Error as ex:
            print(ex)
            raise ErrorException(
                'Error while communicating with the Postgres database'
            ) from ex

    return _adapt_exception_types


@_wrap_postgres_exception
def initialize_backend():
    _Db.connect(psycopg2.connect(
        _getenv_required(_ENV_DATABASE_CONNECTION)),
        paramstyle='%s')

    with _Db.write_cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pastes (
              id TEXT,
              content TEXT,
              PRIMARY KEY (id))
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pastes_metadata (
              id TEXT,
              key TEXT,
              value TEXT,
              PRIMARY KEY (id, key))
        ''')


@_wrap_postgres_exception
def new_paste(paste_id, paste_content):
    with _Db.write_cursor() as cursor:
        cursor.execute(_Db.prepare_sql('''
            INSERT INTO pastes (id, content) VALUES (?, ?)
        '''), [paste_id, paste_content])


@_wrap_postgres_exception
def update_paste_metadata(paste_id, metadata):
    with _Db.write_cursor() as cursor:
        cursor.execute(_Db.prepare_sql('''
            DELETE FROM pastes_metadata WHERE id = ?
        '''), [paste_id])
        cursor.executemany(_Db.prepare_sql('''
            INSERT INTO pastes_metadata VALUES (?, ?, ?)
        '''), [(paste_id, key, value) for (key, value) in metadata.items()])


@_wrap_postgres_exception
def does_paste_exist(paste_id):
    with _Db.read_cursor() as cursor:
        cursor.execute(_Db.prepare_sql('''
            SELECT 1 FROM pastes WHERE id = ?
        '''), [paste_id])
        row = cursor.fetchone()
    return row is not None


@_wrap_postgres_exception
def get_paste_contents(paste_id):
    with _Db.read_cursor() as cursor:
        cursor.execute(_Db.prepare_sql('''
            SELECT content FROM pastes WHERE id = ?
        '''), [paste_id])
        row = cursor.fetchone()
    return row[0] if row else None


@_wrap_postgres_exception
def get_paste_metadata(paste_id):
    with _Db.read_cursor() as cursor:
        cursor.execute(_Db.prepare_sql('''
            SELECT key, value FROM pastes_metadata WHERE id = ?
        '''), [paste_id])
        rows = cursor.fetchall()
    return {key: value for (key, value) in rows}


@_wrap_postgres_exception
def get_paste_metadata_value(paste_id, key):
    with _Db.read_cursor() as cursor:
        cursor.execute(_Db.prepare_sql('''
            SELECT value FROM pastes_metadata WHERE id = ? AND key = ?
        '''), [paste_id, key])
        row = cursor.fetchone()
    return row[0] if row else None


def _filters_match(metadata, filters, fdefaults):
    for metadata_key, filter_value in filters.items():
        try:
            metadata_value = metadata[metadata_key]
        except KeyError:
            metadata_value = fdefaults.get(metadata_key)

        if metadata_value != filter_value:
            return False

    return True


def _get_all_paste_ids(filters, fdefaults):
    with _Db.read_cursor() as cursor:
        cursor.execute(_Db.prepare_sql('''
            SELECT id, key, value FROM pastes_metadata
            UNION
            SELECT id, '', '' FROM pastes
        '''))
        rows = cursor.fetchall()

    for paste_id, rows in groupby(rows, itemgetter(0)):
        metadata = {key: value for (_, key, value) in rows}
        if _filters_match(metadata, filters, fdefaults):
            yield paste_id


@_wrap_postgres_exception
def get_all_paste_ids(filters={}, fdefaults={}):
    return list(_get_all_paste_ids(filters, fdefaults)) or ['none']
