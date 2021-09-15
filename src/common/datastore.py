# coding: utf-8
#
import sys
import sqlite3

__app_name__ = 'Lab183 DataStore Module'
__author__ = 'Robert L. Carr'
__copyright__ = 'Copyright 2016,2017 Lab183'
__credits__ = ["Robert L. Carr"]
__maintainer__ = 'Robert L. Carr'
__email__ = 'dev@lab183.com'
__license__ = 'MIT'


class DataStore(object):

    def __init__(self, dbpath):
        self.dbpath = dbpath

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def _connect(self):
        conn = sqlite3.connect(self.dbpath, isolation_level=None)

        # the default cursor returns the data in a tuple of tuples.
        # we want to use a dictionary cursor so the data is sent in
        # the form of Python dictionaries.
        # this way we can refer to the data by their column names.
        conn.row_factory = self.dict_factory

        # this makes sure that strings retrieved are returned as UTF-8
        # instead of Unicoide
        conn.text_factory = str

        return conn

    def clean_name(self, some_var):
        return ''.join(char for char in some_var if char.isalnum())

    def version(self):
        conn = self._connect()
        sql = "SELECT SQLITE_VERSION()"
        rsp = self.do_query(sql)
        return "SQLite version: %s" % rsp

    def do_query(self, sql, params=None, domany=False):
        conn = self._connect()
        try:
            c = conn.cursor()
            if params is None:
                if domany is False:
                    c.execute(sql)
                else:
                    c.executemany(sql)
            else:
                if domany is False:
                    c.execute(sql, params)
                else:
                    c.executemany(sql, params)

            if sql[:6].lower() == 'select':
                rows = c.fetchall()
                c.close()
                return rows
            elif sql[:6].lower() == 'update':
                conn.commit()
                return c.rowcount
            elif sql[:6].lower() == 'insert':
                conn.commit()
                new_id = c.lastrowid
                c.close()
                return new_id
            else:
                new_id = c.lastrowid
                conn.commit()
                c.close()
                return new_id
        except sqlite3.Error as e:
            if conn:
                conn.rollback()

            print(f"Error {e.args[0]}:")
            sys.exit(1)

    def escape_string(self, v):
        t = str(v)
        return t.replace("'", "''")
