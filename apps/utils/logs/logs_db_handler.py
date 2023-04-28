# Standard Library
from datetime import datetime, timedelta
from typing import Optional

# Internal
from apps.utils.patterns.singleton import Singleton
from apps.utils.sqlite_engine import SQLiteEngine


class LogsDBHandler(SQLiteEngine, metaclass=Singleton):
    def __init__(self):
        super().__init__("data/logs.db")
        self.create_table()

    def create_table(self):
        self.execute(
            """CREATE TABLE IF NOT EXISTS Logs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT,
                level TEXT,
                app TEXT,
                timestamp TEXT)"""
        )
        self.commit()

    def insert_log(
        self,
        *,
        message: str | dict,
        level: str,
        app: str,
        timestamp: Optional[datetime] = None
    ):
        if isinstance(message, dict):
            message = str(message)
        if not timestamp:
            timestamp = datetime.now()
        timestamp = timestamp.strftime(self.TIMESTAMP_FORMAT)
        sql_ = """INSERT INTO Logs (message, level, app, timestamp) VALUES (?, ?, ?, ?)"""
        self.execute(sql_, (message, level, app, timestamp))
        self.commit()

    def get_logs(self, *, timestamp: str = None):
        params = None
        sql_ = """SELECT * FROM Logs"""
        if timestamp:
            params = (timestamp,)
            sql_ = """SELECT * FROM Logs WHERE timestamp = ?"""
        self.execute(sql_, params)
        return self.fetchall()

    def delete_logs(self, days):
        now = datetime.now()
        delta = timedelta(days=days)
        cutoff = (now - delta).strftime(self.TIMESTAMP_FORMAT)
        self.execute("""DELETE FROM Logs WHERE timestamp < ?""", (cutoff,))
        self.commit()
