#! python 3
# --*-- encoding: UTF-8 --*--

import os
import sqlite3
import contextlib
from dataclasses import dataclass
from typing import NamedTuple


@dataclass
class ImageInfo:
    startdate: str
    fullstartdate: str
    enddate: str
    url: str
    copyright: str


class WallpaperDatabase:
    """ 数据库调用接口
    """

    def __init__(self, path, auto_commit=True):
        self._auto_commit = auto_commit
        self._path = path
        self._db_conn = None
        self._db_cur = None
        if not os.path.exists(os.path.join(self._path, self.db_name)):
            self.create()

    @property
    def db_name(self):
        return "wallpaper.db"

    def create(self):
        sqlstr = '''CREATE TABLE ImageInfo (
                startdate    TEXT,
                enddate      TEXT,
                fullImageUrl TEXT UNIQUE
                      PRIMARY KEY,
                copyright    TEXT
                );'''
        db_conn = sqlite3.connect(os.path.join(self._path, self.db_name))
        db_conn.execute(sqlstr)

    def set_auto_commit(self, is_auto=True):
        self._auto_commit = is_auto

    @contextlib.contextmanager
    def open_db_context(self):
        self.open()
        yield
        self.close()

    def open(self):
        self._db_conn = sqlite3.connect(os.path.join(self._path, self.db_name))
        self._db_cur = self._db_conn.cursor()

    def close(self):
        if not self._auto_commit:
            self.commit()
        self._db_conn.close()

    def save_info(self, info: ImageInfo):
        info.copyright = info.copyright.replace("'", "''")
        self._db_cur.execute(f"INSERT INTO ImageInfo VALUES('{info.startdate}', '{info.enddate}', "
                             f"'{info.url}', '{info.copyright}')")
        if self._auto_commit:
            self._db_conn.commit()

    def get_content_by_startdate(self, startdate, field):
        content = 'not found!'
        sql = f"SELECT {field} FROM ImageInfo WHERE startdate='{startdate}'"
        self._db_cur.execute(sql)
        r = self._db_cur.fetchall()
        if r:
            content = r[0][0]

        return content

    def record_exist(self, startdate):
        sql = f"SELECT 1 FROM ImageInfo WHERE startdate='{startdate}'"
        self._db_cur.execute(sql)
        r = self._db_cur.fetchall()
        return len(r) > 0

    def commit(self):
        self._db_conn.commit()
