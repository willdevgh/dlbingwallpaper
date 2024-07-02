#! python 3
# --*-- encoding: UTF-8 --*--

import os
import logging
import sqlite3
import contextlib
from collections import namedtuple

FULLSTARTDATE, ENDDATE, URL, COPYRIGHT, COPYRIGHTLINK, TITLE = 'fullstartdate', 'enddate', 'url', 'copyright', 'copyrightlink', 'title'
ImageInfo = namedtuple('ImageInfo', [FULLSTARTDATE, ENDDATE, URL, COPYRIGHT, COPYRIGHTLINK, TITLE])

logger = logging.getLogger(__name__)


class WallpaperDatabase:
    """ 数据库调用接口
    """

    def __init__(self, path, auto_commit=True):
        self._auto_commit = auto_commit
        self._path = path
        self._db_conn = None
        self._db_cur = None
        if not os.path.exists(os.path.join(self._path, self.db_name)):
            logger.info(f"database file(*.db) not exist! create database file in path: {self._path}")
            self.create()

    @property
    def db_name(self):
        return "wallpaper.db"
    
    @property
    def table_name_image_info(self):
        return "TblImageInfo"

    def create(self):
        sqlstr = f'''CREATE TABLE IF NOT EXISTS {self.table_name_image_info} (
                fullstartdate   TEXT,
                enddate    TEXT UNIQUE PRIMARY KEY,
                url    TEXT,
                copyright    TEXT,
                copyrightlink    TEXT,
                title    TEXT,
                data    BLOB
                );'''
        logger.debug(sqlstr)
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

    def save_info(self, info: ImageInfo, data: bytes) -> bool:
        try:
            #self._db_cur.execute(f"INSERT INTO {self.table_name_image_info} VALUES('{fullstartdate}', '{enddate}', '{url}', '{copyright}', '{copyrightlink}', '{title}', {data})")
            sqlstr = f"INSERT INTO {self.table_name_image_info} VALUES(?,?,?,?,?,?,?);"
            logger.debug(sqlstr)
            self._db_cur.execute(sqlstr, (info.fullstartdate, info.enddate, info.url, info.copyright.replace("'", "''"), info.copyrightlink, info.title, data))
            if self._auto_commit:
                self._db_conn.commit()
            
            return True
        except sqlite3.DatabaseError as e:
            logger.error(f"sqlite3.DatabaseError: errorcode: {e.sqlite_errorcode}, errorname: {e.sqlite_errorname}")
            return False

    def get_content_by_enddate(self, enddate, field):
        sqlstr = f"SELECT {field} FROM {self.table_name_image_info} WHERE enddate='{enddate}'"
        logger.debug(sqlstr)
        self._db_cur.execute(sqlstr)
        r = self._db_cur.fetchone()
        return None if r is None else r[0]
    
    def get_record_by_enddate(self, enddate) -> tuple[ImageInfo, bytes]:
        sqlstr = f"SELECT * FROM {self.table_name_image_info} WHERE enddate='{enddate}'"
        logger.debug(sqlstr)
        self._db_cur.execute(sqlstr)
        r = self._db_cur.fetchone()
        info = ImageInfo(*r[:-1])
        return info, r[6]

    def record_exist(self, enddate):
        sqlstr = f"SELECT 1 FROM {self.table_name_image_info} WHERE enddate='{enddate}'"
        logger.debug(sqlstr)
        self._db_cur.execute(sqlstr)
        r = self._db_cur.fetchone()
        return r is not None

    def commit(self):
        self._db_conn.commit()
