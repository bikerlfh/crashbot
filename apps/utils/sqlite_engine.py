# Standard Library
import os
import sqlite3


class SQLiteEngine:
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, database):
        # validate dir path
        directory = os.path.dirname(database)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.conn = sqlite3.connect(database)
        self.cursor = self.conn.cursor()

    def execute(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)

    def executemany(self, query, params):
        self.cursor.executemany(query, params)

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
