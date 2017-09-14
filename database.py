#! python 3
# --*-- encoding: UTF-8 --*--

import os
import sqlite3
import contextlib


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
        sqlstr = '''CREATE TABLE info (
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

    def save_info(self, start_date, end_date, full_image_url, copyright):
        copyright = copyright.replace("'", "''")
        self._db_cur.execute("INSERT INTO info VALUES('%s', '%s', '%s', '%s')" \
                             % (start_date, end_date, full_image_url, copyright))

        if self._auto_commit:
            self._db_conn.commit()

    def get_copyright(self, startdate):
        copyright_text = 'not found!'
        sql = "SELECT copyright FROM info WHERE startdate='{}'".format(startdate)
        self._db_cur.execute(sql)
        r = self._db_cur.fetchall()
        if len(r) > 0:
            copyright_text = r[0][0]

        return copyright_text

    def get_fullImageUrl(self, startdate):
        fullImageUrl_text = 'not found!'
        sql = "SELECT fullImageUrl FROM info WHERE startdate='{}'".format(startdate)
        self._db_cur.execute(sql)
        r = self._db_cur.fetchall()
        if len(r) > 0:
            fullImageUrl_text = r[0][0]

        return fullImageUrl_text

    def record_exist(self, startdate):
        sql = "SELECT 1 FROM info WHERE startdate='{}'".format(startdate)
        self._db_cur.execute(sql)
        r = self._db_cur.fetchall()
        return len(r) > 0

    def commit(self):
        self._db_conn.commit()